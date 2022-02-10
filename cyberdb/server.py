import socket
import pickle
import asyncio
from multiprocessing import Process


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
        self._s.bind((host, port))
        self._s.listen(max_con)
        self._data['config']['host'] = host
        self._data['config']['port'] = port
        self._data['config']['password'] = password
        while True:
            sock, addr = self._s.accept() # Accept a new connection.
            data = sock.recv(1024)
            print(pickle.loads(data))

    def listener_start(self):
        '''
            Start the listener process.
        '''
        p = Process(target=self.__listener)
        p.daemon = True
        p.start()
        self.server_process = p

    def __listener(self):
        while True:
            sock, addr = self._s.accept() # Accept a new connection.
            data = sock.recv(1024)
            print(data.decode())

    async def daemon(self):
        while True:
            await asyncio.sleep(0.5)
            if not self.server_process.is_alive():
                self.server_process.terminate()
                self.listener_start()