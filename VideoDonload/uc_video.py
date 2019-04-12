import os
import re
import time
from random import choice

import pymysql
import requests
from selenium import webdriver
from settings import User_Agent_list, MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE
from tool import download, download_img, deeimg, deep_img_video, oss_upload


class UcDownload(object):
    def __init__(self):
        self.opt = webdriver.ChromeOptions()
        self.proxy = requests.get('http://http.tiqu.alicdns.com/getip3?num=1&type=1&pro=0&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=110000,320000,350000,440000,500000')
        # self.proxy = requests.get('http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=7&fa=20&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson=')
        self.opt.add_argument('--proxy-server=http://{}'.format(self.proxy.text))
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.opt.add_experimental_option("prefs", self.prefs)
        # self.opt.set_headless()

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
        sql = 'select url, osskey, id, img , video_type, title, video_from, width, height from tb_spider_video where status=1 and video_from= "UC浏览器" limit 30'
        cursor.execute(sql)
        for video in cursor.fetchall():
            urls.append([video[0], video[1], video[2], video[3], video[4], video[5], video[6], video[7], video[8]])

        cursor.close()
        return urls

    def update_mysql(self, video_info):

        cursor = self.connection.cursor()
        video_url = 'https://jiuban-image.oss-cn-hangzhou.aliyuncs.com/video_spider/video/'
        img_url = 'https://jiuban-image.oss-cn-hangzhou.aliyuncs.com/video_spider/img/'

        try:
            sql = 'UPDATE tb_spider_video SET status=3, video_oss_url= "%s", img_oss_url="%s" WHERE id="%s"' % (
                video_url + video_info[1] + '.mp4', img_url + video_info[1]+ '.png', video_info[2]
            )

            # sql2 = 'UPDATE tb_spider_video SET status=4" WHERE video_type="%s"' % ('佳品')
            print("""
                上传成功，修改状态,
                video地址: {}
                img地址: {}
            """.format(video_url + video_info[1] + '.mp4', img_url + video_info[1]+ '.png')
                  )

            cursor.execute(sql)
            self.connection.commit()
        except Exception as f:
            print(f)
            self.connection.rollback()

        cursor.close()

    def run(self):
        try:
            video_infos = self.get_info()
            if video_infos:
                for video_info in video_infos:
                    self.broser.get(video_info[0])
                    time.sleep(5)
                    url = self.broser.find_element_by_xpath('//video').get_attribute("src")
                    filename = download(video_info[1], url, False)
                    img_dowonload_info = download_img(video_info[3], video_info[1])
                    if filename and img_dowonload_info:
                        oss_upload(video_info[1], filename, img_dowonload_info)

                        if os.path.exists(filename):
                            os.remove(filename)

                        if os.path.exists(img_dowonload_info):
                            os.remove(img_dowonload_info)

                        self.update_mysql(video_info)

                self.broser.quit()

            else:
                pass


        except Exception as f:
            print(f)
            cursor = self.connection.cursor()
            try:
                sql = "DELETE FROM tb_spider_video WHERE id = '%s' and osskey = '%s'" % (
                    video_info[2], video_info[1])
                cursor.execute(sql)
                self.connection.commit()
            except:
                self.connection.rollback()
            cursor.close()
            self.broser.quit()
            self.run()

if __name__ == '__main__':
    while True:
        obj = UcDownload()
        obj.run()
        time.sleep(600)











