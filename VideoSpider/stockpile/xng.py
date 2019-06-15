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


class XngSpider(scrapy.Spider):
    name = 'xng'

    def start_requests(self):
        item = {}
        item['token'] = '65431454eee2e3585b95e34210ccac43'
        item['uid'] = '716a9609-af87-4dd0-bf73-8a3f19349ca5'
        for video_url, video_type in xng_spider_dict.items():
            choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
            item['view_cnt_compare'] = int(5000 * choice(choice_list))
            item['cmt_cnt_compare'] = int(5000 * choice(choice_list))
            item['category'] = video_type[0]
            item['data'] = video_url % (item['token'], item['uid'])
            item['old_type'] = video_type[4]
            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

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

                pprint(item)
                # 筛选条件
                if item['view_cnt'] >= item['view_cnt_compare']:
                    img_filename = ''
                    video_size_img = ''
                    # # 通过条件下载文件，提取视频一帧的图片的二进制生成md5名字用于判断视频是否存在
                    # filename = download(str(item['id']), item['download_url'], True)
                    # md5_name = get_md5_name(item['id'], filename)
                    # is_presence = redis_check(md5_name)
                    #
                    # item['osskey'] = md5_name
                    #
                    # # 视频不存在执行
                    # if is_presence is True:
                    #     # 获取视频封面，已经视频的尺寸
                    #     img_filename = download_img(item['thumbnails'], item['osskey'])
                    #     video_size = deeimg(item['download_url'])
                    #     video_size_img = video_size[2]
                    #
                    #     # 竖屏视频执行：
                    #     if video_size[0] < video_size[1]:
                    #         # 定义遮挡水印的新文件名字
                    #         deeimg_filename = item['osskey'] + '.mp4'
                    #         # 遮挡水印
                    #         deep_img_video(video_size[0], video_size[1], video_size[1]-70, 100, 50, 120, filename, deeimg_filename)
                    #         if deeimg_filename:
                    #             # 转码成功后，去掉文件 .mp4后缀准备oss上传
                    #             os.rename(deeimg_filename, item['osskey'])
                    #             # oss上传
                    #             oss_upload(item['osskey'], item['osskey'], img_filename)
                    #
                    #             yield item
                    #
                    #     else:
                    #         # print('横屏转码')
                    #         deeimg_filename = item['osskey'] + '.mp4'
                    #         deep_img_video(video_size[0], video_size[1], video_size[1] - 68, 130, 50, 150, filename, deeimg_filename)
                    #
                    #         if deeimg_filename:
                    #             os.rename(deeimg_filename, item['osskey'])
                    #             oss_upload(item['osskey'], item['osskey'], img_filename)
                    #
                    #             yield item

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
            pprint('小年糕爬虫错误:{}'.format(f) )
            pass

