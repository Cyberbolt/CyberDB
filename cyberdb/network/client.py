import time
import asyncio

from obj_encrypt import Secret

from . import read
from ..data import datas
from ..extensions.signature import Signature


class ConPool:
    '''
        Maintain connection pool.
    '''
    
    def __init__(self, host: str, port: str):
        self._host = host
        self._port = port
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


class DBClient:

    def connect(self, host: str='127.0.0.1', port: int=9980, password: 
        str=None):
        if not password:
            raise RuntimeError('The password cannot be empty.')
        
        # Responsible for encrypting and decrypting objects.
        secret = Secret(key=password)
        # for digital signature
        signature = Signature(salt=password.encode())
        self._dp = datas.DataParsing(secret, signature)
        self._con_pool = ConPool(host, port)

        asyncio.run(self.confirm_the_connection(host, port))

    async def confirm_the_connection(self, host: str='127.0.0.1', 
        port: int=9980):
        reader, writer = await self._con_pool.get()

        client_obj = {
            'route': '/connect'
        }
        data = self._dp.obj_to_data(client_obj)
        writer.write(data)
        await writer.drain()

        data = await read(reader, writer)
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            writer.close()
            raise RuntimeError(r['errors-code'])
        server_obj = r['content']
        print(r)
        
        self._con_pool.put(reader, writer)

    def send(self, data):
        pass