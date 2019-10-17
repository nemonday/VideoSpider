import json
import time
import requests
from selenium import webdriver



def adfly():
    opt = webdriver.FirefoxOptions()
    proxy_url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=0&city=0&yys=100017&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    proxy = requests.get(proxy_url)
    proxy = json.loads(proxy.text)['data'][0]
    proxies = {
        'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
    }
    print(proxies['https'])
    opt.add_argument("--proxy-server={}".format(proxies['https']))
    # opt.add_argument('--headless')

    broser = webdriver.Firefox(options=opt)
    url = 'http://gestyy.com/w5rSGn'
    # url = 'http://clkmein.com/w5rSGn#.Xafziw0DQbs.twitter'
    broser.get(url)
    broser.delete_all_cookies()

    time.sleep(10)
    broser.find_element_by_xpath('//*[@id="skip_button"]').click()

    broser.quit()


if __name__ == '__main__':
    adfly()