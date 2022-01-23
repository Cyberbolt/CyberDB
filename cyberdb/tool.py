from cyberdb import CyberDict, CyberList


def generate(data):
    '''
        通过生成器访问数据库
    '''
    if data.get_type() == type(CyberDict()):
        for key in data.keys():
            yield key
    elif data.get_type() == type(CyberList()):
        for i in range(data.get_length()):
            yield data.loc(i)