# -*- coding: utf-8 -*-
import base64
import json
import re
from copy import deepcopy
import requests
import scrapy
from VideoSpider.settings import *
from VideoSpider.tool import check, jieba_ping, download, download_img, oss_upload, ky_download


class KySpider(scrapy.Spider):
    name = 'ky'

    def start_requests(self):
        item = {}
        for video_url, video_type in ky_spider_dict.items():
            proxy = requests.get(PROXY_URL)
            proxies = {
                'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['match_from'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3],
                                 callback=self.parse, meta={'proxy': ''.format(proxies['https']),
                                                            'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        json_data = json.loads(response.text)
        try:
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

                osskey = item['osskey'][0]
                item['osskey'] = osskey

                result = check(item['from'], item['id'])

                if (result is None) and (item['view_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']):
                    match_type = jieba_ping(item)
                    item['match_type'] = match_type

                    yield item

        except Exception as f:
            print(f)
            pass

        page = json_data['nextPageUrl']
        if page:
            proxy = requests.get(PROXY_URL)
            proxies = {
                'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

            yield scrapy.Request(json_data['nextPageUrl'], headers=openeye_headers,
                                 callback=self.parse, meta={'proxy': ''.format(proxies['https']),
                                                            'item': deepcopy(item)}, dont_filter=True)
        else:
            pass
