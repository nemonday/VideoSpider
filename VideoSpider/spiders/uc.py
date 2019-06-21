# -*- coding: utf-8 -*-
import hashlib
import json
import re
from copy import deepcopy
import requests
import scrapy
from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import *

class UcSpider(scrapy.Spider):

    name = 'uc'

    def start_requests(self):
        item ={}
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }

        for video_url, video_type in uc_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['old_type'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3],
                                 callback=self.parse, meta={'proxy': ''.format(proxies['https']),
                                                            'item': deepcopy(item)}, dont_filter=True)

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
                for id in ids if json_data['data']['articles'][id['id']]['videos'][0]['view_cnt'] > item['view_cnt_compare']
                                 or json_data['data']['articles'][id['id']]['cmt_cnt'] > item['cmt_cnt_compare']
            ]

            item['video_datas'] = video_datas

            for gzh_cids in item['video_datas']:
                md = hashlib.md5()  # 构造一个md5
                md.update(str(gzh_cids['url']).encode())
                item['osskey'] = md.hexdigest()

                # 判断视频是否存在
                is_ture = Iduoliao.redis_check(item['osskey'])
                if is_ture is True:
                    item['url'] = gzh_cids['url']
                    item['download_url'] = gzh_cids['url']
                    item['like_cnt'] = 0
                    item['cmt_cnt'] = gzh_cids['cmt_cnt']
                    item['sha_cnt'] = 0
                    item['view_cnt'] = gzh_cids['view_cnt']
                    item['thumbnails'] = gzh_cids['thumbnails']
                    item['title'] = gzh_cids['title']
                    item['id'] = gzh_cids['id']
                    item['video_height'] = gzh_cids['video_height']
                    item['video_width'] = gzh_cids['video_width']
                    item['spider_time'] = gzh_cids['spider_time']
                    item['from'] = 'UC浏览器'
                    item['old_type'] = gzh_cids['old_type']

                    yield item

        except Exception as f:
            Print.error('UC浏览器爬虫错误:{}'.format(f))
            pass
