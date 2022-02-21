import asyncio

from obj_encrypt import Secret

from ..data import datas
from ..extensions.signature import Signature


class DBClient:
    
    # def __init__(self):
    #     self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str='127.0.0.1', port: int=9980, password: 
        str=None):
        if not password:
            raise RuntimeError('The password cannot be empty.')
        secret = Secret(key=password) # Responsible for encrypting and decrypting objects.
        signature = Signature(salt=password.encode()) # for digital signature
        self._dp = datas.DataParsing(secret, signature)
        asyncio.run(self.confirm_the_connection(host, port))

    async def confirm_the_connection(self, host: str='127.0.0.1', 
        port: int=9980):
        self._reader, self._writer = await asyncio.open_connection(
        host, port)

        client_obj = {
            'route': '/connect'
        }
        data = self._dp.obj_to_data(client_obj)

        self._writer.write(data)
        data = await self._reader.read(1024)
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._writer.close()
            raise RuntimeError(r['errors-code'])
        client_obj = r['content']
        print(r)
        self._writer.close()

    def send(self, data):
        pass