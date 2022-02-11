'''
    This data type is used for TCP transmission, the underlying layer uses AES encryption, and SHA-256 is used for digital signatures.
'''


def generate():
    '''
        Generate TCP transport data.
    '''
    data = {
        'content': None,
        'header': {
            'signature': None
        }
    }
    return data