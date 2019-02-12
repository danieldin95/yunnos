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

class TcpReply(object):
    """"""
    def __init__(self, bind_to, **kwargs):
        """"""
        self.ctx = zmq.Context.instance()
        self.s = self.ctx.socket(zmq.REP)
        self.s.bind("tcp://%s"%bind_to)

        print("bind to %s"%bind_to)

        self.txq = Queue.Queue()
        self.poller = zmq.Poller()
        self.poller.register(self.s, zmq.POLLIN|zmq.POLLOUT)
        self.idle = kwargs.get("idle", "idle from server")

        self.__running__ = True
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
        if not self.txq.empty():
            msg = self.txq.get()
            print("%s send: %s"%(nowtime, repr(msg)))
            self.s.send(msg)
        else:
            if self.DEBUG:
                print("%s send: %s"%(nowtime, repr(self.idle)))
            self.s.send(self.idle)

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
        @param msg: MimicRawMesg 
        """
        nowtime = time.time()
        if self.DEBUG or m.type != mesg.MimicIdle.type:
            print("%s receive: %s"%(nowtime, m))

    def loopForever(self):
        """"""
        while True and self.__running__:
            self.loop()

    def utSendSoftVer(self, ver='Mimic version 5.0.1 @copyright Nanjing Yunnex.'):
        """"""
        m = mesg.MimicSoftVer(ver)
        self.sendMsg(m.pack())

    def utSendPortStats(self, name='eth2', 
                        state=mesg.MimicPortStats.phyStateUp, 
                        txCount=1024, rxCount=2049, crcErr=356, speed=12):
        """"""
        portNo = int(name[3:])
        m = mesg.MimicPortStats(portNo, name, 
                                phyState = state, txCount = txCount,
                                rxCount = rxCount, crcErrCount = crcErr,
                                speed = speed)
        self.sendMsg(m.pack())

class TcpReplyJob(job.YunJob):
    """"""

def main():
    if len (sys.argv) != 2:
        print('usage: reply <bind-to>')
        sys.exit (1)

    bind_to = sys.argv[1]
    rep = TcpReply(bind_to, idle=mesg.MimicIdle("idle from reply").pack())
    repjob = TcpReplyJob(rep)
    repjob.start()
    repjob.join()

if __name__ == "__main__":
    main()
