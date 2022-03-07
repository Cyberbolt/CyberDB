import time
import sys
import asyncio

import cyberdb


async def test():
    client = cyberdb.connect(password='123456')
    proxy = client.get_proxy()
    await proxy.connect()

    dict_test = {i: i * i for i in range(10000)}
    await proxy.create_cyberdict('dict1', dict_test)
    dict1 = await proxy.get_cyberdict('dict1')
    r = await dict1[9999]
    print(r)


def main():
    asyncio.run(test())
    # time.sleep(1)
    # client.test()
    # dict1 = {i: i * i for i in range(10000)}
    # print(sys.getsizeof(dict1))


    


if __name__ == '__main__':
    main()