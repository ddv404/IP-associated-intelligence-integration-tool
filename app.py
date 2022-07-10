from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import socket, struct
from tool import *
import base64
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from datetime import datetime, timedelta
from typing import Optional
from starlette import status
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI()


# 预定义内容
# 这里包含了安全认证类，秘钥，算法，过期时间的定义，以及两个验证model。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2558c818166b7a9563b93f7099f6f0f4caa6cf63b08e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# 模拟数据库
# 假设通过用户名从数据库中获取user的过程
USER_LIST = [
    User(username=login_username, password=login_password)
]

def get_user(username: str) -> User:
    # 伪数据库
    for user in USER_LIST:
        if user.username == username:
            return user


# 登录获取token
form_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "DDV"},
)


def create_token(user: User, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + expires_delta or timedelta(minutes=15)
    return jwt.encode(
        claims={"sub": user.username, "exp": expire},
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )


base_dir = os.path.dirname(os.path.abspath(__file__))
static_file_path = Path(base_dir, './html')

# 静态文件的路径
app.mount(path="/html", app=StaticFiles(directory=static_file_path))


# 设置允许访问的域名
origins = ["*"]  #也可以设置为"*"，即为所有。

# 设置跨域传参
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  # 允许跨域的headers，可以用来鉴别来源等作用。


# 前端认证接口
@app.post("/web/login")
def login(api: str = Form(...), data: str = Form(...)):

    # 判断传入的数据是否是json格式
    try:
        data_json = json.loads(str(base64.b64decode(data), 'utf-8'))
    except:
        return {
            'state': 'fail',
            'message': '参数data数据无效'
        }

    username = data_json['username']
    password = data_json['password']

    user: User = get_user(username)
    if not user or user.password != password:
        return {
            'state':'fail',
            'message':'账号或密码不正确'
        }
    access_token = create_token(user=user, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {
        'state':'success',
        'message':{"access_token": access_token, "token_type": "bearer"}
    }


# 认证token获取用户
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def token_to_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username, expire = payload.get("sub"), payload.get("exp")
        user = get_user(username)
        if user is None:
            raise JWTError
    except JWTError:
        raise credentials_exception
    return user


# web接口
@app.post("/web/index")
def login(api: str = Form(...), data: str = Form(...),user: User = Depends(token_to_user)):

    # 判断传入的数据是否是json格式
    try:
        data_json = json.loads(str(base64.b64decode(data), 'utf-8'))
    except:
        return {
            'state': 'fail',
            'message': '参数data数据无效'
        }

    print('/web/index')
    print(api)
    print(data_json)
    
    # 添加ip的借口
    if api == 'add_ip':
        if 'ips' in data_json and len(data_json['ips']) > 0 :
            ips = data_json['ips']
            (conn,cursor) = get_mysql_client()
            for ip in ips:
                if ip2long(ip) and ip.find(".") != -1 and len(ip.split(".")) == 4:

                    ip_uuid = get_uuid()
                    cursor.execute('''insert ignore into ip (uuid, ip, number) values (%s,%s,1)''',(ip_uuid, ip))
                    # 如果数据已经存在则对状态进行+1
                    if cursor.lastrowid == 0:
                        cursor.execute("update ip set number=number+1 where ip = %s",(ip,))
                    # 如果数据是新增的，则同步生成其他数据
                    else:
                        # 插入数据的时候，还需要根据工具类型，进行数据生成
                        # 此时需要生成针对ip的工具数据
                        cursor.execute("select * from tool where data_type = 'IP'")
                        ip_tools = cursor.fetchall()
                        for ip_tool in ip_tools:
                            tool_uuid = ip_tool['uuid']
                            cursor.execute("insert ignore into tool_data (uuid, data_uuid, tool_uuid) values (%s, %s, %s)",(get_uuid(), ip_uuid, tool_uuid))
            conn.commit()
            conn.close()

            return {
                'state':'success',
                'message':''
            }

        else:
            return {
                'state':'fail',
                'message':'参数不合规'
            }
    # 统计查询接口
    # page_number 查询页面
    # ip_like_val ip模糊查询的值
    # data_like_val 数据模糊查询的值
    # tool_uuids 要显示的工具uuid
    elif api == 'check_data':
        if 'page_number' in data_json and 'ip_like_val' in data_json and 'data_like_val' in data_json and 'tool_uuids' in data_json and 'page_ip_number' in data_json:
            page_number = data_json['page_number']
            ip_like_val = data_json['ip_like_val']
            data_like_val = data_json['data_like_val']
            tool_uuids = data_json['tool_uuids']
            page_ip_number = data_json['page_ip_number']

            (conn,cursor) = get_mysql_client()
            if page_number <= 0:
                page_number = 1

            pars = []
            sql = 'select ip.uuid,ip.ip from ip'

            if len(data_like_val) > 0:
                sql += ' inner join tool_data on ip.uuid = tool_data.data_uuid and ( data like "%%"%s"%%" or data like "%%"%s"%%")'
                pars.append(data_like_val)
                pars.append(str(data_like_val.encode('unicode_escape'),'utf-8').replace("\\","\\\\"))


            if len(ip_like_val) > 0 :
                sql += ' where ip.ip like "%%"%s"%%"'
                pars.append(ip_like_val)

            sql += ' order by ip.id desc limit %s,%s '
            # pars.append((page_number-1) * 10)
            # pars.append(10)

            pars.append((page_number-1) * page_ip_number)
            pars.append(page_ip_number)


            cursor.execute(sql, tuple(pars))

            ip_infos = cursor.fetchall()
            result_datas = []
            for ip_info in ip_infos:
                ip_uuid = ip_info['uuid']
                ip = ip_info['ip']

                sql1 = "select  tool_data.uuid as uuid, name, data from tool_data,tool where tool_data.data_uuid = %s and tool_data.tool_uuid = tool.uuid"
                pars1 = []
                pars1.append(ip_uuid)
                if len(tool_uuids) > 0:
                    sql1 += ' and tool.uuid in %s'
                    pars1.append(tool_uuids)

                cursor.execute(sql1, tuple(pars1))
                ip_datas = cursor.fetchall()
                new_ip_datas = []
                for ip_data in ip_datas:
                    data = ip_data['data']
                    uuid = ''
                    if data and len(data) > one_show_data_length:
                        data = data[0:one_show_data_length]
                        uuid = ip_data['uuid']
                    
                    new_ip_datas.append({
                        'name':ip_data['name'],
                        'data':data,
                        'uuid':uuid
                    })

                sql2 = "select  tool_data.uuid as uuid, name, ip_port.port as port, ip_port.service as service, data from ip_port,tool_data,tool where ip_port.ip_uuid = %s and ip_port.uuid = tool_data.data_uuid and tool_data.tool_uuid = tool.uuid"
                pars2 = []
                pars2.append(ip_uuid)
                if len(tool_uuids) > 0:
                    sql2 += ' and tool.uuid in %s'
                    pars2.append(tool_uuids)

                cursor.execute(sql2, tuple(pars2))
                port_datas = cursor.fetchall()
                new_port_datas = []
                for port_data in port_datas:
                    data = port_data['data']
                    uuid = ''
                    if data and len(data) > one_show_data_length:
                        data = data[0:one_show_data_length]
                        uuid = port_data['uuid']
                    
                    new_port_datas.append({
                        'name':port_data['name'],
                        'data':data,
                        'port':port_data['port'],
                        'service':port_data['service'],
                        'uuid':uuid
                    })

                result_datas.append({
                    'ip':ip,
                    'ip_datas':new_ip_datas,
                    'port_datas':new_port_datas
                })
            conn.commit()
            conn.close()

            return {
                'state':'success',
                'message':{
                    'datas':result_datas
                }
            }
        else:
            return {
                'state':'fail',
                'message':'包体参数异常'
            }

    # 加载指定数据
    elif api == 'show_content':
        if 'uuid' in data_json and len(data_json['uuid']) > 0:
            uuid = data_json['uuid']
            (conn,cursor) = get_mysql_client()
            cursor.execute("select data from tool_data where uuid = %s",(uuid,))
            data_infos = cursor.fetchall()
            if len(data_infos) == 0:
                return {
                    'state': 'fail',
                    'message': 'uuid参数无效'
                }
            data_info = data_infos[0]
            conn.commit()
            conn.close()

            return {
                'state':'success',
                'message':data_info
            }

    # 加载每个工具的执行进度
    elif api == 'progress':

        (con,cur) = get_mysql_client()
        cur.execute("select tool.name,tool.message,data from tool,tool_data where tool.uuid = tool_data.tool_uuid;")
        datas = cur.fetchall()
        names = list(set(map(lambda x: x['name'], datas)))
        result_datas = []
        for name in names:
            tool_datas = list(filter(lambda x: x['name'] == name ,datas))
            total = len(tool_datas)
            # data为None的为没有进行的
            # data为‘’的为没有进行的
            # data为ing..的为正在进行的
            # data为其他数据的为结束的
            none_number = len(list(filter(lambda x:  x['data'] == None or x['data'] == '',tool_datas)))
            ing_number = len(list(filter(lambda x:  x['data'] == 'ing..',tool_datas)))

            result_datas.append({
                'name': name,
                'total': total,
                'done': (total - none_number - ing_number),
                'ing': ing_number,
                'none': none_number
            })
        # 获取工具列表
        cur.execute("select uuid,name from tool")
        tool_infos = cur.fetchall()

        cur.execute("select count(id) as count from ip")
        ip_number = cur.fetchall()[0]['count']

        con.commit()
        con.close()

        return {
            'state': 'success',
            'message': {
                'count':ip_number,
                'progress':result_datas,
                'tool_infos':tool_infos
            }
        }


    return {
        'state':'fail',
        'message':'API参数不合规'
    }



# api接口
@app.post("/api/{path}")
def api(path:str,api: str = Form(...), data: str = Form(...)):

    # 判断访问路径是否有效
    if api_key != path :
        return {
            'state':'fail',
            'message': '无效的访问路径'
        }

    # 判断传入的数据是否是json格式
    try:
        data_json = json.loads(str(base64.b64decode(data), 'utf-8'))
    except:
        return {
            'state': 'fail',
            'message': '参数data数据无效'
        }

    
    print('/api/%s'%(path))
    print(api)
    print(data_json)
    

    # 注册工具
    if api == 'regist_tool':
        if 'script_name' in data_json and len(data_json['script_name']) > 0 and 'tool_name' in data_json and len(data_json['tool_name']) > 0 and 'tool_message' in data_json and len(data_json['tool_message']) > 0 and 'tool_type' in data_json and len(data_json['tool_type']) > 0 and 'minutes_time' in data_json and data_json['minutes_time'] > 0 :
            script_name = data_json['script_name']
            tool_name = data_json['tool_name']
            tool_message = data_json['tool_message']
            tool_type = data_json['tool_type']
            minutes_time = data_json['minutes_time']

            try:
                minutes_time = int(minutes_time)
                if minutes_time <= 0:
                    
                    return {
                        'state': 'fail',
                        'message': 'minutes_time err'
                    }
            except:
                return {
                    'state': 'fail',
                    'message': 'minutes_time err'
                }

            if tool_type not in ["IP","PORT"]:
                return (False,"tool_type只能是IP或PORT")
            (con,cur) = get_mysql_client()

            tool_uuid = get_uuid()
            cur.execute('''insert ignore into tool (uuid, script_name, name, message, data_type,minutes_time) values (%s,%s,%s,%s,%s,%s)''',(tool_uuid, script_name, tool_name, tool_message, tool_type,minutes_time))

            if new_regist_tool_link_old_data and cur.lastrowid != 0:
                if tool_type == 'IP':
                    cur.execute("select uuid from ip")
                    ip_infos = cur.fetchall()
                    for ip_info in ip_infos:
                        ip_uuid = ip_info['uuid']
                        cur.execute("insert ignore into tool_data (uuid, data_uuid, tool_uuid) values (%s, %s, %s)",(get_uuid(), ip_uuid, tool_uuid))

                elif tool_type == "PORT":
                    cur.execute("select uuid from ip_port")
                    ip_port_infos = cur.fetchall()
                    for ip_port_info in ip_port_infos:
                        ip_port_uuid = ip_port_info['uuid']
                        cur.execute("insert ignore into tool_data (uuid, data_uuid, tool_uuid) values (%s, %s, %s)",(get_uuid(), ip_port_uuid, tool_uuid))
            con.commit()
            con.close()

            return {
                'state': 'success',
                'message': 'ok'
            }
            

    # 获取数据
    elif api == 'get_check_data':
        if 'script_name' in data_json and len(data_json['script_name']) > 0 and  'number' in data_json and data_json['number'] > 0 :
            script_name = data_json['script_name']
            number = data_json['number']


            (con,cur) = get_mysql_client()
            cur.execute("select uuid,data_type from tool where script_name = %s",(script_name,))
            tool_infos = cur.fetchall()
            if len(tool_infos) == 0:
                return {
                    'state': 'fail',
                    'message': 'script_name名称不正确，请填写与regist_tool内script_name相同值'
                }

            tool_info = tool_infos[0]
            tool_uuid = tool_info['uuid']
            data_type = tool_info['data_type']

            if data_type == 'IP':
                cur.execute("select ip.ip as ip, tool_data.uuid as uuid from ip,tool_data where ip.uuid = tool_data.data_uuid and tool_data.tool_uuid ='%s' and (tool_data.data is null or tool_data.data = '') limit %s"%(tool_uuid,number))
            elif data_type == 'PORT':
                cur.execute("select ip_port.ip as ip, ip_port.port as port,  tool_data.uuid as uuid from ip_port,tool_data where ip_port.uuid = tool_data.data_uuid and tool_data.tool_uuid = '%s' and (tool_data.data is null or tool_data.data = '') limit %s"%(tool_uuid,number))
            # 获取所有结果
            res = cur.fetchall()
            # 获取数据后，还需要修改当前数据的状态
            tool_data_uuids = list(map(lambda x: x['uuid'] , res))
            if len(tool_data_uuids) > 0:
                cur.execute("update tool_data set data = 'ing..' where uuid in %s",(tuple(tool_data_uuids),))
            con.commit()
            con.close()

            return {
                'state': 'success',
                'message': res
            }


    # 保存数据
    elif api == 'save_data':
        if 'datas' in data_json and len(data_json['datas']) > 0 :

            data_infos = data_json['datas']
            (con,cur) = get_mysql_client()
                
            for data_info in data_infos:
                data = data_info['data']
                tool_data_uuid = data_info['uuid']

                # 如果data是数组，并且数组中的元素包含port,protocol,service
                # 那么
                # 端口数据需要添加到端口表中
                # 同时生成关联数据
                # 并修改对应的状态
                if isinstance(data, list) and len(data) > 0:
                    # 取第一个数据看下是否包含port,protocol,service
                    if 'port' in data[0] and 'protocol' in data[0] or 'service' in data[0]:
                        # 获取对应ip表中的ip和uuid
                        cur.execute("select ip.uuid as uuid,ip from ip,tool_data where ip.uuid = tool_data.data_uuid and tool_data.uuid = %s",(tool_data_uuid,))
                        ip_infos = cur.fetchall()
                        if len(ip_infos) == 0:
                            return {
                                'state':'fail',
                                'message': 'uuid有误'
                            }
                        ip_uuid = ip_infos[0]['uuid']
                        ip = ip_infos[0]['ip']

                        for port_info in data:
                            port = port_info['port']
                            protocol = port_info['protocol']
                            service = port_info['service']

                            port_uuid = get_uuid()

                            cur.execute('''insert ignore into ip_port
                            (
                                uuid,
                                ip_uuid,
                                ip,
                                port,
                                protocol,
                                service
                            )
                            values
                            (%s, %s, %s, %s, %s, %s)
                            ''',( port_uuid, ip_uuid, ip, port, protocol, service))
                                        
                            if cur.lastrowid != 0:
                                # 插入port的时候同时生成关联工具的数据
                                cur.execute("select * from tool where data_type = 'PORT'")
                                ports_tools = cur.fetchall()
                                for ports_tool in ports_tools:
                                    tool_uuid = ports_tool['uuid']
                                    cur.execute("insert ignore into tool_data (uuid, data_uuid, tool_uuid) values (%s, %s, %s)",(get_uuid(), port_uuid, tool_uuid))
                    data_str = json.dumps(data)
                    # if len(data_str) > 5000:
                        # data_str = data_str[0:5000]
                    cur.execute("update tool_data set data = %s where uuid = %s",(data_str, tool_data_uuid))
                else:
                    cur.execute("update tool_data set data = %s where uuid = %s",(data, tool_data_uuid))
                
            con.commit()
            con.close()

            return {
                'state': 'success',
                'message': ''
            }

    
    return {
        'state':'fail',
        'message':'参数不合规'
    }

    
if __name__ == '__main__':
    uvicorn.run(
        app='app:app',
        host="0.0.0.0",
        port=web_port,
        workers=4,
        reload=True,
        debug=True)