import asyncio


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
    return data