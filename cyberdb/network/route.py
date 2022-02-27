import time
import asyncio

from . import read
from ..data import datas
from ..extensions import nonce


class Route:
    '''
        TCP event mapping.
    '''
    
    def __init__(self, db: dict, dp: datas.DataParsing, reader: 
        asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter):
        self._db = db
        self._dp = dp
        self._reader = reader
        self._writer = writer
        # TCP Jump path
        self._map = {
            '/connect': self.connect,
            '/exam': self.exam,
        }

    async def find(self):
        # Send Token to client.
        # Receive data in small chunks.
        data = await read(self._reader, self._writer)
        r = self._dp.data_to_obj(data)
        
        if r['code'] != 1:
            print(r['errors-code'])
            self._writer.close()
            return
        
        client_obj = r['content']
        
        print(client_obj)
        # Go to the corresponding routing function.
        await self._map[client_obj['route']]()

    async def connect(self):
        server_obj = {
            'code': 1,
            'message': 'connection succeeded.'
        }
        data = self._dp.obj_to_data(server_obj)
        self._writer.write(data)
        await self._writer.drain()
        self._writer.close()

    async def exam(self):
        pass
