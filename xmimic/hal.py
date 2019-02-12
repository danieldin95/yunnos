#!/usr/bin/env python

'''
Created on Jan 18, 2019

@author: Albert 
'''

import mesg
import server

import job

class HalServer(server.YunServer):
    """"""
    def __init__(self, bind_to = '127.0.0.1:5563'):
        """"""
        self.bind_to = bind_to
        super(HalServer, self).__init__(self.bind_to)
 
    def recvMsg(self, topic, m):
        """
        @param m: MimicRawMesg
        """
        print("%s receive message %s %s"%(self.__class__.__name__, topic, m))
        if self.recvHookFunc:
            self.recvHookFunc(m)

    def utSendPortStats(self, name='eth2', state=mesg.MimicPortStats.phyStateUp, 
                        txCount=1024, rxCount=2049, crcErr=356, speed=12):
        """"""
        portNo = int(name[3:])
        m = mesg.MimicPortStats(portNo, name, phyState = state, txCount = txCount,
                                            rxCount = rxCount, crcErrCount = crcErr,
                                            speed = speed)
        self.sendMsg(m.topic, m.pack())

class HalServerJob(job.YunJob):
    """"""

def main():
    """"""
    server = HalServer()
    job = HalServerJob(server)
    job.start()
    job.join()

if __name__ == "__main__":
    main()
