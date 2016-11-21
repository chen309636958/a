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
