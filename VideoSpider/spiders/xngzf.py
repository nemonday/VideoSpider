# -*- coding: utf-8 -*-
import hashlib
import json
from copy import deepcopy
import requests
import scrapy
from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import *


class XngzfSpider(scrapy.Spider):
    def __init__(self, **kwargs):
        super(XngzfSpider, self).__init__()
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=&city=0&yys=0&port=11&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        self.proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }
    name = 'xngzf'

    def start_requests(self):
        item = {}
        item['uid'] = '2b213f38-f682-4c3b-8e2d-089c84190684'
        item['token'] = '12075f07b016d34a27db743df4589c12'
        for video_url, video_type in xng_zf_spider_dict.items():
            choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
            item['view_cnt_compare'] = int(5000 * choice(choice_list))
            item['cmt_cnt_compare'] = int(5000 * choice(choice_list))
            item['old_type'] = video_type[4]

            item['data'] = video_url % (item['uid'], item['token'])

            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        url = 'https://api.xiaoniangao.cn/trends/get_recommend_trends'
        try:
            res = requests.post(url, headers=xng_zf_headers, proxies=self.proxies, data=item['data'], timeout=30)
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

                # 构造一个md5
                md = hashlib.md5()
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()  # 加密结果
                # 筛选条件
                if item['view_cnt'] >= item['view_cnt_compare']:
                    is_ture = Iduoliao.redis_check(item['osskey'])
                    if is_ture is True:
                        # 开始去水印上传
                        Iduoliao.upload(item['url'], item['thumbnails'], item['osskey'], '小年糕祝福', item['title'],item['old_type'])

        except Exception as f:
            Print.error('小年糕祝福爬虫错误:{}'.format(f))
            pass
