# [Performance Test] Python In-memory Database CyberDB VS Redis

How does [CyberDB](https://github.com/Cyberbolt/CyberDB) perform as a Python-based in-memory database? This article mainly tests the performance of CyberDB and Redis in Python Web.

Since the connect method of the proxy in CyberDB will detect whether the connection is valid, in order to ensure the fairness of the test, we will use the ping method of redis to correspond to it.

The article will be tested using the Gunicorn 3 process + Gevent coroutine method. Environment: Python 3.8.12, PyPy 7.3.7

The directory structure of this project is
```bash
.
├── app.py
├── app_redis.py
├── cyberdb_init.py
├── cyberdb_serve.py
├── redis_init.py
└── requirements.txt
```

The content of each file is as follows

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

Test conditions: Redis and wrk in your own environment.

Test steps:

(Note: This article is not a basic tutorial of Python. If you do not understand virtual environment, please check the operation of related documents)

1. Create and activate a virtual environment, install the dependencies in requirements.txt, create a new terminal, run `python cyberdb_init.py` to initialize the table structure of CyberDB, and run `python cyberdb_serve.py` to start the CyberDB server.

2. And run `redis-server` in another terminal to start the Redis server. Run `python redis_init.py` in the activated virtual environment to initialize the Redis table structure.

3. Run `gunicorn -w 3 -b 127.0.0.1:8000 -k gevent app:app` (Flask runs CyberDB), then use `wrk -t8 -c100 -d120s --latency http://127.0.0.1:8000 ` test. The result is as follows:

```
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

1. Run `gunicorn -w 3 -b 127.0.0.1:8000 -k gevent app_redis:app` (Flask runs Redis), then use `wrk -t8 -c100 -d120s --latency http://127.0.0.1:8000 ` test. The result is as follows:

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

### Summarize

In this test, the result of CyberDB is 4020.84 HPS, and the result of Redis is 4365.66 HPS, both are on the same level.

This result is not surprising, both CyberDB and redis-py are socket-based interfaces, and both servers are also single-threaded. The Python dictionaries and lists that CyberDB relies on, the same as Redis, are developed in C.

The biggest difference between the two is that [CyberDB](https://github.com/Cyberbolt/CyberDB) is natively based on Python, and you can use CyberDB like dictionaries and lists; Redis-py is just an interface for operating Redis in Python.