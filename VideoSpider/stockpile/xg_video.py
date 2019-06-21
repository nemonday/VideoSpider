import json
import os
import time
from random import choice

import requests
from pyvirtualdisplay import Display
import pymysql
from selenium import webdriver

from VideoSpider.API.iduoliaotool import IduoliaoTool, Print
from VideoSpider.settings import User_Agent_list, MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.ui as ui

class XgDownload(object):
    def __init__(self):
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.opt.add_argument('--disable-dev-shm-usage')
        self.opt.add_argument('--no-sandbox')
        # display = Display(visible=0, size=(800, 600))
        # display.start()
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=440000&city=440100&yys=100017&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        self.proxies = {
            'https': 'http://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }
        self.opt.add_argument("--proxy-server={}".format(self.proxies['https']))

        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.opt.add_experimental_option("prefs", self.prefs)
        # self.opt.set_headless

        self.broser = webdriver.Chrome(options=self.opt)
        self.connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

    def get_info(self):
        urls = []
        cursor = self.connection.cursor()
        sql = 'select id, url, title, video_from, video_type, download_status from tb_spider_video where download_status=0 and video_from="UC浏览器" limit 30'
        cursor.execute(sql)
        for video in cursor.fetchall():
            urls.append([video[0], video[1], video[2], video[3], video[4]])

        cursor.close()
        return urls

    def update_mysql(self, id):

        cursor = self.connection.cursor()
        try:
            sql = 'UPDATE tb_spider_video SET download_status=1 WHERE id="%s"' % id
            Print.info('把id为 {} 的作品状态修改为1'.format(id))
            cursor.execute(sql)
            self.connection.commit()
        except Exception as f:
            print(f)
            self.connection.rollback()

        cursor.close()

    def is_visible(self, locator, timeout=10):
        try:
            ui.WebDriverWait(self.broser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except Exception as f:
            return False

    def run(self):
        try:
            infos = self.get_info()
            for info in infos:
                id = info[0]
                url = info[1]
                title = info[2]
                video_from = info[3]
                video_type = info[4]

                self.broser.get(url)
                is_visible = self.is_visible('//video')
                if is_visible is True:
                    url = self.broser.find_element_by_xpath('//video').get_attribute("src")
                    new_filename = IduoliaoTool.video_download(id, url, title, video_type, video_from, ifdewatermark=False)
                    if new_filename:
                        self.update_mysql(id)
                    print(url)
            self.broser.quit()

        except Exception as f:
            print(f)
            cursor = self.connection.cursor()
            try:
                sql = "DELETE FROM tb_spider_video WHERE id = '%s' " % id
                cursor.execute(sql)
                self.connection.commit()
            except:
                self.connection.rollback()
            cursor.close()
            self.broser.quit()


if __name__ == '__main__':
    obj = XgDownload()
    obj.run()











