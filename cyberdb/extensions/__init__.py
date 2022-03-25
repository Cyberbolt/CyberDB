from threading import Thread


class MyThread(Thread):
    def __init__(self, target, args):
        super(MyThread, self).__init__()
        self.target = target
        self.args = args

    def run(self):
        self.result = self.target(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class CyberDBError(RuntimeError):
    '''
        CyberDB basic error
    '''
    pass


class DisconCyberDBError(CyberDBError):
    '''
        TCP connection has been disconnected.
    '''
    pass


class WrongPasswordCyberDBError(CyberDBError):
    pass

class WrongFilenameCyberDBError(CyberDBError):
    pass

class BackupCyberDBError(CyberDBError):
    pass

class TypeCyberDBError(CyberDBError):
    pass

class WrongTableNameCyberDBError(CyberDBError):
    pass

class WrongInputCyberDBError(CyberDBError):
    pass
