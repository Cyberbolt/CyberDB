import re
import time
import socket
import asyncio
import threading

from obj_encrypt import Secret

from ..data import datas
from ..extensions.signature import Signature
from .route import Route
from . import SComm


class DBServer:

    def __init__(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._data = {
            'config': {
                'host': None,
                'port': None,
                'password': None
            },
            'db': None
        }
        self.ips = {'127.0.0.1'} # ip whitelist

    def start(self, host: str='127.0.0.1', port: int=9980, password: str=None, 
    max_con: int=300):
        '''
            The server starts from the background.\n
                max_con -- Maximum number of waiting connections.
        '''
        t = threading.Thread(target=self.running, args=(host, port, password, max_con))
        t.daemon = True
        t.start()

    def running(self, host: str='127.0.0.1', port: int=9980, password: str=None, 
    max_con: int=300):
        '''
            The server runs in the foreground.\n
                max_con -- Maximum number of waiting connections.
        '''
        if not password:
            raise RuntimeError('The password cannot be empty.')
        self._s.bind((host, port))
        self._s.listen(max_con)
        self._data['config']['host'] = host
        self._data['config']['port'] = port
        self._data['config']['password'] = password
        secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        signature = Signature(salt=password.encode()) # for digital signature
        self._dp = datas.DataParsing(secret, signature) # Convert TCP data and encrypted objects to each other.
        asyncio.run(self._main())

    async def _main(self):
        await asyncio.gather(*[self._listener() for i in range(50)])

    async def _listener(self):
        while True:
            sock, addr = self._s.accept() # Accept a new connection.
            route = Route(self._dp, sock, addr) # TCP route of this connection
            # Check if the ip is in the whitelist.
            if self.ips:
                if addr[0] not in self.ips:
                    self._s.close()
                    continue
            await route.find()

    def set_ip_whitelist(self, ips: list):
        for ip in ips:
            if not re.match(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}', 
            ip):
                raise RuntimeError('Please enter a valid ipv4 address.')
        self.ips = set(ips)

