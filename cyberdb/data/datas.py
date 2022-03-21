'''
    Data used for TCP transmission
'''


import base64
import pickle

from obj_encrypt import Secret

from ..extensions.signature import Signature
from ..extensions import CyberDBError


def generate_client_obj():
    return {
        'route': None,
        'message': None
    }


def generate_server_obj():
    return {
        'code': None,
        'message': None
    }


errors_code = {
    2: 'Incorrect password or data tampering.'
}


class DataParsing:
    '''
        Convert TCP data and encrypted objects to each other.
    '''

    def __init__(self, secret: Secret, signature: Signature, encrypt: bool=False):
        self._secret = secret
        self._signature = signature
        self._encrypt = encrypt

    def data_to_obj(self, data):
        '''
            Restore TCP encrypted data as an object.
        '''
        # Determine whether to decrypt and verify the signature.
        if self._encrypt:
            try:
                data = base64.b64decode(data)
            except:
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }

            try:
                data = self._secret.decrypt(data)
            except UnicodeDecodeError:
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }

            # Check if the dictionary is intact.
            if type(data) != type(dict()):
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }
            elif type(data.get('content')) != type(b'') or not data.get('header') or not \
                data.get('header').get('signature'):
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }

            # Verify signature
            if self._signature.encrypt(data['content']) != data['header']['signature']:
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }
                
            obj = pickle.loads(data['content'])
            return {
                'code': 1,
                'content': obj
            }
            
        else:
            try:
                data = base64.b64decode(data)
            except:
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }
            
            try:
                obj = pickle.loads(data)
                return {
                    'code': 1,
                    'content': obj
                }
            except Exception as e:
                return {
                    'code': 2,
                    'errors-code': errors_code[2]
                }

    def obj_to_data(self, obj):
        '''
            Convert object to TCP transmission data.
        '''
        data = {
            'content': None,
            'header': {
                'signature': None
            }
        }
        
        # Determine whether to encrypt and sign.
        if self._encrypt:
            try:
                data['content'] = pickle.dumps(obj)
            except pickle.PickleError as e:
                raise CyberDBError('CyberDB does not support this data type.')
            
            data['header']['signature'] = self._signature.encrypt(data['content'])
            data = self._secret.encrypt(data)
            data = base64.b64encode(data)
            
        else:
            data = base64.b64encode(pickle.dumps(obj))

        return data


