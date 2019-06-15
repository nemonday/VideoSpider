# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import os
import re
import time
from copy import deepcopy
from pprint import pprint
from random import choice
import requests
import scrapy

from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE, \
    xng_spider_dict, PROXY_URL, xng_headers


class XngSpider(scrapy.Spider):
    name = 'xng'

    def start_requests(self):
        item = {}
        item['token'] = '8f8135b40677be896a6270ddff99cb71'
        item['uid'] = '9077df59-0135-4ecf-abaa-eae77159673b'
        for video_url, video_type in xng_spider_dict.items():
            choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
            item['view_cnt_compare'] = int(5000 * choice(choice_list))
            item['cmt_cnt_compare'] = int(5000 * choice(choice_list))
            item['category'] = video_type[0]
            item['data'] = video_url % (item['token'], item['uid'])
            item['old_type'] = video_type[4]
            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

        url = 'https://api.xiaoniangao.cn/trends/get_recommend_trends'
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'https://' + re.search(r'(.*)', proxy.text).group(1)}
        res = requests.post(url, headers=xng_headers, data=item['data'], timeout=30)
        json_data = json.loads(res.text)
        video_datas = json_data['data']['list']
        try:
            for video in video_datas:
                item['url'] = video['v_url']
                item['download_url'] = video['v_url']
                item['like_cnt'] = video['favor']['total']
                item['cmt_cnt'] = 0
                item['sha_cnt'] = 0
                item['view_cnt'] = video['views']
                item['thumbnails'] = video['url']
                item['title'] = video['title']
                item['id'] = video['album_id']
                item['video_height'] = 0
                item['video_width'] = 0
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '小年糕'
                item['category'] = item['category']

                # 构造一个md5
                md = hashlib.md5()
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()  # 加密结果
                # 筛选条件
                if item['view_cnt'] >= item['view_cnt_compare']:
                    is_ture = Iduoliao.redis_check(item['osskey'])
                    if is_ture is True:
                        # 开始去水印上传
                        Iduoliao.upload(item['url'], item['thumbnails'], item['osskey'], '小年糕', item['title'],item['old_type'])

        except Exception as f:
            Print.error('小年糕爬虫错误:{}'.format(f) )
            pass


