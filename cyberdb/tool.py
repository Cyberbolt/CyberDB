from cyberdb import CyberDict, CyberList


def generate(data):
    '''
        generate 是 CyberDB 提供的生成器，用于迭代 CyberDict 或 CyberList。generate 每次迭代通过 TCP 获取数据，能显著提升内存利用率。对 CyberDict，generate 会获取所有 key，每次迭代时获取 value；对 CyberList，generate 只在每次迭代时获取内容。
        \n
        若 data 为 CyberDict 对象，打印所有 value\n
        for key in generate(data):\n
            print(data[key])\n
        \n
        若 data 为 CyberList 对象，打印所有值\n
        for v in generate(data):\n
            print(v)
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