# coding=utf-8
from lib.DB import *

if __name__ == '__main__':
    resetTABLES('data_save_status')
    import time
    from lib.baselib import *
    print DateStrtoFloat(DateFloattoStr())
    print DateStrtoFloat()
    print time.mktime(time.strptime(time.strftime('%Y-%m-%d',time.localtime()),'%Y-%m-%d'))