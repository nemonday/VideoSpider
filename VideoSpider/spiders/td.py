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


class TdSpider(scrapy.Spider):
    def __init__(self):
        super(TdSpider, self).__init__()
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        self.proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }

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
                # 构造一个md5
                md = hashlib.md5()
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()  # 加密结果
                # 筛选条件
                if item['view_cnt'] >= item['view_cnt_compare']:
                    is_ture = Iduoliao.redis_check(item['osskey'])
                    if is_ture is True:
                        # 开始去水印上传
                        Iduoliao.upload(item['url'], item['thumbnails'], item['osskey'], '糖豆', item['title'], item['old_type'])

        except Exception as f:
            Print.error('糖豆爬虫错误:{}'.format(f))
            pass


