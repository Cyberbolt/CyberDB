import time
import socket

import cyberdb


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect(('127.0.0.1', 9980))
        time.sleep(11)


if __name__ == '__main__':
    main()