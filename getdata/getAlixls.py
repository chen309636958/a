# coding=utf-8
from lib.buildAliSession import buildAliSession
from lib.baselib import *
from lib.DB import connDB,fetchDB,countTable
from tqdm import tqdm
from MySQLdb import Error as DBERROR
import xlrd
from config import XLS_URL,ROOTPATH
warnings.filterwarnings("ignore")

class getAlixls(object):
    def __init__(self):
        self.session = buildAliSession()
        self.tb_token = self.session.cookies['_tb_token_']
        self.pvid = ''
        self.xls_updatetime = DateStrtoFloat() + 36600
        self.xls_date = self.xlsUpDate()
        self.xls_filetime = DateStrtoFloat(self.xls_date)
        self.xls_filename = r'{}\ali1w-{}.xls'.format(ROOTPATH,self.xls_date)
    def xlsUpDate(self):
        filedate = self.xls_updatetime if time.time() >= self.xls_updatetime else self.xls_updatetime - 86400
        return DateFloattoStr(filedate)
    def getxls(self):
        """
        :return:
        """
        url = XLS_URL
        r = robustHttpConn(url, session = self.session,method = 'get',stream = True)
        with open(self.xls_filename, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size = 1024)):
                f.write(chunk)
    def formatAlixls(self):
        if not os.path.isfile(self.xls_filename):self.getxls()
        data = xlrd.open_workbook(self.xls_filename)
        table = data.sheets()[0]
        tabledata =[table.row_values(rownum) for rownum in xrange(1,table.nrows)]
        productlist = list()
        for rowdata in tabledata:
        # for rowdata in tabledata[100:200]:
            auctionid = int(rowdata[0])
            sellerid = int(rowdata[11])
            activityid = rowdata[14]
            (ismall,producturl) = (2,'https://item.taobao.com/item.htm?id={}'.format(auctionid)) if rowdata[13] == u'淘宝' else (1,'https://detail.tmall.com/item.htm?id={}'.format(auctionid))
            quanstr = rowdata[17]
            quanvalue = int(strCompile(quanstr,u'减(\d+)元')) if u'减' in quanstr else int(strCompile(quanstr,u'(\d+)元无条件'))
            originalprice = float(rowdata[6])
            discountprice = float((int(originalprice*100) - quanvalue*100)/100)
            quantotal = int(rowdata[15])
            quanrest = int(rowdata[16])
            quanused = quantotal - quanrest
            commrate = float(rowdata[8])
            productlist.append((
                auctionid,#'1 AUCTION_ID':
                1,
                producturl,#'3 PRODUCT_URL':
                ismall,#'4 IS_MALL':
                rowdata[1],#'5 TITLE':
                rowdata[2],#'6 PIC_URL':
                int(rowdata[7]),#7 MONTH_SELL
                sellerid,#'8 SELLER_ID':
                activityid,#'9 ACTIVITY_ID':
                originalprice,#'10 ORIGINAL_PRICE':
                discountprice,#'11 DISCOUNT_PRICE':
                quanvalue,#'12 QUAN_VALUE':
                rowdata[17],#13 QUAN_STR
                'http://shop.m.taobao.com/shop/coupon.htm?seller_id={}&activity_id={}'.format(sellerid,activityid),#'14 QUAN_URL':
                rowdata[20],#'15 QUAN_ADPURL':
                quanused,#'16 QUAN_USED':
                quanrest,#'17 QUAN_REST':
                quantotal,#'18 QUAN_TOTAL':
                # int(time.mktime(time.strptime(rowdata[19] + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))),#'QUAN_DEADTIME':
                DateStrtoFloat(rowdata[19]),#'19 QUAN_DEADTIME':
                rowdata[4],#'21 TAG':
                commrate,#25 COMM_RATE
                rowdata[5],#26 COMM_SCLICK
                rowdata[21]#27 COMM_COMP_URL
            ))
        return productlist
    @timer
    def run(self):
        xlssaved = fetchDB("""SELECT XLS_SAVED_DATE FROM DATA_SAVE_STATUS LIMIT 1""",0)
        if xlssaved is not None and self.xls_filetime in xlssaved:
            logger.info(u'The {} xls had been saved'.format(self.xls_date))
        else:
            productlist = self.formatAlixls()
            sql = """INSERT INTO PRODUCT_DATA (
                    AUCTION_ID,
                    SOURCE,
                    PRODUCT_URL,
                    IS_MALL,
                    TITLE,
                    PIC_URL,
                    MONTH_SELL,
                    SELLER_ID,
                    ACTIVITY_ID,
                    ORIGINAL_PRICE,
                    DISCOUNT_PRICE,
                    QUAN_VALUE,
                    QUAN_STR,
                    QUAN_URL,
                    QUAN_ADPURL,
                    QUAN_USED,
                    QUAN_REST,
                    QUAN_TOTAL,
                    QUAN_DEADTIME,
                    TAG,
                    COMM_RATE,
                    COMM_SCLICK,
                    COMM_COMP_URL
                    )values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            conn = connDB()
            cur = conn.cursor()
            cur.executemany(sql,productlist)
            cur.execute("INSERT INTO DATA_SAVE_STATUS (XLS_SAVED_DATE) VALUES (%s)"%self.xls_filetime)
            conn.commit()
            # try:
            #     cur.executemany(sql,productlist)
            #     conn.commit()
            #     cur.execute("INSERT INTO DATA_SAVE_STATUS (XLS_SAVED_DATE) VALUES (%s)"%self.xls_filetime)
            #     conn.commit()
            #     logger.info(u'保存数据成功，共存入{}条数据'.format(len(productlist)))
            #     os.remove(self.xls_filename)
            # except DBERROR as e:
            #     logger.error(u'保存数据失败：{}'.format(e))
            #     conn.rollback()
            conn.close()
            return len(productlist)


if __name__ == '__main__':
    s = getAlixls()
    res1 = countTable('product_data')
    res2 = s.run()
    res3 = countTable('product_data')
    print res1
    print res2
    print res3

