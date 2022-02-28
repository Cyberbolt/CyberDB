import re
import asyncio
import threading

from obj_encrypt import Secret

from . import Con, Stream
from .route import Route
from ..data import datas
from ..extensions.signature import Signature


class Server:

    def __init__(self):
        self._data = {
            'config': {
                'host': None,
                'port': None,
                'password': None
            },
            'db': {}
        }
        self.ips = {'127.0.0.1'} # ip whitelist

    def start(self, host: str='127.0.0.1', port: int=9980, 
        password: str=None, max_con: int=500, timeout: int=0):
        '''
            The server starts from the background.

                max_con -- Maximum number of waiting connections.
        '''
        t = threading.Thread(target=self.run, 
            args=(host, port, password, max_con, timeout))
        t.daemon = True
        t.start()

    def run(self, host: str='127.0.0.1', port: int=9980, 
        password: str=None, max_con: int=500, timeout: int=0):
        '''
            The server runs in the foreground.

                max_con -- Maximum number of waiting connections.
                timeout -- Connection timeout time, the default is not timeout.
        '''
        if not password:
            raise RuntimeError('The password cannot be empty.')

        self._data['config']['host'] = host
        self._data['config']['port'] = port
        self._data['config']['password'] = password
        self._data['config']['max_con'] = max_con
        self._data['config']['timeout'] = timeout

        # Responsible for encrypting and decrypting objects.
        secret = Secret(key=password)
        # for digital signature
        signature = Signature(salt=password.encode())
        # Convert TCP data and encrypted objects to each other.
        self._dp = datas.DataParsing(secret, signature)

        asyncio.run(self._main())

    async def _main(self):
        server = await asyncio.start_server(
            self._listener, self._data['config']['host'], 
            self._data['config']['port'], 
            limit=2 ** 16, # 64 KiB
            # the maximum number of queued connections
            backlog=self._data['config']['max_con']
        )
        
        # async with server:
        #     await server.serve_forever()
        
        async def task():
            '''
                If the timeout is set, it will automatically disconnect.
            '''
            while True:
                async with server:
                    if self._data['config']['timeout'] == 0:
                        await server.serve_forever()
                    else:
                        try:
                            await asyncio.wait_for(server.serve_forever(), 
                                timeout=self._data['config']['timeout'])
                        except asyncio.TimeoutError:
                            pass
        
        async with server:
            await server.serve_forever()

    async def _listener(self, reader: asyncio.streams.StreamReader, 
        writer: asyncio.streams.StreamWriter):
        '''
            This method is entered as long as a TCP connection is established,
             even if no data is sent.
        '''

        addr = writer.get_extra_info('peername')
        
        # Check if the ip is in the whitelist.
        if self.ips:
            if addr[0] not in self.ips:
                print('The request for {}, the ip is not in the whitelist.'.format(addr[0]))
                writer.close()
                return

        # TCP route of this connection
        stream = Stream(reader, writer, self._dp)
        route = Route(self._data['db'], self._dp, stream)

        # If the timeout is set, it will automatically disconnect.
        if self._data['config']['timeout'] == 0:
            await route.find()
        else:
            try:
                await asyncio.wait_for(route.find(), 
                    timeout=self._data['config']['timeout'])
            except asyncio.TimeoutError:
                print('{} connection timed out.'.format(addr[0]))
                writer.close()

    def set_ip_whitelist(self, ips: list):
        for ip in ips:
            if not re.match(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})\
            (\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}', ip):
                raise RuntimeError('Please enter a valid ipv4 address.')
        self.ips = set(ips)

    def create_cyberdict(self, name: str):
        if type(name) != type(''):
            raise RuntimeError('Please use str for the table name.')
        if name in self._data['db']:
            raise RuntimeError('Duplicate table names already exist!')

        self._data['db'][name] = {}

