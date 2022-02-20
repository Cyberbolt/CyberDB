import time
import socket
import asyncio

from ..data import datas
from ..extensions import nonce


class Route:
    '''
        TCP event mapping.
    '''
    
    def __init__(self, dp: datas.DataParsing, sock: socket.socket, addr):
        self._dp = dp
        self._sock = sock
        self._addr = addr
        # Generates 32 random strings. Each socket connection corresponds to a key.
        self.token = nonce.generate(32)
        self.route = {
            '/connect': self.connect
        }

    async def recv(self):
        # Receive data in small chunks.
        buffer = []
        while True:
            d = self._sock.recv(4096)
            if d == b'exit':
                break
            elif d:
                buffer.append(d)
                data = self._dp.obj_to_data({
                    'code': 1
                })
                self._sock.send(data)
        data = b''.join(buffer) # Splice into complete data.
        return data

    async def find(self):
        # Send Token to client.
        # Receive data in small chunks.
        data = await self.recv()
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            print('Coding exception.')
            self._sock.close()
        client_obj = r['content']
        if client_obj['token'] != self.token:
            print('Coding exception.')
            self._sock.close()
        print(client_obj)
        self.route[client_obj['route']]() # Go to the corresponding routing function.

    def connect(self):
        server_obj = {
            'code': 1,
            'message': 'connection succeeded.'
        }
        data = self._dp.obj_to_data(server_obj)
        self._sock.send(data)
        self._sock.close()