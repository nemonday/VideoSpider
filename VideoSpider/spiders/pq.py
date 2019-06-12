# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import time
from copy import deepcopy
import random
from pprint import pprint
import traceback
import requests
import scrapy

from VideoSpider.settings import pq_spider_dict, pq_headers, PROXY_URL
from VideoSpider.tool import redis_check, download_img, oss_upload


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

                pprint(item)
                # # 筛选视频是否合格
                # if item['view_cnt'] >= item['view_cnt_compare'] or item['sha_cnt'] >= item['cmt_cnt_compare']:
                #     is_ture = redis_check(item['osskey'])
                #     if is_ture is True:
                #         # 获取ffmpeg导出视频名字
                #         synthesis_filename = re.match(r'https://rescdn.yishihui.com/longvideo/(.*)/(.*)/(.*)/(.*)',item['url']).group(4)
                #         ffmpeg_filename = re.match(r'(.*)\.m3u8', synthesis_filename).group(1) + '.mp4'
                #
                #         # 下载封面地址
                #         img_filename = download_img(item['thumbnails'], item['osskey'])
                #         # 下载视频
                #         os.system('ffmpeg -i {} {}'.format(item['url'], ffmpeg_filename))
                #
                #         # 把视频的mp4格式去掉
                #         os.rename(ffmpeg_filename, item['osskey'])
                #
                #         # oss上传视频和图片
                #         oss_upload(item['osskey'], item['osskey'], img_filename)
                #
                #         # 上传完毕，删除文件
                #         if os.path.exists(img_filename):
                #             os.remove(img_filename)
                #
                #         if os.path.exists(item['osskey']):
                #             os.remove(item['osskey'])
                #
                #         yield item

        except Exception as f:
            traceback.print_exc()
            pass