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
from VideoSpider.tool import check, jieba_ping, download, download_img, oss_upload, deeimg, deep_img_video, \
    get_md5_name, redis_check


class XngzfSpider(scrapy.Spider):
    name = 'xngzf'

    def start_requests(self):
        while True:
            item = {}
            item['uid'] = '270bd624-46f5-483f-82ca-19aa07e1c374'
            item['token'] = '658561f5cad5ace806ed73db84af0179'
            for video_url, video_type in xng_zf_spider_dict.items():
                choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
                item['view_cnt_compare'] = int(5000 * choice(choice_list))
                item['cmt_cnt_compare'] = int(5000 * choice(choice_list))
                item['category'] = video_type[0]
                item['old_type'] = video_type[4]

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

                # 筛选条件
                if item['view_cnt'] >= item['view_cnt_compare']:
                    img_filename = ''
                    video_size_img = ''
                    # 通过条件下载文件，提取视频一帧的图片的二进制生成md5名字用于判断视频是否存在
                    filename = download(str(item['id']), item['download_url'], True)
                    md5_name = get_md5_name(item['id'], filename)
                    is_presence = redis_check(md5_name)
                    item['osskey'] = md5_name

                    # 视频不存在执行
                    if is_presence is True:

                        # 匹配关键字获取视频类型
                        match_type = jieba_ping(item)
                        if match_type is None:
                            item['match_type'] = item['category']
                        else:
                            item['match_type'] = match_type

                        # 获取视频封面，已经视频的尺寸
                        img_filename = download_img(item['thumbnails'], item['osskey'])
                        video_size = deeimg(item['download_url'])
                        video_size_img = video_size[2]

                        # 竖屏视频执行：
                        if video_size[0] < video_size[1]:
                            # 定义遮挡水印的新文件名字
                            deeimg_filename = item['osskey'] + '.mp4'
                            # 遮挡水印
                            deep_img_video(video_size[0], video_size[1], video_size[1] - 70, 100, 50, 120, filename,
                                           deeimg_filename)
                            if deeimg_filename:
                                # 转码成功后，去掉文件 .mp4后缀准备oss上传
                                os.rename(deeimg_filename, item['osskey'])
                                # oss上传
                                oss_upload(item['osskey'], item['osskey'], img_filename)

                                yield item

                        else:
                            # print('横屏转码')
                            deeimg_filename = item['osskey'] + '.mp4'
                            deep_img_video(video_size[0], video_size[1], video_size[1] - 68, 130, 50, 150, filename,
                                           deeimg_filename)

                            if deeimg_filename:
                                os.rename(deeimg_filename, item['osskey'])
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
            pprint('小年糕祝福爬虫错误:{}'.format(f))
            pass
