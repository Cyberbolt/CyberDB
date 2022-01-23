import os
import shutil
from multiprocessing import Process
from multiprocessing.managers import BaseManager

import joblib
from apscheduler.schedulers.blocking import BlockingScheduler

from cyberdb.cyberdict import CyberDict
from cyberdb.cyberlist import CyberList
from cyberdb.tool import generate


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
            创建 CyberDict
            name: 表名
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
            创建 CyberList
            name: 表名
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
            创建自定义对象
            type_name: 自定义类型名
            obj_name: 对象名
            obj: 对象
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
        
    def save_db(self, file_name: str='cyberdb_file/backup/data.cdb'):
        '''
            安全备份数据库，文件格式 cdb
        '''
        # 获取数据库表实例数据
        data = {}
        for type in self._db:
            data[type] = {}
            for name in self._db[type]:
                loc = locals()
                self.manager.connect()
                exec('table = self.manager.{}()'.format(name))
                table = loc['table']
                data[type][name] = table.show()
        # 保存到硬盘
        joblib.dump(data, 'cyberdb_file/backup/data_temp.cdb')
        shutil.move('cyberdb_file/backup/data_temp.cdb', file_name)

    def load_db(self, file_name: str='cyberdb_file/backup/data.cdb'):
        '''
            加载 cdb 格式的文件, 可通过返回值查看内容
        '''
        self._db = joblib.load(file_name)
        # 添加变量注册
        for type in self._db:
            for name in self._db[type]:
                register(name, self._db[type][name])
        return self._db

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
            生成表格数据
        '''
        tables = {}
        for type in self._db:
            tables[type] = {}
            for name in self._db[type]:
                tables[type][name] = None
        joblib.dump(tables, 'cyberdb_file/config.cdb')

    def start(self, host: str='127.0.0.1', password: str=None, port: int=9980):
        '''
            (服务端)后台运行服务器
            host: 运行地址(默认: 127.0.0.1)
            password: 密码
            port: 端口(默认: 9980)
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

    def stop(self):
        '''
            停止运行服务器
        '''
        self._process['server'].terminate()
        print('Server stopped.')

    def set_backup(self, period: int=900):
        '''
            设置备份周期
            period: 备份周期, 单位 秒。若 period 为 None，则不备份
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

    def show_tables(self):
        '''
            显示数据库表
        '''
        for type in self._db:
            for name in self._db[type]:
                print('name:' + name, ' type:' + type)


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
            配置文件路径
        '''
        self._db = joblib.load(config_file)

    def connect(self, host: str='127.0.0.1', password: str=None, port: int=9980, table_names: list=[]):
        '''
            (客户端)连接数据库
            host: 主机地址
            password: 密码
            port: 端口
            table_names: 需要连接的表名称的列表, 如 a、b、c 表输入 ['a', 'b', 'c']
        '''
        if not password:
            raise RuntimeError('Password not found, please set password!')
        if not self._db:
            raise RuntimeError('The configuration file is not loaded.')
        # 绑定数据库表实例
        for type in self._db:
            for name in self._db[type]:
                ClientManager.register(name)
        manager = ClientManager(address=(
            host, # 地址
            port), # 端口
            authkey=password.encode() # 密码
        )
        manager.connect()
        # 获取数据库表实例
        for type in self._db:
            for name in self._db[type]:
                loc = locals()
                exec('table = manager.{}()'.format(name))
                table = loc['table']
                self._db[type][name] = table
        return self._db
    
    def get_forms(self):
        '''
            获取该连接的所有表
        '''
        return self._db

    def show_tables(self):
        '''
            显示数据库表
        '''
        for type in self._db:
            for name in self._db[type]:
                print('name:' + name, ' type:' + type)
