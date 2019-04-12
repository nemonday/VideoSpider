# -*- coding: utf-8 -*-
import base64
import json
import os
import random
import re
from contextlib import closing
from copy import deepcopy
from pprint import pprint

import pymysql
import requests
import scrapy
from random import choice
from VideoSpider.settings import *
from VideoSpider.tool import check, jieba_ping, download, download_img, oss_upload, deeimg, deep_img_video


class XngzfSpider(scrapy.Spider):
    name = 'xngzf'

    def start_requests(self):
            connection = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORK,
                db=MYSQL_DATABASE,
                charset='utf8'
            )

            item = {}
            cursor = connection.cursor()
            try:
                sql = """select token,uid from video_token where name='小年糕祝福'"""
                cursor.execute(sql)
                for video in cursor.fetchall():
                    item['token'] = video[0]
                    item['uid'] = video[1]

            except Exception as f:
                connection.rollback()

            cursor.close()
            for video_url, video_type in xng_zf_spider_dict.items():
                choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
                item['view_cnt_compare'] = int(5000 * choice(choice_list))
                item['cmt_cnt_compare'] = int(5000 * choice(choice_list))
                item['category'] = video_type[0]
                item['data'] = video_url % (item['uid'], item['token'])

                url = 'https://www.baidu.com/'

                yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        url = 'https://api.xiaoniangao.cn/trends/get_recommend_trends'
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'https://' + re.search(r'(.*)', proxy.text).group(1)}

        try:
            res = requests.post(url, headers=xng_zf_headers, data=item['data'], timeout=30)
            json_data = json.loads(res.text)

            video_datas = json_data['data']['list']

            for video in video_datas:
                item['url'] = video['v_url']
                item['download_url'] = video['v_url']
                item['like_cnt'] = video['favor']['total']
                item['cmt_cnt'] = 0
                item['sha_cnt'] = 0
                item['view_cnt'] = video['views']
                item['thumbnails'] = video['url']
                item['title'] = video['title']
                item['id'] = video['album_id']
                item['video_height'] = video['vw']
                item['video_width'] = video['w']
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '小年糕祝福'
                item['category'] = item['category']
                item['osskey'] = base64.b64encode((str(video['album_id']) + 'xngzf').encode('utf-8')).decode('utf-8')

                result = check(item['from'], item['id'])

                if (result is None) and (item['view_cnt'] >= item['view_cnt_compare']):
                    match_type = jieba_ping(item)
                    if not match_type is None:
                        item['match_type'] = item['category']
                    else:
                        item['match_type'] = match_type
                    filename = download(item['osskey'], item['download_url'], True)
                    img_filename = download_img(item['thumbnails'], item['osskey'])
                    video_size = deeimg(item['download_url'])
                    if not video_size is False and (video_size[0] < video_size[1]):
                        deeimg_filename = item['osskey'] + '.mp4'
                        is_ture = deep_img_video(video_size[0], video_size[1], video_size[1] - 70, 100, 50, 120,
                                                 filename, deeimg_filename)
                        if is_ture is True:
                            oss_upload(item['osskey'], deeimg_filename, img_filename)
                            if os.path.exists(img_filename):
                                os.remove(img_filename)

                            if os.path.exists(filename):
                                os.remove(filename)

                            if os.path.exists(video_size[2]):
                                os.remove(video_size[2])
                            yield item
                        else:
                            print('去水印失败')
                    else:
                        deeimg_filename = item['osskey'] + '.mp4'
                        is_ture = deep_img_video(video_size[0], video_size[1], video_size[1] - 120, 130, 50, 140,
                                                 filename, deeimg_filename)
                        if is_ture is True:
                            oss_upload(item['osskey'], deeimg_filename, video_size[2])
                            if os.path.exists(video_size[2]):
                                os.remove(video_size[2])

                            if os.path.exists(filename):
                                os.remove(filename)

                            if os.path.exists(img_filename):
                                os.remove(img_filename)

                            yield item

        except Exception as f:
            print(f)
            pass


