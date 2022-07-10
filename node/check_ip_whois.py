import io
import sys
import socket
import struct
import json
from tool import *
import time
# pip3 install ipwhois 
from ipwhois import IPWhois




regist_result = regist_tool('check_ip_whois', 'IP_WHOIS', '对IP地址进行whois查询', 'IP',2)
if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)




while True:
    ip_infos_result = get_check_data('check_ip_whois',2)
    if ip_infos_result['state'] == 'fail':
        print(ip_infos_result['message'])
        time.sleep(10)
        continue

    ip_infos = ip_infos_result['message']
    if len(ip_infos) == 0:
        print("暂无新数据，等待10秒后再运行")
        time.sleep(10)
        continue

    save_data_infos = []
    for ip_info in ip_infos:
        print(ip_info)
        # continue
        ip = ip_info['ip']
        uuid = ip_info['uuid']
                
        try:
            obj = IPWhois(ip)
            data_str = json.dumps(obj.lookup_whois())
        except Exception as e:
            print(e)
            data_str = "NONE:%s"%(e)
        print(data_str)
        save_data_infos.append({
            'data': data_str,
            'uuid': uuid
        })
        print('----------')
    save_data_result = save_data(save_data_infos)
    if save_data_result['state'] == 'fail':
        print(save_data_result['message'])
        time.sleep(10)