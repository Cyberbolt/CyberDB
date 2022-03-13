import asyncio

from obj_encrypt import Secret

from . import AioStream
from ..data import datas
from ..extensions import MyThread, CyberDBError
from ..extensions.signature import Signature


result = None # Check whether the connection is successful


class Connection:
    '''
        Asyncio TCP connection data type
    '''

    def __init__(
        self,
        reader: asyncio.streams.StreamReader=None,
        writer: asyncio.streams.StreamWriter=None
    ):
        self.reader = reader
        self.writer = writer


class ConPool:
    '''
        Maintain connection pool.
    '''
    
    def __init__(self, host: str, port: str, dp: datas.DataParsing):
        self._host = host
        self._port = port
        self._dp = dp
        self._connections = []

    async def get(self):
        '''
            Get the connection from the connection pool.
        '''
        if self._connections:
            # If the connection is full, the loop waits until a connection 
            # is free.
            while self._connections:
                reader, writer = self._connections.pop(0)
                if await self.exam(reader, writer):
                    return reader, writer

        reader, writer = await asyncio.open_connection(
        self._host, self._port)
        return reader, writer

    def put(self, reader: asyncio.streams.StreamReader, 
        writer: asyncio.streams.StreamWriter):
        '''
            Return the connection to the connection pool.
        '''
        self._connections.append((reader, writer))

    async def exam(self, reader: asyncio.streams.StreamReader, 
        writer: asyncio.streams.StreamWriter):
        '''
            Check if the connection is valid.
        '''
        # try:
        stream = AioStream(reader, writer, self._dp)
        client_obj = {
            'route': '/connect'
        }
        await stream.write(client_obj)

        server_obj = await stream.read()
        return True
        # except:
        #     return False


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
        
    async def __getitem__(self, key):
        stream = AioStream(self._con.reader, self._con.writer, self._dp)

        client_obj = {
            'route': self._route + '/getitem',
            'table_name': self._table_name,
            'key': key
        }
        
        await stream.write(client_obj)

        server_obj = await stream.read()
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

    async def connect(self):
        '''
            Get the latest connection from the connection pool.

            This method does not necessarily create a new connection, if the 
            connection of the connection pool is available, it will be 
            obtained directly.
        '''
        # If the proxy already has a connection, the connection will be 
        # returned to the connection pool first.
        if self._con.reader != None and self._con.writer != None:
            self._con_pool.put(self._con.reader, self._con.writer)
            
        reader, writer = await self._con_pool.get()
        self._con.reader = reader
        self._con.writer = writer

    async def close(self):
        '''
            Return the connection to the connection pool.
        '''
        if self._con.reader == None or self._con == None:
            raise CyberDBError('The connection could not be closed, the proxy has not acquired a connection.')

        self._con_pool.put(self._con.reader, self._con.writer)
        self._con.reader = None
        self._con.writer = None

    async def create_cyberdict(self, table_name: str, content: dict={}):
        if type(table_name) != type(''):
            raise CyberDBError('Please use str for the table name.')
        if type(content) != type(dict()):
            raise CyberDBError('The input database table type is not a Python dictionary.')

        stream = AioStream(self._con.reader, self._con.writer, self._dp)
        client_obj = {
            'route': '/create_cyberdict',
            'table_name': table_name,
            'content': content
        }
        await stream.write(client_obj)

        server_obj = await stream.read()

        if server_obj['code'] == 0:
            raise CyberDBError('Duplicate table names already exist!')

        return server_obj

    async def get_cyberdict(self, table_name: str) -> CyberDict:
        '''
            Get the network object of the table from the database.
        '''
        if type(table_name) != type(''):
            raise CyberDBError('Please use str for the table name.')
        
        stream = AioStream(self._con.reader, self._con.writer, self._dp)

        client_obj = {
            'route': '/exam_cyberdict',
            'table_name': table_name
        }
        await stream.write(client_obj)

        server_obj = await stream.read()
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
    str=None) -> Client:
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
    t = MyThread(target=asyncio.run, 
        args=(confirm_the_connection(con_pool, dp), ) )
    t.daemon = True
    t.start()
    t.join()
    result = t.get_result()
    if result['code'] == 0:
        raise result['Exception']

    client = Client(con_pool, dp)
    return client


async def confirm_the_connection(con_pool: ConPool, dp: datas.DataParsing) -> \
    dict:
    '''
        The connection is detected when the database connects for the first 
        time.
    '''
    try:
        reader, writer = await con_pool.get()
        stream = AioStream(reader, writer, dp)

        client_obj = {
            'route': '/connect'
        }
        await stream.write(client_obj)

        server_obj = await stream.read()
        
        writer.close()
        
        return {
            'code': 1,
            'content': server_obj
        }
    except (ConnectionRefusedError, CyberDBError) as e:
        return {
            'code': 0,
            'Exception': e
        }
    # except Exception as e:
    #     return {
    #         'code': 0,
    #         'Exception': CyberDBError('Incorrect address, port or password for database.')
    #     }


