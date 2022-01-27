# CyberDB

CyberDB 是一个轻量级的 Python 内存数据库。它旨在利用 Python 内置数据结构 Dictionaries、Lists 作数据存储，通过 Socket TCP 高效通信，并提供数据持久化。开发者可以基于该模块定制自己的数据结构，常用于 Gunicorn 进程间通信、分布式计算、机器学习部署 等领域。

### 安装方法

推荐 Python 版本: 3.8 及以上

1.进入命令窗口，创建虚拟环境，依次输入以下命令

Linux 和 macOS:


```python
python3 -m venv venv # 创建虚拟环境
. venv/bin/activate # 激活虚拟环境
```

Windows:


```python
python -m venv venv # 创建虚拟环境
venv\Scripts\activate # 激活虚拟环境
```

2.安装 CyberDB，依次输入


```python
pip install --upgrade pip
pip install cyberdb
```

如果你的服务端和客户端在两个不同的项目目录运行，请分别在服务端、客户端的虚拟环境中安装 CyberDB。

### 链接

- GitHub: [https://github.com/Cyberbolt/CyberDB](https://github.com/Cyberbolt/CyberDB) 
- PyPI: [https://pypi.org/project/CyberDB/](https://pypi.org/project/CyberDB/)
- 文档: 正在撰写中

### 快速使用

在该模块中，请使用 CyberDict 和 CyberList 替代 dict 和 list （CyberDict 和 CyberList 是一种基于 TCP 的类 Dictionaries、类 Lists 对象）。

#### 服务端

请进入你的项目根目录

首次运行单独创建一个 py 文件，用于服务端初始化时创建数据库表，运行服务端后将表信息保存至本地。（该文件于第一次建表时使用，后续将不再运行）


```python
from cyberdb import DBServer

server = DBServer()
server.create_cyberdict('dict1') # 创建名为 dict1 的数据库表
server.create_cyberdict('dict2') # 创建名为 dict2 的数据库表
server.create_cyberlist('list1') # 创建名为 list1 的数据库表
server.start(password='123123') # 后台运行服务器
'''
本次运行只是初始化时保存表，密码可随意设置，之后不会用到
'''
server.save_db() # 保存服务器数据到本地
server.stop() # 停止运行服务器
```

    CyberDB is starting...
    Server stopped.


服务端启动后，会在项目根目录下创建 cyberdb_file 目录（请勿删除），生成**客户端配置文件** cyberdb_file/config.cdb (客户端运行依赖于此)，数据库持久化的默认文件为 cyberdb_file/backup/data.cdb

正式开始部署服务端


```python
from cyberdb import DBServer

server = DBServer()
server.load_db() # 会自动加载 cyberdb_file/backup/data.cdb
server.start(host='127.0.0.1', password='123123', port=9980)
'''
启动服务器，填写运行地址、密码和端口号
若使用 server.start(password='123123')，将以默认地址 127.0.0.1 和端口 9980 运行
'''
server.set_backup(period=900)
'''
设置数据库备份，默认时间 900s 一次，永久备份直至服务端停止运行
若不调用此接口，将不会数据持久化
如果想停止正在运行的备份，请调用 server.set_backup(period=None)
'''
# 如果你的程序不会永久在后台运行，请增加以下命令使程序永久运行
import time
while True:
    time.sleep(1000000000)
```

    File cyberdb_file/backup/data.cdb loaded successfully.
    CyberDB is starting...
    The backup cycle: 900s
    


数据库备份的默认文件为 cyberdb_file/backup/data.cdb (该文件将在设置的备份时间自动备份或更新)

#### 客户端

请进入你的客户端项目根目录（可以和服务端一致）

将服务端的 cyberdb_file 拷贝至客户端的项目根目录中(如果你的服务端和客户端的项目目录本身就是同一个，则无需拷贝)

连接数据库



```python
from cyberdb import DBClient
client = DBClient()
client.load_config('cyberdb_file/config.cdb') 
'''
加载配置文件 config.cdb
配置文件路径的默认值为 cyberdb_file/config.cdb ,此处路径若一致，无需填写参数。
'''
db = client.connect(host='127.0.0.1', password='123123', port=9980)
'''
输入服务端配置的地址、密码和端口号，获取数据库连接实例 db
若使用 db = client.connect(password='123123')，将连接默认地址 127.0.0.1 
和端口 9980
'''
```

    


操作 CyberDict 和 CyberList (之后的代码使用 Jupyter Notebook 展示)


```python
dict1 = db.CyberDict.dict1
dict2 = db.CyberDict.dict2
list1 = db.CyberList.list1
```

该命令将获取服务端创建的数据库表，格式为 数据库实例.数据类型.表名
也可使用以下命令获取


```python
dict1 = db['CyberDict']['dict1']
dict2 = db['CyberDict']['dict2']
list1 = db['CyberList']['list1']
```

此处获取的 dict1、dict2、list1 均为网络对象，调用对象方法，则是和数据库远程交互

在 dict1 和 dict2 中新增键值对


```python
dict1.put(0, 'dict1')
dict1.put(10, 'test')
dict2.put(0, 'dict2')
```

获取对应值


```python
dict1.get(0)
```




    'dict1'




```python
dict2.get(0)
```




    'dict2'



我们使用 show 方法看看 dict1 和 dict2 的表内容


```python
dict1.show()
```




    {0: 'dict1', 10: 'test'}




```python
dict2.show()
```




    {0: 'dict2'}



此处的 show 方法可以直接提取出表中的数据(这里是 dict)，可以进行任何 dict 操作。执行过程是:从数据库中将变量复制到客户端。如果你的服务端和客户端使用的同一台机器，会占用2倍内存，相同主机中不建议频繁使用 show 方法。

CyberDict 和 CyberList 本身支持 dict 和 list 的所有公有方法(如 dict.get(key), dict.items(), list.append(v), list.pop() 等)，使用任何公有方法都是基于 TCP 的数据交互。所以不支持迭代、不支持私有方法(Python 魔术方法)，不能使用 dict[key] 和 list[index] 访问数据。CyberDB 给出了相应办法替代，请仔细阅读本文。(如果你执意要用魔术方法，CyberDB 的文档中提供了相应 API)

注:使用 show 方法可以复制表中的变量到客户端本地，show 方法得到的变量是完整的 dict 或 list 对象，可以执行 Python 魔术方法。如:


```python
dict1.show()[10]
```




    'test'



我们可以使用 get_length 方法获取 CyberDict 的长度


```python
dict1.get_length()
```




    2



使用 delete 方法删除键值对


```python
dict1.delete(10)
```

dict1.delete(10) 等效于在本地使用 del dict1[10]

下面对 CyberList 执行常用操作

将 list1 增加为 5 * 5 的全 0 表格


```python
for i in range(5):
    list1.append([0 for i in range(5)])
```

使用 show 方法获取 list1 的所有数据(此处的 show 方法和 CyberDict 效果相同)


```python
list1.show()
```




    [[0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0]]



使用 update 方法修改 list1 的第 4 个值(下标为 3)，更改为全 1。（update 只能作用于表格的第一维）


```python
list1.update(3, [1 for i in range(5)])
list1.show()
```




    [[0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [1, 1, 1, 1, 1],
     [0, 0, 0, 0, 0]]



使用 update_form 方法修改 list1 的第 5 行第 5 个值(下标为 4, 4)为 1。（update_form 用于修改二维表格）


```python
list1.update_form(4, 4, 1)
list1.show()
```




    [[0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [1, 1, 1, 1, 1],
     [0, 0, 0, 0, 1]]



loc 方法用于定位一维表格
如下，使用 loc 方法定位 list1 的第 4 行


```python
list1.loc(3)
```




    [1, 1, 1, 1, 1]



使用 loc_form 定位二维表格，此处定位表格的第 5 行第 5 列


```python
list1.loc_form(4, 4)
```




    1



使用 slice 进行切片


```python
list1.slice(4, 6)
```




    [[0, 0, 0, 0, 1]]



获取 list1 的长度


```python
list1.get_length()
```




    5



关于迭代，虽然可以用 show 方法获取列表后迭代，但会占用较多内存（如果 CyberList 很大）。CyberDB 内置提供生成器，开发者可以优雅地使用生成器迭代，如下


```python
from cyberdb import generate

for row in generate(list1):
    print(row)
```

    [0, 0, 0, 0, 0]
    [0, 0, 0, 0, 0]
    [0, 0, 0, 0, 0]
    [1, 1, 1, 1, 1]
    [0, 0, 0, 0, 1]


该方法也适用于迭代 CyberDict

#### 概括

有了 CyberDB，便能充分利用内存性能，不同进程(甚至不同主机)通过 Python 的数据结构通信。自定义数据结构、机器学习部署等教程请参考文档，感谢你的支持！

电光笔记官网 [https://www.cyberlight.xyz/](https://www.cyberlight.xyz/)
