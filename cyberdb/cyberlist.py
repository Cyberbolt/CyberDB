class CyberList(list):

    def show(self):
        return self

    def loc(self, i: int):
        '''
            定位
            i: 列表下标
        '''
        return self[i]

    def loc_form(self, i: int, j: int):
        '''
            定位表格
            第 i 行, 第 j 列
        '''
        return self[i][j]

    def slice(self, i: int=None, j: int=None):
        '''
            切片
        '''
        return self[i:j]

    def get(self, index: int):
        return self[index]

    def update(self, index: int, value):
        '''
            修改 CyberList 的第 index 个值
        '''
        self[index] = value

    def update_form(self, i: int, j: int, value):
        '''
            修改 CyberList 的第 i 行、第 j 列的值
        '''
        self[i][j] = value

    def get_length(self):
        return len(self)

    def get_type(self):
        return type(CyberList())