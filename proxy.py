# coding=utf-8
from lib.baselib import *
from multiprocessing import Pool as ThreadPool
from bs4 import BeautifulSoup,SoupStrainer
import glob,json

def proxyTest(proxy):
    t1 = time.time()
    try:
        r= requests.get('http://baidu.com',proxies = {'http':proxy},timeout = 5)
        timeusd = time.time()-t1
        if r.status_code == 200 and timeusd < 1:
            print '{} 有效 timeused：{}'.format(proxy,timeusd)
            return proxy
    except Exception:
       pass
def saveProxyFile():
    proxyurl ='http://api.xicidaili.com/free2016.txt'
    proxyget = requests.get(proxyurl)
    iplist= strCompile(proxyget.content,'\d+\.\d+\.\d+\.\d+\:\d+',all = 1)
    pool = ThreadPool(8)
    proxylist = pool.map(proxyTest,iplist)
    pool.close()
    pool.join()
    proxylist =  filter(lambda i: i is not None,proxylist)
    proxyfilename = 'proxylist_{}.txt'.format(time.time())
    with open(proxyfilename, 'wb') as f:
        f.write('\r\n'.join(proxylist))
    return proxyfilename
def saveProxyFile2():
    listpage = robustHttpConn('http://www.youdaili.net/Daili/guonei/')
    ptag = SoupStrainer(class_ = 'chunlist')
    psoup = BeautifulSoup(listpage.content, 'lxml', parse_only = ptag, from_encoding = 'utf-8')
    lasturl = psoup.find('a')['href']
    lastpage = robustHttpConn(lasturl)
    lastnum = strCompile(lasturl,'(\d+)')
    contenttag = SoupStrainer(class_ = 'content')
    breaktag = SoupStrainer(class_ = 'pagebreak')
    contentsoup = BeautifulSoup(lastpage.content,'lxml',parse_only = contenttag,from_encoding = 'utf-8')
    content = [strCompile(i,'\d+\.\d+\.\d+\.\d+\:\d+') for i in contentsoup.stripped_strings]
    breaksoup = BeautifulSoup(lastpage.content,'lxml',parse_only = breaktag,from_encoding = 'utf-8')
    breaklengh = int(strCompile(breaksoup.find('a').get_text(),'\d+'))
    lasturllist = ['http://www.youdaili.net/Daili/guonei/{}_{}.html'.format(lastnum,i) for i in xrange(2,breaklengh+1)]
    pool1 = ThreadPool(breaklengh-1)
    [[content.append(strCompile(m,'\d+\.\d+\.\d+\.\d+\:\d+')) for m in BeautifulSoup(i.content,'lxml',parse_only = contenttag,from_encoding = 'utf-8').stripped_strings] for i in pool1.map(robustHttpConn,lasturllist)]
    pool1.close()
    pool1.join()

    pool = ThreadPool(8)
    proxylist = pool.map(proxyTest,content)
    pool.close()
    pool.join()
    proxylist =  filter(lambda i: i is not None,proxylist)
    with open('proxylist.json', 'wb') as f:
        f.write(json.dumps({
            'url':lasturl,
            'proxylist':proxylist
        }))
def loadProxy():
    proxyfile = []
    while 1:
        proxyfile = glob.glob(r'proxylist_*.txt')
        if proxyfile is not []:
            break
        time.sleep(1)
    proxyfilename = proxyfile[0]
    with open(proxyfilename,'rb') as f:
        iplist = strCompile(f.read(),'\d+\.\d+\.\d+\.\d+\:\d+',all = 1)
    return [{'http':i} for i in iplist]


def refreshProxy():
    proxyfile = glob.glob(r'proxylist_*.txt')
    proxyfilename = saveProxyFile() if proxyfile == [] else proxyfile[0]
    while 1:
        filesavetime = int(strCompile(proxyfilename,'(\d+)')) if proxyfilename else 0
        timeindex = time.time() - filesavetime
        if timeindex > 900:
            oldproxyname = proxyfilename
            proxyfilename = saveProxyFile()
            os.remove(oldproxyname)
        time.sleep(900-timeindex)

if __name__ == '__main__':
    global usdlist
    usdlist = []
    proxylist = loadProxy()
    listlen = len(proxylist)
    for i in xrange(50):
        if len(usdlist) == listlen:
            proxylist, usdlist = usdlist[::-1], []
        proxy = proxylist.pop()
        usdlist.append(proxy)
        print i
        print proxy
        print usdlist
        print proxylist

