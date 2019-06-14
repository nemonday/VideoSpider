# -*- coding: utf-8 -*-
import base64
import json
import os
import re
from contextlib import closing
from copy import deepcopy
from pprint import pprint
# from moviepy.video.io.VideoFileClip import VideoFileClip
import requests
import scrapy
from VideoSpider.settings import *



class TdSpider(scrapy.Spider):
    name = 'td'

    def start_requests(self):
        item = {}

        for video_url, video_type in td_spider_dict.items():
            proxy = requests.get(PROXY_URL)
            proxies = {
                'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['old_type'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3],
                                 callback=self.parse, meta={'proxy': ''.format(proxies['https']),
                                                            'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']

        # 糖豆搞笑视频
        if response.url.startswith('https://wx.tangdou.com/api.php?mod=gaoxiao'):
            tangdou_funny_url = 'https://wx.tangdou.com/api.php?mod=gaoxiao&ac=index_new&page={}&appname=gaoxiao&pname=gaoxiao&version=2.1.6&s=&c=&nt=wifi&width=600&height=940&device=Android%205.1.1&model=MIX&sdkv=2.6.2&pr=1.2&lg=zh_CN&wv=7.0.3&wvv=android&fs=16&sbh=25&sw=600&sh=1067&brad=Xiaomi&uuid=oATSP4qll0-cLSfzi-zR41-hlREQ'
            try:
                for i in range(2000):
                    proxy = requests.get(PROXY_URL)
                    proxies = {
                        'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

                    yield scrapy.Request(tangdou_funny_url.format(i), headers=td_headers,
                                         callback=self.tangdou, meta={'proxy': ''.format(proxies['https']),
                                                                      'item': deepcopy(item)}, dont_filter=True)
            except:
                pass
        # 糖豆广场舞
        elif response.url.startswith('https://wx.tangdou.com/api.php?mod=video'):
            tangdou_dance_url = 'https://wx.tangdou.com/api.php?mod=video&ac=choice&page={}&version=3.2.6&appname=squaredance&uuid=o0VD60GG3_jBdjqfAjKQlch0XlZ4&s=&c=&nt=wifi&width=393&height=687&device=Android%208.1.0&model=Redmi%206%20Pro&sdkv=2.6.2&pr=2.75&lg=zh_CN&wv=7.0.3&wvv=android&fs=16&sbh=40&sw=393&sh=830&brad=xiaomi&userid=82130228'
            try:
                for i in range(2000):
                    proxy = requests.get(PROXY_URL)
                    proxies = {
                        'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

                    yield scrapy.Request(tangdou_dance_url.format(i), headers=td_headers,
                                         callback=self.tangdou, meta={'proxy': ''.format(proxies['https']),
                                                                      'item': deepcopy(item)}, dont_filter=True)

            except:
                pass
        # 糖豆生活
        elif response.url.startswith('https://wx.tangdou.com/api.php?mod=yangsheng'):
            tangdou_life_url = 'https://wx.tangdou.com/api.php?mod=yangsheng&ac=index_new&page={}&type=2&appname=yangsheng&pname=yangsheng&version=2.7.3&s=&c=&nt=wifi&width=393&height=687&device=Android%208.1.0&model=Redmi%206%20Pro&sdkv=2.6.2&pr=2.75&lg=zh_CN&wv=7.0.3&wvv=android&fs=16&sbh=40&sw=393&sh=830&brad=xiaomi&uuid=otSul5NvK28dfVlBt5XIbrEesvJY'
            try:
                for i in range(2000):
                    proxy = requests.get(PROXY_URL)
                    proxies = {
                        'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

                    yield scrapy.Request(tangdou_life_url.format(i), headers=td_headers,
                                         callback=self.tangdou, meta={'proxy': ''.format(proxies['https']),
                                                                          'item': deepcopy(item)}, dont_filter=True)
            except:
                pass

    def tangdou(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        json_data = json.loads(response.text)
        video_info = json_data['datas']['list']
        try:
            for video in video_info:
                item['url'] = 'http://aqiniu.tangdou.com/' + video['videourl'] + '-20.mp4'
                item['download_url'] = 'http://aqiniu.tangdou.com/' + video['videourl'] + '-20.mp4'
                item['like_cnt'] = 0
                item['cmt_cnt'] = 0
                item['sha_cnt'] = 0
                item['view_cnt'] = video['hits_total']
                item['thumbnails'] = 'https://aimg.tangdou.com' + video['pic']
                item['title'] = video['title']
                item['id'] = video['vid']
                item['video_height'] = 0
                item['video_width'] = 0
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '糖豆'
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
                            deep_img_video(video_size[0], video_size[1], 10, 100, 50, 110, filename, deeimg_filename)
                            if deeimg_filename:
                                # 转码成功后，去掉文件 .mp4后缀准备oss上传
                                os.rename(deeimg_filename, item['osskey'])
                                # oss上传
                                oss_upload(item['osskey'], item['osskey'], img_filename)

                                yield item

                        else:
                            # print('横屏转码')
                            deeimg_filename = item['osskey'] + '.mp4'
                            deep_img_video(video_size[0], video_size[1], video_size[1] - 20, 100, 50, 118, filename,
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
            pprint('糖豆爬虫错误:{}'.format(f))
            pass


