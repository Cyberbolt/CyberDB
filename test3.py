import time
import socket

import cyberdb


def main():
    client = cyberdb.connect(password='123456', encrypt=True)
    proxy = client.get_proxy()
    proxy.connect()
    
    list1 = proxy.get_cyberlist('list1')
    list1[2] = 2
    list1.sort()
    print(list1[0], ' ', 1)
    
    test = []
    for i in range(5):
        test.append(0)
        
    print(test)


if __name__ == '__main__':
    main()