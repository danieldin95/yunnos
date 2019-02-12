#!/usr/bin/env python

'''
Created on Jan 18, 2019

@author: Albert 
'''

import mesg
import server

import job

class XshellServer(server.YunServer):
    """"""
    verfile = '/usr/local/etc/version'

    def __init__(self, bind_to = '127.0.0.1:5564'):
        """"""
        self.bind_to = bind_to
        super(XshellServer, self).__init__(self.bind_to)
        self.history = []

    def recvHisMsg(self, m):
        """"""
        (c, t) = self.getStrFromData(m.data[12:])
        print("receive history update <%s>"%c)
        self.history.append(c)
        print("\n---------HISROTY--------")
        print("%s"%('\n'.join(self.history)))
        print("\n----------END------------")
 
    def recvMsg(self, topic, m):
        """
        @param m: MimicRawMesg
        """
        print("%s receive message %s %s"%(self.__class__.__name__, topic, m))
        if m.type == mesg.MimicHistory.type:
            self.recvHisMsg(m)
        elif self.recvHookFunc:
            self.recvHookFunc(m)

    def saveVer(self, m):
        """"""
        try:
            f = open(self.verfile, 'w')
            f.write(m[4:])
            f.close()
        except Exception as e:
            print e

    def utSendSoftVer(self, ver='Mimic version 5.0.1 @copyright Nanjing Yunnex.'):
        """"""
        m = mesg.MimicSoftVer(ver)
        self.sendMsg(m.topic, m.pack())   

class XshellServerJob(job.YunJob):
    """"""

def main():
    """"""
    server = XshellServer()
    job = XshellServerJob(server)
    job.start()
    job.join()

if __name__ == "__main__":
    main()
