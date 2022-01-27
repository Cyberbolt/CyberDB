import time

from cyberdb.cyberdict import CyberDict
from cyberdb.cyberlist import CyberList
from cyberdb import DBServer


db = DBServer()
db.create_cyberdict('dict1')
db.create_cyberdict('dict2')
db.create_cyberlist('list1')
# db.load_db()
db.start(host='127.0.0.1', password='123123')
while True:
    time.sleep(10000)