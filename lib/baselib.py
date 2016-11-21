# coding=utf-8
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib,re,time,requests,sys,cPickle,os
from requests.exceptions import ConnectionError, ReadTimeout
sys.path.append("..")
from config import QUANLIMIT,USER_AGENT
from logger import logger
import warnings

def robustHttpConn(url, **kwargs):
    """
    "包含处理服务器连接错误的get函数"
    :param url:
    :param kwargs:
    :return:
    """
    stream = kwargs['stream'] if 'stream' in kwargs else False
    session = kwargs['session'] if 'session' in kwargs else None
    method = kwargs['method'] if 'method' in kwargs else 'get'
    data = kwargs['data'] if 'data' in kwargs else None
    headers = kwargs['headers'] if 'headers' in kwargs else {'User-Agent':USER_AGENT}
    verify = kwargs['verify'] if 'verify' in kwargs else False
    timeout = kwargs['timeout'] if 'timeout' in kwargs else 15
    allow_redirects = kwargs['allow_redirects'] if 'allow_redirects' in kwargs else True
    addcookies = kwargs['cookies'] if 'cookies' in kwargs else None
    getjosn = kwargs['getjson'] if 'getjson' in kwargs else 0
    sleeptime = kwargs['sleeptime'] if 'sleeptime' in kwargs else 1
    proxies = kwargs['proxies'] if 'proxies' in kwargs else None
    retryTimes = 1
    r = None
    time.sleep(sleeptime)
    while 1:
        try:
            if session is not None and method in ['get','GET','Get']:
                r = session.get(url, headers=headers, verify=verify, timeout=timeout,allow_redirects=allow_redirects,
                                data=data, cookies=addcookies,stream = stream)
            elif session is not None and method in ['post','POST','Post']:
                r = session.post(url, headers=headers, verify=verify, timeout=timeout,allow_redirects=allow_redirects,
                                 data=data, cookies=addcookies,stream = stream)
            elif session is not None and method in ['put','PUT','Put']:
                r = session.put(url, headers=headers, verify=verify, timeout=timeout,allow_redirects=allow_redirects,
                                 data=data, cookies=addcookies,stream = stream)
            elif session is not None and method in ['delete','DELETE','Delete']:
                r = session.delete(url, headers=headers, verify=verify, timeout=timeout,allow_redirects=allow_redirects,
                                 data=data, cookies=addcookies,stream = stream)
            elif session is not None and method in ['patch','PATCH','Patch']:
                r = session.patch(url, headers=headers, verify=verify, timeout=timeout,allow_redirects=allow_redirects,
                                 data=data, cookies=addcookies,stream = stream)
            elif session is None and method in ['get','GET','Get']:
                r = requests.get(url, headers=headers, verify=verify, timeout=timeout, allow_redirects=allow_redirects,
                                 data=data, cookies=addcookies, stream = stream, proxies = proxies)
            elif session is None and method in ['post','POST','Post']:
                r = requests.post(url, headers=headers, verify=verify, timeout=timeout, allow_redirects=allow_redirects,
                                  data=data, cookies=addcookies, stream = stream, proxies = proxies)
            elif session is None and method in ['put','PUT','Put']:
                r = requests.put(url, headers=headers, verify=verify, timeout=timeout, allow_redirects=allow_redirects,
                                 data=data, cookies=addcookies, stream = stream, proxies = proxies)
            elif session is None and method in ['delete','DELETE','Delete']:
                r = requests.delete(url, headers=headers, verify=verify, timeout=timeout, allow_redirects=allow_redirects,
                                    data=data, cookies=addcookies, stream = stream, proxies = proxies)
            elif session is None and method in ['patch','PATCH','Patch']:
                r = requests.patch(url, headers=headers, verify=verify, timeout=timeout, allow_redirects=allow_redirects,
                                   data=data, cookies=addcookies, stream = stream, proxies = proxies)
            if getjosn == 1:
                return r.json()
            else:
                return r
        except (ConnectionError, ReadTimeout)as e:
            time.sleep(10)
            logger.error(e)
            print e
            retryTimes += 1
            if retryTimes == 10:
                logger.log( u'退出程序:{}'.format(e))
                sys.exit()
        except ValueError as e:
            time.sleep(120)
            logger.error(e)
            retryTimes += 1
            if retryTimes == 10:
                logger.error(r.content)
                return None
def getRealAliUrl(url):
    """
    获取真实链接及商品id
    :param url:
    :return:
    """
    if url.find('s.click') != -1:
        if url.find('t?e='):
            surl = url
        else:
            r = robustHttpConn(url, allow_redirects=False)
            surl = r.headers['location']
        _refer = robustHttpConn(surl).url
        rheaders = {'Referer': _refer}
        url = robustHttpConn(urllib.unquote(_refer.split('tu=')[1]), headers=rheaders).url.split('&ali_trackid=')[0]
    return url

# return [i[0] for i in cur.fetchall()]

def strCompile(str, parm, all = 0):
    pattern = re.compile(parm,re.S)
    strcomp = pattern.findall(str)
    if len(strcomp) == 0:
        return None
    else:
        if all == 0:
            return  strcomp[0]
        elif all == 1:
            return strcomp
def quanCheck(quanUrl,get = 1):
    """
    Args:
        quanUrl:
        limit:
    Returns:
        None 券无效或数量小于limit
    """
    if quanUrl is None:return None
    getquanInfo = robustHttpConn(quanUrl).content
    quanSeller = strCompile(getquanInfo,'<title>(.*)</title>').decode('utf-8')
    if '不存在或者已经过期' in getquanInfo:
        logger.log(u'{}:券不存在或已过期'.format(quanSeller))
        return 0
    quanPattern = '<dt>(\d+)元优惠券</dt>.*class="rest".*?>(\d+)</span>.*<span.*?class="count".*?>(\d+)</span>.*?</dd>.*<dd>.*至(\d{4}-\d{2}-\d{2})</dd>'
    quanInfo = strCompile(getquanInfo, quanPattern)
    quanRest = int(quanInfo[1])
    if quanRest < QUANLIMIT:
        logger.log(u'{}:券数量小于{}'.format(quanSeller,QUANLIMIT))
        return 0
    else:
        if get is 1:
            quanUsed = int(quanInfo[2])
            return {
                'quanRest':quanRest,
                'quanValue':float(quanInfo[0]),
                'quanUsed':quanUsed,
                'quanTotal':quanRest + quanUsed,
                'quanDeadTime':int(time.mktime(time.strptime(quanInfo[3] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')))
            }
        elif get is 0:
            return 1

def checkFile(file):
    return os.path.isfile(file)

def DateFloattoStr(t = time.time(),dateonly = 1):
    """
    输入时间戳 转换为 格式化字符串
    :param t:
    :param dateonly:
    :return:
    """
    t = t if isinstance(t, float) else float(t)
    if dateonly == 1:
        return time.strftime('%Y-%m-%d',time.localtime(t))
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t))
def DateStrtoFloat(*args):
    """
    :param args: 输入格式化字符串 转换为 时间戳
    :return:
    """
    datestr = args[0] if args else time.strftime('%Y-%m-%d',time.localtime())
    return time.mktime(time.strptime(datestr,'%Y-%m-%d'))

def timer(func):
    def _d(*arg, **karg):
        timestart = time.time()
        r= func(*arg, **karg)
        print time.time() - timestart
        return r
    return _d