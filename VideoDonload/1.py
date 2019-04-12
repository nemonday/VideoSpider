from random import choice

import requests
from selenium import webdriver

from VideoDonload.settings import User_Agent_list


class XgDownload(object):
    def __init__(self):
        self.opt = webdriver.ChromeOptions()
        # self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        # self.proxy = requests.get('http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=7&fa=20&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson=')
        # self.opt.add_argument('--proxy-server=http://{}'.format(self.proxy.text))
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.opt.add_experimental_option("prefs", self.prefs)
        # self.opt.set_headless
        # self.opt.add_argument('--proxy-server=http://{}'.format(requests.get(proxy_url).text))
        self.broser = webdriver.Chrome(options=self.opt)

    def run(self):
        self.broser.get('https://miku.tools/tools/toutiao_video_downloader')


if __name__ == '__main__':
    ob = XgDownload()
    ob.run()