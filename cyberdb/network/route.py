import time
import asyncio

from ..data import datas
from ..extensions import nonce


class Route:
    '''
        TCP event mapping.
    '''
    
    def __init__(self, dp: datas.DataParsing, addr, reader: 
        asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter):
        self._dp = dp
        self._addr = addr
        self._reader = reader
        self._writer = writer
        # Generates 32 random strings. Each socket connection corresponds to a key.
        self.route = {
            '/connect': self.connect
        }

    async def recv(self):
        # Receive data in small chunks.
        buffer = []
        while True:
            d = self._writer.recv(4096)
            if d == b'exit':
                break
            elif d:
                buffer.append(d)
                data = self._dp.obj_to_data({
                    'code': 1
                })
                self._writer.send(data)
        data = b''.join(buffer) # Splice into complete data.
        return data

    async def find(self):
        # Send Token to client.
        # Receive data in small chunks.\
        data = await self._reader.read()
        r = self._dp.data_to_obj(data)

        if r['code'] != 1:
            print('Coding exception.')
            self._writer.close()
        
        client_obj = r['content']
        
        print(client_obj)
        await self.route[client_obj['route']]() # Go to the corresponding routing function.

    async def connect(self):
        server_obj = {
            'code': 1,
            'message': 'connection succeeded.'
        }
        data = self._dp.obj_to_data(server_obj)
        self._writer.write(data)
        await self._writer.drain()
        self._writer.close()