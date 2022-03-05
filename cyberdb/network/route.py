import time
import asyncio

from . import Connection, Stream
from ..data import datas
from ..extensions import nonce


class Route:
    '''
        TCP event mapping.
    '''
    
    def __init__(self, db: dict, dp: datas.DataParsing, stream: Stream, 
        print_log: bool=False):
        self._db = db
        self._dp = dp
        self._stream = stream
        self._print_log = print_log
        # TCP Jump path
        self._map = {
            '/connect': self.connect,
            '/create_cyberdict': self.create_cyberdict,
            '/exam_cyberdict': self.exam_cyberdict,
            '/cyberdict': {
                '/getitem': self.dict_getitem
            }
        }

    async def find(self):
        '''
            Loop accepting client requests.
        '''
        addr = self._stream.get_addr()
        addr = '{}:{}'.format(addr[0], addr[1])

        while True:
            client_obj = await self._stream.read()
            if self._print_log:
                print('{}  {}'.format(addr, client_obj['route']))

            # Jump to the specified function by routing.
            routes = client_obj['route'].split('/')[1:]
            func = self._map # objective function
            for route in routes:
                func = func['/' + route]

            # Go to the corresponding routing function.
            self._client_obj = client_obj
            await func()

    async def connect(self):
        server_obj = {
            'code': 1,
            'message': 'connection succeeded.'
        }

        await self._stream.write(server_obj)

    async def create_cyberdict(self):
        table_name = self._client_obj['table_name']
        content = self._client_obj['content']
        if self._db.get(table_name) == None:
            # New CyberDict
            self._db[table_name] = content
            # Create table successfully.
            server_obj = {
                'code': 1
            }
        else:
            # Failed to create table.
            server_obj = {
                'code': 0
            }

        await self._stream.write(server_obj)
        
    async def exam_cyberdict(self):
        '''
            Check if the table in the database exists.
        '''
        
        table_name = self._client_obj['table_name']
        if self._db.get(table_name) != None:
            server_obj = {
                'code': 1
            }
        else:
            server_obj = {
                'code': 0
            }

        data = await self._stream.write(server_obj)

    async def dict_getitem(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        try:
            r = self._db[table_name][key]
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        await self._stream.write(server_obj)

