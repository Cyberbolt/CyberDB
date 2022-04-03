# CyberDB

[中文版](https://github.com/Cyberbolt/CyberDB#中文版)

CyberDB is a lightweight Python in-memory database. It is designed to use Python's built-in data structures Dictionaries, Lists for data storage, efficient communication through Socket TCP, and provide data persistence. This module can be used in hard disk database caching, Gunicorn inter-process communication, distributed computing and other fields.

The CyberDB server uses Asyncio for TCP communication. The client is developed based on Socket, so it supports the Gevent coroutine, but it has not yet adapted to Asyncio. Both the server and the client support PyPy, and it is recommended to use PyPy to run for better performance.

In high concurrency scenarios, the performance bottleneck of traditional databases is mainly hard disk I/O. Even if CyberDB is developed based on the dynamic language Python, the speed is still much faster than that of hard disk databases (such as MySQL), and CyberDB can be used as its cache. In addition, the core of CyberDB lies in programming in a Pythonic way, you can use CyberDB like Dictionaries and Lists.

## Installation

1. Enter the command window, create a virtual environment, and enter the following commands in turn

Linux and macOS:



```python
python3 -m venv venv # Create a virtual environment.
. venv/bin/activate # Activate the virtual environment.
```

Windows:


```python
python -m venv venv # Create a virtual environment.
venv\Scripts\activate # Activate the virtual environment.
```

2.Install CyberDB, enter


```python
pip install --upgrade pip
pip install cyberdb
```

If your server and client are running in two different project directories, please install CyberDB in the virtual environment of the server and client respectively.

## Links

- GitHub: [https://github.com/Cyberbolt/CyberDB](https://github.com/Cyberbolt/CyberDB) 
- PyPI: [https://pypi.org/project/CyberDB/](https://pypi.org/project/CyberDB/)
- Documentation: [https://www.cyberlight.xyz/static/cyberdb](https://www.cyberlight.xyz/static/cyberdb)
- CyberLight: [https://www.cyberlight.xyz/](https://www.cyberlight.xyz/)

## Quick to Use

In this module, please use CyberDict and CyberList instead of dict and list (a TCP-based Dictionaries-like, Lists-like object).

### Server

Run the database server.

```python
import time
import cyberdb

db = cyberdb.Server()
# The data is persistent, the backup file is data.cdb, and the backup cycle is every 900 seconds.
db.set_backup('data.cdb', cycle=900)
# Set the TCP address, port number, and password.
# The start method will not block the operation. If you want the operation to block, please use the run method instead of start, and the parameters remain unchanged.
db.start(host='127.0.0.1', port=9980, password='123456')

while True:
    time.sleep(10000)
```

After the above server runs, data.cdb and data_backup.cdb (backup files) will be generated (or overwritten) in the project root directory every 900 seconds. The file can be read the next time the database is started using the load method.

### Client

#### Connect to the Database


```python
import cyberdb

# Generate a client instance and connect.
client = cyberdb.connect(host='127.0.0.1', port=9980, password='123456')
```

#### Generate proxy Object


```python
# Generate proxy for this request.
proxy = client.get_proxy()
# Automatically obtain database connections from the connection pool.
proxy.connect()
```

The proxy object is not thread-safe, please generate the proxy object separately in each thread (or coroutine), and obtain the database connection through the connect method. You only need to use the close method to return the connection after the operation is completed, and the returned connection is managed intelligently by the client object.

#### Manipulate proxy Objects

Create CyberDict and CyberList


```python
# Create dict1 and dict2 tables of type CyberDict and 
# list1 table of type CyberList in the database respectively.
proxy.create_cyberdict('dict1')
proxy.create_cyberdict('dict2')
proxy.create_cyberlist('list1')
```


```python
dict1 = proxy.get_cyberdict('dict1')
dict2 = proxy.get_cyberdict('dict2')
list1 = proxy.get_cyberlist('list1')
```

The dict1, dict2, and list1 obtained here are all network objects, and the data is transmitted through TCP. The three objects are controlled by the proxy, and when proxy.close() is called to return the connection, the three objects will also be invalid. Similarly, use proxy.connect() to get connections from the connection pool again, and dict1, dict2, list1 also become available.

Once you understand this operation, you can operate dict1, dict2 like Dictionaries, and list1 like Lists! (CyberDict and CyberList support most methods of Dictionaries, Lists)

Examples are as follows

##### Common Operations of CyberDict

Add key-value pairs in dict1 and dict2


```python
dict1[0] = 100
dict1['test'] = 'Hello CyberDB!'
dict2[0] = 200
```

Get the corresponding value


```python
dict1.get(0)
```




    100




```python
dict2[0]
```




    200



View dict1 and dict2 (can also be printed with print )


```python
dict1
```




    {0: 100, 'test': 'Hello CyberDB!'}




```python
dict2
```




    {0: 200}



Get length


```python
len(dict1)
```




    2



Delete key-value pair


```python
del dict1[0]
```


```python
dict1
```




    {'test': 'Hello CyberDB!'}



Empty dict1


```python
dict1.clear()
dict1
```




    {}



##### Common Operations of CyberList

Generate the contents of list1


```python
for i in range(5):
    list1.append(99)
    
list1
```




    [99, 99, 99, 99, 99]



Change coordinate values


```python
list1[3] = 100
list1
```




    [99, 99, 99, 100, 99]



To slice


```python
list1[3:]
```




    [100, 99]



Get the length of list1


```python
len(list1)
```




    5



Print each element of list1 by iterating


```python
for v in list1:
    print(v)
```

    99
    99
    99
    100
    99


It is strongly recommended to use a for loop to iterate CyberList, each iteration will get v from the server, and the space complexity of the client is o(1). Iteration can also be used for CyberDict. In the iteration of CyberDict, the client space complexity is o(n), and n is the size of CyberDict.keys().

#### Release the Proxy Object

After the use is complete, return the connection of the proxy to the connection pool.


```python
proxy.close()
```

The proxy object also supports context managers, such as


```python
with client.get_proxy() as proxy:
    list1 = proxy.get_cyberlist('list1')
    print(list1)
```

    [99, 99, 99, 100, 99]


## Generalize

With CyberDB, memory performance can be fully utilized, and different processes (or even different hosts) can communicate through Python's data structures. For more tutorials, please refer to the documentation, Thank you!

## Notice

Due to encoding limitations, CyberDB will recognize 0 as None, but it does not affect the calculation, please convert None to 0 in the desired position.


# 中文版

CyberDB 是一个轻量级的 Python 内存数据库。它旨在利用 Python 内置数据结构 Dictionaries、Lists 作数据存储，通过 Socket TCP 高效通信，并提供数据持久化。该模块可用于 硬盘数据库缓存、Gunicorn 进程间通信、分布式计算 等领域。

CyberDB 服务端使用 Asyncio 进行 TCP 通信。客户端基于 Socket 开发，所以支持 Gevent 协程，暂未适配 Asyncio。服务端和客户端均支持 PyPy，推荐使用 PyPy 运行，以获得更好的性能。

高并发场景下，传统数据库的性能瓶颈主要在硬盘 I/O，即便 CyberDB 基于动态语言 Python 开发，速度仍然远快于硬盘数据库(如 MySQL)，CyberDB 可以作为它的缓存。此外，CyberDB 的核心在于使用 Pythonic 的方式编程，你可以像使用 Dictionaries 和 Lists 一样使用 CyberDB。

## 安装方法

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

## 链接

- GitHub: [https://github.com/Cyberbolt/CyberDB](https://github.com/Cyberbolt/CyberDB) 
- PyPI: [https://pypi.org/project/CyberDB/](https://pypi.org/project/CyberDB/)
- 文档: [https://www.cyberlight.xyz/static/cyberdb-chn](https://www.cyberlight.xyz/static/cyberdb-chn)
- 电光笔记: [https://www.cyberlight.xyz/](https://www.cyberlight.xyz/)

## 快速使用

该模块中请使用 CyberDict 和 CyberList 替代 dict 和 list （一种基于 TCP 的类 Dictionaries、类 Lists 对象）。

### 服务端


服务端初始化，设置备份和 TCP 监听地址。


```python
import time
import cyberdb

db = cyberdb.Server()
# 数据持久化，备份文件为 data.cdb，备份周期 900 秒一次。
db.set_backup('data.cdb', cycle=900)
# 设置 TCP 地址、端口号、密码，生产环境中密码建议使用大小写字母和数字的组合。
# start 方法不会阻塞运行，若希望该操作阻塞，请使用 run 方法代替 start，参数不变。
db.start(host='127.0.0.1', port=9980, password='123456')

while True:
    time.sleep(10000)
```

上述服务端运行后，每 900 秒将在此项目根目录生成（或覆盖）data.cdb。下次启动数据库可使用 load 方法读取该文件。

### 客户端

#### 连接数据库


```python
import cyberdb

# 生成客户端实例并连接。
client = cyberdb.connect(host='127.0.0.1', port=9980, password='123456')
```

#### 生成 proxy 对象


```python
# 生成本次请求的 proxy。
proxy = client.get_proxy()
# 从连接池自动获取数据库连接。
proxy.connect()
```

建议在每个线程(或协程)中单独生成 proxy 对象，并通过 connect 方法获取数据库连接。你只需在操作完成后使用 close 方法归还连接即可，归还后的连接由 client 对象智能管理。

#### 操作 proxy 对象

创建 CyberDict 和 CyberList


```python
# 在数据库中分别创建类型为 CyberDict 的 dict1、dict2 表，
# 类型为 CyberList 的 list1 表。
proxy.create_cyberdict('dict1')
proxy.create_cyberdict('dict2')
proxy.create_cyberlist('list1')
```


```python
dict1 = proxy.get_cyberdict('dict1')
dict2 = proxy.get_cyberdict('dict2')
list1 = proxy.get_cyberlist('list1')
```

此处获取的 dict1、dict2、list1 均为网络对象，数据通过 TCP 传输。三个对象受 proxy 控制，当调用 proxy.close() 归还连接后，三个对象也会失效。同样，使用 proxy.connect() 可重新从连接池获取连接，dict1、dict2、list1 也变为可用。

了解此操作后，你便可以像操作 Dictionaries 一样操作 dict1、dict2，像操作 Lists 一样操作 list1 了！（CyberDict 和 CyberList 支持 Dictionaries、Lists 的大部分方法）

示例如下

##### CyberDict 常用操作

在 dict1 和 dict2 中新增键值对


```python
dict1[0] = 100
dict1['test'] = 'Hello CyberDB!'
dict2[0] = 200
```

获取对应的值


```python
dict1.get(0)
```




    100




```python
dict2[0]
```




    200



查看 dict1 和 dict2 (也可以使用 print 打印)


```python
dict1
```




    {0: 100, 'test': 'Hello CyberDB!'}




```python
dict2
```




    {0: 200}



获取长度


```python
len(dict1)
```




    2



删除键值对


```python
del dict1[0]
dict1
```




    {'test': 'Hello CyberDB!'}



清空 dict1


```python
dict1.clear()
dict1
```




    {}



##### CyberList 常用操作

生成 list1 的内容


```python
for i in range(5):
    list1.append(99)
    
list1
```




    [99, 99, 99, 99, 99]



更改坐标值


```python
list1[3] = 100
list1
```




    [99, 99, 99, 100, 99]



进行切片


```python
list1[3:]
```




    [100, 99]



获取 list1 的长度


```python
len(list1)
```




    5



通过迭代打印 list1 每个元素


```python
for v in list1:
    print(v)
```

    99
    99
    99
    100
    99


强烈推荐使用 for 循环迭代 CyberList，每次迭代将从服务端获取 v，客户端的空间复杂度为 o(1)。迭代同样可用于 CyberDict，CyberDict 的迭代中，客户端空间复杂度为 o(n), n 为 CyberDict.keys() 的长度。

#### 释放 proxy 对象

使用完成，将 proxy 的连接归还至连接池即可。


```python
proxy.close()
```

proxy 对象同样支持上下文管理器，如


```python
with client.get_proxy() as proxy:
    list1 = proxy.get_cyberlist('list1')
    print(list1)
```

    [99, 99, 99, 100, 99]


## 概括

有了 CyberDB，便能充分利用内存性能，不同进程(甚至不同主机)能通过 Python 的数据结构通信。更多教程请参考文档，感谢你的支持！

## 注意

由于编码限制，CyberDB 会将 0 识别为 None，但并不影响计算，请在所需位置将 None 转为 0。
