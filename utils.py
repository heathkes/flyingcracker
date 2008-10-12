#!/usr/bin/env python
from datetime import *

class ElapseMark():
    
    def __init__(self, label, elapsed):
        self.label = label
        self.elapsed = elapsed.__str__().lstrip('0:')
        
class ElapsedTime():

    def __init__(self):
        self.last = datetime.now()
        self.mark = []

    def mark_time(self, label):
        now = datetime.now()
        elapsed = now - self.last
        self.last = now
        self.mark.append(ElapseMark(label, elapsed))
        
    def list(self):
        return self.mark
    
if __name__ == '__main__':
    et = ElapsedTime()
    x = [i for i in range(0,10000)]
    et.mark_time('end of loop')
    for e in et.list():
        print e.label + ': ' + e.elapsed