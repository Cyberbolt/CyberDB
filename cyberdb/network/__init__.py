import socket

from ..extensions import nonce


class SComm:
    '''
        Server Communication
        TCP communication between the client and the server.
    '''

    def __init__(self):
        self.token = nonce.generate(32) # Generates 32 random strings.
    
    async def serve(self, sock: socket.socket, addr):
        buffer = []
        while True:
            d = await sock.recv(1024)
            print(d)
            if d:
                buffer.append(d)
            elif d == b'exit':
                break
            else:
                break