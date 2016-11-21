# coding=utf-8
from lib.buildAliSession import buildAliSession
from lib.baselib import DateFloattoStr, robustHttpConn, checkFile,strCompile ,time,urllib,os
from lib.DB import connDB
from tqdm import tqdm
import xlrd, glob
from config import DX_APPLY_REASON, PID
from lib.logger import logger
from var_dump import var_dump

def timer(func):
    def _d(*arg, **karg):
        timestart = time.time()
        r= func(*arg, **karg)
        print time.time() - timestart
        return r
    return _d

class Alixls(object):
    def __init__(self):
        self.session = buildAliSession()
        self.tb_token = self.session.cookies['_tb_token_']
        self.pvid = ''
    def saveAlixls(self):
        xls_filename = 'ali1w-{}_{}.xls'.format(DateFloattoStr(), time.time())
        url = 'http://pub.alimama.com/coupon/qq/export.json?adzoneId=65026808&siteId=18074623'
        r = robustHttpConn(url, session = self.session,method = 'get',stream = True)
        with open('rownum.txt', 'w') as f:
            f.write('0')
        with open(xls_filename, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size = 1024)):
                f.write(chunk)
        return xls_filename
    def exitDx(self,pubCampaignid):
        """
        退出计划
        :param pubCampaignid:
        :return:
        """
        exitdxdata = {
            'pubCampaignid': pubCampaignid,
            't': int(time.time() * 1000),
            '_tb_token_': self.tb_token,
            'pvid': self.pvid
        }
        return robustHttpConn('http://pub.alimama.com/campaign/exitCampaign.json', method = 'post', session=self.session, data=exitdxdata, cookies={'account-path-guide-s1': 'true', 'dxjh-guide-1': 'true'})
    def applyDx(self,CampaignID, ShopKeeperID):
        """
        申请计划
        :param CampaignID:
        :param ShopKeeperID:
        :return:
        """
        applyDxData = {
            'campId': CampaignID,
            'keeperid': ShopKeeperID,
            'applyreason': DX_APPLY_REASON,
            't': int(time.time() * 1000),
            '_tb_token_': self.tb_token,
            'pvid': self.pvid
        }
        return robustHttpConn('http://pub.alimama.com/pubauc/applyForCommonCampaign.json',method = 'post' ,session=self.session, data=applyDxData, cookies={'account-path-guide-s1': 'true', 'dxjh-guide-1': 'true'},getjson = 1)
    def selectTypeFULL(self, productUrl):
        """
        '选择转换链接'
        :param productUrl:
        :return:  通用：1 鹊桥：2 定向：3 无淘宝客计划：0
        """
        auctionid = strCompile(productUrl, 'id=(\d+)')
        dxUrl = 'http://pub.alimama.com/pubauc/getCommonCampaignByItemId.json?itemId=%s&t=%d&_tb_token_=%s&pvid=' % (auctionid, time.time() * 1000, self.tb_token)
        queqiaoUrl = 'http://pub.alimama.com/items/channel/qqhd.json?q=%s&channel=qqhd&_t=%d&perPageSize=40&shopTag=&t=%d&_tb_token_=%s&pvid=' % (urllib.quote(productUrl), time.time() * 1000 - 55, time.time() * 1000, self.tb_token)
        tongyongUrl = 'http://pub.alimama.com/items/search.json?q=%s&_t=%d&perPageSize=40&shopTag=&t=%d&_tb_token_=%s&pvid=' % (urllib.quote(productUrl), time.time() * 1000 - 55, time.time() * 1000, self.tb_token)
        #获取鹊桥 不存在则获取通用
        commGet = robustHttpConn(queqiaoUrl, getjson = 1)
        if commGet is not None and commGet['data']['pageList'] is not None:
            commSign = 2
            commStr = u'鹊桥'
            commRate = commGet['data']['pageList'][0]['eventRate']
        else:
            commGet = robustHttpConn(tongyongUrl,getjson = 1)
            if commGet is not None and commGet['data']['pageList'] is not None:
                commSign = 1
                commStr = u'通用'
                commRate = commGet['data']['pageList'][0]['tkRate']
            else:
                logger.exception(u'[商品ID：{}]:淘宝客计划不存在'.format(auctionid))
                return 0
        self.pvid = commGet['info']['pvid']
        dxmap = commGet['data']['pageList'][0]['tkSpecialCampaignIdRateMap']
        dxLargerRate = 0 if dxmap is None or dxmap == {} else [float(i) for i in dxmap.itervalues() if float(i) > commRate * 0.95]
        if dxLargerRate == 0 or dxLargerRate is []:
            logger.exception(u'[商品ID：{}]:选取{}计划 rate = {}'.format(auctionid,commStr,commRate))
            return commSign
        # # 佣金列表 <generator object <genexpr> at 0x0000000004376D80>
        dxDetail = robustHttpConn(dxUrl, session = self.session,getjson = 1)['data']
        dxAPPLYED = filter(lambda i: i['Exist'] is True,dxDetail)
        dxAPPLYEDMaxRate = 0 if dxAPPLYED == [] else max([i['commissionRate'] for i in dxAPPLYED])
        dxLargerID = [int(k) for k, v in dxmap.iteritems() if float(v) in dxLargerRate]
        dxLargerDetail = [i for i in dxDetail if i['CampaignID'] in dxLargerID and i['manualAudit'] is 0]
        dxLargerMaxRate = 0 if dxLargerDetail == [] else max([i['commissionRate'] for i in dxLargerDetail])
        if dxAPPLYEDMaxRate is not 0 and dxAPPLYEDMaxRate >= dxLargerMaxRate:
            logger.exception(u'[商品ID：{}]:已存在最高定向计划：Rate:{}'.format(auctionid,dxAPPLYEDMaxRate))
        elif dxLargerMaxRate is not 0 and dxLargerMaxRate > dxAPPLYEDMaxRate:
            dxSelect = filter(lambda i:i['commissionRate'] == dxLargerMaxRate,dxLargerDetail)[0]
            CampaignID = dxSelect['CampaignID']
            ShopKeeperID = dxSelect['ShopKeeperID']
            CampaignName = dxSelect['CampaignName']
            manualAudit = dxSelect['manualAudit']
            dxreturn = self.applyDx(CampaignID,ShopKeeperID)['info']
            logger.exception(u'[商品ID：{}]:申请定向计划:{}，佣金比例：{} -[Status:{},Message:{},manualAudit:{}]-({}:{})'.format(auctionid,CampaignName,dxLargerMaxRate,dxreturn['ok'],dxreturn['message'],manualAudit,commStr,commRate))
        else:
            logger.exception(u'[商品ID：{}]:选取{}计划 rate = {}'.format(auctionid,commStr,commRate))
            return commSign
        return 3
    def aliType(self,auctionid,commRate):
        """
        :param auctionid:
        :param commrate:
        :return: 通用or鹊桥：1 定向：3 无淘宝客计划：0 无json返回：4
        """
        dxUrl = 'http://pub.alimama.com/pubauc/getCommonCampaignByItemId.json?itemId=%s&t=%d&_tb_token_=%s&pvid=' % (auctionid, time.time() * 1000, self.tb_token)
        dxGet = robustHttpConn(dxUrl, session = self.session, getjson = 1)
        # dxGet = robustHttpConn(dxUrl, session = self.session,getjson = 1)['data']
        if dxGet is None:
            return (4,0,0)
        elif dxGet['data'] is {}:
            return (1,0,0)
        dxDetail = dxGet['data']
        dxAPPLYED = filter(lambda i: i['Exist'] is True,dxDetail)
        dxAPPLYEDMaxRate = 0 if dxAPPLYED == [] else max([i['commissionRate'] for i in dxAPPLYED])
        dxLargerDetail = filter(lambda i: i['commissionRate'] > 0.95*commRate and i['manualAudit'] is 0,dxDetail)
        dxLargerMaxRate = 0 if dxLargerDetail == [] else max([i['commissionRate'] for i in dxLargerDetail])
        if dxAPPLYEDMaxRate == 0 and dxLargerMaxRate == 0:
            logger.exception(u'[商品ID：{}]:保留原有链接 rate = {}'.format(auctionid,commRate))
            return (1,0,0)
        elif dxAPPLYEDMaxRate is not 0 and dxAPPLYEDMaxRate >= dxLargerMaxRate:
            logger.exception(u'[商品ID：{}]:已存在最高定向计划：Rate:{}'.format(auctionid,dxAPPLYEDMaxRate))
            return (3,[i['CampaignID'] for i in dxAPPLYED if i['commissionRate'] == dxAPPLYEDMaxRate][0],dxAPPLYEDMaxRate)
        elif dxLargerMaxRate is not 0 and dxLargerMaxRate > dxAPPLYEDMaxRate:
            dxSelect = filter(lambda i:i['commissionRate'] == dxLargerMaxRate,dxLargerDetail)[0]
            CampaignID = dxSelect['CampaignID']
            ShopKeeperID = dxSelect['ShopKeeperID']
            CampaignName = dxSelect['CampaignName']
            manualAudit = dxSelect['manualAudit']
            dxreturn = self.applyDx(CampaignID,ShopKeeperID)['info']
            logger.exception(u'[商品ID：{}]:申请定向计划:{}，佣金比例：{} -[Status:{},Message:{},manualAudit:{}]-(已存在rate:{})'.format(auctionid,CampaignName,dxLargerMaxRate,dxreturn['ok'],dxreturn['message'],manualAudit,commRate))
            return (3,CampaignID,dxLargerMaxRate)
        # {u'info': {u'message': None, u'ok': True}, u'ok': True, u'invalidKey': None, u'data': {}}
        # ------------
        # {u'info': {u'message': None, u'ok': True}, u'ok': True, u'invalidKey': None, u'data': [{u'CampaignType': u'\u5b9a\u5411\u63a8\u5e7f\u8ba1\u5212', u'CampaignID': 7889558, u'manualAudit': 0, u'ShopKeeperID': 110302212, u'AvgCommission': u'4.75 %', u'commissionRate': 5.3, u'Exist': False, u'CampaignName': u'\u62db\u52df\u6dd8\u5b9d\u5ba2', u'Properties': u'\u5426'}]}
    def readAlixls(self):
        """

        :return:
        """
        xlsupdatetime = int(time.mktime(time.strptime('{} 10:10:00'.format(DateFloattoStr()), '%Y-%m-%d %H:%M:%S')))
        xlsfilename = glob.glob(r'ali1w-*.xls')[0]
        filesavetime = int(strCompile(xlsfilename,'_(\d+).*.xls')) if xlsfilename else 0
        if xlsupdatetime - filesavetime > 86400:
            oldxls = xlsfilename
            xlsfilename = self.saveAlixls()
            os.remove(oldxls)
        data = xlrd.open_workbook(xlsfilename)
        table = data.sheets()[0]
        tabledata =[table.row_values(rownum) for rownum in xrange(1,table.nrows)]
        return tabledata
    @timer
    def formatAlixls(self):
        tabledata = self.readAlixls()
        productlist = list()
        with open('rownum.txt','r') as f:
            num = int(f.read())
        sql = """INSERT INTO PRODUCT_DATA (AUCTION_ID,SOURCE,PRODUCT_URL,IS_MALL,TITLE,PIC_URL,MONTH_SELL,SELLER_ID,ACTIVITY_ID,ORIGINAL_PRICE,DISCOUNT_PRICE,QUAN_VALUE,QUAN_STR,QUAN_URL,QUAN_ADPURL,QUAN_USED,QUAN_REST,QUAN_TOTAL,QUAN_DEADTIME,IS_WB,TAG,ALITYPE,DX_RATE,DX_ID,COMM_RATE,COMM_SCLICK,COMM_COMP_URL,IS_SELECT)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        for rowdata in tabledata[num:]:
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
            dx = self.aliType(auctionid,commrate)
            alitype = dx[0]
            dx_id = dx[1]
            dx_rate = dx[2]
            productlist.append((
                auctionid,#'1 AUCTION_ID':
                1,#'2 SOURCE':
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
                rowdata[15],#13 QUAN_STR
                'http://shop.m.taobao.com/shop/coupon.htm?seller_id={}&activity_id={}'.format(sellerid,activityid),#'14 QUAN_URL':
                rowdata[20],#'15 QUAN_ADPURL':
                quanused,#'16 QUAN_USED':
                quanrest,#'17 QUAN_REST':
                quantotal,#'18 QUAN_TOTAL':
                # int(time.mktime(time.strptime(rowdata[19] + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))),#'QUAN_DEADTIME':
                int(time.mktime(time.strptime(rowdata[19], '%Y-%m-%d'))),#'19 QUAN_DEADTIME':
                0,#'20 IS_WB':
                rowdata[4],#'21 TAG':
                alitype,#'22 ALITYPE':
                dx_id, #23 DX_ID
                dx_rate, #24 DX_RATE
                commrate,#25 COMM_RATE
                rowdata[3],#26 COMM_SCLICK
                rowdata[19],#27 COMM_COMP_URL
                0#28 IS_SELECT
            ))
            if len(productlist) == 10:
                with open('rownum.txt','w') as f:
                    f.write(str(num))
                conn = connDB()
                cur = conn.cursor()
                try:
                    cur.executemany(sql,productlist)
                    conn.commit()
                except:
                    conn.rollback()
                conn.close()
                productlist = list()
            num += 1


    # def run(self):

