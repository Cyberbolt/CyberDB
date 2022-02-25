import asyncio

from . import datas


class CyberDict:

    def __init__(self, name: str, dp: datas.DataParsing, reader: 
        asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter):
        self._name = name
        self._dp = dp
        self._reader = reader
        self._writer = writer

    async def read(self):
        # Receive data in small chunks.
        buffer = []
        while True:
            try:
                block = await self._reader.readuntil(separator=b'exit')
                buffer.append(block)
                break
            except asyncio.LimitOverrunError:
                block = await self._reader.read()
        data = b''.join(buffer) # Splice into complete data.
        return data

    async def __getitem__(self, key):
        client_obj = {
            'route': '/{}/get_key',
            'key': key
        }
        data = self._dp.obj_to_data(client_obj)
        self._writer.write(data)
        await self._writer.drain()

        data = await self.read()
        r = self._dp.data_to_obj(data)
        if r['code'] != 1:
            self._writer.close()
            raise RuntimeError(r['errors-code'])
        server_obj = r['content']
        return server_obj
