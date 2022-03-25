import time
import inspect
import socket
from typing import List, Tuple, Dict

from obj_encrypt import Secret

from ..data import datas
from ..extensions import CyberDBError, WrongInputCyberDBError, WrongPasswordCyberDBError, WrongTableNameCyberDBError
from ..extensions.signature import Signature
from . import Stream


class Connection:
    '''
        TCP connection data type
    '''

    def __init__(
        self,
        s: socket.socket = None,
    ):
        self.s = s


class ConPool:
    '''
        Maintain connection pool.
    '''

    def __init__(self, host: str, port: str, dp: datas.DataParsing,
                 time_out: int = None):
        self._host = host
        self._port = port
        self._dp = dp
        self._time_out = time_out
        self._connections = []

    def get(self):
        '''
            Get the connection from the connection pool.
        '''
        while self._connections:
            # If the connection is full, the loop waits until a connection
            # is free.
            connection = self._connections.pop()
            time_now = int(time.time())
            if self._time_out:
                if time_now > connection['timestamp'] + self._time_out:
                    continue
            # Check if the server is down.
            r = confirm_the_connection(connection['s'], self._dp)
            if r['code'] == 1:
                return connection['s']
            else:
                pass

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._host, self._port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s

    def put(self, s: socket.socket):
        '''
            Return the connection to the connection pool.
        '''
        # If a connection timeout is set, get the current timestamp.
        timestamp = None
        if self._time_out:
            timestamp = int(time.time())

        self._connections.insert(0, {
            's': s,
            'timestamp': timestamp
        })


def network(func):
    '''
        Network operations before and after encapsulating CyberDB data 
        structure methods.
    '''

    def wrapper(self, *args, **kw):
        stream = Stream(self._con.s, self._dp)
        client_obj = func(self, *args, **kw)
        stream.write(client_obj)

        server_obj = stream.read()
        if server_obj['code'] == 0:
            self._con.s.close()
            raise server_obj['Exception']

        if server_obj.get('content'):
            return server_obj['content']

    return wrapper


class CyberDict:

    def __init__(
        self,
        table_name: str,
        dp: datas.DataParsing,
        con: Connection
    ):
        self._table_name = table_name
        self._dp = dp
        self._con = con
        self._route = '/cyberdict'

    @network
    def __repr__(self):
        return {
            'route': self._route + '/repr',
            'table_name': self._table_name
        }

    @network
    def __str__(self):
        return {
            'route': self._route + '/str',
            'table_name': self._table_name
        }

    @network
    def __len__(self):
        return {
            'route': self._route + '/len',
            'table_name': self._table_name
        }

    def __iter__(self):
        return self.generate()

    @network
    def __getitem__(self, key):
        return {
            'route': self._route + '/getitem',
            'table_name': self._table_name,
            'key': key
        }

    @network
    def __setitem__(self, key, value):
        return {
            'route': self._route + '/setitem',
            'table_name': self._table_name,
            'key': key,
            'value': value
        }

    @network
    def __delitem__(self, key):
        return {
            'route': self._route + '/delitem',
            'table_name': self._table_name,
            'key': key
        }

    @network
    def todict(self) -> Dict:
        return {
            'route': self._route + '/todict',
            'table_name': self._table_name
        }

    @network
    def get(self, key, default=None) -> any:
        return {
            'route': self._route + '/get',
            'table_name': self._table_name,
            'key': key,
            'default': default
        }

    @network
    def setdefault(self, key, default=None) -> None:
        return {
            'route': self._route + '/setdefault',
            'table_name': self._table_name,
            'key': key,
            'default': default
        }

    @network
    def update(self, dict2) -> None:
        return {
            'route': self._route + '/update',
            'table_name': self._table_name,
            'dict2': dict2,
        }

    @network
    def keys(self) -> List:
        return {
            'route': self._route + '/keys',
            'table_name': self._table_name
        }

    @network
    def values(self) -> List:
        return {
            'route': self._route + '/values',
            'table_name': self._table_name
        }

    @network
    def items(self) -> List[Tuple]:
        return {
            'route': self._route + '/items',
            'table_name': self._table_name
        }

    @network
    def pop(self, key, default=None) -> any:
        return {
            'route': self._route + '/pop',
            'table_name': self._table_name,
            'key': key,
            'default': default
        }

    @network
    def popitem(self) -> Tuple[any, any]:
        return {
            'route': self._route + '/popitem',
            'table_name': self._table_name
        }

    @network
    def clear(self) -> None:
        return {
            'route': self._route + '/clear',
            'table_name': self._table_name
        }

    def generate(self):
        for key in self.keys():
            yield key


class CyberList:

    def __init__(
        self,
        table_name: str,
        dp: datas.DataParsing,
        con: Connection
    ):
        self._table_name = table_name
        self._dp = dp
        self._con = con
        self._route = '/cyberlist'

    @network
    def __repr__(self):
        return {
            'route': self._route + '/repr',
            'table_name': self._table_name
        }

    @network
    def __str__(self):
        return {
            'route': self._route + '/str',
            'table_name': self._table_name
        }

    @network
    def __len__(self):
        return {
            'route': self._route + '/len',
            'table_name': self._table_name
        }

    def __iter__(self):
        return self.generate()

    @network
    def __getitem__(self, index):
        return {
            'route': self._route + '/getitem',
            'table_name': self._table_name,
            'index': index
        }

    @network
    def __setitem__(self, index, value):
        return {
            'route': self._route + '/setitem',
            'table_name': self._table_name,
            'index': index,
            'value': value
        }

    @network
    def __delitem__(self, index):
        return {
            'route': self._route + '/delitem',
            'table_name': self._table_name,
            'index': index
        }

    @network
    def tolist(self) -> List:
        return {
            'route': self._route + '/tolist',
            'table_name': self._table_name
        }

    @network
    def append(self, value) -> None:
        return {
            'route': self._route + '/append',
            'table_name': self._table_name,
            'value': value
        }

    @network
    def extend(self, obj) -> None:
        if type(obj) == CyberList:
            obj = obj.tolist()

        return {
            'route': self._route + '/extend',
            'table_name': self._table_name,
            'obj': obj
        }

    @network
    def insert(self, index, value) -> None:
        return {
            'route': self._route + '/insert',
            'table_name': self._table_name,
            'index': index,
            'value': value
        }

    @network
    def pop(self, index: int = -1) -> any:
        return {
            'route': self._route + '/pop',
            'table_name': self._table_name,
            'index': index
        }

    @network
    def remove(self, value) -> None:
        return {
            'route': self._route + '/remove',
            'table_name': self._table_name,
            'value': value
        }

    @network
    def count(self, value) -> int:
        return {
            'route': self._route + '/count',
            'table_name': self._table_name,
            'value': value
        }

    @network
    def index(self, value) -> int:
        return {
            'route': self._route + '/index',
            'table_name': self._table_name,
            'value': value
        }

    @network
    def reverse(self) -> None:
        return {
            'route': self._route + '/reverse',
            'table_name': self._table_name
        }

    @network
    def sort(self, key=None, reverse=False) -> None:
        # Reference the lambda part to func.
        if key:
            if key.__code__.co_name == '<lambda>':
                key = 'func = ' + \
                    inspect.getsource(key).split('=')[1].rsplit(')')[0]
            # De-indent the code and reference the function to the func.
            elif key.__code__.co_name:
                code = inspect.getsource(key)
                num = 0
                for i in range(len(code)):
                    if code[i] != ' ':
                        num = i
                        break
                if i != 0:
                    code_new = ''
                    for line in code.splitlines():
                        code_new += line[num:] + '\n'
                else:
                    code_new = code
                key = code_new + '\nfunc = {}'.format(key.__code__.co_name)

        return {
            'route': self._route + '/sort',
            'table_name': self._table_name,
            'key': key,
            'reverse': reverse
        }

    @network
    def clear(self) -> None:
        return {
            'route': self._route + '/clear',
            'table_name': self._table_name,
        }

    def generate(self):
        for i in range(self.__len__()):
            yield self.__getitem__(i)


class Proxy:
    '''
        Database instance per session

        This object is not thread safe, please regenerate in each thread or 
        coroutine.
    '''

    def __init__(self, con_pool: ConPool, dp: datas.DataParsing):
        self._con_pool = con_pool
        self._dp = dp
        # The connection used by the proxy, the first is the reader and the
        # second is the writer.
        self._con = Connection()

    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return True

    def connect(self):
        '''
            Get the latest connection from the connection pool.

            This method does not necessarily create a new connection, if the 
            connection of the connection pool is available, it will be 
            obtained directly.
        '''
        # If the proxy already has a connection, the connection will be
        # returned to the connection pool first.
        if self._con.s != None:
            self._con_pool.put(self._con.s)

        s = self._con_pool.get()
        self._con.s = s

    def close(self):
        '''
            Return the connection to the connection pool.
        '''
        if self._con == None:
            raise CyberDBError(
                'The connection could not be closed, the proxy has not acquired a connection.')

        self._con_pool.put(self._con.s)
        self._con.s = None

    def create_cyberdict(self, table_name: str, content: dict = {}):
        if type(table_name) != str:
            raise WrongInputCyberDBError('Please use str for the table name.')
        if type(content) != dict:
            raise WrongInputCyberDBError(
                'The input database table type is not a Python dictionary.')

        stream = Stream(self._con.s, self._dp)
        client_obj = {
            'route': '/create_cyberdict',
            'table_name': table_name,
            'content': content
        }
        stream.write(client_obj)

        server_obj = stream.read()

        if server_obj['code'] == 0:
            raise WrongTableNameCyberDBError('Duplicate table names already exist!')

    def get_cyberdict(self, table_name: str) -> CyberDict:
        '''
            Get the network object of the table from the database.
        '''
        if type(table_name) != str:
            raise WrongInputCyberDBError('Please use str for the table name.')

        stream = Stream(self._con.s, self._dp)

        client_obj = {
            'route': '/exam_cyberdict',
            'table_name': table_name
        }
        stream.write(client_obj)

        server_obj = stream.read()
        if server_obj['code'] == 0:
            raise WrongTableNameCyberDBError('{} table does not exist.'.format(table_name))
        else:
            table = CyberDict(table_name, self._dp, self._con)
            return table

    def create_cyberlist(self, table_name: str, content: list = []):
        if type(table_name) != str:
            raise WrongInputCyberDBError('Please use str for the table name.')
        if type(content) != type(list()):
            raise WrongInputCyberDBError(
                'The input database table type is not a Python dictionary.')

        stream = Stream(self._con.s, self._dp)
        client_obj = {
            'route': '/create_cyberlist',
            'table_name': table_name,
            'content': content
        }
        stream.write(client_obj)

        server_obj = stream.read()

        if server_obj['code'] == 0:
            raise WrongTableNameCyberDBError('Duplicate table names already exist!')

    def get_cyberlist(self, table_name: str) -> CyberList:
        '''
            Get the network object of the table from the database.
        '''
        if type(table_name) != str:
            raise WrongInputCyberDBError('Please use str for the table name.')

        stream = Stream(self._con.s, self._dp)

        client_obj = {
            'route': '/exam_cyberlist',
            'table_name': table_name
        }
        stream.write(client_obj)

        server_obj = stream.read()
        if server_obj['code'] == 0:
            raise WrongTableNameCyberDBError('{} table does not exist.'.format(table_name))
        else:
            table = CyberList(table_name, self._dp, self._con)
            return table

    def print_tables(self):
        @network
        def get_tables(self):
            return {
                'route': '/print_tables'
            }
            
        r = get_tables(self)
        for line in r:
            print('table name: {}  type name: {}'.format(line[0], line[1]))

    def delete_table(self, table_name: str):
        if type(table_name) != str:
            raise WrongInputCyberDBError('Please use str for the table name.')

        stream = Stream(self._con.s, self._dp)

        client_obj = {
            'route': '/exam_cyberlist',
            'table_name': table_name
        }
        stream.write(client_obj)

        server_obj = stream.read()
        if server_obj['code'] == 0:
            raise WrongTableNameCyberDBError('{} table does not exist.'.format(table_name))
        
        client_obj = {
            'route': '/delete_table',
            'table_name': table_name
        }
        stream.write(client_obj)
        stream.read()


class Client:
    '''
        This object blocks execution and is recommended to be used as a 
        global variable instead of running in an async function.
    '''

    def __init__(self, con_pool: ConPool, dp: datas.DataParsing):
        self._con_pool = con_pool
        self._dp = dp

    def get_proxy(self) -> Proxy:
        '''
            Get proxy data.
        '''
        proxy = Proxy(self._con_pool, self._dp)
        return proxy


def connect(host: str = '127.0.0.1', port: int = 9980, password:
            str = None, encrypt: bool = False, time_out: int = None):
    '''
        Connect to the CyberDB server via TCP, this method will run 
        synchronously.
    '''
    if not password:
        raise WrongPasswordCyberDBError('The password cannot be empty.')
    if time_out and type(time_out) != int:
        raise CyberDBError('time_out must be an integer.')

    # Responsible for encrypting and decrypting objects.
    secret = Secret(key=password)
    # for digital signature
    signature = Signature(salt=password.encode())
    dp = datas.DataParsing(secret, signature, encrypt=encrypt)
    con_pool = ConPool(host, port, dp, time_out=time_out)

    # Synchronously test whether the connection is successful.
    s = con_pool.get()
    confirm_the_connection(s, dp)
    con_pool.put(s)

    client = Client(con_pool, dp)
    return client


def confirm_the_connection(s: socket.socket, dp: datas.DataParsing) -> dict:
    '''
        The connection is detected when the database connects for the first 
        time.
    '''
    try:
        stream = Stream(s, dp)

        client_obj = {
            'route': '/connect'
        }
        stream.write(client_obj)

        server_obj = stream.read()

        return {
            'code': 1,
            'content': server_obj
        }
    except Exception as e:
        return {
            'code': 0,
            'Exception': e
        }
