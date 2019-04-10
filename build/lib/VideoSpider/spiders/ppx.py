# -*- coding: utf-8 -*-
import base64
import json
import os
import random
import re
from copy import deepcopy
import requests
import scrapy
from VideoSpider.tool import check, jieba_ping, download, download_img, deeimg, deep_img_video, oss_upload
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
            item['match_from'] = video_type[4]

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
                item['osskey'] = base64.b64encode('{}{}'.format(item['id'], 'ppx').encode('utf-8')).decode('utf-8'),

                result = check(item['from'], item['id'])
                if (result is None) and (item['like_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']):
                    match_type = jieba_ping(item)
                    item['match_type'] = match_type
                    osskey = item['osskey'][0]
                    item['osskey'] = osskey
                    filename = download(item['osskey'], item['download_url'], False)
                    img_filename = download_img(item['thumbnails'], item['osskey'])

                    oss_upload(item['osskey'], filename, img_filename)

                    yield item

        except Exception as f:
            print(f)
            pass
