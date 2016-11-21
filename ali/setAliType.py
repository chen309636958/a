# coding=utf-8
from lib.baselib import *
from lib.DB import connDB
@timer
def checkquandate():
    """
    删除过期券
    :return:
    """
    now_datetime = DateStrtoFloat()
    conn = connDB()
    cur = conn.cursor()
    cur.execute("DELETE FROM PRODUCT_DATA WHERE QUAN_DEADTIME = %s"%now_datetime)
    conn.commit()
    conn.rollback()
if __name__ == '__main__':
    checkquandate()

