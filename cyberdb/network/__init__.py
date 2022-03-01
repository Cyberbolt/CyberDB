import asyncio

from ..data import datas
from ..extensions import CyberDBError, DisconCyberDBError, \
    WrongPasswordCyberDBError


class Con:
    '''
        Asyncio TCP connection data type
    '''

    def __init__(
        self, 
        reader: asyncio.streams.StreamReader=None, 
        writer: asyncio.streams.StreamWriter=None
    ):
        self.reader = reader
        self.writer = writer


async def read(reader: asyncio.streams.StreamReader, 
    writer: asyncio.streams.StreamWriter):
    # print(id(writer))
    # Receive data in small chunks.
    # buffer = []
    # while True:
    #     try:
    #         block = await reader.readuntil(separator=b'exit')
    #         buffer.append(block)
    #         break
    #     except asyncio.LimitOverrunError:
    #         block = await reader.read()
    # data = b''.join(buffer) # Splice into complete data.
    data = await reader.readuntil(separator=b'exit')
    data = data.rstrip(b'exit')
    return data


class Stream:
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

        # Receive data according to the separator b'\n' and concatenate it, 
        # and b'exit\n' is the terminator.
        buffer = []
        while True:
            try:
                block = await reader.readuntil(separator=b'\nnnn')
                block = block.rstrip(b'\nnnn')
                if block == b'exit':
                    break
                buffer.append(block)
            except asyncio.exceptions.IncompleteReadError:
                raise DisconCyberDBError('The TCP connection was disconnected by the other end.')
        data = b''.join(buffer) # Splice into complete data.

        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            writer.close()
            raise WrongPasswordCyberDBError(r['errors-code'])

        return r['content']

    async def write(self, obj: dict):
        writer = self._writer

        data = self._dp.obj_to_data(obj)
        
        # Divide and send every 2048 B.
        left = 0
        i = 2048
        while i < len(data):
            writer.write(data[left:i] + b'\nnnn')
            await writer.drain()
            left = i
            i += 2048
        
        writer.write(data[left:i] + b'\nnnn' + b'exit\nnnn')
        await writer.drain()

    def get_addr(self):
        return self._writer.get_extra_info('peername')