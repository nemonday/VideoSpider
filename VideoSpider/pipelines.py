# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pprint import pprint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from VideoSpider.Model import Work
import hashlib


class VideospiderPipeline(object):
    def __init__(self):
        # 数据库位置
        self.engine = create_engine("mysql+pymysql://root:pythonman@127.0.0.1/UC?charset=utf8")

        # 创建会话
        self.session = sessionmaker(self.engine)
        self.mySession = self.session()

    def process_item(self, item, spider):
        if spider.name == 'uc':
            result = self.mySession.query(Work).filter_by(url_md5=item['url_md5']).first()
            if result is None:
                print('添加视频：{}'.format(item['title']))
                work = Work(url=item['url'], thumbnails=item['thumbnails'],
                            title=item['title'],url_md5=item['url_md5'],
                            video_height=item['video_height'], video_width=item['video_width'], status=0)

                self.mySession.add(work)
                self.mySession.commit()




