
import requests
import json
import base64



url = 'http://127.0.0.1:8889/api/7a45609a232b4a469b70ad15787724d3'



headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
    'Upgrade-Insecure-Requests': '1',
    # 'Content-Type': 'multipart/form-data'
}

# 与服务端交互
def service(api,data):
    try:
        r = requests.post(url, headers=headers, data={
            'api':api,
            'data':base64.b64encode( json.dumps(data).encode(encoding="utf-8"))
        }, timeout=10,verify=False)
        return r.json()

    except Exception as e:  
        return {
            'state': 'fail',
            'message': e
        }

def regist_tool(script_name, name, describe, tool_type, minutes_time):
    res = service('regist_tool', {'script_name':script_name, 'tool_name':name, 'tool_message':describe, 'tool_type':tool_type, 'minutes_time':minutes_time })
    return res

def get_check_data(script_name, number):
    res = service('get_check_data', {'script_name':script_name, 'number':number})
    return res

def save_data(datas):
    res = service('save_data', {'datas':datas})
    return res