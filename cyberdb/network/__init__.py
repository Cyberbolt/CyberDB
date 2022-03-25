import math
import socket
import asyncio

from ..data import datas
from ..extensions import CyberDBError, DisconCyberDBError, \
    WrongPasswordCyberDBError


SLICE_SIZE = 4096


class AioStream:
    '''
        Encapsulates TCP read and write and object encryption.
    '''

    def __init__(
        self,
        reader: asyncio.streams.StreamReader,
        writer: asyncio.streams.StreamWriter,
        dp: datas.DataParsing
    ):
        self._reader = reader
        self._writer = writer
        self._dp = dp

    async def read(self) -> dict:
        reader, writer = self._reader, self._writer

        # Gets the number of times TCP loops to receive data.
        number_of_times = await reader.read(SLICE_SIZE)

        # The client actively disconnects.
        if number_of_times == b'':
            raise DisconCyberDBError('The TCP connection was disconnected by the other end.')

        r = self._dp.data_to_obj(number_of_times)
        if r['code'] != 1:
            writer.close()
            raise WrongPasswordCyberDBError(r['errors-code'])
        number_of_times = r['content']

        # Informs the client that it is ready to receive data.
        ready = self._dp.obj_to_data('ready')
        writer.write(ready)
        await writer.drain()

        buffer = [await reader.read(SLICE_SIZE) for i in range(number_of_times)]
        data = b''.join(buffer) # Splice into complete data.

        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            writer.close()
            raise WrongPasswordCyberDBError(r['errors-code'])

        return r['content']

    async def write(self, obj: dict):
        reader, writer = self._reader, self._writer

        data = self._dp.obj_to_data(obj)

        # The number of times the other end TCP loops to 
        # receive data.
        number_of_times = self._dp.obj_to_data(
            math.ceil(len(data) / SLICE_SIZE)
        )
        writer.write(number_of_times)
        await writer.drain()

        # Get the client's readiness status.
        ready = await reader.read(SLICE_SIZE)
        r = self._dp.data_to_obj(ready)
        if r['code'] != 1:
            writer.close()
            raise WrongPasswordCyberDBError(r['errors-code'])
        ready = r['content']

        if ready != 'ready':
            raise RuntimeError('error')

        writer.write(data)
        await writer.drain()

    def get_addr(self):
        return self._writer.get_extra_info('peername')


class Stream:
    '''
        Synchronous TCP read and write
    '''

    def __init__(self, s: socket.socket, dp: datas.DataParsing):
        self._s = s
        self._dp = dp
        
    def read(self) -> dict:
        # Gets the number of times TCP loops to receive data.
        number_of_times = self._s.recv(SLICE_SIZE)

        # The client actively disconnects.
        if number_of_times == b'':
            raise DisconCyberDBError('The TCP connection was disconnected by the other end.')

        r = self._dp.data_to_obj(number_of_times)
        if r['code'] != 1:
            self._s.close()
            raise WrongPasswordCyberDBError(r['errors-code'])
        number_of_times = r['content']

        # Informs the client that it is ready to receive data.
        ready = self._dp.obj_to_data('ready')
        self._s.sendall(ready)

        buffer = [self._s.recv(SLICE_SIZE) for i in range(number_of_times)]
        data = b''.join(buffer) # Splice into complete data.

        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._s.close()
            raise WrongPasswordCyberDBError(r['errors-code'])

        return r['content']
    
    def write(self, obj: dict):
        obj['password'] = self._dp._secret.key
        
        data = self._dp.obj_to_data(obj)
        
        # The number of times the other end TCP loops to 
        # receive data.
        number_of_times = self._dp.obj_to_data(
            math.ceil(len(data) / SLICE_SIZE)
        )
        try:
            self._s.sendall(number_of_times)
        except BrokenPipeError as e:
            raise DisconCyberDBError('The TCP connection has been lost, please run proxy.connect() to regain the connection.')
        
        # Get the client's readiness status.
        ready = self._s.recv(SLICE_SIZE)
        try:
            r = self._dp.data_to_obj(ready)
        except EOFError as e:
            raise DisconCyberDBError('The TCP connection has been lost, please run proxy.connect() to regain the connection.')
        
        if r['code'] != 1:
            self._s.close()
            raise WrongPasswordCyberDBError(r['errors-code'])
        ready = r['content']

        if ready != 'ready':
            raise RuntimeError('error')
        
        self._s.sendall(data)
    