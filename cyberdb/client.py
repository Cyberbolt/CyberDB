import socket

from obj_encrypt import Secret

from cyberdb import cyberdata
from .signature import Signature


class DBClient:
    
    def __init__(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str='127.0.0.1', port: int=9980, password: str=None):
        if not password:
            raise RuntimeError('The password cannot be empty.')
        self._s.connect((host, port))
        self._secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        self._signature = Signature(salt=password.encode()) # for digital signature
        data = self.__obj_to_data(1)
        self._s.send(data)

    def __obj_to_data(self, obj):
        '''
            Convert object to TCP transmission data.
        '''
        data = cyberdata.generate()
        data['content'] = self._secret.encrypt(obj)
        data['header']['signature'] = self._signature.encrypt(data['content'])
        data = self._secret.encrypt(data)
        return data