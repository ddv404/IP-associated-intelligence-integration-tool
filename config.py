# 数据库相关配置
mysql_host = ''
mysql_user='root'
mysql_port=60603
mysql_password=''
mysql_database='ddv_ip_scan'


# web服务运行端口
web_port = 80
# web默认访问路径：http://ip:8889/html/login.html


# 脚本调用接口的路径 http://ip:port/api_key
api_key = '7a45609a232b4a469b70ad15787724d3'
# 脚本编写参照node内脚本


# 登录的账号
login_username = 'username_DDV'
# 登录的密码
login_password = 'password_DDV'


# 新工具注册进行，是否对已经存在的数据进行关联
new_regist_tool_link_old_data = True

# 限制数据长度。搜索时，单个数据长度超过该值，前端页面显示局部内容。
# 例如shodan的结果数据量都很大，这里设置1000，那么前端预览区域只显示一部分数据。可通过“查看全部内容”按钮查看所有内容。
# 该值越大，页面段响应的越慢。
one_show_data_length = 9999999
