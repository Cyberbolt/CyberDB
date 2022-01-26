import os
import shutil
from multiprocessing import Process
from multiprocessing.managers import BaseManager

import joblib
from apscheduler.schedulers.blocking import BlockingScheduler

from cyberdb.cyberdict import CyberDict
from cyberdb.cyberlist import CyberList
from cyberdb.tool import generate, DBCon


class ServerManager(BaseManager):
    pass

class ClientManager(BaseManager):
    pass


def register(name, instance):
    '''
        注册 Manager 的实例
        name: 名称
        v: 待注册的实例
    '''
    ServerManager.register(name, callable=lambda: instance)


TYPES = {'CyberDict', 'CyberList'} # TYPSE 必须满足 show 方法


class DBServer:

    def __init__(self):
        self._db = {
            'CyberDict': {},
            'CyberList': {}
        }
        self._process = {}
        #初始化时检测目录是否存在
        if not os.path.isdir('cyberdb_file'):
            os.makedirs('cyberdb_file')
        if not os.path.isdir('cyberdb_file/backup'):
            os.makedirs('cyberdb_file/backup')

    def create_cyberdict(self, name: str):
        '''
            创建 CyberDict 表\n
            参数:\n
                name -- 表名称\n
            返回类型: None
        '''
        if type(name) != type(''):
            raise RuntimeError('Please use str for the table name.')
        if name in self._db['CyberDict'] or name in self._db['CyberList']:
            raise RuntimeError('Duplicate table names already exist!')
        self._db['CyberDict'][name] = CyberDict()
        # 添加变量注册
        register(name, self._db['CyberDict'][name])

    def create_cyberlist(self, name: str):
        '''
            创建 CyberList 表\n
            参数:\n
                name -- 表名称\n
            返回类型: None
        '''
        if type(name) != type(''):
            raise RuntimeError('Please use str for the table name.')
        if name in self._db['CyberDict'] or name in self._db['CyberList']:
            raise RuntimeError('Duplicate table names already exist!')
        self._db['CyberList'][name] = CyberList()
        # 添加变量注册
        register(name, self._db['CyberList'][name])

    def create_object(self, type_name: str, obj_name: str, obj: object):
        '''
            创建自定义对象\n
            参数:\n
                type_name -- 类型名\n
                obj_name -- 对象名\n
                obj -- 对象(object 及其子类的对象均可)\n
            返回类型: None
        '''
        if type(type_name) != type(''):
            raise RuntimeError('Please use str for the type name.')
        if type(obj_name) != type(''):
            raise RuntimeError('Please use str for the table name.')
        if not self._db.get(type_name):
            self._db[type_name] = {}
        self._db[type_name][obj_name] = obj
        # 添加变量注册
        register(obj_name, self._db[type_name][obj_name])

    def start(self, host: str='127.0.0.1', password: str=None, port: int=9980):
        '''
            (服务端)后台运行数据库，并自动开启 multiprocessing 守护进程。该方法将自动生成客户端配置文件 cyberdb_file/config.cdb ，客户端运行必须依赖该文件。\n
            参数:\n
                host -- 服务端运行地址，默认 127.0.0.1\n
                password -- 密码\n
                port -- 服务端监听端口，默认 9980\n
            返回类型: None
        '''
        self.__server_init(password) # 服务器初始化
        self.manager = ServerManager(address=(
            host, # 地址
            port), # 端口
            authkey=password.encode() # 密码
        ) # 保存本次连接的实例
        print('CyberDB is starting...')
        self.__generate_tables() # 生成本次服务的配置文件
        p = Process(target=self.manager.get_server().serve_forever)
        p.daemon = True
        p.start()
        self._process['server'] = p
        self.manager.connect()

    def stop(self):
        '''
            停止运行数据库
        '''
        self._process['server'].terminate()
        print('Server stopped.')

    def set_backup(self, period: int=900):
        '''
            设置备份周期，调用本方法，数据库将定时备份至 cyberdb_file/backup/data.cdb\n
            参数:\n
                period -- 备份周期，默认 900 秒\n
            返回类型: None
        '''
        if self._process.get('backup'):
            self._process['backup'].terminate()
        if not period:
            print('Backup closed.')
            return
        sched = BlockingScheduler(timezone="Asia/Shanghai") # 初始化时间, 此处时区不影响数据库运行
        sched.add_job(self.save_db, 'interval', seconds=period) # 单位 秒
        p = Process(target=sched.start)
        p.daemon = True
        p.start()
        self._process['backup'] = p
        print('The backup cycle: {}s'.format(period))

    def save_db(self, file_name: str='cyberdb_file/backup/data.cdb'):
        '''
            安全保存数据库文件，格式 cdb (仅支持内置数据结构 CyberDict 和 CyberList)。如需保存自定义数据结构，请参考本文档的教程。\n
            参数: \n
                file_name -- 需保存数据库文件的相对路径，默认路径 cyberdb_file/backup/data.cdb\n
            返回类型: None
        '''
        # 获取数据库表实例数据
        data = self.get_data()
        # 保存到硬盘
        joblib.dump(data, 'cyberdb_file/backup/data_temp.cdb')
        shutil.move('cyberdb_file/backup/data_temp.cdb', file_name)

    def load_db(self, file_name: str='cyberdb_file/backup/data.cdb'):
        '''
            加载 cdb 格式的数据库文件（一般为 set_backup 或 save_db 保存的文件）\n
            参数:\n
                file_name -- 文件路径，默认路径 cyberdb_file/backup/data.cdb\n
            返回类型: None
        '''
        file_suffix = file_name.rsplit('.')[1]
        if file_suffix != 'cdb':
            raise RuntimeError('The file suffix must be cdb.')
        self._db = joblib.load(file_name)
        # 添加变量注册
        for type in self._db:
            for name in self._db[type]:
                register(name, self._db[type][name])
        print('File {} loaded successfully.'.format(file_name))

    def get_data(self) -> dict:
        '''
            获取数据库内容，将返回数据库支持类型的所有数据(默认 CyberDict 和 CyberList)\n
            返回类型: dict
        '''
        # 获取数据库表实例数据
        data = {}
        for type in self._db:
            if type in TYPES:
                data[type] = {}
                for name in self._db[type]:
                    loc = locals()
                    exec('table = self.manager.{}()'.format(name))
                    table = loc['table']
                    data[type][name] = table.show()
        return data

    def __server_init(self, password: str=None):
        '''
            初始化服务器配置
        '''
        # 检测数据库表是否存在
        tables_exist = False
        for type in self._db:
            if self._db[type]:
                tables_exist = True
                break
        if not tables_exist:
            raise RuntimeError('No tables have created.')
        if not password:
            raise RuntimeError('Password not found, please set password!')

    def __generate_tables(self):
        '''
            生成表格数据(配置文件信息)
        '''
        tables = {}
        for type in self._db:
            tables[type] = {}
            for name in self._db[type]:
                tables[type][name] = None
        joblib.dump(tables, 'cyberdb_file/config_temp.cdb')
        shutil.move('cyberdb_file/config_temp.cdb', 'cyberdb_file/config.cdb')

    def show_tables_list(self):
        '''
            打印数据库中所有表，格式 name:表名称 type:数据类型 
        '''
        for type in self._db:
            for name in self._db[type]:
                print('name:' + name, ' type:' + type)

    def delete_table(self, type_name: str, name: str):
        '''
            删除数据库中的表\n
            参数:\n
                type_name:数据类型名\n
                name:表名\n
            返回类型: None
        '''
        if type(type_name) != type(''):
            raise RuntimeError('Please use str for the type name.')
        if type(name) != type(''):
            raise RuntimeError('Please use str for the table name.')
        if type_name not in self._db:
            raise RuntimeError('The type_name you entered is incorrect.')
        if name not in self._db[type_name]:
            raise RuntimeError('The obj_name you entered is incorrect.')
        del self._db[type_name][name]
        # 保存到硬盘
        joblib.dump(self._db, 'cyberdb_file/backup/data_temp.cdb')
        shutil.move('cyberdb_file/backup/data_temp.cdb', 'cyberdb_file/backup/data.cdb')

    def delete_type(self, type_name: str):
        '''
            删除数据库的数据类型，此操作会同时删除该数据类型下的所有表\n
            参数:\n
                type_name:数据类型名\n
            返回类型: None
        '''
        if type(type_name) != type(''):
            raise RuntimeError('Please use str for the type name.')
        del self._db[type_name]
        # 保存到硬盘
        joblib.dump(self._db, 'cyberdb_file/backup/data_temp.cdb')
        shutil.move('cyberdb_file/backup/data_temp.cdb', 'cyberdb_file/backup/data.cdb')


class DBClient:

    def __init__(self):
        self._db = None
        #初始化时检测目录是否存在
        if not os.path.isdir('cyberdb_file'):
            os.makedirs('cyberdb_file')
        if not os.path.isdir('cyberdb_file/backup'):
            os.makedirs('cyberdb_file/backup')

    def load_config(self, config_file: str='cyberdb_file/config.cdb'):
        '''
            加载配置文件(该文件由服务端运行时生成)\n
            参数:\n
                config_file -- 配置文件的路径，默认路径 cyberdb_file/config.cdb\n
            返回类型: None
        '''
        file_suffix = config_file.rsplit('.')[1]
        if file_suffix != 'cdb':
            raise RuntimeError('The file suffix must be cdb.')
        self._db = joblib.load(config_file)

    def connect(self, host: str='127.0.0.1', password: str=None, port: int=9980) -> DBCon:
        '''
            (客户端)连接数据库，并获取本次连接的实例\n
            参数:\n
                host -- 主机地址，默认地址 127.0.0.1\n
                password -- 连接密码\n
                port -- 连接端口，默认端口 9980\n
            返回类型: DBCon -- 本次连接的数据库实例
        '''
        if not password:
            raise RuntimeError('Password not found, please set password!')
        if not self._db:
            raise RuntimeError('The configuration file is not loaded.')
        # 绑定数据库表实例
        for type in self._db:
            for name in self._db[type]:
                ClientManager.register(name)
        self.manager = ClientManager(address=(
            host, # 地址
            port), # 端口
            authkey=password.encode() # 密码
        )
        self.manager.connect()
        # 获取数据库表实例
        for type in self._db:
            for name in self._db[type]:
                loc = locals()
                exec('table = self.manager.{}()'.format(name))
                table = loc['table']
                self._db[type][name] = table
        # 返回本次连接的实例
        return self.get_db()
    
    def get_db(self) -> DBCon:
        '''
            获取本次连接的数据库实例（此操作不会再次连接数据库，需要用在 connect 方法之后）\n
            返回类型: DBCon -- 本次连接的数据库实例
        '''
        # 构建本次连接的实例
        db_con = DBCon()
        for type in self._db:
            loc = locals()
            exec('db_con.{} = DBCon()'.format(type))
            for name in self._db[type]:
                v = self._db[type][name]
                exec('db_con.{}.{} = v'.format(type, name))
        self._db_con = db_con
        return self._db_con

    def show_tables_list(self):
        '''
            打印数据库中所有表，格式 name:表名称 type:数据类型 
        '''
        for type in self._db:
            for name in self._db[type]:
                print('name:' + name, ' type:' + type)

    def get_data(self) -> dict:
        '''
            获取数据库内容，将返回数据库支持类型的所有数据(默认 CyberDict 和 CyberList)\n
            返回类型: dict
        '''
        # 获取数据库表实例数据
        data = {}
        for type in self._db:
            if type in TYPES:
                data[type] = {}
                for name in self._db[type]:
                    loc = locals()
                    exec('table = self.manager.{}()'.format(name))
                    table = loc['table']
                    data[type][name] = table.show()
        return data

    def save_db(self, file_name: str='cyberdb_file/backup/data.cdb'):
        '''
            安全保存数据库文件到客户端本地，格式 cdb (仅支持内置数据结构 CyberDict 和 CyberList)。如需保存自定义数据结构，请参考本文档的教程。\n
            参数: \n
                file_name -- 需保存数据库文件的相对路径，默认路径 cyberdb_file/backup/data.cdb\n
            返回类型: None
        '''
        # 获取数据库表实例数据
        data = self.get_data()
        # 保存到硬盘
        joblib.dump(data, 'cyberdb_file/backup/data_temp.cdb')
        shutil.move('cyberdb_file/backup/data_temp.cdb', file_name)