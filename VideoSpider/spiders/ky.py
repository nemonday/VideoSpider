# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import re
import time
from copy import deepcopy
from pprint import pprint

import requests
import scrapy

from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.settings import *

from settings import openeye_headers, ky_spider_dict


class KySpider(scrapy.Spider):
    name = 'ky'

    def start_requests(self):
        item = {}
        for video_url, video_type in ky_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['old_type'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3],
                             callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        json_data = json.loads(response.text)
        for i in range(10):
            time.sleep(3)
            item['like_cnt'] = json_data['itemList'][i]['data']['content']['data']['consumption']['collectionCount']
            item['cmt_cnt'] = json_data['itemList'][i]['data']['content']['data']['consumption']['replyCount']
            item['sha_cnt'] = json_data['itemList'][i]['data']['content']['data']['consumption']['shareCount']
            item['view_cnt'] = json_data['itemList'][i]['data']['content']['data']['consumption']['playCount']
            item['thumbnails'] = json_data['itemList'][i]['data']['content']['data']['cover']['detail']
            item['title'] = json_data['itemList'][i]['data']['content']['data']['title']
            item['id'] = json_data['itemList'][i]['data']['content']['data']['id']
            item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
            item['from'] = '开眼视频'
            item['category'] = item['category']
            item['osskey'] = base64.b64encode((str(json_data['itemList'][i]['data']['content']['data']['id']) + 'ky').encode('utf-8')).decode('utf-8'),

            try:
                item['url'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][2]['url']
                item['download_url'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][2]['url']
                item['video_height'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][2]['height']
                item['video_width'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][2]['width']
            except:
                item['url'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][0]['url']
                item['download_url'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][0]['url']
                item['video_height'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][0]['height']
                item['video_width'] = json_data['itemList'][i]['data']['content']['data']['playInfo'][0]['width']

            # 构造一个md5
            md = hashlib.md5()
            md.update(str(item['url']).encode())
            item['osskey'] = md.hexdigest()  # 加密结果

            # 筛选视频是否合格
            if item['view_cnt'] >= item['view_cnt_compare'] or item['sha_cnt'] >= item['cmt_cnt_compare']:
                pprint(item)



        page = json_data['nextPageUrl']
        if page:

            yield scrapy.Request(json_data['nextPageUrl'], headers=openeye_headers,
                                 callback=self.parse, meta={
                                                            'item': deepcopy(item)}, dont_filter=True)
        else:
            pass
