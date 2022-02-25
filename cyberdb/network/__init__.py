import asyncio


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