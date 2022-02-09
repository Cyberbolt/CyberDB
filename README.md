# CyberDB

(This project is in the testing phase. Do not use it in production environment.)
CyberDB is a lightweight main memory database of Python. It can use Python's Dictionaries, Lists for data storage,build an efficient communication through Socket TCP, and provide data persistence. Developers can customize their own data structures based on this module, which is often used in Gunicorn inter-process communication, distributed computing, machine learning deployment and other fields.

### Installation

Python version: 3.8 and above

1. Enter the command window, create a virtual environment, and enter the following commands in turn

Linux and macOS:

```python
python3 -m venv venv # create virtual environment
. venv/bin/activate # Activate the virtual environment
```

Windows:


```python
python -m venv venv # create virtual environment
venv\Scripts\activate # Activate the virtual environment
```

2. Install 'CyberDB', enter in turn


```python
pip install --upgrade pip
pip install cyberdb
```

If your server and client are running in two different project directories, please install 'CyberDB' in the virtual environment of the server and client respectively.

### Links

- GitHub: [https://github.com/Cyberbolt/CyberDB](https://github.com/Cyberbolt/CyberDB) 
- PyPI: [https://pypi.org/project/CyberDB/](https://pypi.org/project/CyberDB/)
- Documentation: In writing

### Use

In this module,please use 'CyberDict' and 'CyberList' instead of 'dict' and list ('CyberDict' and 'CyberList' are TCP-based Dictionaries-like, Lists-like objects).

#### Server

Please enter the root directory of your project


For the first run, please create a separate 'py' file to create a database table when the server is initialized, and save the table information to the local after running the server. (This file is used when creating a table for the first time, and will not run in the future)


```python
from cyberdb import DBServer

server = DBServer()
server.create_cyberdict('dict1') # Create a database table named dict1
server.create_cyberdict('dict2') # Create a database table named dict2
server.create_cyberlist('list1') # Create a database table named list1
server.start(password='123123') # run the server in the background
'''
This run only saves the table during initialization, the password can be set at will, and will not be used later
'''
server.save_db() # to save server data to local
server.stop() # to stop running the server
```

    CyberDB is starting...
    Server stopped.

After the server runs, the 'cyberdb_file' directory will be created in the project root directory (do not delete it), and the client configuration file 'cyberdb_file/config.cdb' will be generated (client operation depends on this file). The default file for database persistence is 'cyberdb_file/backup /data.cdb' 

Deploying the server


```python
from cyberdb import DBServer

server = DBServer()
server.load_db() # will automatically load 'cyberdb_file/backup/data.cdb'
server.start(host='127.0.0.1', password='123123', port=9980)
'''
Start the server, fill in the running address, password and port number
If server.start(password='123123') is used, it will run at default address '127.0.0.1' and port'9980'
'''
server.set_backup(period=900)
'''
Set database backup, the default time is once every 900s, and the backup will be permanent until the server stops running
If this interface is not called, the data will not be persisted
If you want to stop a running backup, call 'server.set_backup(period=None)'
'''
# If your program will not run permanently in the background, please add the following command to make the program run permanently
import time
while True:
    time.sleep(1000000000)
```

    File cyberdb_file/backup/data.cdb loaded successfully.
    CyberDB is starting...
    The backup cycle: 900s



The default file for database backup is 'cyberdb_file/backup/data.cdb' (this file will be automatically backed up or updated at the set backup time)

#### Client

Please enter the root directory of your project

Copying the 'cyberdb_file' of the server to the project root directory of the client (if the same project directory is used as the server and the client, there is no need to copy)

Connect to the database

```python
from cyberdb import DBClient
client = DBClient()
client.load_config('cyberdb_file/config.cdb') 
'''
Load the configuration file 'config.cdb'
The default value of the configuration file path is 'cyberdb_file/config.cdb' . If the path here is the same, you will not need to fill in the parameters.
'''
db = client.connect(host='127.0.0.1', password='123123', port=9980)
'''
Enter the address, password and port number configured on the server to obtain the connected database instance db
If you use db = client.connect(password='123123'), it will connect to the default address 127.0.0.1
and port 9980
'''
```


Manipulate CyberDict and CyberList (code shown later using Jupyter Notebook)


```python
dict1 = db.CyberDict.dict1
dict2 = db.CyberDict.dict2
list1 = db.CyberList.list1
```

This command can get the database table created by the server in the format of database's 'instance.datatype.tablename'
You can also use the following command to get


```python
dict1 = db['CyberDict']['dict1']
dict2 = db['CyberDict']['dict2']
list1 = db['CyberList']['list1']
```

The 'dict1', 'dict2', and 'list1' obtained here are all network objects. Calling the object method is to interact with the database remotely.

Add key-value pairs in 'dict1' and 'dict2'


```python
dict1.put(0, 'dict1')
dict1.put(10, 'test')
dict2.put(0, 'dict2')
```

To get the corresponding value


```python
dict1.get(0)
```




    'dict1'




```python
dict2.get(0)
```




    'dict2'



We use the ‘show’ method to see the table contents of 'dict1' and 'dict2'


```python
dict1.show()
```




    {0: 'dict1', 10: 'test'}




```python
dict2.show()
```




    {0: 'dict2'}



The ‘show’ method here can directly extract the data in the table ('dict' here), and can perform any 'dict' operation. Here the execution is: Copying the variate  from the database to the client. If your server and client use the same machine, it will occupy twice the memory. It is not recommended to use the ‘show’ method frequently on the same host.

'CyberDict' and 'CyberList'  support all public methods of 'dict' and list (such as 'dict.get(key), dict.items(), list.append(v), list.pop()', etc.), using any public method is based on TCP data interaction. So there is no support for iteration, no support for private methods (Python magic methods),and no access to data using 'dict[key]' and list[index] . 'CyberDB' gives corresponding alternatives, please read this article carefully. (If you insist on using magic methods, the corresponding API is provided in 'CyberDB's' official documentation)

Note: Use the ’show‘ method to copy the variate in the table to the client's local. The variate obtained by the ‘show’ method are complete dict or list objects, which can perform any operation of Python. Like:


```python
dict1.show()[10]
```




    'test'



We can get the length of 'CyberDict' using the 'get_length' method


```python
dict1.get_length()
```




    2



Deleting a key-value pair using the delete method


```python
dict1.delete(10)
```

'dict1.delete(10)' is equivalent to using 'del dict1[10]' locally

Performing common operations on 'CyberList' below

Increment 'list1' to a 5 * 5 all-zeros table


```python
for i in range(5):
    list1.append([0 for i in range(5)])
```

Using the 'show' method to get all the data of 'list1' (the 'show' method here is the same as 'CyberDict')


```python
list1.show()
```




    [[0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0]]



Using the 'update' method to modify the 4th value (subscript 3) of 'list1' to 1. ('update' only works on the first dimension of the table)


```python
list1.update(3, [1 for i in range(5)])
list1.show()
```




    [[0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [1, 1, 1, 1, 1],
     [0, 0, 0, 0, 0]]



Using the 'update_form' method to modify the 5th value (subscript 4, 4) of the 5th row of 'list1' to 1. ('update_form' is used to modify the two-dimensional form)


```python
list1.update_form(4, 4, 1)
list1.show()
```




    [[0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [1, 1, 1, 1, 1],
     [0, 0, 0, 0, 1]]



The 'loc' method can locate a one-dimensional table
As follows, using the 'loc' method to locate the 4th row of list1


```python
list1.loc(3)
```




    [1, 1, 1, 1, 1]



Use 'loc_form' to locate a two-dimensional table,the 5th row and 5th column of the table are located here


```python
list1.loc_form(4, 4)
```




    1



Slicing with 'slice'


```python
list1.slice(4, 6)
```




    [[0, 0, 0, 0, 1]]



To get the length of list1


```python
list1.get_length()
```




    5



Regarding the iteration of the list, although you can directly use the 'show' method to get the list and iterate, it will take up more memory (if the CyberList is large). CyberDB has built-in generators that can be used to iterate the CyberList as follows


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


This method is also suitable for iterating over the 'key' of CyberDict

####  Generalization 

With CyberDB, memory performance can be fully utilized, and different processes (or even different hosts) can communicate through Python's data structures. For tutorials on custom data structures and machine learning deployment, please refer to the official documentation. Thank you for your support!

CyberLight [https://www.cyberlight.xyz/](https://www.cyberlight.xyz/)