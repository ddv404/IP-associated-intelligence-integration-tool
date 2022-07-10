# -*- coding: utf-8 -*-
import os
import pymysql
import re
from tool import *

import time



# 调用扫描命令
def run_cmd(ip):
    cmd = "docker run -it --ulimit nofile=20480:40960 --rm --name rustscan rustscan/rustscan:2.0.0 -a %s --range 1-65535 -t 5000 -- -Pn > rustscan_result/%s.txt"%(ip,ip)
    os.system(cmd)
    time.sleep(20)
    print('%s扫描完成'%(ip))    




    
# 解析rustscan扫描结果
def parse_rustscan_result(ip):
    lines = open("rustscan_result/%s.txt"%(ip)).readlines()
    lines = list(filter(lambda y: 'pen' in y and 'Discovered' not in y and "didn't find any open ports" not in y, map(lambda x: x.strip(), lines)))
    # lines1 = list(lines)
    Open_infos = list(filter(lambda x: 'Open' in x, lines))
    open_infos = list(filter(lambda x: 'open' in x and 'default' not in x, lines))
    # print(lines1)
    ports = []
    port_infos = []
    for line in open_infos:
        print(line)
        port_info = list(filter(lambda x: len(x) > 0, line.split(' ')))
        port = port_info[0].split("/")[0]

        if port not in ports:
            ports.append(port)


            port_infos.append({
                'port':port,
                'protocol':port_info[0].split("/")[1],
                'service':port_info[2],
            })
    
    for line in Open_infos:
        # line = line.replace("")
        line = re.sub('\x1b.*?m', '', line)
        # print(line)
        port_info = list(filter(lambda x: len(x) > 0, line.split(' ')))
        # print(port_info)
        port = port_info[1].split(":")[1]

        if port not in ports:
            ports.append(port)

            port_infos.append({
                'port':port,
                'protocol':'',
                'service':'',
            })
    

    return port_infos




regist_result = regist_tool('check_ip_all_port', '全端口扫描', '对IP地址进行全端口扫描', 'IP',10)

if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)







while True:
    ip_infos_result = get_check_data('check_ip_all_port',1)
    if ip_infos_result['state'] == 'fail':
        print(ip_infos_result['message'])
        time.sleep(10)
        # continue
        exit(0)

    ip_infos = ip_infos_result['message']

    if len(ip_infos) == 0:
        print("暂无新数据，等待10秒后再运行")
        time.sleep(10)
        # continue
        exit(0)


    for ip_info in ip_infos:
        print(ip_info)
        # exit(0)
        ip = ip_info['ip']
        tool_data_uuid = ip_info['uuid']

        # 查看结果文件是否已经存在，不存在则新建扫描
        file_path = "rustscan_result/%s.txt"%(ip)
        if not os.path.exists(file_path):
            # 对ip进行全端口扫描
            run_cmd(ip)
        # 获取扫描到的结果
        port_infos = parse_rustscan_result(ip)
        # print(port_infos)

        if len(port_infos) > 0:
            data = [{
                'uuid': tool_data_uuid,
                'data': port_infos
            }]
        else:
            data = [{
                'uuid': tool_data_uuid,
                'data': "NONE"
            }]
        print(data)
        save_data_result = save_data(data)
        if save_data_result['state'] == 'fail':
            print(save_data_result['message'])
            time.sleep(10)


        print('----------------------')
    

# docker run -it --ulimit nofile=20480:40960 --rm --name rustscan rustscan/rustscan:2.0.0 -a 117.73.8.111 --range 1-65535 -t 5000 -- -Pn 