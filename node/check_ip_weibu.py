import requests
import time
from tool import *
import json


api_key = ''


# 对ip进行微步查询
def weibub_search_ip(ip):
  try:
    url = "https://api.threatbook.cn/v3/scene/ip_reputation"

    query = {
      "apikey":api_key,
      "resource":ip,
      'lang':'zh'
    }

    response = requests.request("GET", url, params=query)
    # print(response.json())
    if response.status_code == 200:
        result_data = response.json()
        if result_data['response_code'] == 0:
            return {
                'state':'success',
                'message':response.json()
            }
        else:
            return {
                'state':'fail',
                'message':response.json()
            }

    else:
      return {
        'state':'fail',
        'message': response.text()
      }
  except Exception as e:      
      return {'state':'fail', 'message':e}
    



# 第一步注册脚本
regist_result = regist_tool('check_ip_weibu', '微步', '微步情报数据', 'IP',2)
if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)


# 第二步获取待处理的数据
while True:
    ip_infos_result = get_check_data('check_ip_weibu',10)
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
        weibu_result = weibub_search_ip(ip)
        if weibu_result['state'] == 'fail':
            print(weibu_result['message'])
            exit(0)


        save_datas.append({
            'uuid':uuid,
            'data':json.dumps(weibu_result['message'])
        })

    # 第四步保存数据
    if len(save_datas) > 0:
        save_data_result = save_data(save_datas)
        if save_data_result['state'] == 'fail':
            print(save_data_result['message'])
            time.sleep(10)

