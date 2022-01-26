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
    else:
        raise RuntimeError('The data type is not CyberDict or CyberList.')


class DBCon(object):
    '''
        数据库连接对象
        动态构建对象
    '''
    def __getitem__(self, attr):
        loc = locals()
        exec('result = self.{}'.format(attr))
        result = loc['result']
        return result