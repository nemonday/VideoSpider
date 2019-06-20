# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import os
import re
from copy import deepcopy
from pprint import pprint

import requests
import scrapy

from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.settings import *
from random import choice


class HkSpider(scrapy.Spider):
    def __init__(self):
        super(HkSpider, self).__init__()
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=0&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        self.proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }

    name = 'hk'

    def start_requests(self):
        item = {}
        for video_url, video_type in hk_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['data'] = video_url
            item['old_type'] = video_type[4]

            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

        url = 'https://sv.baidu.com/haokan/api?tn=1008350o&ctn=1008350o&imei=02B4B04B-2F2E-49DB-AF2D-AFFC79A3B0D2&cuid=3E8B5CD30DC5CF707754338AB6C6B1B408204C669OMPAQEKPQC&os=ios&osbranch=i0&ua=750_1334_326&ut=iPhone8%2C1_12.2&net_type=1&apiv=4.10.3.10&appv=1&version=4.10.3.10&life=1551235144&clife=1551235144&sids=2518_4-2540_1-2583_1-2627_2-2604_2-2635_1-2659_4-2665_2-2673_1-2685_1-2686_2-2691_2-2694_2-2697_2-2704_1-2717_3-2731_2-2732_4-2739_1-2743_2-2745_2-2498_1-2750_1-2753_1-2761_2-2772_1-2776_1-2782_2-2787_1-2796_1-2803_2&idfa=AB9793B9-CEE3-4EB2-9994-6DB2632BF4E6&hid=E0D63A86979B6633AB05F6AE72350416&log=vhk&location=&cmd=feed'

        res = requests.post(url, headers=hk_headers, proxies=self.proxies, data=item['data'])
        json_data = json.loads(res.text)
        video_info = json_data['feed']['data']['list']

        for video in video_info:
            item['url'] = ''
            item['download_url'] = video['content']['video_src']
            item['like_cnt'] = video['content']['praiseNum']
            item['cmt_cnt'] = video['content']['comment_cnt']
            item['sha_cnt'] = 0
            item['view_cnt'] = video['content']['playcnt']
            item['thumbnails'] = video['content']['thumbnails']
            item['title'] = video['content']['title']
            item['id'] = video['content']['vid']
            item['video_height'] = video['content']['height']
            item['video_width'] = video['content']['width']
            item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
            item['from'] = '好看视频'
            item['category'] = item['category']
            # 构造一个md5
            md = hashlib.md5()
            md.update(str(item['url']).encode())
            item['osskey'] = md.hexdigest()  # 加密结果

            # 筛选视频是否合格
            if item['view_cnt'] >= item['view_cnt_compare'] or item['sha_cnt'] >= item['cmt_cnt_compare']:
                is_ture = Iduoliao.redis_check(item['osskey'])
                if is_ture is True:
                    # 开始去水印上传
                    Iduoliao.upload(item['url'], item['thumbnails'], item['osskey'], '好看视频', item['title'],
                                    item['old_type'], width=item['width'], height=item['height'])





