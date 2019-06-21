# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql

from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import *
from VideoSpider.spiders.uc import UcSpider

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

    def insert_mysql(self, item):
        cursor = self.connection.cursor()
        try:
            sql = "INSERT INTO tb_spider_video(vid, video_from, play_volume, comment_volume, title, osskey, url, share_volume, like_volume, video_type) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                  (item['id'], item['from'], item['view_cnt'], item['cmt_cnt'], item['title'], item['osskey'], item['url'], item['sha_cnt'], item['like_cnt'], item['old_type'])

            cursor.execute(sql)
            self.connection.commit()
            Print.info('添加id {} 到数据库'.format(item['id']))
        except Exception as f:
            print('添加错误')
            print(f)
            self.connection.rollback()

        cursor.close()

    def process_item(self, item, spider):
        if spider.name == UcSpider.name:
            self.insert_mysql(item)


