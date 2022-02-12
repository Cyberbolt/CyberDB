import time
import socket
import asyncio

from ..data import datas


class Route:
    '''
        TCP event mapping.
    '''
    
    def __init__(self, dp: datas.DataParsing):
        self._dp = dp
        self.route = {
            'connect': self.connect
        }

    async def connect(self, sock: socket.socket, addr, client_obj):
        if client_obj['message'] == 1:
            server_obj = datas.generate_client_obj()
            server_obj['code'] = 1
            server_obj['message'] = 1
            data = self._dp.obj_to_data(server_obj)
            print(data)
            sock.send(data)
            sock.send(b'exit')
            sock.close()