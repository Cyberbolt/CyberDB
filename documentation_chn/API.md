# API

这部分文档涵盖了 CyberDB 的所有接口。对于 CyberDB 依赖于外部库的部分，我们在此处记录最重要的部分并提供指向规范文档的链接。


### class DBServer

该类可以创建 CyberDB 服务端实例，初始化会自动生成 cyberdb_file 、cyberdb_file/backup 目录，请勿删除。

**create_cyberdict(self, name: str)**
		
	创建 CyberDict 表
	参数:
		name -- 表名称
	返回类型: None

**create_cyberlist(self, name: str)**

	创建 CyberList 表
	参数:
		name -- 表名称
	返回类型: None

**create_object(self, type_name: str, obj_name: str, obj: object)**

	创建自定义对象
	参数:
		type_name -- 类型名
		obj_name -- 对象名
		obj -- 对象(object 及其子类的对象均可)
	返回类型: None

**start(self, host: str='127.0.0.1', password: str=None, port: int=9980)**

	(服务端)后台运行数据库，并自动开启 multiprocessing 守护进程。该方法将自动生成客户端配置文
	件 cyberdb_file/config.cdb ，客户端运行必须依赖该文件。
	参数:
		host -- 服务端运行地址，默认 127.0.0.1
		password -- 密码
		port -- 服务端监听端口，默认 9980
	返回类型: None

**stop(self)**

	停止运行数据库
	返回类型: None

**set_backup(self, period: int=900)**

	设置备份周期，调用本方法，数据库将定时备份至 cyberdb_file/backup/data.cdb
	参数:
		period -- 备份周期，默认 900 秒
	返回类型: None

**save_db(self, file_name: str='cyberdb_file/backup/data.cdb')**

	安全保存数据库文件，格式 cdb (仅支持内置数据结构 CyberDict 和 CyberList)。如需保存自定
	义数据结构，请参考本文档的教程。
	参数: 
		file_name -- 需保存数据库文件的路径，默认路径 cyberdb_file/backup/data.cdb
	返回类型: None

**load_db(self, file_name: str='cyberdb_file/backup/data.cdb')**

	加载 cdb 格式的数据库文件（一般为 set_backup 或 save_db 保存的文件）
	参数:
		file_name -- 文件路径，默认路径 cyberdb_file/backup/data.cdb
	返回类型: None

**get_data(self) -> dict**

	获取数据库内容，将返回数据库支持类型的所有数据(默认 CyberDict 和 CyberList)
	返回类型: dict
	
**show_tables_list(self)**

	打印数据库中所有表，格式 name -- 表名称 type:数据类型 
	返回类型: None

**delete_table(self, type_name: str, name: str)**

	删除数据库中的表
	参数:
		type_name --数据类型名
		name --表名
	返回类型: None

**delete_type(self, type_name: str)**

	删除数据库的数据类型，此操作会同时删除该数据类型下的所有表
	参数:
		type_name -- 数据类型名
	返回类型: None


### class DBClient

该类可以创建 CyberDB 客户端实例，若 cyberdb_file 、cyberdb_file/backup 目录不存在，实例初始化时将自动生成（可以直接将服务端生成的 cyberdb_file 目录拷贝至此）。

**load_config(self, config_file: str='cyberdb_file/config.cdb')**

	加载配置文件(该文件由服务端运行时生成)
	参数:
		config_file -- 配置文件的路径，默认路径 cyberdb_file/config.cdb
	返回类型: None

**connect(self, host: str='127.0.0.1', password: str=None, port: int=9980) -> DBCon:**

	(客户端)连接数据库，并获取本次连接的实例
	参数:
		host -- 主机地址，默认地址 127.0.0.1
		password -- 连接密码
		port -- 连接端口，默认端口 9980
	返回类型: DBCon -- 本次连接的数据库实例

**get_db(self)**

	获取本次连接的数据库实例（此操作不会再次连接数据库，需要用在 connect 方法之后）
	返回类型: DBCon -- 本次连接的数据库实例

**show_tables_list(self)**

	打印数据库中所有表，格式 name -- 表名称 type:数据类型 
	返回类型: None

**get_data(self)**

    获取数据库内容，将返回数据库支持类型的所有数据(默认 CyberDict 和 CyberList)
    返回类型: dict

**save_db(self, file_name: str='cyberdb_file/backup/data.cdb')**

    安全保存数据库文件到客户端本地，格式 cdb (仅支持内置数据结构 CyberDict 和 CyberList)。
	如需保存自定义数据结构，请参考本文档的教程。
    参数:
        file_name -- 需保存数据库文件的相对路径，默认路径 cyberdb_file/backup/data.cdb
    返回类型: None




