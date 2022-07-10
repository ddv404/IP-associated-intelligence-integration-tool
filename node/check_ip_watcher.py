import requests
import time
from tool import *
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

api_key = ''



headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
    'Upgrade-Insecure-Requests': '1',
    'Content-Type': 'application/json',
    'token':  api_key
}



# 对ip进行微步查询
def watcher_search_ip(ip):
  try:

    data = {
        "type": "data",
        "data": ip,
        "cursor": 0
    }   
    
    response = requests.post("https://feed.watcherlab.com/api/query/v1/gbt", headers=headers,json=data, timeout=10,verify=False)
    if response.status_code == 200:
        response_json = response.json()
        if response_json['code'] == 0:
            data = response_json['data']['object']
            return {
                'state':'success',
                'message':data
            }
        else:
            return {
                'state':'success',
                'message':response.json()
            }

    else:
      return {
        'state':'fail',
        'message': response.text()
      }
    

  except Exception as e:      
      return {'state':'fail', 'message':e}
    
# print(watcher_search_ip("220.205.224.60"))
# exit(0)



# 第一步注册脚本
regist_result = regist_tool('check_ip_watcher', 'WATCHER情报', 'FEED系统情报数据', 'IP',2)
if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)


# 第二步获取待处理的数据
while True:
    ip_infos_result = get_check_data('check_ip_watcher',2)
    if ip_infos_result['state'] == 'fail':
        print(ip_infos_result['message'])
        time.sleep(10)
        continue

    ip_infos = ip_infos_result['message']
    
    if len(ip_infos) == 0:
        print("暂无新数据，等待10秒后再运行")
        time.sleep(10)
        continue

    save_datas = []
    # 第三步对数据进行梳理
    for ip_info in ip_infos:
        ip = ip_info['ip']
        uuid = ip_info['uuid']
        watcher_result = watcher_search_ip(ip)
        if watcher_result['state'] == 'fail':
            print(watcher_result['message'])
            exit(0)


        save_datas.append({
            'uuid':uuid,
            'data':json.dumps(watcher_result['message'])
        })

    # 第四步保存数据
    if len(save_datas) > 0:
        save_data_result = save_data(save_datas)
        if save_data_result['state'] == 'fail':
            print(save_data_result['message'])
            time.sleep(10)

