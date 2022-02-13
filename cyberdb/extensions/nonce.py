import random


seed = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def generate(num: int):
    '''
        Generate num random strings.
    '''
    text = ''
    for i in range(num):
        text += random.choice(seed)
    return text
