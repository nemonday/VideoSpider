import os
import time
from random import choice
from pyvirtualdisplay import Display

import pymysql
import requests
from selenium import webdriver

from settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE, \
    User_Agent_list
from tool import download, download_img, oss_upload, submit_ranscoding, deep_img_video, deeimg


class XgDownload(object):
    def __init__(self):
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.opt.add_argument('--disable-dev-shm-usage')
        self.opt.add_argument('--no-sandbox')
        display = Display(visible=0, size=(800, 600))
        display.start()
        # self.proxy = requests.get('http://http.tiqu.alicdns.com/getip3?num=1&type=1&pro=0&city=0&yys=0&port=1&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=')
        # self.opt.add_argument('--proxy-server=http://{}'.format(self.proxy.text))
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
        sql = 'select url, osskey, id, img , video_type, title, video_from, width, height from tb_spider_video where status=1 and video_from="西瓜视频"  limit 30'
        cursor.execute(sql)
        for video in cursor.fetchall():
            urls.append([video[0], video[1], video[2], video[3], video[4], video[5], video[6], video[7], video[8]])
        cursor.close()
        return urls

    def update_mysql(self, video_info, code_list):
        cursor = self.connection.cursor()
        try:
            sql = 'UPDATE tb_spider_video SET status=2, job_id="%s" WHERE id="%s"' % (code_list, video_info[2])
            print('上传成功，修改状态')
            cursor.execute(sql)
            self.connection.commit()
        except Exception as f:
            print(f)
            self.connection.rollback()
        cursor.close()

    def run(self):
        # try:
        video_infos = self.get_info()
        if video_infos:
            for video_info in video_infos:
                self.broser.get(video_info[0])
                time.sleep(10)
                try:
                    url = self.broser.find_element_by_xpath('//video').get_attribute("src")
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

                filename = download(video_info[1], url, True)
                img_dowonload_info = download_img(video_info[3], video_info[1])
                # video_size = deeimg(video_info[3])
                # video_size_img = video_size[2]
                #
                # # 横屏视频执行：
                # if video_size[0] > video_size[1]:
                #     # 定义遮挡水印的新文件名字
                #     deeimg_filename = video_info[1] + '.mp4'
                #     # 遮挡水印
                #     deep_img_video(video_size[0], video_size[1], 20, 200, 50, 204, filename, deeimg_filename)
                #
                #     os.rename(deeimg_filename, video_info[1])
                #     oss_upload(video_info[1], video_info[1], img_dowonload_info)
                #     code_list = submit_ranscoding(video_info[1])
                #     if code_list[0] is True:
                #         if os.path.exists(filename):
                #             os.remove(filename)
                #         self.update_mysql(video_info, code_list[1])
                #
                # elif video_size[0] < video_size[1]:
                os.rename(filename, video_info[1])
                oss_upload(video_info[1], video_info[1], img_dowonload_info)
                code_list = submit_ranscoding(video_info[1])
                #     if code_list[0] is True:
                #         if os.path.exists(filename):
                #             os.remove(filename)
                self.update_mysql(video_info, code_list[1])

                # if os.path.exists(img_dowonload_info):
                #     os.remove(img_dowonload_info)
                #
                # if os.path.exists(filename):
                #     os.remove(filename)
                #
                # if os.path.exists(video_size_img):
                #     os.remove(video_size_img)

                if os.path.exists(video_info[1]):
                    os.remove(video_info[1])

            self.broser.quit()

        # except Exception as f:
        #     print(f)
        #     cursor = self.connection.cursor()
        #     try:
        #         sql = "DELETE FROM tb_spider_video WHERE id = '%s' and osskey = '%s'" % (
        #             video_info[2], video_info[1])
        #         cursor.execute(sql)
        #         self.connection.commit()
        #     except:
        #         self.connection.rollback()
        #     cursor.close()
        #     self.broser.quit()


if __name__ == '__main__':
    obj = XgDownload()
    obj.run()










