# coding=utf-8
import sys
import MySQLdb
from logger import logger
from config import DBUSER,DBPASSWD

PRODUCT_DATA_SQL = """CREATE TABLE PRODUCT_DATA (
                  ID INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                  AUCTION_ID BIGINT(13) UNSIGNED UNIQUE DEFAULT 0 COMMENT '商品id',
                  SOURCE TINYINT(2) UNSIGNED DEFAULT 0 COMMENT '来源 默认0，1：阿里后台，2：喵惠',
                  PRODUCT_URL VARCHAR(50) DEFAULT '' COMMENT '产品链接',
                  IS_MALL TINYINT(1) UNSIGNED DEFAULT 0 COMMENT '是否天猫 天猫：1 淘宝：2',
                  TITLE VARCHAR(100) DEFAULT '' COMMENT '标题',
                  PIC_URL VARCHAR(100) DEFAULT '' COMMENT '图片链接',
                  MONTH_SELL INT UNSIGNED DEFAULT 0 COMMENT '月销量',
                  SELLER_ID BIGINT(11) UNSIGNED DEFAULT 0 COMMENT '商家id',
                  ACTIVITY_ID CHAR(35) DEFAULT '' COMMENT '优惠券id',
                  ORIGINAL_PRICE DECIMAL(5,2) UNSIGNED DEFAULT 0.00 COMMENT '原价',
                  DISCOUNT_PRICE DECIMAL(5,2) UNSIGNED DEFAULT 0.00 COMMENT '折扣价',
                  QUAN_VALUE DECIMAL(5,2) UNSIGNED DEFAULT 0.00 COMMENT '优惠券面值',
                  QUAN_STR VARCHAR(10) DEFAULT '' COMMENT '优惠券介绍',
                  QUAN_URL CHAR(110) DEFAULT '' COMMENT '券手机端链接',
                  QUAN_ADPURL CHAR(115) DEFAULT '' COMMENT '券自适应链接',
                  QUAN_USED INT(6) UNSIGNED DEFAULT 0 COMMENT '券已领量',
                  QUAN_REST INT(6) UNSIGNED DEFAULT 0 COMMENT '券剩余量',
                  QUAN_TOTAL INT(6) UNSIGNED DEFAULT 0 COMMENT '券总量',
                  QUAN_DEADTIME INT(10) UNSIGNED DEFAULT 0 COMMENT '券过期时间戳',
                  IS_WB TINYINT(1) UNSIGNED DEFAULT 0 COMMENT '是否发送微博',
                  TAG VARCHAR(60) DEFAULT '' COMMENT '标签',
                  ALITYPE TINYINT(1) UNSIGNED DEFAULT 0 COMMENT '选择链接：通用and鹊桥：1，定向：3',
                  DX_RATE DECIMAL(5,2) UNSIGNED DEFAULT 0.00 COMMENT '定向计划Rate',
                  DX_ID INT UNSIGNED DEFAULT 0 COMMENT '定向计划id',
                  COMM_RATE DECIMAL(5,2) UNSIGNED DEFAULT 0.00 COMMENT '通用或鹊桥Rate',
                  COMM_SCLICK VARCHAR(280) DEFAULT '' COMMENT '网站端通用淘宝客链接',
                  COMM_COMP_URL VARCHAR(280) DEFAULT '' COMMENT '网站端通用二合一链接',
                  IS_SELECT TINYINT(1) UNSIGNED DEFAULT 0 COMMENT '是否添加到选品库中 已添加 1 未添加 0'
                  );
"""
DATA_SAVE_STATUS_SQL = """CREATE TABLE DATA_SAVE_STATUS(
                  XLS_SAVED_DATE CHAR(10) DEFAULT '' COMMENT '保存xls日期' PRIMARY KEY
);
"""
WEIBO_CHANNEL_SQL = """CREATE TABLE WEIBO_CHANNEL(
                  ID INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                  AUCTION_ID BIGINT(13) UNSIGNED COMMENT '商品id',
                  UNI_URL CHAR(150) COMMENT '二合一链接',
                  UNI_KOULIN CHAR(12) COMMENT '二合一口令',
                  WEIBO_URL CHAR(35) COMMENT '微博淘链接',
                  WEIBO_KOULIN CHAR(35) COMMENT '微博淘口令'
                  );
"""
WEIBO_UPED_SQL = """CREATE TABLE WEIBO_UPED(
                  ID INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                  AUCTION_ID BIGINT(13) UNSIGNED COMMENT '商品id',
                  ACTIVITY_ID CHAR(35) COMMENT '优惠券id'
                  );
"""
def connDB():
    return MySQLdb.connect(host = 'localhost', user = DBUSER ,passwd = DBPASSWD , db = 'ALI_DB',port = 3306,charset = 'utf8')

def resetDB(confirm = 0):
    """
    初始化数据库
    :return:
    """
    if confirm is 0:
        pass
    elif confirm is 1:
        while 1:
            resetconfirm = raw_input(u'press "y" to reset database else press "n" to cansel:')
            if resetconfirm  in ['y','Y']:
                break
            elif resetconfirm in ['n','N']:
                print(u'resetting canseled')
                return None
            else:
                print(u'worong input')
    conn = MySQLdb.connect(host = "localhost", user = DBUSER, passwd = DBPASSWD , charset = 'utf8')
    cur = conn.cursor()
    try:
        cur.execute("""CREATE DATABASE IF NOT EXISTS ALI_DB;""")
        conn.commit()
        cur.execute("""USE ALI_DB;""")
        conn.commit()
        cur.execute("""DROP TABLE IF EXISTS PRODUCT_DATA,DATA_SAVE_STATUS,WEIBO_CHANNEL, WEIBO_UPED;""")
        conn.commit()
        cur.execute(PRODUCT_DATA_SQL)
        conn.commit()
        cur.execute(DATA_SAVE_STATUS_SQL)
        conn.commit()
        cur.execute(WEIBO_CHANNEL_SQL)
        conn.commit()
        cur.execute(WEIBO_UPED_SQL)
        conn.commit()
        logger.info(u'ali_db reset successful')
    except MySQLdb.Error as e:
        logger.error(e)
        conn.rollback()
    conn.close()

    if confirm is 1:
        print(u'ali_db reset successful')

def resetTABLES(table):
    conn = connDB()
    cur = conn.cursor()
    try:
        if table in ['PRODUCT_DATA','product_data']:
            cur.execute("""DROP TABLE IF EXISTS PRODUCT_DATA""")
            conn.commit()
            cur.execute(PRODUCT_DATA_SQL)
            conn.commit()
        elif table in ['WEIBO_CHANNEL','weibo_channel']:
            cur.execute("""DROP TABLE IF EXISTS WEIBO_CHANNEL""")
            conn.commit()
            cur.execute(WEIBO_CHANNEL_SQL)
            conn.commit()
        elif table in ['WEIBO_UPED','weibo_uped']:
            cur.execute("""DROP TABLE IF EXISTS WEIBO_UPED""")
            conn.commit()
            cur.execute(WEIBO_UPED_SQL)
            conn.commit()
        elif table in ['DATA_SAVE_STATUS','data_save_status']:
            cur.execute("""DROP TABLE IF EXISTS DATA_SAVE_STATUS""")
            conn.commit()
            cur.execute(DATA_SAVE_STATUS_SQL)
            conn.commit()
        logger.info(u'{} reset successful'.format(table))
    except MySQLdb.Error as e:
        logger.error(e)
        conn.rollback()

    conn.close()

def getDataFromDB(sql,fetchall = True):
    conn = connDB()
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall() if fetchall is True else cur.fetchone()
    conn.close()
    return result

def existAID():
    return [i[0] for i in getDataFromDB('SELECT AUCTION_ID FROM PRODUCT_DATA')]

