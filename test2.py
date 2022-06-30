import time
import sys
import asyncio

import cyberdb


def test():
    client = cyberdb.connect(password='123456', encrypt=False)
    proxy = client.get_proxy()
    proxy.connect()

    dict_test = {i: i * i for i in range(10000)}
    try:
        proxy.create_cyberdict('dict1', dict_test)
    except:
        pass
    dict1 = proxy.get_cyberdict('dict1')
    dict1[1] = 'test1'
    print(dict1[1])
    del dict1[1]
    print(dict1.get(1))
    dict1['test'] = 'testprint'
    dict1[1] = 3920
    dict1[2] = 2930
    dict1.setdefault(3, 3333)
    dict1.setdefault(2, 3333)
    print(dict1.todict(), ' ', type(dict1.todict()))
    print(dict1.keys(), '\n', dict1.values())
    for k, v in dict1.items():
        print(k, v)
    print(dict1.pop('s'))
    print(dict1.popitem())
    dict1.clear()
    print(dict1)
    dict2 = {333: 666, 777: 888}
    dict1.update(dict2)
    print(dict1)
    for key in dict1:
        print(dict1[key])
    print(len(dict1))
    
    dict1.clear()

def test2():
    client = cyberdb.connect(password='123456', encrypt=False)
    proxy = client.get_proxy()
    proxy.connect()
    
    try:
        proxy.create_cyberlist('list1')
    except:
        pass
    list1 = proxy.get_cyberlist('list1')
    list1.append(1)
    list1.append(3)
    print(list1)
    list1[0] = 2
    print(list1)
    print(list1.tolist(), ' ', type(list1))
    # print(len(list1))
    print(min(list1))
    proxy.connect()
    print(type(list1))
    list1.extend([1, 2, 3])
    print(list1)
    try:
        proxy.create_cyberlist('list2')
    except:
        pass
    list2 = proxy.get_cyberlist('list2')
    list2.append(11)
    list1.extend(list2)
    print(list1)
    list1.insert(1, 99999)
    print(list1)
    list1.pop()
    print(list1)
    list1.remove(99999)
    print(list1)
    print(list1.count(2))
    print(list1.index(1))
    list1.reverse()
    print(list1)
    list1.clear()
    list2.clear()
    print(list1)
    list1.extend([(2, 2), (3, 4), (4, 1), (1, 3)])
    print(list1)
    
    def takeSecond(elem):
        return elem[1]
    # list1.sort(key=lambda ele:ele[1])
    list1.sort(key=takeSecond)
    print(list1)
    
    for one in list1:
        print(one)
    
    list1.clear()
    list2.clear()

def test3():
    client = cyberdb.connect(password='123456', encrypt=True)
    proxy = client.get_proxy()
    proxy.connect()
    proxy.create_cyberlist('list1')
    list1 = proxy.get_cyberlist('list1')
    for i in range(10):
        list1.append(0)
    list1[1] = 1
    print(list1, '\n', list1[0])

def main():
    test()
    # test2()
    # asyncio.run(test())
    # time.sleep(1)
    # client.test()
    # dict1 = {i: i * i for i in range(10000)}
    # print(sys.getsizeof(dict1))


if __name__ == '__main__':
    main()
