import time

import cyberdb


def main():
    db = cyberdb.Server()
    db.set_backup('data.cdb', cycle=3)
    # db.run(password='123456', print_log=True, encrypt=False)
    db.start(password='123456', print_log=True, encrypt=False)
    time.sleep(10000)


if __name__ == '__main__':
    main()
