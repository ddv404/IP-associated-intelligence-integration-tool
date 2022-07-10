import requests
import time
from tool import *
import json
from  shodan import Shodan


api_key = ''


# 对ip进行微步查询
def shodan_search_ip(ip):
  try:
    
    SHODAN_API_KEY = api_key
    shodan_api = Shodan(SHODAN_API_KEY)
    host_infos = shodan_api.host(ip).items()
    data = {}
    for host_info in host_infos:
        # print(host_info)
        key = host_info[0]
        val =  host_info[1]
        if key == 'data':
            new_data = []
            for va in val:
                if 'data' in va:
                    del va['data']
                if 'html' in va:
                    del va['html']
                
                new_data.append(va)
            
            data[key] = new_data
        else:
            data[key] = val

    # print(data)

    # exit(0)
    # print(response.json())
    return {
        'state':'success',
        'message':data
    }

  except Exception as e:      
        print(str(e))
        if 'No information available for that IP' in str(e):
            return {
                'state':'success',
                'message':str(e)
            }
        return {'state':'fail', 'message':e}
    
print(len(json.dumps(shodan_search_ip('89.248.168.215'))))
exit(0)



# 第一步注册脚本
regist_result = regist_tool('check_ip_shodan', 'shodan', 'shodan搜索ip', 'IP',2)
if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)


# 第二步获取待处理的数据
while True:
    ip_infos_result = get_check_data('check_ip_shodan',10)
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
        print(ip_info)
        ip = ip_info['ip']
        uuid = ip_info['uuid']
        shodan_result = shodan_search_ip(ip)
        if shodan_result['state'] == 'fail':
            print(shodan_result['message'])
            exit(0)


        save_datas.append({
            'uuid':uuid,
            'data':json.dumps(shodan_result['message'])
        })

    # 第四步保存数据
    if len(save_datas) > 0:
        save_data_result = save_data(save_datas)
        if save_data_result['state'] == 'fail':
            print(save_data_result['message'])
            time.sleep(10)

