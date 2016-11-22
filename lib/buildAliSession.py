# coding=utf-8
from lib.baselib import *
from config import USER_AGENT,ROOTPATH
cookiefile = r'{}\tb_cookies.pkl'.format(ROOTPATH)
def setAliCookie():
    """
    "登录淘宝，更新cookie"
    :return:
    """
    browser = webdriver.Ie()
    browser.set_window_size(400, 400)
    browser.set_window_position(600, 200)
    wb_login_url = 'https://login.taobao.com/member/login.jhtml?style=minisimple&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&c_isScure=true&quicklogin=true'
    browser.get(wb_login_url)
    if browser.find_element_by_class_name('userlist').is_displayed():
        # WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME,'userlist')))
        # # # 保存cookie到文件
        browser.find_element_by_id('J_SubmitQuick').click()
    WebDriverWait(browser, 100).until(EC.title_contains(u'阿里妈妈'))
    logger.info(u'阿里妈妈cookie已更新')
    cPickle.dump(browser.get_cookies(), open(cookiefile, "wb"))
    browser.close()
    browser.quit()

def buildAliSession():
    """
    登录淘宝
    :return:
    """
    headers = {
        'User-Agent': USER_AGENT,
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache'
    }
    session = requests.session()
    session.headers.update(headers)
    if not os.path.isfile(cookiefile):
        setAliCookie()
    cookies = cPickle.load(open(cookiefile, "rb"))
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    islogin = robustHttpConn('http://pub.alimama.com/myunion.htm', session=session, allow_redirects=False)
    if islogin.status_code == 302:
        logger.info(u'阿里妈妈cookie失效，重新登录')
        setAliCookie()
        cookies = cPickle.load(open(cookiefile, "rb"))
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
    elif islogin.status_code == 200:
        logger.info(u'阿里妈妈cookie有效')
    return session