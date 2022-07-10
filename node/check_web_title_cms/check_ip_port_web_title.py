# -*- coding:UTF-8 -*-
import gevent
from gevent import monkey
monkey.patch_all(select=False)

from bs4 import BeautifulSoup
import json
import os
import requests

from tool import *

from TideFinger import *


from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
    'Upgrade-Insecure-Requests': '1'
}



def request_url(port_info):
    print(port_info)
    ip = port_info['ip']
    port = port_info['port']
    uuid = port_info['uuid']
    try:
        print('run http...')
        #print(url)
        r = requests.get("http://%s:%s"%(ip, port), headers=headers, timeout=10,verify=False)
        soup = BeautifulSoup(r.content, 'lxml') 
        if soup.title:
            title=soup.title.string
        else:
            title = ''        
        print("----")
        title = title.replace("\r\n","").replace("\n","").replace("\n","").replace("\t","")#,.replace(" ",""),
        print(title)
        
        return {
            'uuid': uuid,
            'agreement': 'http',
            'web_title': title,
            'header':r.headers,
            'body':r.text,
            'respone_code': r.status_code
        }

    except Exception as e:   
        print('run https...')
        try:
            #print(url)
            r = requests.get("https://%s:%s"%(ip, port), headers=headers, timeout=10,verify=False)
            soup = BeautifulSoup(r.content, 'lxml') 
            if soup.title:
                title=soup.title.string
            else:
                title = ''        
            print("----")
            title = title.replace("\r\n","").replace("\n","").replace("\n","").replace("\t","")#,.replace(" ",""),
            print(title)
            
            return {
                'uuid': uuid,
                'agreement': 'https',
                'web_title': title,
                'header':r.headers,
                'body':r.text,
                'respone_code': r.status_code
            }

        except Exception as e:   
            print(e)
            return {
                'uuid': uuid,
                'agreement': '',
                'web_title': None,
                'header':None,
                'body':None,
                'respone_code': 0
            }   




regist_result = regist_tool('check_ip_port_web_title', 'WEB标题', '获取目标站点标题', 'PORT',2)

if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)


# 对没有web信息的 进行实时获取
def request_web_supplement_web_info():
    while True:
        port_infos_result = get_check_data('check_ip_port_web_title', 10)
        if port_infos_result['state'] == 'fail':
            print(port_infos_result['message'])
            time.sleep(10)
            # continue
            exit(0)


        port_infos = port_infos_result['message']
        if len(port_infos) == 0:
            print("暂无新数据，等待10秒后再运行")
            time.sleep(10)
            continue

        tasks = []
        for port_info in port_infos:
            print(port_info)
            # exit(0)


            tasks.append(gevent.spawn(request_url, port_info,))
            
            if len(tasks) == 50:

                gevent.joinall(tasks)
                url_banners = (list(map(lambda t: t.value , filter(lambda task: task.value != None , tasks) )))
                # print(url_banners)
                if len(url_banners) > 0:
                    # print(url_banners)
                    web_title_infos = []
                    for url_banner in url_banners:
                        # print(url_banner)

                        uuid = url_banner['uuid']
                        agreement = url_banner['agreement']
                        web_title = url_banner['web_title']
                        header = url_banner['header']
                        body = url_banner['body']
                        respone_code = url_banner['respone_code']
                        
                        if web_title:
                            web_title_infos.append({
                                'uuid': uuid,
                                'data': json.dumps({
                                    'agreement': agreement,
                                    'web_title': web_title,
                                    'respone_code': respone_code,
                                    'cms': check_banner(web_title,header,body)
                                })
                            })
                        else:
                            web_title_infos.append({
                                'uuid': uuid,
                                'data': "NONE"
                            })
                save_data(web_title_infos)
                tasks = []


        if len(tasks) > 0 :
            gevent.joinall(tasks)
            url_banners = (list(map(lambda t: t.value , filter(lambda task: task.value != None , tasks) )))
            if len(url_banners) > 0:
                web_title_infos = []
                for url_banner in url_banners:
                    # print(url_banner)
                    uuid = url_banner['uuid']
                    agreement = url_banner['agreement']
                    web_title = url_banner['web_title']
                    header = url_banner['header']
                    body = url_banner['body']
                    respone_code = url_banner['respone_code']
                    # print(header)
                    if web_title:
                        web_title_infos.append({
                            'uuid': uuid,
                            'data': json.dumps({
                                'agreement': agreement,
                                'web_title': web_title,
                                'respone_code': respone_code,
                                'cms': check_banner(web_title,header,body)
                            })
                        })
                    else:
                        web_title_infos.append({
                            'uuid': uuid,
                            'data': "NONE"
                        })
                print(web_title_infos)
                save_data(web_title_infos)



request_web_supplement_web_info()