import time

from obj_encrypt import Secret

import cyberdb


def main():
    db = cyberdb.Server()
    db.run(password='123456', print_log=True)
    # time.sleep(10000)


if __name__ == '__main__':
    main()