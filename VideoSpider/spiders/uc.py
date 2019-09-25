# -*- coding: utf-8 -*-
import hashlib
import json
import re
from copy import deepcopy
from pprint import pprint

import requests
import scrapy

from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Model import Work, Url
from settings import *


class UcSpider(scrapy.Spider):

    name = 'uc'

    def start_requests(self):
        engine = create_engine("mysql+pymysql://root:pythonman@127.0.0.1/UC?charset=utf8")
        # 创建会话
        session = sessionmaker(engine)
        mySession = session()

        item ={}
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }

        result = mySession.query(Url).filter_by(status=0).all()
        for video in result:
            url = video.url.replace('&xss_enc=31', '')
            id= video.id
            item['view_cnt_compare'] = 1
            item['cmt_cnt_compare'] = 1
            item['id'] = id
            yield scrapy.Request(url, headers=uc_headers,
                                 callback=self.parse, meta={
                                                            'proxy': ''.format(proxies['https']),
                                                            'item': deepcopy(item)}, dont_filter=True
                                 )

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

        try:
            # UC浏览器
            json_data = json.loads(response.text)
            ids = json_data['data']['items']
            ids = [id for id in ids if len(id['id']) == 20]

            video_datas = [{
                # 视频id
                'id': json_data['data']['articles'][id['id']]['id'],
                # 视频地址
                'url': json_data['data']['articles'][id['id']]['url'],
                # 视频标题
                'title': json_data['data']['articles'][id['id']]['title'],
                # 视频分类
                'category': json_data['data']['articles'][id['id']]['category'][0],
                # 原始分类
                'old_type': json_data['data']['articles'][id['id']]['category'][0],
                # 视频封面地址
                'thumbnails': json_data['data']['articles'][id['id']]['videos'][0]['poster']['url'],
                # 视频宽
                'video_width': json_data['data']['articles'][id['id']]['videos'][0]['video_width'],
                # 视频高
                'video_height': json_data['data']['articles'][id['id']]['videos'][0]['video_height'],
                # 播放量
                'view_cnt': json_data['data']['articles'][id['id']]['videos'][0]['view_cnt'],
                # 评论数
                'cmt_cnt': json_data['data']['articles'][id['id']]['cmt_cnt'],
                'from': 'UC浏览器',
                'spider_time': time.strftime(isotimeformat, time.localtime(time.time())),
            }
                for id in ids if json_data['data']['articles'][id['id']]['videos'][0]['view_cnt']
            ]

            item['video_datas'] = video_datas
            self.engine = create_engine("mysql+pymysql://root:pythonman@127.0.0.1/UC?charset=utf8")

            # 创建会话
            self.session = sessionmaker(self.engine)
            self.mySession = self.session()

            for gzh_cids in item['video_datas']:
                work = {}
                work['url'] = gzh_cids['url']
                work['thumbnails'] = gzh_cids['thumbnails']
                work['title'] = gzh_cids['title']
                work['work_id'] = int(gzh_cids['id'])
                work['video_height'] = gzh_cids['video_height']
                work['video_width'] = gzh_cids['video_width']
                md = hashlib.md5()  # 构造一个md5
                md.update(str(work['thumbnails']).encode())
                url_md5 = md.hexdigest()  # 加密结果
                work['url_md5'] = url_md5
                # if work['video_width'] >= 1000:
                result = self.mySession.query(Work).filter_by(url_md5=work['url_md5']).first()
                if result is None:
                    print('添加视频：{}'.format(work['title']))
                    work = Work(url=work['url'], thumbnails=work['thumbnails'],
                                title=work['title'], url_md5=work['url_md5'],
                                video_height=work['video_height'], video_width=work['video_width'], status=0)

                    self.mySession.add(work)
                    self.mySession.commit()

                else:
                    pprint('视频已存在')

                self.mySession.query(Url).filter(Url.id == item['id']).update({"status": "1"})
                self.mySession.commit()

                self.mySession.query(Url).filter(Url.id < 1000000).update({"status": "1"})
                self.mySession.commit()

        except Exception as f:
            Print.error('UC浏览器爬虫错误:{}'.format(f))

            pass
