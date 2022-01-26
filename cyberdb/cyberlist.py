class CyberList(list):

    def show(self):
        '''
            获取 CyberList 的原始数据，返回的对象可以当作 Python list 使用\n
            返回类型: CyberList
        '''
        return self

    def loc(self, i: int):
        '''
            获取 CyberList 的第 i 个值(第 0 个值为起点)\n
            参数:\n
                i -- CyberList 的下标\n
            返回类型: CyberList[i] 对应的值类型
        '''
        return self[i]

    def loc_form(self, i: int, j: int):
        '''
            获取二维嵌套 CyberList 的第 i 行第 j 列对应的值(第 0 行第 0 列为起点)\n
            参数:\n
                i -- CyberList 的一维下标\n
                j -- CyberList 的二维下标\n
            返回类型: CyberList[i][j] 对应的值
        '''
        return self[i][j]

    def slice(self, i: int=None, j: int=None):
        '''
            此方法能替代 Python 切片的部分功能\n
            CyberList.slice(i, j) 等同于 list[i:j]，但是 i、j 不能为 *\n
            返回类型: list[i:j] 的返回值类型
        '''
        return self[i:j]

    def get(self, index: int):
        '''
            此方法可以被 CyberList.loc(index) 替代\n
            获取 CyberList 的第 index 个值(第 0 个值为起点)\n
            参数:\n
                index -- CyberList 的下标\n
            返回类型: CyberList[index] 对应的值类型
        '''
        return self[index]

    def update(self, index: int, value):
        '''
            修改 CyberList 的第 index 个值(第 0 个值为起点)为 value\n
            CyberList.update(index, value) 等同于 list[index] = value\n
            参数:\n
                index -- CyberList 的下标\n
                value -- 需更改的 CyberList 值\n
            返回类型: None
        '''
        self[index] = value

    def update_form(self, i: int, j: int, value):
        '''
            修改二维嵌套 CyberList 的第 i 行第 j 列的值为 value\n
            CyberList.update_form(i, j, value) 等同于 list[i][j] = value\n
            参数:\n
                i -- CyberList 的一维下标\n
                j -- CyberList 的二维下标\n
                value -- 需更改的 CyberList 值\n
            返回类型: None
        '''
        self[i][j] = value

    def get_length(self) -> int:
        '''
            此方法用于替代 len(list) 获取列表长度\n
            返回类型: int
        '''
        return len(self)

    def get_type(self) -> type:
        '''
            获取 CyberList 内置数据类型\n
            由于客户端获取的 CyberList 对象仅为网络对象，type(CyberList) 和此处 get_type() 并不\n
            相同。如无必要，无需使用此方法\n
            返回类型: type
        '''
        return type(CyberList())

    def box(self, command: str):
        '''
            魔术方法 list[x] 的替代方案\n
            使用该方法应该自行考虑 Python 脚本注入等安全问题\n
            参数:\n
                command -- 等同于 list[x] 中 x 表达式对应的字符串(command = str(x))\n
                即 CyberList.box(command) = list[x]，其中 command = str(x)\n
            返回类型: list[x] 的返回类型
        '''
        if type(command) != type(''):
            raise RuntimeError('command is not of type str.')
        loc = locals()
        exec('result = self' + command)
        result = loc['result']
        return result