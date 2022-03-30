# CyberDB

CyberDB 是一个轻量级的 Python 内存数据库。它旨在利用 Python 内置数据结构 Dictionaries、Lists 作数据存储，通过 Socket TCP 高效通信，并提供数据持久化。该模块常用于 Gunicorn 进程间通信、分布式计算 等领域。

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


强烈推荐使用 for 循环迭代 CyberDict，每次迭代将从服务端获取 v，客户端的空间复杂度为 o(1)。迭代同样可用于 CyberDict，CyberDict 的迭代中，客户端空间复杂度为 o(n), n 为 CyberDict.keys() 的长度。

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

有了 CyberDB，便能充分利用内存性能，不同进程(甚至不同主机)能通过 Python 的数据结构通信。感谢你的支持！

## 注意

由于编码限制，CyberDB 会将 0 识别为 None，但并不影响计算，请在所需位置将 None 转为 0。
