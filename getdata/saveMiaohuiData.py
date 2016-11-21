# coding=utf-8
from lib.baselib import getRealAliUrl,urllib,strCompile,quanCheck,robustHttpConn,time
from lib.DB import connDB,existAID,fetchDB
from multiprocessing import Pool as ThreadPool ,freeze_support
from itertools import repeat


def formatMhData(args):
    mhdata = args[0]
    existaid = args[1]
    isMall = 0
    productUrl = ''
    auctionId = ''
    title = mhdata['title']
    if 's.click' in mhdata['url']:
        productUrl = getRealAliUrl(urllib.unquote(mhdata['url'].split('openurl=')[1]))
        isMall = 1 if 'tmall' in productUrl else isMall
        auctionId = strCompile(productUrl, 'id=(\d+)')
    elif 'mallid=1' in mhdata['url']:
        auctionId = strCompile(mhdata['url'], 'itemid=(\d+)')
        productUrl = 'https://item.taobao.com/item.htm?id={}'.format(auctionId)
    elif 'mallid=0' in mhdata['url']:
        auctionId = strCompile(mhdata['url'], 'itemid=(\d+)')
        productUrl = 'https://detail.tmall.com/item.htm?id={}'.format(auctionId)
        isMall = 1
    if auctionId in existaid: return None
    mquanlink = urllib.unquote(mhdata['ticket'])
    activityid = strCompile(mquanlink, 'activity(?:_?[i|I])d=([a-z0-9]+)')
    sellerget = robustHttpConn('http://pub.alimama.com/items/search.json?q={}'.format(urllib.quote(productUrl)))
    sellerid = sellerget.json()['data']['pageList'][0]['sellerId']
    picUrl = sellerget.json()['data']['pageList'][0]['pictUrl']
    quanUrl = 'http://shop.m.taobao.com/shop/coupon.htm?sellerId={}&activityId={}'.format(sellerid, activityid)
    quanInfo = quanCheck(quanUrl)
    if quanInfo is None or quanInfo is 0:
        return None
    discountPrice = float(mhdata['price'])
    originalPrice = float(sellerget.json()['data']['pageList'][0]['zkPrice'])
    return (
        auctionId,
        2,
        productUrl,
        isMall,
        title,
        picUrl,
        sellerid,
        activityid,
        originalPrice,
        discountPrice,
        quanInfo['quanValue'],
        quanUrl,
        quanInfo['quanUsed'],
        quanInfo['quanRest'],
        quanInfo['quanTotal'],
        quanInfo['quanDeadTime'],
        1,
    )
def saveMhData(poolnum = 4):
    headers = {
        'Accept': '*/*',
        'Custom-Auth-Name': '',
        'system': '4.2.2',
        'model': 'GT-P5210',
        'client': '0',
        'Custom-Auth-Key': '',
        'nettype': 'WIFI',
        'imei': '133524855096680',
        'timeToken': '%s' % time.time() * 1000,
        'showimg': '0',
        'channel': 'update',
        'version': '24',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-P5210 Build/JDQ39E)',
        'Host': 'hmapp.huim.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    mqdata = {
        'tags': '全部分类',
        'id': '0',
        'way': 'back',
    }
    mhget = robustHttpConn('http://hmapp.huim.com/api/product/getmiaoquan', method = 'post',headers=headers, data=mqdata)
    mhjson = mhget.json()['data']
    for i in mhjson:
        print i
    existAuctionId = existAID()
    freeze_support()
    pool = ThreadPool(poolnum)
    mhdataformat = pool.map(formatMhData, zip(mhjson,repeat(existAuctionId)))
    pool.close()
    pool.join()
    print u'----------------------'
    for i in  mhdataformat:
        print i
    # mhSecondDel = filter(lambda t: t is not None and t[2] not in existAuctionId, mhdataformat)
    # if len(mhSecondDel) is 0:
    #     return 0
    # sql = "INSERT INTO PRODUCT_DATA (AUCTION_ID,SOURCE,PRODUCT_URL,IS_MALL,TITLE,SELLER_ID,ACTIVITY_ID,ORIGINAL_PRICE,DISCOUNT_PRICE,QUAN_VALUE,QUAN_URL,QUAN_USED,QUAN_REST,QUAN_TOTAL,QUAN_DEADTIME,IS_WB)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # conn = connDB()
    # cur = conn.cursor()
    # cur.executemany(sql,mhSecondDel)
    # conn.commit()
    # conn.close()
    # return len(mhSecondDel)







