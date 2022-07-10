#!/usr/bin/python3
 
import pymysql
from config import *
 
# 使用docker安装mysql 5.7数据库
#  docker run -p 60603:3306 --name scan_mysql -v /data/mysql_v/conf:/etc/mysql -v /data/mysql_v/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=passwoed -d mysql:5.7


# CREATE DATABASE IF NOT EXISTS ddv_ip_scan DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
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




# 初始化ip表
def init_ip_table(cursor):
    # ip表
    # id
    # uuid
    # number ip被标记查询的次数默认1
    # ip ip地址
    cursor.execute('''CREATE TABLE if not exists ip (
        id INTEGER AUTO_INCREMENT PRIMARY KEY, 
        uuid VARCHAR(32) default '',
        number INTEGER,
        ip VARCHAR(32),
        create_date datetime default CURRENT_TIMESTAMP,
        update_date datetime ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE(ip)
        )''')

# 初始化ip_port表
def init_ip_port_table(cursor):
    # ip端口表
    # ip_port
    # id
    # uuid
    # ip_uuid ip表对应的uuid
    # ip    ip地址
    # port  端口号
    # service   端口服务
    cursor.execute('''CREATE TABLE if not exists ip_port (
        id INTEGER AUTO_INCREMENT PRIMARY KEY, 
        uuid VARCHAR(32) default '',
        ip_uuid VARCHAR(32),
        ip VARCHAR(32),
        port INTEGER,
        protocol VARCHAR(32),
        service VARCHAR(32),
        create_date datetime default CURRENT_TIMESTAMP,
        UNIQUE(ip,port)
        )''')


# 初始化工具表
def init_tool_table(cursor):
    # tool工具表
    # id
    # uuid
    # name  工具名称
    # message   工具描述
    # minutes_time 工具最大运行时间，超过这个时间将为重制状态
    # data_type ip|port 
    cursor.execute('''CREATE TABLE if not exists tool (
        id INTEGER AUTO_INCREMENT PRIMARY KEY, 
        uuid VARCHAR(32) default '',
        script_name VARCHAR(320),
        name VARCHAR(320),
        message VARCHAR(2000),
        data_type VARCHAR(32),
        minutes_time INTEGER default 10,
        create_date datetime default CURRENT_TIMESTAMP,
        UNIQUE(script_name)
        )''')



# 初始化工具表数据表
def init_tool_data_table(cursor):
    # data使用工具获取的数据
    # id
    # uuid
    # data_uuid     关联数据的uuid
    # tool_name 关联工具的名称
    # data  使用工具处理后得到的数据
    cursor.execute('''CREATE TABLE if not exists tool_data (
        id INTEGER AUTO_INCREMENT PRIMARY KEY, 
        uuid VARCHAR(32) default '',
        data_uuid VARCHAR(32),
        tool_uuid VARCHAR(516),
        data longtext ,
        create_date datetime default CURRENT_TIMESTAMP,
        update_date datetime ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE(data_uuid,tool_uuid)
        )''')

# 初始化表
def init_table():
    (conn,cursor) = get_mysql_client()

    # 初始化ip表
    init_ip_table(cursor)

    init_ip_port_table(cursor)

    init_tool_table(cursor)

    init_tool_data_table(cursor)

    conn.commit()

    # 关闭数据库连接
    conn.close()

init_table()