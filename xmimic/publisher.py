#!/usr/bin/env python

"""A test that publishes NumPy arrays.
"""

import sys
import time

import zmq

class Publisher(object):
    """"""
    def __init__(self, bind_to):
        """"""
        self.ctx = zmq.Context()
        self.s = self.ctx.socket(zmq.PUB)
        self.s.bind(bind_to)
        
    def loop(self):
        """"""
        while True:
            time.sleep(1)
            self.s.send("Hello %s"%time.time())
    
def main():
    if len (sys.argv) != 2:
        print('usage: publisher <bind-to>')
        sys.exit (1)

    bind_to = sys.argv[1]
    pub = Publisher(bind_to)
    pub.loop()

if __name__ == "__main__":
    main()
