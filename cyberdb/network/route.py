import inspect
import datetime

from . import AioStream
from ..data import datas
from ..extensions import nonce, WrongPasswordCyberDBError


MAP = {}


def bind(path):
    def decorator(func):
        async def wrapper(self, *args, **kw):
            server_obj = await func(self, *args, **kw)
            server_obj['password'] = self._dp._secret.key
            
            await self._stream.write(server_obj)

        MAP[path] = wrapper
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

            # Check if the password is correct.
            if self._stream._dp._secret.key != client_obj['password']:
                self._stream._writer.close()
                raise WrongPasswordCyberDBError(
                    'The password entered by the client is incorrect.')

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
        return server_obj

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

        return server_obj

    @bind('/create_cyberlist')
    async def create_cyberlist(self):
        table_name = self._client_obj['table_name']
        content = self._client_obj['content']
        if self._db.get(table_name) == None:
            # New CyberList
            self._db[table_name] = content
            server_obj = {
                'code': 1
            }
        else:
            server_obj = {
                'code': 0
            }

        return server_obj

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

        return server_obj

    @bind('/exam_cyberlist')
    async def exam_cyberlist(self):
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

        return server_obj

    @bind('/print_tables')
    async def print_tables(self):
        inform = []
        for table_name in self._db:
            if type(self._db[table_name]) == dict:
                type_name = 'CyberDict'
            elif type(self._db[table_name]) == list:
                type_name = 'CyberList'
            inform.append((table_name, type_name))
            
        server_obj = {
            'code': 1,
            'content': inform
        }
        
        return server_obj

    @bind('/delete_table')
    async def delete_table(self):
        table_name = self._client_obj['table_name']
        try:
            del self._db[table_name]
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }
        
        return server_obj

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

        return server_obj

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

        return server_obj

    @bind('/cyberdict/len')
    async def dict_len(self):
        table_name = self._client_obj['table_name']
        try:
            r = len(self._db[table_name])
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

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

        return server_obj

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

        return server_obj

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

        return server_obj

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

        return server_obj

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

        return server_obj

    @bind('/cyberdict/setdefault')
    async def dict_setdefault(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        default = self._client_obj['default']
        try:
            r = self._db[table_name].setdefault(key, default)
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/update')
    async def dict_update(self):
        table_name = self._client_obj['table_name']
        dict2 = self._client_obj['dict2']
        try:
            self._db[table_name].update(dict2)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/keys')
    async def dict_keys(self):
        table_name = self._client_obj['table_name']
        try:
            r = list(self._db[table_name].keys())
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/values')
    async def dict_values(self):
        table_name = self._client_obj['table_name']
        try:
            r = list(self._db[table_name].values())
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/items')
    async def dict_items(self):
        table_name = self._client_obj['table_name']
        try:
            r = list(self._db[table_name].items())
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/pop')
    async def dict_pop(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        default = self._client_obj['default']

        try:
            r = self._db[table_name].pop(key, default)
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/popitem')
    async def dict_popitem(self):
        table_name = self._client_obj['table_name']
        try:
            r = self._db[table_name].popitem()
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberdict/clear')
    async def dict_clear(self):
        table_name = self._client_obj['table_name']
        try:
            self._db[table_name].clear()
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/repr')
    async def list_repr(self):
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

        return server_obj

    @bind('/cyberlist/str')
    async def list_str(self):
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

        return server_obj

    @bind('/cyberlist/len')
    async def list_len(self):
        table_name = self._client_obj['table_name']
        try:
            r = len(self._db[table_name])
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/getitem')
    async def list_getitem(self):
        table_name = self._client_obj['table_name']
        index = self._client_obj['index']
        try:
            r = self._db[table_name][index]
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/setitem')
    async def list_setitem(self):
        table_name = self._client_obj['table_name']
        index = self._client_obj['index']
        value = self._client_obj['value']
        try:
            self._db[table_name][index] = value
            server_obj = {
                'code': 1,
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/delitem')
    async def list_delitem(self):
        table_name = self._client_obj['table_name']
        index = self._client_obj['index']
        try:
            del self._db[table_name][index]
            server_obj = {
                'code': 1,
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/tolist')
    async def tolist(self):
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

        return server_obj

    @bind('/cyberlist/append')
    async def list_append(self):
        table_name = self._client_obj['table_name']
        value = self._client_obj['value']
        try:
            self._db[table_name].append(value)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/extend')
    async def list_extend(self):
        table_name = self._client_obj['table_name']
        obj = self._client_obj['obj']
        try:
            self._db[table_name].extend(obj)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/insert')
    async def list_insert(self):
        table_name = self._client_obj['table_name']
        index = self._client_obj['index']
        value = self._client_obj['value']
        try:
            self._db[table_name].insert(index, value)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/pop')
    async def list_pop(self):
        table_name = self._client_obj['table_name']
        index = self._client_obj['index']
        try:
            self._db[table_name].pop(index)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/remove')
    async def list_remove(self):
        table_name = self._client_obj['table_name']
        value = self._client_obj['value']
        try:
            self._db[table_name].remove(value)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/count')
    async def list_count(self):
        table_name = self._client_obj['table_name']
        value = self._client_obj['value']
        try:
            r = self._db[table_name].count(value)
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/index')
    async def list_index(self):
        table_name = self._client_obj['table_name']
        value = self._client_obj['value']
        try:
            r = self._db[table_name].index(value)
            server_obj = {
                'code': 1,
                'content': r
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/reverse')
    async def list_reverse(self):
        table_name = self._client_obj['table_name']
        try:
            self._db[table_name].reverse()
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/sort')
    async def list_sort(self):
        table_name = self._client_obj['table_name']
        key = self._client_obj['key']
        
        if key:
            # Dynamic get function.
            loc = locals()
            key = exec('{}'.format(key))
            key = loc['func']
            
        reverse = self._client_obj['reverse']
        try:
            self._db[table_name].sort(key=key, reverse=reverse)
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj

    @bind('/cyberlist/clear')
    async def list_clear(self):
        table_name = self._client_obj['table_name']
        try:
            self._db[table_name].clear()
            server_obj = {
                'code': 1
            }
        except Exception as e:
            server_obj = {
                'code': 0,
                'Exception': e
            }

        return server_obj
