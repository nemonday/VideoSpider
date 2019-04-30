# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import random
import re
import time
from copy import deepcopy
import pymysql
import requests
import scrapy
from selenium import webdriver
from VideoSpider.tool import jieba_ping, deeimg, download, check, redis_check
from VideoSpider.settings import *


class XgSpider(scrapy.Spider):

    name = 'xg'

    def start_requests(self):
        item = {}
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

        for video_url, video_type in xg_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['old_type'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3], callback=self.parse, meta={'proxy': ''.format(proxies['https']),'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        try:
            isotimeformat = '%Y-%m-%d'
            item = response.meta['item']
            json_data = json.loads(response.text)
            video_info = json_data['data']

            for video in video_info[2:]:
                md = hashlib.md5()  # 构造一个md5

                video = json.loads(video['content'])
                item['id'] = video['group_id']
                item['url'] = video['display_url']
                item['download_url'] = video['display_url']
                item['like_cnt'] = video['video_like_count']
                item['cmt_cnt'] = video['comment_count']
                item['sha_cnt'] = video['share_count']
                item['view_cnt'] = video['video_detail_info']['video_watch_count']
                item['thumbnails'] = video['large_image_list'][0]['url']
                item['title'] = video['title']
                item['video_height'] = json.loads(video['video_play_info'])['video_list']['video_1']['vheight']
                item['video_width'] = json.loads(video['video_play_info'])['video_list']['video_1']['vwidth']
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '西瓜视频'
                item['category'] = item['category']
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()

                if item['view_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']:
                    is_ture = redis_check(item['osskey'])
                    if is_ture is True:
                        yield item

        except Exception as f:
            print(f)
            pass