class CyberDict(dict):

    def show(self):
        '''
            获取 CyberDict 的原始数据，返回的对象可以当作 Python dict 使用\n
            返回类型: CyberDict
        '''
        return self

    def loc(self, key):
        '''
            此方法可以被 CyberDict.get(key) 替代\n
            获取 CyberDict key 键对应的值\n
            参数:\n
                key -- CyberDict 的键\n
            返回内容: 该键存储的数据
        '''
        return self.get(key)

    def put(self, key, value):
        '''
            此方法用于替代 dict[key] = value 新建键值对或赋值\n
            参数:\n
                key -- CyberDict 的新增或已有键\n
                value -- CyberDict key 对应的新值\n
            返回类型: None
        '''
        self[key] = value

    def delete(self, key):
        '''
            此方法用于替代 del dict[key] 删除键值对\n
            参数:\n
                key -- CyberDict 需删除的键\n
                    返回类型: None
        '''
        del self[key]

    def get_length(self) -> int:
        '''
            此方法用于替代 len(dict) 获取字典长度
            返回类型: int
        '''
        return len(self)

    def get_type(self) -> type:
        '''
            获取 CyberDict 内置数据类型\n
            由于客户端获取的 CyberDict 对象仅为网络对象，type(CyberDict) 和此处 get_type() 并不相同。如无必要，无需使用此方法\n
            返回类型: type
        '''
        return type(CyberDict())

    def box(self, command: str):
        '''
            魔术方法 dict[x] 的替代方案\n
            使用该方法应该自行考虑 Python 脚本注入等安全问题\n
            参数:\n
                command -- 等同于 dict[x] 中 x 表达式对应的字符串(command = str(x))\n
                即 CyberDict.box(command) = dict[x]，其中 command = str(x)\n
            返回类型: dict[x] 的返回类型
        '''
        if type(command) != type(''):
            raise RuntimeError('command is not of type str.')
        loc = locals()
        exec('result = self' + command)
        result = loc['result']
        return result