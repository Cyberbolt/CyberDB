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