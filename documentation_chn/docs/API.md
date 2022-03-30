# API

这部分文档涵盖了 CyberDB 的所有接口。对于 CyberDB 依赖于外部库的部分，我们在此处记录最重要的部分并提供指向规范文档的链接。


## cyberdb.Server 类

**class cyberdb.Server**

该类用于创建 CyberDB 服务端对象。

```python
def start(self, host: str = '127.0.0.1', port: int = 9980,
            password: str = None, max_con: int = 500, timeout: int = 0,
            print_log: bool = False, encrypt: bool = False):
'''
	后台启动 CyberDB 服务器，该操作不会阻塞前台任务。
	参数:
		host -- TCP 监听主机地址，如 127.0.0.1。
		port -- TCP 监听端口。
		password -- TCP 通信密码，建议采用 英文字母和数字的组合方式，
		最长不超过 32 个字符。
		max_con -- 最大并发数。
		timeout -- 单个连接的超时时间，单位 秒。
		print_log -- 是否打印通信日志，Fasle 为不打印。
		encrypt -- 是否加密通信内容，Fasle 为不加密。此加密算法为 AES-256，密钥为 password。
	返回类型: None
'''
```

```python
def run(self, host: str = '127.0.0.1', port: int = 9980,
        password: str = None, max_con: int = 500, timeout: int = 0,
        print_log: bool = False, encrypt: bool = False):
'''
	前台运行 CyberDB 服务器，该操作会阻塞前台任务。
	参数和 start 方法相同。
	返回类型: None
'''
```

```python
def set_ip_whitelist(self, ips: list):
'''
	设置 ip 白名单，CyberDB 加密通信时仅允许白名单的 ip 连接，
	该方法仅在 cyberdb.Server.start(encrypt=True) 或 
	cyberdb.Server.run(encrypt=True) 启用时有效。
	参数:
		ips -- 类型为列表，格式如 ['192.168.1.1', '118.123.89.137']
	返回类型: None
'''
```

```python
def set_backup(self, file_name: str = 'data.cdb', cycle: int = 900):
'''
    设置定时备份，该操作设置后，将在指定周期进行数据持久化备份，将 CyberDB 数据库保存至硬盘。
    参数:
        file_name -- 备份生成的文件名，文件后缀必须是 .cdb。
        cycle -- 循环备份的周期，单位 秒。
    返回类型: None
'''
```

```python
def save_db(self, file_name: str = 'data.cdb'):
'''
    数据持久化，将 CyberDB 数据库保存至硬盘。
    参数:
        file_name -- 备份生成的文件名，文件后缀必须是 .cdb。
    返回类型: None
'''
```

```python
def load_db(self, file_name: str = 'data.cdb'):
'''
    加载 .cdb 格式的文件，将硬盘中备份的 CyberDB 数据库加载回内存。
    参数:
        file_name -- 经数据持久化生成的文件名，文件后缀必须是 .cdb。
    返回类型: None
'''
```

## cyberdb.connect 函数

```python
def cyberdb.connect(host: str = '127.0.0.1', port: int = 9980, password:
            str = None, encrypt: bool = False, time_out: int = None) -> Client:
'''
	将客户端连接至 CyberDB 服务端。
	参数:
        host -- 连接地址，如 127.0.0.1
        port -- 连接端口
        password -- 连接密码
        encrypt -- 是否加密通信，如果服务端启用 encrypt 为 True，此处必须为
        True，反之亦然。
        time_out -- 连接池中每个连接的超时时间，单位 秒。连接池的连接经 time_out 
        秒无操作将被舍弃，下次连接将生成新连接。连接池将自动管理连接，开发者无需关注细节。
		此参数若为 None，则不会超时，连接池将维持连接直至失效，之后将重新生成新连接。
	返回类型: Client
'''
```

## cyberdb.Client 类

**class cyberdb.Client**

cyberdb.connect 函数返回的 cyberdb.Client 对象，用于生成 Proxy 对象。

```python
def get_proxy(self) -> Proxy:
'''
	生成 Proxy 对象。
	返回类型: None
'''
```

## Proxy 类

cyberdb.Client.get_proxy 方法生成的 Proxy 对象，可对 CyberDB 数据库进行操作，并管理由 Proxy 生成的 CyberDict、CyberList 子对象的 TCP 连接。Proxy 对象初始化后，执行 Proxy.connect 方法后才能使用。Proxy 对象及其子对象将执行远程操作，作用于服务端 CyberDB 数据库。

**class Proxy**

```python
def connect(self):
'''
	从连接池获取 TCP 连接，绑定至该 Proxy 对象。
	返回类型: None
'''
```

```python
def close(self):
'''
	取消该 Proxy 对象绑定的 TCP 连接，归还至连接池，下次操作前需重新
	执行 Proxy.connect 方法。
	返回类型: None
'''
```

```python
def create_cyberdict(self, table_name: str, content: dict = {}):
'''
	创建 CyberDict 表。
	参数:
		table_name -- 表名。
		content -- 表内容，需要是字典类型，默认为空字典。
	返回类型: None
'''
```

```python
def create_cyberlist(self, table_name: str, content: list = []):
'''
	创建 CyberList 表。
	参数:
		table_name -- 表名。
		content -- 表内容，需要是列表类型，默认为空列表。
	返回类型: None
'''
```

```python
def get_cyberdict(self, table_name: str) -> CyberDict:
'''
	获取 CyberDict 表。
	参数:
		table_name -- 表名。
	返回类型: CyberDict，该对象是 Proxy 生成的子对象，由 Proxy 控制 TCP 连接。
'''
```

```python
def get_cyberlist(self, table_name: str) -> CyberList:
'''
	获取 CyberList 表。
	参数:
		table_name -- 表名。
	返回类型: CyberList，该对象是 Proxy 生成的子对象，由 Proxy 控制 TCP 连接。
'''
```

```python
def print_tables(self):
'''
	打印 CyberDB 数据库中的所有表。
	返回类型: None
'''
```

```python
def delete_table(self, table_name: str):
'''
	删除 CyberDB 数据库中的 table_name 表。
	参数:
		table_name -- 删除的表名。
	返回类型: None
'''
```

## cyberdb.CyberDict 类

**class cyberdb.CyberDict**

由 Proxy 对象生成的子对象，用于执行 Dictionaries 操作。该对象将执行远程操作，作用于服务端 CyberDB 数据库。和 Proxy 对象共用同一个 TCP 连接。将跟随 Proxy 的连接而连接，Proxy 释放连接后，该对象也会失去连接。CyberDict 可以执行 Dictionaries 的 get、setdefault、update、keys、values、items、pop、popitem、clear 方法以及常用魔术方法，此部分请参考[ Python 字典官方文档](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)。

使用 for 循环迭代 CyberDict，客户端空间复杂度为 o(n), n 为 CyberDict.keys() 的长度。

```python
def todict(self) -> Dict:
'''
	将 CyberDict 转为 Dictionaries。
	返回类型: Dict
'''
```

## cyberdb.CyberList 类

**class cyberdb.CyberList**

由 Proxy 对象生成的子对象，用于执行 Lists 操作。该对象将执行远程操作，作用于服务端 CyberDB 数据库。和 Proxy 对象共用同一个 TCP 连接。将跟随 Proxy 的连接而连接，Proxy 释放连接后，该对象也会失去连接。CyberList 可以执行 Lists 的 append、extend、insert、pop、remove、count、index、reverse、sort、clear 方法以及常用魔术方法，此部分请参考[ Python 列表官方文档](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)。

使用 for 循环迭代 CyberList，每次迭代将从服务端获取内容，客户端的空间复杂度为 o(1)。

```python
def tolist(self) -> List:
'''
	将 CyberList 转为 Lists。
	返回类型: List
'''
```

