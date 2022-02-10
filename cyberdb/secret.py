import pickle

from AesEverywhere import aes256


class Secret:

    def __init__(self, key: str=''):
        # A 256 bit (32 byte) key
        if type(key) != type(''):
            raise RuntimeError('The key must be a string.')
        if len(key) > 32:
            raise RuntimeError('The key cannot contain more than 32 characters.')
        self.__key = key
        # Less than 32 characters complement 0.
        for i in range(32 - len(key)):
            self.__key += '0'
        # self.__aes = pyaes.AESModeOfOperationCTR(self.__key.encode())

    def encrypt(self, obj) -> bytes:
        '''
            Encrypt Python objects using AES.
                obj -- Most Python objects.
        '''
        obj_bin = pickle.dumps(obj)
        obj_bin_str = str(obj_bin)
        encrypted = aes256.encrypt(obj_bin_str, self.__key)
        return encrypted

    def decrypt(self, encrypted: str):
        '''
            AES decryption.
            Return: Python object
        '''
        decrypted = aes256.decrypt(encrypted, self.__key)
        obj_bin_str_part = decrypted.decode()[2:-1]
        loc = locals()
        exec("obj_bin = b'{}'".format(obj_bin_str_part))
        obj_bin = loc['obj_bin']
        obj = pickle.loads(obj_bin)
        return obj