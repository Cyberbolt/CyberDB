import re
import shutil
import pickle
import datetime
import asyncio
import threading

from obj_encrypt import Secret
from apscheduler.schedulers.background import BackgroundScheduler

from . import AioStream
from .route import Route
from ..data import datas
from ..extensions import DisconCyberDBError, WrongFilenameCyberDBError, \
WrongPasswordCyberDBError, BackupCyberDBError, TypeCyberDBError
from ..extensions.signature import Signature


class Server:

    def __init__(self):
        self._data = {
            'config': {
                'host': None,
                'port': None,
                'password': None
            },
            'db': {}
        }
        self.ips = {'127.0.0.1'}  # ip whitelist
        self.sched = None

    def start(self, host: str = '127.0.0.1', port: int = 9980,
              password: str = None, max_con: int = 500, timeout: int = 0,
              print_log: bool = False, encrypt: bool = False):
        '''
            The server starts from the background.

                max_con -- Maximum number of waiting connections.
        '''
        t = threading.Thread(target=self.run,
                             args=(host, port, password, max_con, timeout, print_log, encrypt))
        t.daemon = True
        t.start()

    def run(self, host: str = '127.0.0.1', port: int = 9980,
            password: str = None, max_con: int = 500, timeout: int = 0,
            print_log: bool = False, encrypt: bool = False):
        '''
            The server runs in the foreground.

                max_con -- Maximum number of waiting connections.
                timeout -- Connection timeout time, the default is not timeout.
                print_log -- Whether to print the log, the default is False.
        '''
        if not password:
            raise RuntimeError('The password cannot be empty.')

        self._data['config']['host'] = host
        self._data['config']['port'] = port
        self._data['config']['password'] = password
        self._data['config']['max_con'] = max_con
        self._data['config']['timeout'] = timeout
        self._data['config']['print_log'] = print_log
        self._data['config']['encrypt'] = encrypt

        # Responsible for encrypting and decrypting objects.
        secret = Secret(key=password)
        # for digital signature
        signature = Signature(salt=password.encode())
        # Convert TCP data and encrypted objects to each other.
        self._dp = datas.DataParsing(secret, signature, encrypt=encrypt)

        asyncio.run(self._main())

    async def _main(self):
        server = await asyncio.start_server(
            self._listener, self._data['config']['host'],
            self._data['config']['port'],
            limit=2 ** 16,  # 64 KiB
            # the maximum number of queued connections
            backlog=self._data['config']['max_con']
        )

        async with server:
            await server.serve_forever()

    async def _listener(self, reader: asyncio.streams.StreamReader,
                        writer: asyncio.streams.StreamWriter):
        '''
            This method is entered as long as a TCP connection is established,
             even if no data is sent.
        '''

        try:
            addr = writer.get_extra_info('peername')
            if self._data['config']['print_log']:
                print('{}  {}:{}  establishes a connection.'.format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    addr[0], addr[1]))

            if self._data['config']['encrypt']:
                # Check if the ip is in the whitelist.
                if self.ips:
                    if addr[0] not in self.ips:
                        if self._data['config']['print_log']:
                            print('{}  The request for {}, the ip is not in the whitelist.'.format(
                                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                addr[0]))
                        writer.close()
                        return

            # TCP route of this connection
            stream = AioStream(reader, writer, self._dp)
            route = Route(self._data['db'], self._dp, stream,
                          print_log=self._data['config']['print_log'])

            # If the timeout is set, it will automatically disconnect.
            if self._data['config']['timeout'] == 0:
                await route.find()
            else:
                try:
                    await asyncio.wait_for(route.find(),
                                           timeout=self._data['config']['timeout'])
                except asyncio.TimeoutError:
                    if self._data['config']['print_log']:
                        print('{}  {}:{}  connection timed out.'.format(
                            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            addr[0], addr[1]))
                    writer.close()

        except DisconCyberDBError:
            if self._data['config']['print_log']:
                print('{}  {}:{}  Client disconnected.'.format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    addr[0], addr[1])
                )
        except WrongPasswordCyberDBError:
            if self._data['config']['print_log']:
                print('{}  {}:{}  The password entered by the client is incorrect.'.format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    addr[0], addr[1]))

    def set_ip_whitelist(self, ips: list):
        for ip in ips:
            if not re.match(r'^((2((5[0-5])|([0-4]\d)))|([0-1]?\d{1,2}))(\.((2((5[0-5])|([0-4]\d)))|([0-1]?\d{1,2}))){3}$', ip):
                raise RuntimeError('Please enter a valid ipv4 address.')
        ips = set(ips)
        ips.add('127.0.0.1')
        self.ips = ips

    def set_backup(self, file_name: str = 'data.cdb', cycle: int = 900):
        '''
            Set the backup period.
        '''
        prefix_name, suffix_name = file_name.rsplit('.', 1)

        if suffix_name != 'cdb':
            raise WrongFilenameCyberDBError(
                'Please enter a filename with a .cdb suffix.')

        if type(cycle) != int:
            raise TypeCyberDBError('The type of cycle is not an integer.')

        # If the scheduled task exists, reset it.
        if self.sched:
            self.sched.shutdown(wait=False)

        # The time here is for looping only and does not affect usage anywhere in the world.
        self.sched = BackgroundScheduler(timezone='Asia/Shanghai')
        self.sched.add_job(self.save_db, 'interval',
                           seconds=cycle, args=[file_name])
        self.sched.start()

    def save_db(self, file_name: str = 'data.cdb'):
        prefix_name, suffix_name = file_name.rsplit('.', 1)

        if suffix_name != 'cdb':
            raise WrongFilenameCyberDBError(
                'Please enter a filename with a .cdb suffix.')

        # save to hard drive
        file_name_backup = prefix_name + '_backup.cdb'
        with open(file_name, 'wb') as f:
            pickle.dump(self._data, f)
        shutil.copyfile(file_name, file_name_backup)

    def load_db(self, file_name: str = 'data.cdb'):
        prefix_name, suffix_name = file_name.rsplit('.', 1)

        if suffix_name != 'cdb':
            raise WrongFilenameCyberDBError('The file suffix must be cdb.')

        with open(file_name, 'rb') as f:
            self._data = pickle.load(f)

        # print('File {} loaded successfully.'.format(file_name))
