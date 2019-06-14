# -*- coding: utf-8 -*-
import hashlib
import json
import re
import time
from copy import deepcopy
import traceback
import requests
import scrapy
from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.settings import pq_spider_dict, pq_headers, PROXY_URL


class PqSpider(scrapy.Spider):
    name = 'pq'

    def start_requests(self):
        item = {}
        for data, video_info in pq_spider_dict.items():
            item['view_cnt_compare'] = video_info[1]
            item['cmt_cnt_compare'] = video_info[2]
            item['data'] = data
            item['old_type'] = video_info[4]
            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

        url = 'https://longvideoapi.qingqu.top/longvideoapi/video/distribute/category/videoList'
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'https://' + re.search(r'(.*)', proxy.text).group(1)}
        res = requests.post(url, headers=pq_headers, data=item['data'], proxies=proxies, timeout=30)
        try:
            videos = json.loads(res.text)['data']
            for video in videos:
                item['url'] = re.match(r'https://.*.m3u8?', video['videoPath']).group()
                item['download_url'] = ''
                item['like_cnt'] = 0
                item['cmt_cnt'] = 0
                item['sha_cnt'] = video['shareCount']
                item['view_cnt'] = video['playCount']
                item['thumbnails'] = video['coverImg']['coverImgPath']
                try:
                    item['title'] = video['title']
                except:
                    item['title'] = video['shareTitle']

                item['id'] = video['id']
                item['video_height'] = video['height']
                item['video_width'] = video['width']
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '票圈长视频'
                # 构造一个md5
                md = hashlib.md5()
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()  # 加密结果

                # 筛选视频是否合格
                if item['view_cnt'] >= item['view_cnt_compare'] or item['sha_cnt'] >= item['cmt_cnt_compare']:
                    is_ture = Iduoliao.redis_check(item['osskey'])
                    if is_ture is True:
                        # 开始去水印上传
                        Iduoliao.upload(url, item['thumbnails'], item['osskey'], '票圈长视频', item['title'], item['old_type'])

        except Exception as f:
            traceback.print_exc()
            pass