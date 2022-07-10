
import uuid
from db_init import *
import socket, struct

def get_uuid():
    return str(uuid.uuid4()).replace("-",'')

def get_mysql_client():
    # 打开数据库连接
    conn = pymysql.connect(host=mysql_host,
                        user=mysql_user,
                        port=mysql_port,
                        password=mysql_password,
                        database=mysql_database,
                        cursorclass=pymysql.cursors.DictCursor)
    
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    return (conn,cursor)



def ip2long(ip):
    try:

        packedIP = socket.inet_aton(ip)
        return struct.unpack("!L", packedIP)[0]
    except Exception as e:
        print(e)
        return