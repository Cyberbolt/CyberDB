# CyberDB

CyberDB 是基于 Python 的内存数据库。你可以使用 Python 内置数据结构 Dictionaries、Lists 作为数据存储，并支持数据持久化。进程间通过 Socket TCP 通信，拥有极高的性能，也可用于分布式计算。此外，你可以基于该模块定制自己的数据结构，支持机器学习模型部署。

### 安装方法

1.进入命令窗口，创建虚拟环境，依次输入以下命令

Linux和macOS:

```
python3 -m venv venv #创建虚拟环境
. venv/bin/activate #激活虚拟环境

```

Windows:

```
python -m venv venv #创建虚拟环境
venv\Scripts\activate #激活虚拟环境
```

2.安装 CyberDB，依次输入

```
pip install --upgrade pip
pip install cyberdb
```

如果你的服务端和客户端在两个不同的项目目录运行，请分别在服务端、客户端的虚拟环境中安装 CyberDB。

### 快速使用

在该模块中，请使用 CyberDict 和 CyberList 替代 dict 和 list （一种类 Dictionaries、Lists 对象）

#### 服务端

```
from cyberdb import DBServer

server = DBServer()
server.create_cyberdict('dict1') # 创建名为 dict1 的数据库表
server.create_cyberdict('dict2') # 创建名为 dict2 的数据库表
server.create_cyberlist('list1') # 创建名为 list1 的数据库表
server.start(host='127.0.0.1', password='123123', port=9980)
'''
启动服务器，填写运行地址、密码和端口号
若使用 server.start(password='123123')，则将以默认地址 127.0.0.1 和端口 9980 运行
'''
server.set_backup(period=900)
'''
设置数据库备份，默认时间 900s 一次，永久备份直至服务端停止运行
如果不调用此接口，将不会数据持久化
如果想停止正在运行的备份，请调用 server.set_backup(period=None)
'''
```

服务端运行后，会在项目根目录下创建 cyberdb_file 目录（程序运行中请勿删除），生成**客户端配置文件** cyberdb_file/config.cdb ，数据库备份的默认文件为 cyberdb_file/backup/data.cdb (该文件将在设置的备份时间自动备份或更新)

#### 客户端

将服务端的 cyberdb_file 拷贝至客户端的项目根目录中(如果使用同一个项目目录作为服务端和客户端，则不需要拷贝)

连接数据库

```
from cyberdb import DBClient
client = DBClient()
client.load_config('cyberdb_file/config.cdb') 
'''
加载配置文件 config.cdb
配置文件路径的默认值为 cyberdb_file/config.cdb ,此处路径如果一致，则无需填写参数。
'''
db = client.connect(host='127.0.0.1', password='123123', port=9980)
'''
输入服务端配置的地址、密码和端口号，获取连接的数据库实例 db
若使用 db = client.connect(password='123123')，将连接默认地址 127.0.0.1 
和端口 9980
'''
```

操作 CyberDict 和 CyberList

```
dict1 = db.CyberDict.dict1
dict2 = db.CyberDict.dict2
list1 = db.CyberList.list1
```
该命令能获取服务端创建的数据库表，格式为 数据库实例.数据类型.表名
也可以使用以下命令获取

```
dict1 = db['CyberDict']['dict1']
dict2 = db['CyberDict']['dict2']
list1 = db['CyberList']['list1']
```

在 dict1 和 dict2 中新增键值对

```
dict1.put(0, 'dict1')
dict2.put(0, 'dict2')
```

获取对应的值

