# -*- coding: utf-8 -*-
import base64
import json
import os
import re
import time
from copy import deepcopy
from pprint import pprint
from random import choice

import pymysql
import requests
import scrapy

from VideoSpider.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE, \
    xng_spider_dict, PROXY_URL, xng_headers
from VideoSpider.tool import check, jieba_ping, download, download_img, oss_upload, deeimg


class XngSpider(scrapy.Spider):
    name = 'xng'

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
            sql = """select token,uid from video_token where name='小年糕'"""
            cursor.execute(sql)
            for video in cursor.fetchall():
                item['token'] = video[0]
                item['uid'] = video[1]

        except Exception as f:
            connection.rollback()

        cursor.close()
        for video_url, video_type in xng_spider_dict.items():
            choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
            item['view_cnt_compare'] = int(5000 * choice(choice_list))
            item['cmt_cnt_compare'] = int(5000 * choice(choice_list))
            item['category'] = video_type[0]
            item['data'] = video_url % (item['token'], item['uid'])
            item['match_from'] = video_type[4]

            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def deep_img_video(self, width, height, y, w, h, excursion, filename, deepcopy_filename):
        try:
            os.system('''ffmpeg -i {} -filter_complex "delogo=x={}:y={}:w={}:h={}:show=0" {}'''.format(filename, int(
                width) - excursion, y, w, h, deepcopy_filename))
            return True
        except:
            return False

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

        url = 'https://api.xiaoniangao.cn/trends/get_recommend_trends'
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'https://' + re.search(r'(.*)', proxy.text).group(1)}
        res = requests.post(url, headers=xng_headers, data=item['data'], timeout=30)
        json_data = json.loads(res.text)
        video_datas = json_data['data']['list']
        try:
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
                item['video_height'] = 0
                item['video_width'] = 0
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '小年糕'
                item['category'] = item['category']
                item['osskey'] = base64.b64encode((str(video['album_id']) + 'xng').encode('utf-8')).decode('utf-8')

                result = check(item['from'], item['id'])

                if (result is None) and (item['view_cnt'] >= item['view_cnt_compare']) :
                    match_type = jieba_ping(item)
                    item['match_type'] = match_type
                    filename = download(item['osskey'], item['download_url'], False)
                    img_filename = download_img(item['thumbnails'], item['osskey'])
                    video_size = deeimg(item['download_url'])
                    if not video_size is False and(video_size[0]<video_size[1]):
                        deeimg_filename = item['osskey'] + '.mp4'
                        is_ture = self.deep_img_video(video_size[0], video_size[1], video_size[1]-70, 100, 50, 120, filename, deeimg_filename)
                        if is_ture is True:
                            oss_upload(item['osskey'], deeimg_filename, video_size[2])
                            if os.path.exists(video_size[2]):
                                os.remove(video_size[2])

                            if os.path.exists(filename):
                                os.remove(filename)

                            yield item
                        else:
                            print('去水印失败')
                    else:
                        oss_upload(item['osskey'], filename, video_size[2])
                        if os.path.exists(video_size[2]):
                            os.remove(video_size[2])

                        if os.path.exists(filename):
                            os.remove(filename)

                        yield item

        except Exception as f:
            pprint(f)
            pass

