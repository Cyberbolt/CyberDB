# CyberDB

[Chinese Version](https://github.com/Cyberbolt/CyberDB/blob/main/README_CHN.md)

CyberDB is a lightweight Python in-memory database. It is designed to use Python's built-in data structures Dictionaries, Lists for data storage, efficient communication through Socket TCP, and provide data persistence. This module is often used in Gunicorn inter-process communication, distributed computing and other fields.

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


It is strongly recommended to use a for loop to iterate CyberDict, each iteration will get v from the server, and the space complexity of the client is o(1). Iteration can also be used for CyberDict. In the iteration of CyberDict, the client space complexity is o(n), and n is the size of CyberDict.keys().

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

With CyberDB, memory performance can be fully utilized, and different processes (or even different hosts) can communicate through Python's data structures. Thank you!

## Notice

Due to encoding limitations, CyberDB will recognize 0 as None, but it does not affect the calculation, please convert None to 0 in the desired position.
