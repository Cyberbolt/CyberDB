# API

This part of the documentation covers all the interfaces of CyberDB. For the parts of CyberDB that depend on external libraries, we document the most important parts here and provide a link to the specification document.


## cyberdb.Server Class

**class cyberdb.Server**

This class is used to create CyberDB server objects.

```python
def start(self, host: str = '127.0.0.1', port: int = 9980,
            password: str = None, max_con: int = 500, timeout: int = 0,
            print_log: bool = False, encrypt: bool = False):
'''
	Starts the CyberDB server in the background, which does not block 
	foreground tasks.
	
	Parameters:
	
		host -- TCP listening host address, such as 127.0.0.1.
		
		port – TCP listening port.
		
		password -- TCP communication password, it is recommended to use 
		a combination of English letters and numbers,
		Up to 32 characters long.
		
		max_con -- the maximum number of concurrency.
		
		timeout -- The timeout for a single connection, in seconds.
		
		print_log -- whether to print the communication log, Fasle does not 
		print it.
		
		encrypt -- Whether to encrypt the communication content, Fasle is 
		not encrypted. The encryption algorithm is AES-256 and the key is 
		password.
		
	Return Type: None
'''
```

```python
def run(self, host: str = '127.0.0.1', port: int = 9980,
        password: str = None, max_con: int = 500, timeout: int = 0,
        print_log: bool = False, encrypt: bool = False):
'''
	Running the CyberDB server in the foreground blocks foreground tasks.
	The parameters are the same as the start method.

	Return Type: None
'''
```

```python
def set_ip_whitelist(self, ips: list):
'''
	Set the ip whitelist. When CyberDB encrypts communication, only 
	whitelisted ip connections are allowed.

	This method only works if cyberdb.Server.start(encrypt=True) or 
	cyberdb.Server.run(encrypt=True) are enabled.

	Parameters:

		ips -- the type is a list, the format is ['192.168.1.1', 
		'118.123.89.137']

	Return Type: None
'''
```

```python
def set_backup(self, file_name: str = 'data.cdb', cycle: int = 900):
'''
	Set timed backup. After this operation is set, data persistent backup 
	will be performed at the specified period, and the CyberDB database 
	will be saved to the hard disk.

	parameter:

		file_name -- the name of the file generated by the backup, the file 
		suffix must be .cdb.

		cycle -- The cycle of the cyclic backup, in seconds.

	Return Type: None
'''
```

```python
def save_db(self, file_name: str = 'data.cdb'):
'''
	Data persistence, save the CyberDB database to the hard disk.

	parameter:

		file_name -- the name of the file generated by the backup, the file 
		suffix must be .cdb.

	Return Type: None
'''
```

```python
def load_db(self, file_name: str = 'data.cdb'):
'''
	Load a file in .cdb format to load the CyberDB database backed up from 
	the hard disk back into memory.

	parameter:
		file_name -- the file name generated by data persistence, the file 
		suffix must be .cdb.

	Return Type: None
'''
```

## cyberdb.connect Function

```python
def cyberdb.connect(host: str = '127.0.0.1', port: int = 9980, password:
            str = None, encrypt: bool = False, time_out: int = None) -> Client:
'''
	Connect the client to the CyberDB server.

	Parameters:

		host -- the connection address, such as 127.0.0.1

		port -- connection port

		password -- connection password

		encrypt -- Whether to encrypt communication, if the server enables 
		encrypt to be True, it must be True here, and vice versa.

		time_out -- The timeout for each connection in the connection pool, 
		in seconds. Connections in the connection pool will be discarded 
		after time_out seconds of inactivity, and a new connection will be 
		generated next time. The connection pool will manage the 
		connections automatically, and the developer does not need to pay 
		attention to the details. If this parameter is None, there will be 
		no timeout, and the connection pool will maintain the connection 
		until it expires, after which a new connection will be regenerated.

	Return Type: Client
'''
```

## cyberdb.Client Class

**class cyberdb.Client**

The cyberdb.Client object returned by the cyberdb.connect function is used to generate the Proxy object.

```python
def get_proxy(self) -> Proxy:
'''
	Generate a Proxy object.

	Return Type: None
'''
```

## Proxy Class

The Proxy object generated by the cyberdb.Client.get_proxy method can operate on the CyberDB database and manage the TCP connections of the CyberDict and CyberList sub-objects generated by the Proxy. After the Proxy object is initialized, it can be used after executing the Proxy.connect method. The Proxy object and its sub-objects will perform remote operations on the server-side CyberDB database.

**class Proxy**

```python
def connect(self):
'''
	Get a TCP connection from the connection pool and bind it to the Proxy 
	object.

	Return Type: None
'''
```

```python
def close(self):
'''
	Cancel the TCP connection bound to the Proxy object and return it to 
	the connection pool. It needs to be reset before the next operation.
	Execute the Proxy.connect method.

	Return Type: None
'''
```

```python
def create_cyberdict(self, table_name: str, content: dict = {}):
'''
	Create a CyberDict table.
	Parameters:
		table_name – table name.
		content -- table content, needs to be a dictionary type, the 
		default is an empty dictionary.
	Return Type: None
'''
```

```python
def create_cyberlist(self, table_name: str, content: list = []):
'''
	Create the CyberList table.

	Parameters:

		table_name – table name.

		content -- table content, it needs to be a list type, the default 
		is an empty list.

	Return Type: None
'''
```

```python
def get_cyberdict(self, table_name: str) -> CyberDict:
'''
	Get the CyberDict table.

	Parameters:

		table_name – table name.

	Return Type: CyberDict, which is a sub-object generated by Proxy, 
	which controls the TCP connection.
'''
```

```python
def get_cyberlist(self, table_name: str) -> CyberList:
'''
	Get the CyberList table.

	Parameters:

		table_name – table name.

	Return type: CyberList, which is a sub-object generated by Proxy, which 
	controls the TCP connection.
'''
```

```python
def print_tables(self):
'''
	Print all tables in the CyberDB database.
	
	Return Type: None
'''
```

```python
def delete_table(self, table_name: str):
'''
	Drop the table_name table in the CyberDB database.

	Parameters:

		table_name – the name of the table to drop.

	Return Type: None
'''
```

## cyberdb.CyberDict Class

**class cyberdb.CyberDict**

A child object generated by a Proxy object for performing Dictionaries operations. This object will perform remote operations on the server-side CyberDB database. Shares the same TCP connection with the Proxy object. The connection will follow the connection of the Proxy. After the Proxy releases the connection, the object will also lose the connection. CyberDict can execute the get, setdefault, update, keys, values, items, pop, popitem, clear methods and common magic methods of Dictionaries, please refer to [Python dictionary official documentation](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict).

Iterate over CyberDict using a for loop with client space complexity o(n), where n is the length of CyberDict.keys() .

```python
def todict(self) -> Dict:
'''
	Convert CyberDict to Dictionaries.

	Return Type: Dict
'''
```

## cyberdb.CyberList 类

**class cyberdb.CyberList**

A child object generated by a Proxy object for performing Lists operations. This object will perform remote operations on the server-side CyberDB database. Shares the same TCP connection with the Proxy object. The connection will follow the connection of the Proxy. After the Proxy releases the connection, the object will also lose the connection. CyberList can execute the append, extend, insert, pop, remove, count, index, reverse, sort, clear methods and common magic methods of Lists, please refer to [Python List Official Documentation](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists).

The CyberList is iterated using a for loop, each iteration will fetch the content from the server, and the space complexity of the client is o(1).

```python
def tolist(self) -> List:
'''
	Convert CyberList to Lists.

	Return Type: List
'''
```

