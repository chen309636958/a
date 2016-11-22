# coding=utf-8
from lib.baselib import *
from lib.DB import *
@timer
def checkquandate():
    """
    删除过期券
    :return:
    """
    now_datetime = DateStrtoFloat()
    conn = connDB()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM PRODUCT_DATA WHERE QUAN_DEADTIME = %s"%now_datetime)
        conn.commit()
    except:
        conn.rollback()
    conn.close()

if __name__ == '__main__':
    checkquandate()
    r = fetchDB("""select * from product_data where IS_MALL = 1""")
    print r
