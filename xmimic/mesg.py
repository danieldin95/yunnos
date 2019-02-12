'''
Created on Jan 17, 2019

@author: Albert
'''

import struct

MIMIC_OPR_ADD = 1
MIMIC_OPR_DEL = 2
MIMIC_OPR_MOD = 3

MIMIC_PORTNAME_LEN = 64

'''
#define MIMIC_TAB_IDLE              0
#define MIMIC_TAB_INPORTSTATS       1
#define MIMIC_TAB_INSOFTVER         2
#define MIMIC_TAB_OUTACL            1001
#define MIMIC_TAB_OUTPORTIP         1002
#define MIMIC_TAB_OUTFIB            1003
#define MIMIC_TAB_OUTARP            1004
#define MIMIC_TAB_OUTFDB            1005
#define MIMIC_TAB_OUTPORTSTP        1006
#define MIMIC_TAB_OUTVLAN           1007
#define MIMIC_TAB_OUTSWITCHPORT     1008
#define MIMIC_TAB_OUTLAG            1009
#define MIMIC_TAB_OUTPORTCONF       1010
#define MIMIC_TAB_OUTMIRROR         1011
#define MIMIC_TAB_OUTHISTORY        1012
#define MIMIC_TAB_OUTSYNCCMD        1013
'''

class MimicMesg(object):
    """"""
    type  = -1

    def __init__(self, *args, **kwargs):
        """"""
        self.topic = self.__class__.__name__
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def unpack(cls, data):
        """"""
        raise NotImplementedError

    def pack(self):
        """"""
        raise NotImplementedError

class MimicIdle(MimicMesg):
    """"""
    type  = 0

    def __init__(self, desc="idle from yunnos"):
        """"""
        self.desc = desc

    @classmethod
    def unpack(cls, data):
        """"""
        return cls(data[4:])

    def pack(self):
        """"""
        return struct.pack('I', self.type)+self.desc

class MimicPortStats(MimicMesg):
    """"""
    phyStateDown = 0
    phyStateUp = 1

    type = 1

    def __init__(self, portNo, portName, **kwargs):
        """"""
        super(MimicPortStats, self).__init__()
        
        self.opr      = MIMIC_OPR_ADD
        self.portNo   = portNo
        self.portName = portName
        self.phyState = kwargs.get('phyState', self.phyStateDown)
        self.txCount  = kwargs.get('txCount', 0)
        self.rxCount  = kwargs.get('rxCount', 0)
        self.crcErrCount = kwargs.get('crcErrCount', 0)
        self.speed    = kwargs.get('speed', 0)

    @classmethod
    def unpack(cls, data):
        """"""
        rets = struct.unpack('III64sIQQQI', data)
        return cls(rets[2], rets[3], {'phyState': rets[4], 'txCount': rets[5], 
                                      'rxCount': rets[6], 'crcErrCount': rets[7], 
                                      'speed': rets[8]})

    def pack(self):
        """"""
        return struct.pack('III64sIQQQI', self.type, self.opr, 
                           self.portNo, self.portName,
                           self.phyState, self.txCount, 
                           self.rxCount, self.crcErrCount, 
                           self.speed)

class MimicSoftVer(MimicMesg):
    """"""
    type = 2

    def __init__(self, ver):
        """"""
        super(MimicSoftVer, self).__init__()
        self.version = ver

    @classmethod
    def unpack(cls, data):
        """"""
        return cls(data[4:])

    def pack(self):
        """"""
        return struct.pack('I', self.type)+self.version

class MimicAcl(MimicMesg):
    """"""
    type = 1001

class MimicPortIp(MimicMesg):
    """"""
    type = 1002

class MimicFib(MimicMesg):
    """"""
    type = 1003

class MimicArp(MimicMesg):
    """"""
    type = 1004

class MimicFdb(MimicMesg):
    """"""
    type = 1005

class MimicPortStp(MimicMesg):
    """"""
    type = 1006

class MimicVlan(MimicMesg):
    """"""
    type = 1007

class MimicSwitchPort(MimicMesg):
    """"""
    type = 1008

class MimicLag(MimicMesg):
    """"""
    type = 1009

class MimicPortConf(MimicMesg):
    """"""
    type = 1010

class MimicMirror(MimicMesg):
    """"""
    type = 1011

class MimicHistory(MimicMesg):
    """"""
    type = 1012
    
    def __init__(self, his):
        """"""
        super(MimicHistory, self).__init__()
        self.opr     = MIMIC_OPR_ADD
        self.len     = len(his)
        self.history = his

    @classmethod
    def unpack(cls, data):
        """"""
        return cls(data[4:])

    def pack(self):
        """"""
        return struct.pack('III', self.type, self.opr, self.len)+self.history
    
class MimicCmdSync(MimicMesg):
    """"""
    type = 1013

mesgType = {
    MimicIdle.type     : MimicIdle,
    MimicPortStats.type: MimicPortStats,
    MimicSoftVer.type  : MimicSoftVer,
    MimicAcl.type      : MimicAcl,
    MimicPortIp.type   : MimicPortIp,
    MimicFib.type      : MimicFib,
    MimicArp.type      : MimicArp,
    MimicFdb.type      : MimicFdb,
    MimicPortStp.type  : MimicPortStp,
    MimicVlan.type     : MimicVlan,
    MimicSwitchPort.type: MimicSwitchPort,
    MimicLag.type      : MimicLag,
    MimicPortConf.type : MimicPortConf,
    MimicMirror.type   : MimicMirror,
    MimicHistory.type  : MimicHistory,
    MimicCmdSync.type  : MimicCmdSync,
}

class MimicRawMesg(object):
    """"""
    def __init__(self, data):
        """"""
        self.data = data
        self.type = struct.unpack('I', data[:4])[0]

    def __str__(self):
        """"""
        return "{type: %s, data: %s}" % (self.type, repr(self.data))

    def typestr(self):
        """"""
        if self.type in mesgType:
            return mesgType[self.type].__name__
        else:
            return "type:%s"%self.type

def pack(obj):
    """"""
    return obj.pack()

def unpack(data):
    """"""
    m = MimicRawMesg(data)
    cls = mesgType.get(m.type)

    return cls.unpack(data)