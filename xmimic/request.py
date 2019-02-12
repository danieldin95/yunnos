#!/usr/bin/env python

'''
Created on Jan 17, 2019

@author: Albert 
'''

import sys
import Queue
import time

import zmq
import job
import mesg

class TcpRequest(object):
    """"""
    INTERVAL = 1 # 1s
    
    def __init__(self, connect_to, **kwargs):
        """"""
        self.ctx = zmq.Context.instance()
        self.s = self.ctx.socket(zmq.REQ)
        self.s.connect("tcp://%s"%connect_to)
        
        print("connect to %s"%connect_to)
        
        self.txq = Queue.Queue()
        self.poller = zmq.Poller()
        self.poller.register(self.s, zmq.POLLIN|zmq.POLLOUT)
        self.idle = kwargs.get("idle", "idle from client")

        self.__running__ = True
        self.lasttime    = time.time()
        self.recvHookFunc = None
        self.DEBUG = False

    def sendMsg(self, msg):
        """"""
        self.txq.put(msg)

    def setIdle(self, msg):
        """"""
        self.idle = msg

    def _recv(self):
        """"""
        d = self.s.recv()
        try:
            m = mesg.MimicRawMesg(d)
        except TypeError as e:
            print("receive invalid message: %s"%repr(d))
            return
    
        self.recvMsg(m)
    
    def _send(self):
        """"""
        nowtime = time.time()
        dt = nowtime - self.lasttime
        if not self.txq.empty():
            msg = self.txq.get()
            print("%s send: %s"%(nowtime, repr(msg)))
            self.s.send(msg)
        elif dt >= self.INTERVAL or dt < 0:
            if self.DEBUG:
                print("%s send: %s"%(nowtime, repr(self.idle)))
            self.s.send(self.idle)
            self.lasttime = nowtime
        else:
            time.sleep(self.INTERVAL-dt)

    def loop(self):
        """"""
        self.socks = dict(self.poller.poll())
        #print self.socks
        if self.socks[self.s] == zmq.POLLIN:
            self._recv()
        elif self.socks[self.s] == zmq.POLLOUT:
            self._send()

    def recvMsg(self, m):
        """
        @param m: MimicRawMesg 
        """
        if self.DEBUG:
            print("%s receive: %s"%(time.time(), m))
        if self.recvHookFunc:
            self.recvHookFunc(m)

    def loopForever(self):
        """
        """
        while True and self.__running__:
            self.loop()

class TcpRequestJob(job.YunJob):
    """"""

def main():
    if len (sys.argv) != 2:
        print('usage: request <connect_to>')
        sys.exit (1)

    bind_to = sys.argv[1]
    req = TcpRequest(bind_to)
    reqjob = TcpRequestJob(req)
    reqjob.start()
    reqjob.join()

if __name__ == "__main__":
    main()
