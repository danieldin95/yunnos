'''
Created on Jan 18, 2019

@author: Albert 
'''

import threading

class YunJob(threading.Thread):
    """"""
    def __init__(self, server, daemon=True, *args,  **kwargs):
        """"""
        super(YunJob, self).__init__(*args, **kwargs)
        self.server = server
        self.setDaemon(daemon)

    def run(self):
        """"""
        print("start %s"%self.__class__.__name__)
        self.server.loopForever()