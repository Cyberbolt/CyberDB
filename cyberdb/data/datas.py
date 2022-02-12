from obj_encrypt import Secret

from ..extensions.signature import Signature


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

    def __init__(self, secret: Secret, signature: Signature):
        self._secret = secret
        self._signature = signature

    def data_to_obj(self, data):
        '''
            Restore TCP encrypted data as an object.
        '''
        # Incorrect password will cause decryption to fail
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
        elif not data.get('content') or not data.get('header').get('signature'):
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
        obj = self._secret.decrypt(data['content'])
        return {
            'code': 1,
            'content': obj
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
        data['content'] = self._secret.encrypt(obj)
        data['header']['signature'] = self._signature.encrypt(data['content'])
        data = self._secret.encrypt(data)
        return data


