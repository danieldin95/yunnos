#!/usr/bin/env python

"""A test that subscribes to yunnos.
"""

import sys

import zmq

class Subsctibe(object):
    """"""
    def __init__(self, connect_to):
        """"""
        self.ctx = zmq.Context()
        self.s = self.ctx.socket(zmq.SUB)
        self.s.connect(connect_to)
        self.subscribe("")
    
    def subscribe(self, title):
        """"""
        self.s.setsockopt(zmq.SUBSCRIBE, title)

    def loop(self):
        """"""
        while True:
            t = self.s.recv()
            a = self.s.recv()
            print "receiving %s:%s"%(t, repr(a))

def main():
    """"""
    if len (sys.argv) != 2:
        print('usage: subscriber <connect_to>')
        sys.exit (1)

    connect_to = sys.argv[1]
    sub = Subsctibe(connect_to)
    sub.loop()

if __name__ == "__main__":
    main()
