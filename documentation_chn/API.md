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


### 数据库连接对象 DBCon

调用 DBClient 的 connect 方法，将返回本次连接的实例。客户端通过它可以获取每张表的实例。获取方法

	DBCon对象.数据类型.表名
	或
	DBCon对象[数据类型][表名] # 此处数据类型和表名均为 str 
	
	例如，已创建 CyberDict 类型的 name1 表，使用以下任意方法获取该表
	DBCon对象.CyberDict.name1
	或
	DBCon对象['CyberDict']['name1']
	
此处获取的表实例为网络对象，调用该对象的任何方法，都将通过 TCP 与服务端交互。CyberList 和 CyberDict 支持 Python 数据结构 Dictionaries 和 Lists 的所有公有方法(如 dict.get(key), dict.items(), list.append(v), list.pop() 等)。不支持迭代、不支持私有方法(Python 魔术方法)，不能使用 dict[key] 和 list[index] 访问数据(CyberDB 给出了相应办法替代)。

生产环境中，建议每次请求执行前重新调用 connect 方法，获取 DBCon 的实例，以确保连接的可靠性。


### class CyberDict

DBCon对象.CyberDict.表名 获取的实例是基于 CyberDict 的网络对象。CyberDict 兼容 [Python dict](https://docs.python.org/3.10/library/stdtypes.html#dict) 的所有公有方法，此处只列举不同于 dict 的部分。

**show(self):**

	获取 CyberDict 的原始数据，返回的对象可以当作 Python dict 使用
	返回类型: CyberDict

**loc(self, key)**
	
	此方法可以被 CyberDict.get(key) 替代
	获取 CyberDict key 键对应的值
	参数:
		key -- CyberDict 的键
	返回类型: 该键存储的数据

**put(self, key, value)**

	此方法用于替代 dict[key] = value 新建键值对或赋值
	参数:
		key -- CyberDict 的新增或已有键
		value -- CyberDict key 对应的新值
	返回类型: None

**delete(self, key)**

	此方法用于替代 del dict[key] 删除键值对
	参数:
		key -- CyberDict 需删除的键
	返回类型: None

**get_length(self)**

	此方法用于替代 len(dict) 获取字典长度
	返回类型: int

**get_type(self) -> type**

	获取 CyberDict 内置数据类型
	由于客户端获取的 CyberDict 对象仅为网络对象，type(CyberDict) 和此处 get_type() 并不
	相同。如无必要，无需使用此方法
	返回类型: type

**box(self, command: str)**

	魔术方法 dict[x] 的替代方案
	使用该方法应该自行考虑 Python 脚本注入等安全问题
	参数:
		command -- 等同于 dict[x] 中 x 表达式对应的字符串(command = str(x))
		即 CyberDict.box(command) = dict[x]，其中 command = str(x)
	返回类型: dict[x] 的返回类型

### class CyberList

DBCon对象.CyberList.表名 获取的实例是基于 CyberList 的网络对象。CyberList 兼容 [Python list](https://docs.python.org/3.10/library/stdtypes.html#list) 的所有公有方法，此处只列举不同于 dict 的部分。

**show(self):**

	获取 CyberList 的原始数据，返回的对象可以当作 Python list 使用
	返回类型: CyberList

**loc(self, i: int)**

	获取 CyberList 的第 i 个值(第 0 个值为起点)
	参数:
		i -- CyberList 的下标
	返回类型: CyberList[i] 对应的值类型

**loc_form(self, i: int, j: int)**

	获取二维嵌套 CyberList 的第 i 行第 j 列对应的值(第 0 行第 0 列为起点)
	参数:
		i -- CyberList 的一维下标
		j -- CyberList 的二维下标
	返回类型: CyberList[i][j] 对应的值

**slice(self, i: int=None, j: int=None)**

	此方法能替代 Python 切片的部分功能
	CyberList.slice(i, j) 等同于 list[i:j]，但是 i、j 不能为 *
	返回类型: list[i:j] 的返回值类型

**get(self, index: int)**

	此方法可以被 CyberList.loc(index) 替代
	获取 CyberList 的第 index 个值(第 0 个值为起点)
	参数:
		index -- CyberList 的下标
	返回类型: CyberList[index] 对应的值类型

**update(self, index: int, value)**

	修改 CyberList 的第 index 个值(第 0 个值为起点)为 value
	CyberList.update(index, value) 等同于 list[index] = value
	参数:
		index -- CyberList 的下标
		value -- 需更改的 CyberList 值
	返回类型: None

**update_form(self, i: int, j: int, value)**

	修改二维嵌套 CyberList 的第 i 行第 j 列的值为 value
	CyberList.update_form(i, j, value) 等同于 list[i][j] = value
	参数:
		i -- CyberList 的一维下标
		j -- CyberList 的二维下标
		value -- 需更改的 CyberList 值
	返回类型: None

**get_length(self)**

	此方法用于替代 len(list) 获取列表长度
	返回类型: int

**get_type(self) -> type**

	获取 CyberList 内置数据类型
	由于客户端获取的 CyberList 对象仅为网络对象，type(CyberList) 和此处 get_type() 并不
	相同。如无必要，无需使用此方法
	返回类型: type

**box(self, command: str)**

	魔术方法 list[x] 的替代方案
	使用该方法应该自行考虑 Python 脚本注入等安全问题
	参数:
		command -- 等同于 list[x] 中 x 表达式对应的字符串(command = str(x))
		即 CyberList.box(command) = list[x]，其中 command = str(x)
	返回类型: list[x] 的返回类型



