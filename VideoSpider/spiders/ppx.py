# -*- coding: utf-8 -*-
import json
import re
from copy import deepcopy
from pprint import pprint

import requests
import scrapy
from VideoSpider.settings import *


class PpxSpider(scrapy.Spider):
    name = 'ppx'

    def start_requests(self):

        item = {}
        for video_url, video_type in ppx_spider_dict.items():
            proxy = requests.get(PROXY_URL)
            proxies = {
                'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['old_type'] = video_type[4]
            yield scrapy.Request(video_url, headers=video_type[3], callback=self.parse, meta={'proxy': ''.format(proxies['https']),'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        video_datas = []
        ppx_data = json.loads(response.text)
        video_info = ppx_data['data']['data']
        try:
            for video in video_info:
                item['url'] = 'https://h5.pipix.com/item/' + re.search(r'https://h5.pipix.com/item/(\d*)', video['item']['share']['link_text']).group(1)
                item['download_url'] = video['item']['video']['video_download']['url_list'][1]['url']
                item['like_cnt'] = video['item']['stats']['like_count']
                item['cmt_cnt'] = video['item']['stats']['comment_count']
                item['sha_cnt'] = video['item']['stats']['share_count']
                item['view_cnt'] = video['item']['stats']['play_count']
                item['thumbnails'] = video['item']['origin_video_download']['cover_image']['url_list'][0]['url']
                item['title'] = re.search(r'(.*)\n', video['item']['share']['link_text']).group(1)
                item['id'] = re.search(r'https://h5.pipix.com/item/(\d*)', video['item']['share']['link_text']).group(1)
                item['video_height'] = video['item']['origin_video_download']['height']
                item['video_width'] = video['item']['origin_video_download']['width']
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '皮皮虾'
                item['category'] = item['category']

                # 筛选条件
                if item['view_cnt'] >= item['view_cnt_compare']:
                    print(item)
        except Exception as f:
            pprint('皮皮虾爬虫错误:{}'.format(f))
            pass

