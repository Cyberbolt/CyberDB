import time
import socket
import pickle
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

    def start(self, host: str='127.0.0.1', port: int=9980, password: str=None, 
    max_con: int=300):
        '''
            The server starts from the background.\n
                max_con -- Maximum number of waiting connections.
        '''
        if not password:
            raise RuntimeError('The password cannot be empty.')
        self._s.bind((host, port))
        self._s.listen(max_con)
        self._data['config']['host'] = host
        self._data['config']['port'] = port
        self._data['config']['password'] = password
        self._secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        # Run with a daemon thread.
        t = threading.Thread(target=self.__listener)
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
        asyncio.run(self._listener())

    async def _listener(self):
        while True:
            sock, addr = self._s.accept() # Accept a new connection.
            route = Route(self._dp, sock, addr) # TCP route of this connection
            print(addr)
            # route.find()
            task1 = asyncio.create_task(route.find())
            asyncio.to_thread()
            await asyncio.sleep(10)
            # await task1
            print(999)

    def _data_to_obj(self, data):
        '''
            Restore TCP encrypted data as an object.
        '''
        # Incorrect password will cause decryption to fail
        try:
            data = self._secret.decrypt(data)
        except UnicodeDecodeError:
            return {
                'code': 2,
                'errors-code': 'Incorrect password or data tampering.'
            }
        # Check if the dictionary is intact.
        if type(data) != type(dict()):
            return {
                'code': 2,
                'errors-code': 'Incorrect password or data tampering.'
            }
        elif not data.get('content') or not data.get('header').get('signature'):
            return {
                'code': 2,
                'errors-code': 'Incorrect password or data tampering.'
            }
        # Verify signature
        if self._signature.encrypt(data['content']) != data['header']['signature']:
            return {
                'code': 2,
                'errors-code': 'Incorrect password or data tampering.'
            }
        obj = self._secret.decrypt(data['content'])
        return {
            'code': 1,
            'content': obj
        }

    def _obj_to_data(self, obj):
        '''
            Convert object to TCP transmission data.
        '''
        data = {
            'content': None,
            'header': {
                'signature': None
            }
        }
        data['content'] = self._secret.encrypt(obj)
        data['header']['signature'] = self._signature.encrypt(data['content'])
        data = self._secret.encrypt(data)
        return data

