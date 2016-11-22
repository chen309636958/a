# coding=utf-8
from lib.baselib import *
from PIL import Image
from cStringIO import StringIO
from config import WUSERNAME,WPASSWD,USER_AGENT,VERIFY_CODE_PATH,ROOTPATH
cookiefile = r'{}\wb_cookies.pkl'.format(ROOTPATH)
def setWeiBoCookie():
    headers = {
        'User-Agent': USER_AGENT,
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
    }
    for key, value in enumerate(headers):
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

    loginurl = 'http://account.weibo.com/set/bindsns/unicomoauth'
    driver = webdriver.PhantomJS()
    driver.set_window_size(400,400)
    driver.set_window_position(0,0)
    driver.get(loginurl)
    # print(driver.page_source)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'landingDiv')))
    nameinput = driver.find_element_by_id('txtWoID')
    passwordinput = driver.find_element_by_id('txtPassword')
    sbtn = driver.find_element_by_id('btConsent')
    nameinput.send_keys(WUSERNAME)
    passwordinput.send_keys(WPASSWD)
    verify = driver.find_element_by_id('verifyCode')
    # driver.save_screenshot(u'../ichen/2.jpg')
    if verify.is_displayed():
        woverifycode = ''
        verifyimg = driver.find_element_by_id('valueCode')
        left = verifyimg.location['x']+30
        top = verifyimg.location['y']
        right = left + 80
        bottom = top + 32
        # right = left + verifyimg.size['width']
        # bottom = top + verifyimg.size['height']
        imgdata = StringIO(driver.get_screenshot_as_png())
        img = Image.open(imgdata)
        img = img.crop((left, top, right, bottom))
        img.save(VERIFY_CODE_PATH, quality=20)
        while 1:
            woverifycode = raw_input(u'input verify code:')
            if len(woverifycode) != 4 and woverifycode != 'r':
                print(u'reinput verify code：')
            elif woverifycode == u'r':
                driver.refresh()
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'landingDiv')))
                print(u'reget')
                imgdata = StringIO(driver.get_screenshot_as_png())
                img = Image.open(imgdata)
                img = img.crop((left, top, right, bottom))
                img.save(VERIFY_CODE_PATH, quality=20)
            else:
                print(u'your input verify code:{}'.format(woverifycode))
                break
        verify.send_keys(woverifycode)
    sbtn.click()
    time.sleep(3)
    cPickle.dump(driver.get_cookies(), open(cookiefile, "wb"))
    print(u'Set Weibo cookie done')
    driver.close()
    driver.quit()
def buildWeiBoSession():
    """
    登录weibo
    :return:
    """
    headers = {
        'User-Agent': USER_AGENT,
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
    }
    mwbheader = {
        'Host': 'm.weibo.cn',
        'Origin': 'http://m.weibo.cn',
        'Referer': 'http://m.weibo.cn/mblog',
    }
    session = requests.session()
    session.headers.update(headers)
    if not os.path.isfile(cookiefile):
        setWeiBoCookie()
    cookies = cPickle.load(open(cookiefile, "rb"))
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    islogin = robustHttpConn('http://m.weibo.cn',headers=mwbheader,session=session, allow_redirects=False)
    if islogin.status_code == 302:
        print(u'微博cookie失效')
        setWeiBoCookie()
        cookies = cPickle.load(open(cookiefile, "rb"))
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
    elif islogin.status_code == 200:
        print(u'微博cookie有效')
    return session