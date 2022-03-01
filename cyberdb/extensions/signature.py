import hashlib


class Signature:
    '''
        This class is based on the SHA-256 algorithm for signing and checking data integrity.
    '''

    def __init__(self, salt: bytes, iterations: int=1):
        '''
            salt -- SHA-256 salt\n
            iterations -- The number of iterations of the SHA-256 algorithm.
        '''
        if type(salt) != type(b'1'):
            raise RuntimeError('Salt must be bytes.')
        self._salt = salt
        self._iterations = iterations

    def encrypt(self, content: bytes):
        '''
            SHA-256 encryption
        '''
        if type(content) != type(b'1'):
            raise RuntimeError('Content must be bytes.')
        dk = hashlib.pbkdf2_hmac('sha256', content, self._salt, self._iterations)
        return dk.hex()