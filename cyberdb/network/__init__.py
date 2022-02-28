import asyncio

from ..data import datas
from ..extensions import CyberDBError


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

        # Receive data in small chunks.
        buffer = []
        while True:
            try:
                block = await reader.readuntil(separator=b'exit')
                buffer.append(block)
                break
            except asyncio.LimitOverrunError:
                block = await reader.read()
        data = b''.join(buffer) # Splice into complete data.
        data = data.rstrip(b'exit')

        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            writer.close()
            raise CyberDBError(r['errors-code'])

        return r['content']

    async def write(self, obj: dict):
        reader, writer = self._reader, self._writer

        data = self._dp.obj_to_data(obj)
        writer.write(data)
        await writer.drain()
