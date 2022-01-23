class CyberDict(dict):

    def show(self):
        return self

    def loc(self, key):
        return self.get(key)

    def put(self, key, value):
        self[key] = value

    def delete(self, key):
        del self[key]

    def get_length(self):
        return len(self)

    def get_type(self):
        return type(CyberDict())

    def box(self, command: str):
        '''
            使用 [] 访问字典
            command: 访问命令，需要输入 str 类型
        '''
        if type(command) != type(''):
            raise RuntimeError('command is not of type str.')
        loc = locals()
        exec('result = self' + command)
        result = loc['result']
        return result