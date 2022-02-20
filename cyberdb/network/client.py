import time
import socket

from obj_encrypt import Secret

from ..data import datas
from ..extensions.signature import Signature


class DBClient:
    
    def __init__(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str='127.0.0.1', port: int=9980, password: str=None):
        if not password:
            raise RuntimeError('The password cannot be empty.')
        secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        signature = Signature(salt=password.encode()) # for digital signature
        self._dp = datas.DataParsing(secret, signature)
        self._s.connect((host, port))
        # Receive the Token of this session.
        data = self._s.recv(1024)
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._s.close()
            raise RuntimeError(r['errors-code'])
        server_obj = r['content']
        self.token = server_obj['token']
        client_obj = {
            'route': '/connect', # 0 means the last message.
            'token': self.token
        }
        data = self._dp.obj_to_data(client_obj)
        # while True:
        #     self._s.send(data)
        self._s.send(data)
        self._s.send(b'exit')
        data = self._s.recv(1024)
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._s.close()
            raise RuntimeError(r['errors-code'])
        client_obj = r['content']
        print(r)
        self._s.close()

    def send(self, data):
        pass