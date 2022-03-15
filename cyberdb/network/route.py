import datetime

from . import AioStream
from ..data import datas
from ..extensions import nonce


MAP = {}


def bind(path):
    def decorator(func):
        MAP[path] = func

        def wrapper(*args, **kw):
            return func(*args, **kw)
        return wrapper
    return decorator


class Route:
    '''
        TCP event mapping.
    '''

    def __init__(self, db: dict, dp: datas.DataParsing, stream: AioStream,
                 print_log: bool = False):
        self._db = db
        self._dp = dp
        self._stream = stream
        self._print_log = print_log

    async def find(self):
        '''
            Loop accepting client requests.
        '''
        addr = self._stream.get_addr()
        addr = '{}:{}'.format(addr[0], addr[1])

        while True:
            client_obj = await self._stream.read()
            self._client_obj = client_obj

            if self._print_log:
                print('{}  {}  {}'.format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    addr, client_obj['route']))

            # Jump to the specified function by routing.
            func = MAP[client_obj['route']]
            # Go to the corresponding routing function.
            await func(self)

    @bind('/connect')
    async def connect(self):
        server_obj = {
            'code': 1,
            'message': 'connection succeeded.'
        }

        await self._stream.write(server_obj)

    @bind('/create_cyberdict')
    async def create_cyberdict(self):
        table_name = self._client_obj['table_name']
        content = self._client_obj['content']
        if self._db.get(table_name) == None:
            # New CyberDict
            self._db[table_name] = content
            server_obj = {
                'code': 1
            }
        else:
            server_obj = {
                'code': 0
            }

        await self._stream.write(server_obj)

    @bind('/exam_cyberdict')
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

        await self._stream.write(server_obj)

    @bind('/cyberdict/repr')
    async def dict_repr(self):
        table_name = self._client_obj['table_name']
        try:
            r = repr(self._db[table_name])
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
        
    @bind('/cyberdict/str')
    async def dict_str(self):
        table_name = self._client_obj['table_name']
        try:
            r = str(self._db[table_name])
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

    @bind('/cyberdict/getitem')
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

    @bind('/cyberdict/setitem')
    async def dict_setitem(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        value = self._client_obj['value']
        try:
            self._db[table_name][key] = value
            server_obj = {
                'code': 1,
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        await self._stream.write(server_obj)

    @bind('/cyberdict/delitem')
    async def dict_delitem(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        try:
            del self._db[table_name][key]
            server_obj = {
                'code': 1,
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        await self._stream.write(server_obj)

    @bind('/cyberdict/todict')
    async def todict(self):
        table_name = self._client_obj['table_name']
        try:
            r = self._db[table_name]
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

    @bind('/cyberdict/get')
    async def dict_get(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        default = self._client_obj['default']
        try:
            r = self._db[table_name].get(key, default)
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
