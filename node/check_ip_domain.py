# -*- coding: utf-8 -*-
import json
import HackRequests
import time
from bs4 import BeautifulSoup
from tool import *
import tldextract





set_proxy =()
def check_ip_domain(ip):

    hack = HackRequests.hackRequests()
    raw = '''GET /pppppppppppppppp/ HTTP/1.1
Host: site.ip138.com
Connection: close
Pragma: no-cache
Cache-Control: no-cache
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://site.ip138.com/pppppppppppppppp/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6

'''.replace('pppppppppppppppp',ip )

            
    domains = []
    # try:
    hh = hack.httpraw(raw,ssl=True,timeout=10,proxy=set_proxy)
    if (hh.status_code) == 200:
        html = hh.text()
        # print(html)
        if '禁止查询该iP' in html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        result2 = soup.find(id="list")
        lis = result2.find_all('li')
        
        for li in lis:
            li_txt = li.text
            if '上的网站' in li_txt or '绑定过的域名如' in li_txt:
                continue
            if "暂无结果" in li_txt:
                return []
            # print(li)
            subdomain = li.find("a").text
            if subdomain not in domains:
                domains.append(subdomain)
        return domains
    
    
    else:
        print(company_pid)
        print(hh.status_code)
        print("ip范查域名失败")



regist_result = regist_tool('check_ip_domain', 'IP反查域名[IP138]', '使用ip138网站对ip进行反查域名', 'IP',2)
if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)

while True:
    ip_infos_result = get_check_data('check_ip_domain',2)
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
                
        
        subdomains = check_ip_domain(ip)
        domains = list(set(map(lambda subdomain: tldextract.extract(subdomain).registered_domain,subdomains)))

        data = {
            'domain_number': len(domains),
            'domains':domains,
            'subdomains_number': len(subdomains),
            'subdomains':subdomains
        }
        data_str = json.dumps(data)
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




