import time
import asyncio

from . import read, Con
from ..data import datas
from ..extensions import nonce


class Route:
    '''
        TCP event mapping.
    '''
    
    def __init__(self, db: dict, dp: datas.DataParsing, con: Con):
        self._db = db
        self._dp = dp
        self._con = con
        # TCP Jump path
        self._map = {
            '/connect': self.connect,
            '/exam': self.exam,
        }

    async def find(self):
        # Send Token to client.
        # Receive data in small chunks.
        reader, writer = self._con.reader, self._con.writer

        data = await read(reader, writer)
        r = self._dp.data_to_obj(data)
        
        if r['code'] != 1:
            print(r['errors-code'])
            writer.close()
            return
        
        client_obj = r['content']
        
        print(client_obj)
        # Go to the corresponding routing function.
        await self._map[client_obj['route']]()

    async def connect(self):
        reader, writer = self._con.reader, self._con.writer

        server_obj = {
            'code': 1,
            'message': 'connection succeeded.'
        }
        data = self._dp.obj_to_data(server_obj)
        writer.write(data)
        await writer.drain()

    async def exam(self):
        pass
