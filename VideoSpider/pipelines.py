# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from VideoSpider.settings import *
from VideoSpider.stockpile.hk import HkSpider
from VideoSpider.spiders.ky import KySpider
from VideoSpider.stockpile.ppx import PpxSpider
from VideoSpider.spiders.td import TdSpider
from VideoSpider.spiders.uc import UcSpider
from VideoSpider.spiders.xg import XgSpider
from VideoSpider.spiders.xng import XngSpider
from VideoSpider.stockpile.xngzf import XngzfSpider

isotimeformat = '%Y-%m-%d'


class VideospiderPipeline(object):
    def __init__(self):
        self.connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

    def insert_mysql_downlad(self, item):

        # 提交转码作业
        code_list = submit_ranscoding(item['osskey'])
        # 如果显示提交成功（Ture） 把此条信息添加到数据库，等待定时任务确认转码是否成功
        if code_list[0] is True:
            cursor = self.connection.cursor()
            try:
                sql = "INSERT INTO tb_spider_video(vid, height, width, video_from, video_type, play_volume, " \
                      "comment_volume, title, spidertime, osskey, url, img, share_volume, like_volume, match_type, status, job_id, old_type) " \
                      "VALUES (%s, %s, %s, '%s', '%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                          item['id'], item['video_height'], item['video_width'], item['from'], item['category'],
                          item['view_cnt'], item['cmt_cnt'], item['title'], item['spider_time'], item['osskey'],
                          item['url'], item['thumbnails'], item['sha_cnt'], item['like_cnt'], item['match_type'], 2, code_list[1], item['old_type'])

                cursor.execute(sql)
                self.connection.commit()
                print('添加id {} 到数据库'.format(item['id']))
            except Exception as f:
                print('添加错误')
                print(f)
                self.connection.rollback()

            cursor.close()

    def insert_mysql_waitdownlad(self, item):
        cursor = self.connection.cursor()
        try:
            sql = "INSERT INTO tb_spider_video(vid, height, width, video_from, video_type, play_volume, " \
                  "comment_volume, title, spidertime, osskey, url, img, share_volume, like_volume, match_type, old_type) " \
                  "VALUES (%s, %s, %s, '%s', '%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                      item['id'], item['video_height'], item['video_width'], item['from'], item['category'],
                      item['view_cnt'], item['cmt_cnt'], item['title'], item['spider_time'], item['osskey'],
                      item['url'], item['thumbnails'], item['sha_cnt'], item['like_cnt'], item['match_type'], item['old_type'])

            cursor.execute(sql)
            self.connection.commit()
            print('添加id {} 到数据库'.format(item['id']))
        except Exception as f:
            print('添加错误')
            print(f)
            self.connection.rollback()

        cursor.close()

    def process_item(self, item, spider):
        if spider.name == HkSpider.name or spider.name == XngSpider.name or spider.name == XngzfSpider.name or spider.name == TdSpider.name or spider.name == PpxSpider.name :
            self.insert_mysql_downlad(item)

        elif spider.name == UcSpider.name or spider.name == XgSpider or KySpider.name:
            self.insert_mysql_waitdownlad(item)


