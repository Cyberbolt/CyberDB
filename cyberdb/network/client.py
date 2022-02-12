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
        self._s.connect((host, port))
        secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        signature = Signature(salt=password.encode()) # for digital signature
        self._dp = datas.DataParsing(secret, signature)
        client_obj = datas.generate_client_obj()
        client_obj['route'] = 'connect'
        client_obj['message'] = 1
        data = self._dp.obj_to_data(client_obj)
        self._s.send(data)
        self._s.send(b'exit')
        # 接收数据:
        buffer = []
        while True:
            # 每次最多接收1k字节:
            d = self._s.recv(1024)
            if d:
                buffer.append(d)
            elif d == b'exit':
                break
            else:
                break
        data = b''.join(buffer)
        server_obj = self._data_to_obj(data)
        print(server_obj)
        self._s.close()
        # if r['code'] == 1:
        #     print(r)
        # else:
        #     print(r)

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