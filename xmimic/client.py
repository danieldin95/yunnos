#!/usr/bin/env python

"""A test that request to reply server.
"""

import sys
import time
import socket

class TcpClient(object):
    """"""
    def __init__(self, connect_to):
        """"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # s = socket.socket()
        self.s.connect((connect_to.split(':')[0], int(connect_to.split(':')[1])))

    def loop(self):
        """"""
        while True:
            time.sleep(1)
            self.s.send('READY %s..'%id(self))
            data = self.s.recv(1024)
            print("Receive %s"%data)

def main():
    if len (sys.argv) != 2:
        print('usage: request <connect_to>')
        sys.exit (1)

    connect_to = sys.argv[1]
    req = TcpClient(connect_to)
    req.loop()

if __name__ == "__main__":
    main()
