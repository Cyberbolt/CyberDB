# 生产环境下使用 CyberDB 作为 Flask 的内存数据库

前面我们讲述了 CyberDB 的[快速上手](https://www.cyberlight.xyz/static/cyberdb-chn/)，现在我们需要把它带到能发挥其作用的地方，在生产环境中将 CyberDB 作为 Flask 的内存数据库，使用 Gunicorn 运行，并实现多进程间的通信。

这篇文章通过一个尽可能精简的 Flask 实例讲解，不会涉及复杂的 Web 知识。核心思路为 CyberDB + Gunicorn + Gevent + Flask (多进程 + 协程)，启动一个 CyberDB 服务器，使用 Gunicorn 多进程运行 Flask 实例，每个进程的实例通过 Gevent 运行，进程中使用 CyberDB 客户端连接至内存数据库，由此实现 CyberDB 数据库的高并发访问。

文章使用 PyPy 运行，同样适用 CPython。

运行环境: Python 3.8.12, PyPy 7.3.7

此项目的目录结构
```bash
.
├── app.py
├── cyberdb_init.py
├── cyberdb_serve.py
├── requirements.txt
└── venv
```
我们通过列举每个文件的内容顺序讲解 CyberDB 的核心操作。

文件 requirements.txt
```
CyberDB>=0.7.1
Flask==2.1.1
gevent==21.12.0
gunicorn==20.1.0
```
此项目的依赖。这篇文章不是 Python 基础教程，请查询相关文档创建虚拟环境 venv 目录并安装 requirements.txt 中的依赖。

生成 venv 目录并安装好依赖后，下面所有操作都在激活的虚拟环境中运行。

文件 cyberdb_init.py
```python
'''
    该模块用于初始化 CyberDB 的表结构，
    只在第一次运行，后续不再使用。
'''


import time

import cyberdb

db = cyberdb.Server()
# 配置 CyberDB 服务端的 地址、端口、密码
db.start(host='127.0.0.1', port=9980, password='123456')

# 待服务端启动后，连接 CyberDB 服务端
time.sleep(3)
client = cyberdb.connect(host='127.0.0.1', port=9980, password='123456')
# 生成 proxy 对象
with client.get_proxy() as proxy:
    # 创建类型为 CyberDict 的表 centre，并初始化内容
    proxy.create_cyberdict('centre')
    centre = proxy.get_cyberdict('centre')
    centre['content'] = 'Hello CyberDB!'

# 将 CyberDB 保存至 data.cdb
db.save_db('data.cdb')
```

在项目根目录执行
```bash
python cyberdb_init.py
```
此时完成了 CyberDB 数据库表的初始化，在 CyberDB 中创建了一个名为 centre、类型为 CyberDict 的表，初始化 'content' 键的值为 'Hello CyberDB!' ，最后将 CyberDB 数据库保存至硬盘(项目根目录生成了名为 data.cdb 的文件)。

文件 cyberdb_serve.py
```python
import cyberdb


def main():
    # 后台运行 CyberDB 服务端，设置相关信息。
    db = cyberdb.Server()
    # 从硬盘读取 data.cdb 至 CyberDB
    db.load_db('data.cdb')
    # 每 300 秒备份一次数据库
    db.set_backup('data.cdb', cycle=300)
    db.run(
        host='127.0.0.1', # TCP 运行地址
        port=9980, # TCP 监听端口
        password='hWjYvVdqRC', # 数据库连接密码
        max_con=10000, # 最大并发数
        encrypt=True, # 加密通信
        print_log=False # 不打印日志
    )


if __name__ == '__main__':
    main()
```
在项目根目录执行
```bash
python cyberdb_serve.py
```
以运行 CyberDB 服务端。

此处设置了 encrypt=True ，CyberDB 会将 TCP 通信内容使用 AES-256 算法加密。开启 encrypt=True 后，CyberDB 仅允许白名单中的 ip 通信，默认白名单为 ['127.0.0.1']，白名单[设置方法](https://www.cyberlight.xyz/static/cyberdb-chn/API/#cyberdbserver)。一般，若只需在本地进程间通信，无需开启 encrypt=True 和设置白名单，只有远程通信时需要此操作。

文件 app.py
```python
import cyberdb
from flask import Flask, g


# 连接 CyberDB 并生成客户端实例。
client = cyberdb.connect(
    host='127.0.0.1', 
    port=9980, 
    password='hWjYvVdqRC',
    # 服务端若加密，客户端必须加密，反之亦然
    encrypt=True,
    # 每个连接若超过900秒无操作，将舍弃该连接。
    # 连接由连接池智能管理，无需关系细节。
    time_out=900
)

# 创建 Flask 实例，此部分请参考 
# Flask 文档 https://flask.palletsprojects.com/
app = Flask(__name__)


@app.before_request
def before_request():
    # 每次请求执行前生成 proxy 对象。
    g.proxy = client.get_proxy()
    # 从连接池获取连接。
    g.proxy.connect()


@app.get("/")
def hello_world():
    # 从数据库获取 centre 表
    centre = g.proxy.get_cyberdict('centre')
    
    return {
        'code': 1,
        'content': centre['content']
    }


@app.teardown_request
def teardown_request(error):
    # 每次请求执行后归还连接至连接池
    g.proxy.close()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
```
该模块会在每次请求执行前( before_request )使用 client.get_proxy() 获取 proxy 对象，每个获取的 proxy 对象可以绑定一个 TCP 连接，此处使用 proxy.connect() 从连接池获取连接。视图函数 hello_world 中，由 proxy 获取的对象 centre，与 proxy 共用同一个连接，proxy 的连接释放后，centre 也会失去连接。在每次请求后( teardown_request )使用 proxy.close() 方法释放 proxy 绑定的连接，归还至连接池。

cyberdb.connect 的 time_out 参数是连接池中每个连接的超时时间，此处每个连接超过 900 秒无操作将被舍弃。若不设置该参数，连接池的每个连接会维持到失效为止。

在项目根目录运行
```bash
gunicorn -w 4 -b 127.0.0.1:8000 -k gevent app:app
```
使用 4 进程、Gevent 启动 Flask 实例。

浏览器访问 127.0.0.1:8000 会得到如下响应
```JSON
{"code":1,"content":"Hello CyberDB!"}
```
通过此例，你可以把 CyberDB 部署到更复杂的 Web 环境中，充分享受内存的低延迟特性。
