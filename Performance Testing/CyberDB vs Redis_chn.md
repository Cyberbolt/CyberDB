# [性能测试] Python 内存数据库 CyberDB VS Redis

作为基于 Python 的内存数据库，[CyberDB](https://github.com/Cyberbolt/CyberDB) 的表现如何呢？本文主要测试 CyberDB 和 Redis 在 Python Web 中的性能表现。

由于 CyberDB 中 proxy 的 connect 方法会检测连接是否有效，为了确保测试的公平性，我们将使用 redis 的 ping 方法与之对应。

文章将采用 Gunicorn 3进程 + Gevent 协程的方法测试。环境: Python 3.8.12, PyPy 7.3.7

本项目的目录结构为
```bash
.
├── app.py
├── app_redis.py
├── cyberdb_init.py
├── cyberdb_serve.py
├── redis_init.py
└── requirements.txt
```

每个文件的内容如下

app.py
```python
import cyberdb
from flask import Flask, g


client = cyberdb.connect(
    host='127.0.0.1', 
    port=9980, 
    password='hWjYvVdqRC'
)

app = Flask(__name__)


@app.before_request
def before_request():
    g.proxy = client.get_proxy()
    g.proxy.connect()


@app.get("/")
def hello_world():
    centre = g.proxy.get_cyberdict('centre')

    return {
        'code': 1,
        'content': centre['content']
    }


@app.teardown_request
def teardown_request(error):
    g.proxy.close()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
```

app_redis.py
```python
import redis
from flask import Flask, g


rdp = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
r = redis.StrictRedis(connection_pool=rdp)


app = Flask(__name__)


@app.before_request
def before_request():
    r.ping()
    g.r = r


@app.get("/")
def hello_world():
    return {
        'code': 1,
        'content': g.r['content']
    }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
```

cyberdb_init.py
```python
import time

import cyberdb

db = cyberdb.Server()

db.start(host='127.0.0.1', port=9980, password='123456')

time.sleep(3)
client = cyberdb.connect(host='127.0.0.1', port=9980, password='123456')
with client.get_proxy() as proxy:
    proxy.create_cyberdict('centre')
    centre = proxy.get_cyberdict('centre')
    centre['content'] = 'Hello CyberDB!'

db.save_db('data.cdb')
```
cyberdb_serve.py
```python
import cyberdb


def main():
    db = cyberdb.Server()
    db.load_db('data.cdb')
    db.set_backup('data.cdb', cycle=300)
    db.run(
        host='127.0.0.1',
        port=9980,
        password='hWjYvVdqRC',
        max_con=10000,
        print_log=False
    )


if __name__ == '__main__':
    main()
```

redis_init.py
```python
import redis


r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)  
r.set('content', 'Hello CyberDB!')
```

requirements.txt
```
APScheduler==3.9.1
async-timeout==4.0.2
backports.zoneinfo==0.2.1
cffi==1.14.6
click==8.1.2
CyberDB==0.9.1
Deprecated==1.2.13
Flask==2.1.1
gevent==21.12.0
greenlet==0.4.13
gunicorn==20.1.0
hpy==0.0.3
importlib-metadata==4.11.3
itsdangerous==2.1.2
Jinja2==3.1.1
MarkupSafe==2.1.1
obj-encrypt==0.7.0
packaging==21.3
pycryptodome==3.14.1
pyparsing==3.0.8
pytz==2022.1
pytz-deprecation-shim==0.1.0.post0
readline==6.2.4.1
redis==4.2.2
six==1.16.0
tzdata==2022.1
tzlocal==4.2
Werkzeug==2.1.1
wrapt==1.14.0
zipp==3.8.0
zope.event==4.5.0
zope.interface==5.4.0

```

测试条件: 自己的环境中拥有 Redis 和 wrk 。

测试步骤:

(注：本文不是 Python 的基础教程，如果你不了解虚拟环境，请查询相关文档的操作)

1.创建并激活虚拟环境，安装 requirements.txt 中的依赖后，新建终端，运行 `python cyberdb_init.py` 初始化 CyberDB 的表结构，并运行 `python cyberdb_serve.py` 以开启 CyberDB 服务器。

2.并在另一个终端运行 `redis-server` 开启 Redis 服务器。在激活的虚拟环境中运行 `python redis_init.py` 初始化 Redis 的表结构。

3.运行 `gunicorn -w 3 -b 127.0.0.1:8000 -k gevent app:app` (Flask 运行 CyberDB)，之后使用 `wrk -t8 -c100 -d120s --latency  http://127.0.0.1:8000` 测试。结果如下:

```bash
Running 2m test @ http://127.0.0.1:8000
  8 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    24.49ms   12.17ms 310.04ms   86.68%
    Req/Sec   505.40    124.64     1.28k    77.15%
  Latency Distribution
     50%   19.95ms
     75%   29.53ms
     90%   38.15ms
     99%   66.11ms
  482884 requests in 2.00m, 86.58MB read
Requests/sec:   4020.84
Transfer/sec:    738.20KB
```

4.运行 `gunicorn -w 3 -b 127.0.0.1:8000 -k gevent app_redis:app` (Flask 运行 Redis)，之后使用 `wrk -t8 -c100 -d120s --latency  http://127.0.0.1:8000` 测试。结果如下:

```
Running 2m test @ http://127.0.0.1:8000
  8 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    22.59ms   14.58ms 697.21ms   95.14%
    Req/Sec   549.22     85.09     1.08k    78.60%
  Latency Distribution
     50%   21.22ms
     75%   25.28ms
     90%   29.66ms
     99%   54.46ms
  524279 requests in 2.00m, 94.00MB read
Requests/sec:   4365.66
Transfer/sec:    801.51KB
```

### 总结

本测试中，CyberDB 的结果为 4020.84 HPS，Redis 的结果为 4365.66 HPS，两者在同一水平。

该结果并不令人惊讶，CyberDB 和 redis-py 都是基于 socket 开发的接口，两者服务端也均为单线程。CyberDB 所依赖的 Python 字典和列表，与 Redis 相同，都是由 C 开发。

两者最大的区别是，[CyberDB](https://github.com/Cyberbolt/CyberDB)  原生基于 Python，你可以像使用字典和列表一样使用 CyberDB；Redis-py 只是 Python 中操作 Redis 的接口。