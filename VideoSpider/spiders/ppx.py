# -*- coding: utf-8 -*-
import base64
import json
import os
import random
import re
from copy import deepcopy
from pprint import pprint

import requests
import scrapy
from VideoSpider.tool import check, jieba_ping, download, download_img, deeimg, deep_img_video, oss_upload, \
    get_md5_name, redis_check
from VideoSpider.settings import *


class PpxSpider(scrapy.Spider):
    name = 'ppx'

    def start_requests(self):
        while True:
            time.sleep(120)
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
                    img_filename = ''
                    video_size_img = ''
                    # 通过条件下载文件，提取视频一帧的图片的二进制生成md5名字用于判断视频是否存在
                    filename = download(str(item['id']), item['download_url'], False)
                    md5_name = get_md5_name(item['id'], filename)
                    is_presence = redis_check(md5_name)

                    item['osskey'] = md5_name
                    img_filename = download_img(item['thumbnails'], item['osskey'])
                    os.rename(filename, item['osskey'])

                    # 视频不存在执行
                    if is_presence is True:
                        # 匹配关键字获取视频类型
                        match_type = jieba_ping(item)
                        if match_type is None:
                            item['match_type'] = item['category']
                        else:
                            item['match_type'] = match_type

                        oss_upload(item['osskey'], item['osskey'], img_filename)
                        yield item

                    # 上传完毕，删除文件
                    if os.path.exists(img_filename):
                        os.remove(img_filename)

                    if os.path.exists(filename):
                        os.remove(filename)

                    if os.path.exists(item['osskey']):
                        os.remove(item['osskey'])

                    if os.path.exists(video_size_img):
                        os.remove(video_size_img)

        except Exception as f:
            pprint('皮皮虾爬虫错误:{}'.format(f))
            pass

