#!/usr/bin/env python

'''
Created on Jan 19, 2019

@author: Albert 
'''

import sys

import mesg
import xshell
import hal
import request
import time

class TpTabProxy(object):
    """"""
    def __init__(self, address='10.10.10.250', port=8001):
        """
        @param port: 8001-8005
        """
        self.req = request.TcpRequest("%s:%s"%(address, port))
        self.reqjob = request.TcpRequestJob(self.req)
        self.hal = hal.HalServer()
        self.haljob = hal.HalServerJob(self.hal)

    def start(self):
        """"""
        idle = mesg.MimicIdle()

        self.req.setIdle(idle.pack())

        self.reqjob.start()
        self.haljob.start()

class TpCmdProxy(object):
    """"""
    def __init__(self, address='10.10.10.250', port=9001):
        """
        @param port: 9001-9005
        """
        self.req = request.TcpRequest("%s:%s"%(address, port))
        self.reqjob = request.TcpRequestJob(self.req)
        self.xshell = xshell.XshellServer()
        self.xshelljob = xshell.XshellServerJob(self.xshell)

    def start(self):
        """
        """
        idle = mesg.MimicIdle()

        self.req.setIdle(idle.pack())

        self.reqjob.start()
        self.xshelljob.start()

class TpProxy(object):
    """"""
    HIS_INTERVAL = 3 # 3s

    def __init__(self, address="10.10.10.250", tabport=8001, cmdport=9001):
        """"""
        self.tabp = TpTabProxy(address, tabport)
        self.cmdp = TpCmdProxy(address, cmdport)
        self.DEBUG = False

        self.hislasttime = time.time()

    def start(self):
        """"""
        self.tabp.hal.recvHookFunc = self.recvYunMesg
        self.cmdp.xshell.recvHookFunc = self.recvYunMesg

        self.tabp.req.recvHookFunc = self.recvTpMesg
        self.cmdp.req.recvHookFunc = self.recvTpMesg
        
        self.cmdp.xshell.idleFunc = self.historyLoop

        self.tabp.start()
        self.cmdp.start()

        self.tabp.haljob.join()
        self.cmdp.xshelljob.join()

    def historyLoop(self):
        """"""
        nowtime = time.time()
        dt = nowtime - self.hislasttime
        if dt >= self.HIS_INTERVAL or dt < 0:
            m = mesg.MimicHistory('\n'.join(self.cmdp.xshell.history))
            self.tabp.req.sendMsg(m.pack())
            self.hislasttime = nowtime

    def recvYunMesg(self, m):
        """
        @param m: MimicRawMesg
        """
        print("%s receive yun message %s"%(self.__class__.__name__, m))
        if m.type == mesg.MimicCmdSync.type:
            self.cmdp.req.sendMsg(m.data)
        else:
            self.tabp.req.sendMsg(m.data)

    def recvTpMesg(self, m):
        """
        @param m: MimicRawMesg
        """
        if self.DEBUG or m.type != mesg.MimicIdle.type:
            print("%s receive tp message %s"%(self.__class__.__name__, m))

        if m.type == mesg.MimicIdle.type:
            pass
        elif m.type == mesg.MimicSoftVer.type:
            #self.cmdp.xshell.sendMsg(m.typestr(), m.data)
            self.saveVer()
        else:
            self.tabp.hal.sendMsg(m.typestr(), m.data)

def main():
    """"""
    if len (sys.argv) != 4:
        print('usage: request <server> <table-port> <command-port>')
        sys.exit (1)

    p = TpProxy(sys.argv[1], sys.argv[2], sys.argv[3])
    p.start()

if __name__ == "__main__":
    main()
