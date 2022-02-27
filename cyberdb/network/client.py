import asyncio

from obj_encrypt import Secret

from . import read
from ..data import datas
from ..extensions import MyThread
from ..extensions.signature import Signature


result = None # Check whether the connection is successful


class ConPool:
    '''
        Maintain connection pool.
    '''
    
    def __init__(self, host: str, port: str):
        self._host = host
        self._port = port
        self._connections = []

    async def get(self) -> tuple[asyncio.streams.StreamReader, asyncio.streams.StreamWriter]:
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
        else:
            reader, writer = await asyncio.open_connection(
            self._host, self._port)
            return reader, writer

    def put(self, reader: asyncio.streams.StreamReader, 
        writer: asyncio.streams.StreamWriter):
        '''
            Return the connection to the connection pool.
        '''
        self._connections.append({'con': (reader, writer)})

    async def exam(self, reader: asyncio.streams.StreamReader, 
        writer: asyncio.streams.StreamWriter):
        client_obj = {
            'route': '/exam'
        }
        data = self._dp.obj_to_data(client_obj)
        writer.write(data)
        await writer.drain()

        data = await reader.readuntil(separator=b'exit')
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._writer.close()
            raise RuntimeError(r['errors-code'])
        server_obj = r['content']
        print(server_obj)
        return True


class CyberDict:

    def __init__(
        self, 
        table_name: str, 
        con_pool: ConPool, 
        dp: datas.DataParsing,
        this_con: list[asyncio.streams.StreamReader, 
            asyncio.streams.StreamWriter]
    ):
        self._table_name = table_name
        self._con_pool = con_pool
        self._dp = dp
        self._reader, self._writer = this_con

    async def connect(self):
        '''
            Get a connection from the connection pool.
        '''
        self._reader, self._writer = await self._con_pool.get()

    async def check_connection(self):
        # Automatic database connection for the first time.
        if not self._writer:
            self._reader, self._writer = await self._con_pool.get()
            return

        client_obj = {
            'route': '/connect'
        }
        data = self._dp.obj_to_data(client_obj)
        self._writer.write(data)
        await self._writer.drain()

        data = await read(self._reader, self._writer)
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._writer.close()
            raise RuntimeError(r['errors-code'])
        server_obj = r['content']
        
    async def __getitem__(self, key):
        client_obj = {
            'route': '/{}/get_key',
            'key': key
        }
        data = self._dp.obj_to_data(client_obj)
        self._writer.write(data)
        await self._writer.drain()

        data = await read(self._reader, self._writer)
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._writer.close()
            raise RuntimeError(r['errors-code'])
        server_obj = r['content']
        return server_obj


class Data:
    '''
        Database instance per session

        This object is not thread safe, please regenerate in each thread or 
        coroutine.
    '''

    def __init__(self, con_pool: ConPool, dp: datas.DataParsing, 
        this_con: list[asyncio.streams.StreamReader, 
                    asyncio.streams.StreamWriter]):
        self._con_pool = con_pool
        self._dp = dp
        # TCP connection for this instance
        self._con = this_con


class Client:
    '''
        This object blocks execution and is recommended to be used as a 
        global variable instead of running in an async function.
    '''
    
    def __init__(self, con_pool: ConPool, dp: datas.DataParsing):
        self._con_pool = con_pool
        self._dp = dp

    def get_data(self):
        '''
            get database table
        '''
        async def task():
            reader, writer = await self._con_pool.get()
            return reader, writer

        t = MyThread(target=asyncio.run, args=(task(),))
        t.daemon = True
        t.join()
        reader, writer = t.get_result()

        data = Data(self._con_pool, self._dp, [reader, writer])
        return data


def connect(host: str='127.0.0.1', port: int=9980, password: 
    str=None) -> Client:
    '''
        Connect to the CyberDB server via TCP, this method will run 
        synchronously.
    '''
    if not password:
        raise RuntimeError('The password cannot be empty.')

    con_pool = ConPool(host, port)
    # Responsible for encrypting and decrypting objects.
    secret = Secret(key=password)
    # for digital signature
    signature = Signature(salt=password.encode())
    dp = datas.DataParsing(secret, signature)

    # Synchronously test whether the connection is successful.
    t = MyThread(target=asyncio.run, 
        args=(confirm_the_connection(con_pool, dp), ) )
    t.daemon = True
    t.start()
    t.join()
    result = t.get_result()
    if not result:
        raise RuntimeError('Incorrect address, port or password for database.')
    
    client = Client(con_pool, dp)
    return client


async def confirm_the_connection(con_pool, dp) -> dict:
    '''
        The connection is detected when the database connects for the first 
        time.
    '''
    reader, writer = await con_pool.get()

    client_obj = {
        'route': '/connect'
    }
    data = dp.obj_to_data(client_obj)
    writer.write(data)
    await writer.drain()

    data = await read(reader, writer)
    r = dp.data_to_obj(data)
    if r['code'] != 1:
        writer.close()
        raise RuntimeError(r['errors-code'])
    server_obj = r['content']
    
    con_pool.put(reader, writer)
    return server_obj


def check_the_connection(con_pool, dp):
    pass


