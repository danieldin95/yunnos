#!/usr/bin/env python

'''
Created on Jan 17, 2019

@author: Albert 
'''

import sys
import socket
import select
import struct 

import mesg
import job

class TcpServer(object):
    """"""
    def __init__(self, bind_to):
        """"""
        addrs = bind_to.split(':')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((addrs[0], int(addrs[1])))

        print("bind to %s"%bind_to)

        self.s.listen(32)
        self.fds = [self.s]
        self.__running__ = True
        self.lastrecvbuf = ''
        self.lastrecvlen = 0
        self.idleFunc = None

    def accept(self):
        """"""
        conn, addrs = self.s.accept()
        print('accept from %s:%s'%(addrs[0], addrs[1]))

        self.fds.append(conn)

    def recv(self, r, s=1024):
        """"""
        print("receive size: %s"%s)
        d = r.recv(s)
        if not d:
            self.fds.remove(r)
        else:
            print("receive data: %s"%repr(d))

        return d

    def idle(self):
        """"""

    def loop(self):
        """"""
        try:
            rs, ws, es = select.select(self.fds, [], self.fds, 1)
            if len(rs) == 0 and len(es) == 0:
                if self.idleFunc:
                    self.idleFunc()
                return

            for r in rs:
                if r is self.s:
                    self.accept()
                else:
                    self.recv(r)
    
            for e in es:
                if e is self.s:
                    self.stopGracefully()
                    return 
                else:
                    print("socket %s exit"%e)
                    self.fds.remove(e)
        except Exception as e:
            print ("%s: %s"%(type(e), e))

    def close(self):
        """"""  
        self.s.close()

    def loopForever(self):
        """"""
        print("waiting for yunnos to connect...")
        while len(self.fds) > 0 and self.__running__:
            self.loop()

    def stopGracefully(self):
        """"""
        print("stop %s gracefully."%self.__class__.__name__)
        self.__running__  = False
        for r in self.fds:
            r.close()

""" MESSAGE FORMAT
+-+-+-+-+-+-+-+-+-+-+-+-+-+
0      7       15       32
+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Length          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+
+         Topic           +
+-+-+-+-+-+-+-+-+-+-+-+-+-+
+         Payload         +
+-+-+-+-+-+-+-+-+-+-+-+-+-+

Length: uint
   Total length of message
Topic: string
   The topic of message
Payload: struct or bytes
   The struct of mimic table
"""

class YunServer(TcpServer):
    """"""
    HEADER_SIZE = 4

    def __init__(self, bind_to):
        """"""
        super(YunServer, self).__init__(bind_to)
        self.recvHookFunc = None

    def recv(self, r):
        """"""
        d = super(YunServer, self).recv(r, self.HEADER_SIZE)
        if len(d) != self.HEADER_SIZE:
            print("receive data for size %s failed"%self.HEADER_SIZE)
            return

        l = struct.unpack("I", d)[0]-self.HEADER_SIZE

        d = super(YunServer, self).recv(r, l)
        if len(d) != l:
            print("receive data for size %s failed"%l)
            return

        (t, p) = self.getStrFromData(d)
        self.recvMsg(t, mesg.MimicRawMesg(p))

    def getStrFromData(self, d):
        """"""
        for i in range(len(d)):
            if d[i] == '\x00':
                break

        return (d[:i], d[i+1:])

    def recvMsg(self, topic, m):
        """
        @param m: MimicRawMesg
        """
        print("%s receive message %s %s"%(self.__class__.__name__, topic, m))

    def sendMsg(self, topic, data):
        """"""
        print("%s send message %s %s"%(self.__class__.__name__, topic, repr(data)))
        
        s = 4+len(topic)+1+len(data)

        buf = struct.pack('I', s)
        buf += topic
        buf += b'\x00'
        buf += data

        for f in self.fds[1:]:
            f.send(buf)

def main():
    if len (sys.argv) != 2:
        print('usage: reply <bind-to>')
        sys.exit (1)

    bind_to = sys.argv[1]
    server = YunServer(bind_to)
    job = job.YunJob(server)
    job.start()
    job.join()

if __name__ == "__main__":
    main()
