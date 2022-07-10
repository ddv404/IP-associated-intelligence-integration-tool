# IP关联情报集成工具
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144090-f3c5a4a0-83ea-4387-856d-ef1440fbc04a.png">
快捷获取IP关联情报数据。

当前已支持关联情报处理相关项如下：
1、IP whois信息
2、IP地理位置信息
3、IP反差domain信息
4、微步查询IP信息
5、IP全端口扫描（使用rustscan工具）
6、IP端口https证书获取（对所有开放端口发起）
7、IP端口web标题和组件获取（对所有开放端口发起）
8、watcher情报获取（https://feed.watcherlab.com/）
。。。。。。
Node文件夹内的每一个脚本为一个处理事项。

注：每个脚本内可能存在相应的配置（例如微步接口调用需要配置apikey）。配置信息一般都位于脚本头几行内。

工具分为服务端和数据处理脚本。
服务端：用于页面展示，数据管理，对外提供API接口
数据处理脚本：从服务端API接口中获取数据并进行处理再上传到服务端保存结果


脚本启动方式：
1、	直接运行python3 check_xxx_xxx.py
2、	后台运行nohup
3、	自动运行（例如：使用工具supervisorctl）

启动前准备：
1、	服务端：
安装mysql数据库，这里使用docker安装mysql
docker run -p 60603:3306 --name scan_mysql -v /data/mysql_v/conf:/etc/mysql -v /data/mysql_v/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=passwoed -d mysql:5.7
启动mysql后，进去mysql创建ddv_ip_scan库。
CREATE DATABASE IF NOT EXISTS ddv_ip_scan DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
web服务端启动前修改配置信息
<img width="336" alt="image" src="https://user-images.githubusercontent.com/97394404/178144123-1995dfe3-78bf-4105-8086-a51dfb5a6882.png">

2、	脚本测
全端口扫描脚本使用docker版rustscan工具，因此需要事先安装docker，并拉去镜像。
docker安装方式自行百度。
docker pull rustscan/rustscan:2.0.0
微步脚本、shodan脚本、watcher脚本需要配置key。


启动顺序：
1、	运行web服务端。python3 app.py
2、	运行Node内数据处理脚本（无运行优先级。如只想批量获取微步数据则只运行微步数据处理脚本即可）

注：
1、	同一个脚本可在多处同时启动，分布式运行可增加处理效率。
2、	对于爬取数据的脚本运行不宜过快，容易导致被目标站点封禁。
3、	全端口扫描脚本需要使用docker，需提前安装。
4、	全端口扫描脚本启动在需要在同级目录中创建一个名为“rustscan_result”的文件夹。
5、	全端口扫描脚本建议单独运行（占用大量带宽）。


页面操作说明
使用设定的账号密码登录（默认username_DDV/password_DDV）
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144138-8cb44d8d-70c3-4fc5-aefc-ca5c8ea73f1a.png">
新增IP
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144146-bb0fa33d-fc4b-4437-8a5b-74468b2d721f.png">
搜索功能
1、	根据IP进行模糊查询
2、	工具类型选择
3、	根据数据进行模糊查询
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144153-7aa81a7e-687b-4528-b4a1-68bd2bf4355d.png">
进度状态区域可横向滚动
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144160-d8eef068-32f0-45db-8521-ea6f8622f473.png">
可对页面中的数据进行下载
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144169-92287bf7-a17e-4b43-b4a6-d076a96d5dff.png">
支持添加自定义脚本处理项
添加自定义脚本需要使用到三个函数：
1、	工具注册函数 regist_tool(script_name, name, describe, tool_type, minutes_time)
2、	获取待处理的数据 get_check_data(script_name, number)
3、	保存结果数据 save_data(datas)

工具注册函数（序号将当前脚本注册到服务端，后续才能获取到待梳理的数据）
regist_tool(script_name, name, describe, tool_type, minutes_time)
参数script_name（脚本名称）
参数name（别名 应用页面中显示）
参数describe（脚本描述）
参数tool_type（脚本处理的数据类型IP或PORT【当类型为IP时get_check_data获取的数据包含ip和uuid；当前类型为PORT时获取的数据包含ip和port和uuid】）
参数minutes_time（预判值。从获取数据处理到上传结果数据，中间最长需要时间（单位：分钟）。）
返回
	state接口处理状态（success｜fail）
	message响应的信息

获取待处理的数据
get_check_data(script_name, number)
参数script_name（脚本名称，需要和regist_tool注册的script_name相同）
参数number（获取的数据量）
返回
	state接口处理状态（success｜fail）
	message响应的信息
		{
		ip: IP地址
		uuid: 数据的uuid
}
保存结果数据
save_data(datas)
参数datas（数组，每个元素的值为{‘uuid’:uuid, ‘data’:结果数据}）
返回
	state接口处理状态（success｜fail）
	message响应的信息

注：页面处会根据新注册工具新增数据展示项。

这里以联动微步为例子
在自定义脚本中需要导入tool文件
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144185-7960f441-2a5d-4572-8e4f-09d7b38e6b50.png">
第一步注册脚本
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144192-a5d92c80-1062-43d5-9ed7-78d2044854fd.png">
第二步获取待处理的数据
（这里使用循环可以一直执行）
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144201-cde58140-0a2f-41b4-a1d6-febc9aacd068.png">
第三步对数据进行梳理
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144212-d40bd5bd-38a8-4fb1-86c6-dcabf3cc301f.png">
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144216-8f2bd5f7-9c7b-4ca7-b8b8-a0ac04e51db6.png">
第四步保存数据
<img width="416" alt="image" src="https://user-images.githubusercontent.com/97394404/178144219-d2f46674-88dd-463b-a35b-0a4868d5ffa9.png">
注：数据处理脚本注册成功后，web页面端自动展示对应数据。











