import socket
import pickle
import asyncio
import threading

from obj_encrypt import Secret

from .signature import Signature


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
        self._secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        self._signature = Signature(salt=password.encode()) # for digital signature
        self.__listener()

    def __listener(self):
        while True:
            sock, addr = self._s.accept() # Accept a new connection.
            data = sock.recv(1024)
            r = self.__data_to_obj(data)
            if r['code'] == 2:
                print(r['errors-code'])
            print(r)

    def __data_to_obj(self, data):
        '''
            Restores objects encrypted by TCP transmission.
        '''
        # Incorrect password will cause decryption to fail
        try:
            data = self._secret.decrypt(data)
        except UnicodeDecodeError:
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