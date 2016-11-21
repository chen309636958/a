# coding=utf-8
from lib.buildAliSession import buildAliSession
from lib.baselib import *
from lib.DB import connDB,getDataFromDB
from tqdm import tqdm
from MySQLdb import Error as DBERROR
import xlrd, glob
from config import XLS_URL,DX_APPLY_REASON, PID
from var_dump import var_dump
warnings.filterwarnings("ignore")

class saveAlixls(object):
    def __init__(self):
        self.session = buildAliSession()
        self.tb_token = self.session.cookies['_tb_token_']
        self.pvid = ''
        self.xls_updatetime = DateStrtoFloat(DateFloattoStr()) + 36600
        self.xls_date = self.xlsUpDate()
    def xlsUpDate(self):
        filedate = self.xls_updatetime if time.time() >= self.xls_updatetime else self.xls_updatetime - 86400
        return DateFloattoStr(filedate)
    def saveAlixls(self):
        """
        :return:
        """
        xls_filename = 'ali1w-{}.xls'.format(self.xls_date)
        url = XLS_URL
        r = robustHttpConn(url, session = self.session,method = 'get',stream = True)
        with open(xls_filename, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size = 1024)):
                f.write(chunk)
        return xls_filename
    def readAlixls(self):
        """
        :return:
        """
        xlsfile = glob.glob(r'ali1w-*.xls')
        filesavetime = time.mktime(time.strptime(strCompile(xlsfile, '-(\d+-\d+-\d+)'),'%Y-%m-%d'))
        filesavetime = strCompile(xlsfile, '-(\d+-\d+-\d+)_') if xlsfile else 0
        if self.xls_updatetime - filesavetime > 86400:
            oldxls = xlsfile
            xlsfile = self.saveAlixls()
            os.remove(oldxls)
        data = xlrd.open_workbook(xlsfile)

        table = data.sheets()[0]
        tabledata =[table.row_values(rownum) for rownum in xrange(1,table.nrows)]
        return tabledata
    def formatAlixls(self):
        tabledata = self.readAlixls()
        productlist = list()
        for rowdata in tabledata:
        # for rowdata in tabledata[100:200]:
            auctionid = int(rowdata[0])
            sellerid = int(rowdata[11])
            activityid = rowdata[14]
            (ismall,producturl) = (0,'https://item.taobao.com/item.htm?id={}'.format(auctionid)) if rowdata[13] is u'淘宝' else (1,'https://detail.tmall.com/item.htm?id={}'.format(auctionid))
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
                int(time.mktime(time.strptime(rowdata[19], '%Y-%m-%d'))),#'19 QUAN_DEADTIME':
                rowdata[4],#'21 TAG':
                commrate,#25 COMM_RATE
                rowdata[5],#26 COMM_SCLICK
                rowdata[21]#27 COMM_COMP_URL
            ))
        return productlist
    @timer
    def run(self):
        print self.xlsUpDate()
        # xlssaved = getDataFromDB("""SELECT XLS_SAVED_DATE FROM DATA_SAVE_STATUS""")
        # nowdate = currentDateStr()
        # if nowdate in xlssaved:
        #     logger.info(u'The {} xls saved'.format(nowdate))
        # else:
        #     productlist = self.formatAlixls()
        #     sql = """INSERT IGNORE INTO PRODUCT_DATA (AUCTION_ID,SOURCE,PRODUCT_URL,IS_MALL,TITLE,PIC_URL,MONTH_SELL,SELLER_ID,ACTIVITY_ID,ORIGINAL_PRICE,DISCOUNT_PRICE,QUAN_VALUE,QUAN_STR,QUAN_URL,QUAN_ADPURL,QUAN_USED,QUAN_REST,QUAN_TOTAL,QUAN_DEADTIME,TAG,COMM_RATE,COMM_SCLICK,COMM_COMP_URL)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        #     conn = connDB()
        #     cur = conn.cursor()
        #     try:
        #         cur.executemany(sql,productlist)
        #         conn.commit()
        #         cur.execute("""INSERT INTO DATA_SAVE_STATUS (XLS_SAVED_DATE) VALUES (%s)"""%self.xlssavedate,)
        #         logger.info(u'保存数据成功，共存入{}条数据'.format(len(productlist)))
        #     except DBERROR as e:
        #         logger.error(u'保存数据失败：{}'.format(e))
        #         conn.rollback()
        #     conn.close()




