import json
import os
import time
from contextlib import closing
from random import choice
import requests
import pymysql
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui

from Model import Work
from settings import User_Agent_list


class VideoDownload(object):
    def __init__(self):
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }
        self.opt = webdriver.ChromeOptions()
        # self.opt.add_argument("--proxy-server={}".format(proxies['https']))
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.opt.add_argument('--disable-dev-shm-usage')
        self.opt.add_argument('--no-sandbox')
        # self.opt.add_argument('--headless')
        # display = Display(visible=0, size=(800, 600))
        # display.start()
        # proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=440000&city=440100&yys=100017&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        # proxy = requests.get(proxy_url)
        # proxy = json.loads(proxy.text)['data'][0]
        # self.proxies = {
        #     'https': 'http://{0}:{1}'.format(proxy['ip'], proxy['port'])
        # }
        # self.opt.add_argument("--proxy-server={}".format(self.proxies['https']))

        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.opt.add_experimental_option("prefs", self.prefs)

        self.broser = webdriver.Chrome(options=self.opt)
        # 数据库位置
        self.engine = create_engine("mysql+pymysql://root:pythonman@127.0.0.1/UC?charset=utf8")

        # 创建会话
        self.session = sessionmaker(self.engine)
        self.mySession = self.session()

    def is_visible(self, locator, timeout=10):
        try:
            ui.WebDriverWait(self.broser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except Exception as f:
            return False

    def download(self, filename, download_url, end):
        # 传入filename, 下载地址
        # 视频下载
        with closing(requests.get(download_url, stream=True)) as r:
            chunk_size = 1024
            content_size = int(r.headers['content-length'])

            with open(filename + end, "wb") as f:
                n = 1
                for chunk in r.iter_content(chunk_size=chunk_size):
                    loaded = n * 1024.0 / content_size
                    f.write(chunk)
                    num = '\r下载视频: {} ,{}% '.format(filename, int(loaded) * 100)
                    print(num, end='')
                    n += 1

    def run(self):
        try:
            result = self.mySession.query(Work).filter_by(status=0).all()
            for video in result:
                url = video.url
                thumbnails= video.thumbnails
                title = video.title
                url_md5 = video.url_md5
                self.broser.get(url)
                is_visible = self.is_visible('//video')
                if is_visible is True:
                    url = self.broser.find_element_by_xpath('//video').get_attribute("src")
                    dir_name = '/Users/nemo/PycharmProjects/VideoSpider/VideoSpider/{}'.format('视频')
                    # 新建作者文件夹
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)

                    download_name = dir_name + '/{}'.format(title)
                    self.download(download_name, url, '.mp4')
                    # self.download(title, thumbnails, '.jpg')

                    self.mySession.query(Work).filter(Work.url_md5 == url_md5).update({"status": "1"})
                    self.mySession.commit()

            self.broser.quit()
        except Exception as f:
            print(f)
            self.broser.quit()


if __name__ == '__main__':
    obj = VideoDownload()
    obj.run()











