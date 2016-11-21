# coding=utf-8
import multiprocessing
from getdata.getAlixls import saveAlixls
from lib.DB import resetDB,resetTABLES

class aliXlsTask(multiprocessing.Process):
    def __init__(self):
        super(aliXlsTask,self).__init__()
    def run(self):
        print 'alixls start'
        run = saveAlixls()
        run.run()

if __name__ == '__main__':
    # resetTABLES('PRODUCT_DATA')
    from lib.baselib import *
    xlsfile = 'a-2016-03-15.xls'
    s = time.time()
    b = DateStrtoFloat(DateFloattoStr())  + 36600
    d = DateStrtoFloat()  + 36600
    c = DateFloattoStr(b,0)
    print s
    print b
    print c
    print d