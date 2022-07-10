# 每过5分钟刷新一下数据的状态
# 如果某个数据被执行操作指定时间了，那么这个数据的状态装备重制
from tool import *
import datetime

def flust_state():
    (con,cur) = get_mysql_client()

    cur.execute("select tool_data.uuid,update_date,minutes_time from tool_data,tool where tool_data.tool_uuid = tool.uuid and  data = 'ing..'")
    tool_datas = cur.fetchall()
    for tool_data in tool_datas:
        print(tool_data)
        uuid = tool_data['uuid']
        update_date = tool_data['update_date']
        update_timestamp = int(update_date.timestamp())
        minutes_time = int(tool_data['minutes_time'])
        # print(update_timestamp)


        datetime_object = datetime.datetime.now()
        now_timestamp = int(datetime_object.timestamp())
        # print(now_timestamp)
        if (now_timestamp - update_timestamp > minutes_time * 60):
            cur.execute("update tool_data set data = '' where uuid = %s and data = 'ing..'",(uuid, ))

    con.commit()
    con.close()


flust_state()    


# def test():
#     (con,cur) = get_mysql_client()
#     cur.execute('select * from tool_data where data like "%jquery-3.4.1.min.js%";')
#     res = cur.fetchall()
#     print(res)
    

#     con.commit()
#     con.close()

# test()    

