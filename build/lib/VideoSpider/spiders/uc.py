# -*- coding: utf-8 -*-
import base64
import json
import random
import re
from copy import deepcopy
from pprint import pprint
import requests
import scrapy

from VideoSpider.tool import jieba_ping, check
from VideoSpider.settings import *


class UcSpider(scrapy.Spider):
    name = 'uc'

    def start_requests(self):
        item ={}
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}
        for video_url, video_type in uc_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]

            yield scrapy.Request(video_url, headers=video_type[3],
                                 callback=self.parse, meta={'proxy': ''.format(proxies['https']),'item': deepcopy(item)}, dont_filter=True)

    def uc_category(self, gzh_cids):
        if gzh_cids['category'] in uc_life_list:
            return 4
        elif gzh_cids['category'] in uc_chid_list:
            return 16
        elif gzh_cids['category'] in uc_funny_list:
            return 1
        elif gzh_cids['category'] in uc_music_list:
            return 2
        elif gzh_cids['category'] in uc_sport_list:
            return 11
        elif gzh_cids['category'] in uc_dance_list:
            return 10
        elif gzh_cids['category'] in uc_food_list:
            return 13
        elif gzh_cids['category'] in uc_movie_list:
            return 6
        elif gzh_cids['category'] in uc_variety_list:
            return 3
        else:
            return None

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

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
            'osskey': base64.b64encode((json_data['data']['articles'][id['id']]['id'] + 'UC').encode('utf-8')).decode('utf-8'),
            'spider_time': time.strftime(isotimeformat, time.localtime(time.time())),
        }
            for id in ids if json_data['data']['articles'][id['id']]['videos'][0]['view_cnt'] > item['view_cnt_compare']
                             or json_data['data']['articles'][id['id']]['cmt_cnt'] > item['cmt_cnt_compare']
        ]

        item['video_datas'] = video_datas

        for gzh_cids in item['video_datas']:
            result = check(gzh_cids['id'], gzh_cids['from'])
            category = self.uc_category(gzh_cids)
            if (result is None) and (not category is None):
                gzh_cids['category'] = category

                item['url'] = gzh_cids['url']
                item['download_url'] = gzh_cids['url']
                item['like_cnt'] = ''
                item['cmt_cnt'] = gzh_cids['cmt_cnt']
                item['sha_cnt'] = ''
                item['view_cnt'] = gzh_cids['view_cnt']
                item['thumbnails'] = gzh_cids['thumbnails']
                item['title'] = gzh_cids['title']
                item['id'] = gzh_cids['id']
                item['video_height'] = gzh_cids['video_height']
                item['video_width'] = gzh_cids['video_width']
                item['spider_time'] = gzh_cids['spider_time']
                item['from'] = 'UC浏览器'
                item['category'] = gzh_cids['category']
                item['osskey'] = gzh_cids['osskey']

                match_type = jieba_ping(item)
                if not match_type is None:
                    item['match_type'] = item['category']
                else:
                    item['match_type'] = match_type

                yield item
