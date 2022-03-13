import time
import socket

from obj_encrypt import Secret

from ..data import datas
from ..extensions import CyberDBError
from ..extensions.signature import Signature
from . import Stream


class Connection:
    '''
        TCP connection data type
    '''

    def __init__(
        self,
        s: socket.socket=None,
    ):
        self.s = s


class ConPool:
    '''
        Maintain connection pool.
    '''
    
    def __init__(self, host: str, port: str, dp: datas.DataParsing, 
        time_out: int=None):
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
                if connection['timestamp'] + self._time_out <= time_now:
                    # Check if the server is down.
                    if getattr(connection['s'], '_closed'):
                        pass
                    else:
                        return connection['s']
        
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
        
    def __getitem__(self, key):
        stream = Stream(self._con.s, self._dp)

        client_obj = {
            'route': self._route + '/getitem',
            'table_name': self._table_name,
            'key': key
        }
        
        stream.write(client_obj)

        server_obj = stream.read()
        if server_obj['code'] == 0:
            self._con.writer.close()
            raise server_obj['Exception']

        return server_obj['content']


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
            self._con_pool.put(self._con.reader, self._con.writer)
            
        s = self._con_pool.get()
        self._con.s = s

    def close(self):
        '''
            Return the connection to the connection pool.
        '''
        if self._con.reader == None or self._con == None:
            raise CyberDBError('The connection could not be closed, the proxy has not acquired a connection.')

        self._con_pool.put(self._con.reader, self._con.writer)
        self._con.s = None

    def create_cyberdict(self, table_name: str, content: dict={}):
        if type(table_name) != type(''):
            raise CyberDBError('Please use str for the table name.')
        if type(content) != type(dict()):
            raise CyberDBError('The input database table type is not a Python dictionary.')

        stream = Stream(self._con.s, self._dp)
        client_obj = {
            'route': '/create_cyberdict',
            'table_name': table_name,
            'content': content
        }
        stream.write(client_obj)

        server_obj = stream.read()

        if server_obj['code'] == 0:
            raise CyberDBError('Duplicate table names already exist!')

        return server_obj

    def get_cyberdict(self, table_name: str) -> CyberDict:
        '''
            Get the network object of the table from the database.
        '''
        if type(table_name) != type(''):
            raise CyberDBError('Please use str for the table name.')
        
        stream = Stream(self._con.s, self._dp)

        client_obj = {
            'route': '/exam_cyberdict',
            'table_name': table_name
        }
        stream.write(client_obj)

        server_obj = stream.read()
        if server_obj['code'] == 0:
            raise CyberDBError('{} table does not exist.'.format(table_name))
        else:
            table = CyberDict(table_name, self._dp, self._con)
            return table


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

    def check_connection_pool(self):
        pass
    

def connect(host: str='127.0.0.1', port: int=9980, password: 
    str=None):
    '''
        Connect to the CyberDB server via TCP, this method will run 
        synchronously.
    '''
    if not password:
        raise RuntimeError('The password cannot be empty.')

    # Responsible for encrypting and decrypting objects.
    secret = Secret(key=password)
    # for digital signature
    signature = Signature(salt=password.encode())
    dp = datas.DataParsing(secret, signature)
    con_pool = ConPool(host, port, dp)

    # Synchronously test whether the connection is successful.
    confirm_the_connection(con_pool, dp)

    client = Client(con_pool, dp)
    return client

      
def confirm_the_connection(con_pool: ConPool, dp: datas.DataParsing) -> dict:
    '''
        The connection is detected when the database connects for the first 
        time.
    '''
    try:
        s = con_pool.get()
        stream = Stream(s, dp)

        client_obj = {
            'route': '/connect'
        }
        stream.write(client_obj)

        server_obj = stream.read()
        
        con_pool.put(s)
        
        return {
            'code': 1,
            'content': server_obj
        }
    except (ConnectionRefusedError, CyberDBError) as e:
        return {
            'code': 0,
            'Exception': e
        }
        