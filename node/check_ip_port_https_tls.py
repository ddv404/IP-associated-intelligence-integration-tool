# coding: utf-8 
# 查询域名证书到期情况
import gevent
from gevent import monkey
monkey.patch_all(select=False)
from tool import *
from urllib3.contrib import pyopenssl
import time


def get_target_tls(uuid,target,port):
    # print(https_url)
    try:
        conn = pyopenssl.ssl.create_connection((target, port),5)
        sock = pyopenssl.ssl.SSLContext(pyopenssl.ssl.PROTOCOL_SSLv23).wrap_socket(conn, server_hostname=target)
        cert = pyopenssl.ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
        # sock.settimeout(5)
        # conn.settimeout(5)
        data = pyopenssl.OpenSSL.crypto.load_certificate(pyopenssl.OpenSSL.crypto.FILETYPE_PEM, cert)
        CN = data.get_subject().CN
        if not CN or CN == None:
            CN = NONE
        # print(data.get_notAfter().decode()[0:-1])
        # expire_time = datetime.datetime.strptime(data.get_notAfter().decode()[0:-1], '%Y%m%d%H%M%S')
        # expire_days = (expire_time - datetime.datetime.now()).days
        return {'uuid':uuid, 'data':CN}
        # return True, {"expire_time": str(expire_time), "expire_days": expire_days}

    except Exception as e:
        # print(e)
        # pass
        return {'uuid':uuid, 'data':'NONE'}


regist_result = regist_tool('check_ip_port_https_tls', 'https证书', '对https进行证书获取', 'PORT',2)

if regist_result['state'] == 'fail':
    print(regist_result['message'])
    exit(0)


if __name__ == "__main__":

    while True:

        ip_port_infos_result = get_check_data('check_ip_port_https_tls',10)
        if ip_port_infos_result['state'] == 'fail':
            print(ip_port_infos_result['message'])
            time.sleep(10)
            continue
            

        ip_port_infos = ip_port_infos_result['message']

        if len(ip_port_infos) == 0:
            print("暂无新数据，等待10秒后再运行")
            time.sleep(10)
            continue


        tasks = []
        for ip_port_info in ip_port_infos:
            print(ip_port_info)
            uuid = ip_port_info['uuid']

            ip = ip_port_info['ip']
            port = ip_port_info['port']

            tasks.append(gevent.spawn(get_target_tls,uuid, ip,port))

            if len(tasks) == 100:

                gevent.joinall(tasks)
                url_banners = (list(map(lambda t: t.value , filter(lambda task: task.value != None , tasks) )))
                if len(url_banners) > 0:
                    # print(url_banners)
                    for url_banner in url_banners:
                        print(url_banner)
                    # save_data(url_banners)

                    save_data_result = save_data(url_banners)
                    if save_data_result['state'] == 'fail':
                        print(save_data_result['message'])
                        time.sleep(10)

                tasks = []


        if len(tasks) > 0 :
            gevent.joinall(tasks)
            url_banners = (list(map(lambda t: t.value , filter(lambda task: task.value != None , tasks) )))
            if len(url_banners) > 0:
                # print(url_banners)
                for url_banner in url_banners:
                    print(url_banner)
                # save_data(url_banners)

                save_data_result = save_data(url_banners)
                if save_data_result['state'] == 'fail':
                    print(save_data_result['message'])
                    time.sleep(10)
