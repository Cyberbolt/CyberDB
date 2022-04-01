# Using CyberDB as Flask's In-memory Database in Production

Earlier we talked about CyberDB's [Quick Start](https://www.cyberlight.xyz/static/cyberdb/), now we need to bring it to a place where it can play its role, and use CyberDB as Flask's in the production environment An in-memory database that runs with Gunicorn and enables multi-process communication.

This article is explained through a Flask example that is as concise as possible, and will not involve complex web knowledge. The core idea is CyberDB + Gunicorn + Gevent + Flask (multi-process + coroutine), start a CyberDB server, use Gunicorn multi-process to run the Flask instance, the instance of each process runs through Gevent, and the CyberDB client is used to connect to the in-memory database in the process , thereby achieving high concurrent access to the CyberDB database.

Articles are run using PyPy, as well as CPython.

Runtime: Python 3.8.12, PyPy 7.3.7

The directory structure of this project
```bash
.
├── app.py
├── cyberdb_init.py
├── cyberdb_serve.py
├── requirements.txt
└── venv
```
We explain the core operations of CyberDB by listing the contents of each file in order.

File requirements.txt
```
CyberDB>=0.7.1
Flask==2.1.1
gevent==21.12.0
gunicorn==20.1.0
```
dependencies of this project. This article is not a basic Python tutorial, please refer to related documents to create a virtual environment venv directory and install the dependencies in requirements.txt.

After generating the venv directory and installing the dependencies, all the following operations will run in the activated virtual environment.

File cyberdb_init.py
```python
'''
This module is used to initialize the table structure of CyberDB, and it is 
only used for the first run, and will not be used subsequently.
'''


import time

import cyberdb

db = cyberdb.Server()
# Configure the address, port and password of the CyberDB server.
db.start(host='127.0.0.1', port=9980, password='123456')

# After the server starts, connect to the CyberDB server.
time.sleep(3)
client = cyberdb.connect(host='127.0.0.1', port=9980, password='123456')
# Generate proxy object.
with client.get_proxy() as proxy:
    # Create a table centre of type CyberDict and initialize the contents.
    proxy.create_cyberdict('centre')
    centre = proxy.get_cyberdict('centre')
    centre['content'] = 'Hello CyberDB!'

# Save CyberDB to data.cdb.
db.save_db('data.cdb')
```

Execute in the project root directory
```bash
python cyberdb_init.py
```
At this point, the initialization of the CyberDB database table is completed, a table named center and type CyberDict is created in CyberDB, the value of the initial 'content' key is 'Hello CyberDB!', and finally the CyberDB database is saved to the hard disk (project root directory generates a file named data.cdb).

File cyberdb_serve.py
```python
import cyberdb


def main():
    # Run the CyberDB server in the background and set relevant 
    # information.
    db = cyberdb.Server()
    # Read data.cdb from hard disk to CyberDB.
    db.load_db('data.cdb')
    # Backup the database every 300 seconds.
    db.set_backup('data.cdb', cycle=300)
    db.run(
        host='127.0.0.1', # TCP run address
        port=9980, # TCP listening port
        password='hWjYvVdqRC', # Database connection password
        max_con=10000, # max concurrency
        encrypt=True, # encrypted communication
        print_log=False # do not print logs
    )


if __name__ == '__main__':
    main()
```
Execute it in the project root directory
```bash
python cyberdb_serve.py
```
to run the CyberDB server.

If encrypt=True is set here, CyberDB will encrypt the TCP communication content using the AES-256 algorithm. After enabling encrypt=True, CyberDB only allows ip communication in the whitelist, the default whitelist is ['127.0.0.1'], the whitelist [setting method](https://www.cyberlight.xyz/static/cyberdb/API/#cyberdbserver). Generally, if you only need to communicate between local processes, you do not need to enable encrypt=True and set a whitelist. This operation is only required for remote communication.

File app.py
```python
import cyberdb
from flask import Flask, g


# Connect to CyberDB and spawn a client instance.
client = cyberdb.connect(
    host='127.0.0.1', 
    port=9980, 
    password='hWjYvVdqRC',
    # If the server is encrypted, the client must be encrypted, and vice 
    # versa.
    encrypt=True,
    # Each connection will be discarded if there is no operation for more 
    # than 900 seconds.
    # Connections are managed intelligently by the connection pool, 
    # no relationship details are required.
    time_out=900
)

# Create a Flask instance, please refer to the Flask documentation for this 
# section https://flask.palletsprojects.com/
app = Flask(__name__)


@app.before_request
def before_request():
    # Generate a proxy object before each request is executed.
    g.proxy = client.get_proxy()
    # Get a connection from the connection pool.
    g.proxy.connect()


@app.get("/")
def hello_world():
    # Get the centre table from the database.
    centre = g.proxy.get_cyberdict('centre')
    
    return {
        'code': 1,
        'content': centre['content']
    }


@app.teardown_request
def teardown_request(error):
    # Return the connection to the connection pool after each request is executed.
    g.proxy.close()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
```
This module will use client.get_proxy() to get the proxy object before each request is executed ( before_request ). Each obtained proxy object can be bound to a TCP connection. Here, proxy.connect() is used to get the connection from the connection pool. In the view function hello_world, the object center obtained by the proxy shares the same connection with the proxy. After the connection of the proxy is released, the center will also lose the connection. After each request ( teardown_request ), use the proxy.close() method to release the connection bound by the proxy and return it to the connection pool.

The time_out parameter of cyberdb.connect is the timeout for each connection in the connection pool, where each connection will be discarded after 900 seconds of inactivity. If this parameter is not set, each connection in the connection pool will be maintained until it expires.

Run in the project root directory
```bash
gunicorn -w 4 -b 127.0.0.1:8000 -k gevent app:app
```
Start a Flask instance with 4 processes, Gevent.

Browser access to 127.0.0.1:8000 will get the following response
```JSON
{"code":1,"content":"Hello CyberDB!"}
```
With this example, you can deploy CyberDB into more complex web environments and take full advantage of the low-latency characteristics of memory.
