# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import random
import re
from copy import deepcopy
from pprint import pprint
import requests
import scrapy
from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.settings import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class UcSpider(scrapy.Spider):
    def __init__(self, **kwargs):
        super(UcSpider, self).__init__()
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.opt.add_argument('--disable-dev-shm-usage')
        self.opt.add_argument('--no-sandbox')

        # display = Display(visible=0, size=(800, 600))
        # display.start()

        self.broser = webdriver.Chrome(options=self.opt)
        self.wait = WebDriverWait(self.broser, 20, 0.5)

    name = 'uc'

    def start_requests(self):
        item ={}
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}
        for video_url, video_type in uc_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['old_type'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3],
                                 callback=self.parse, meta={'proxy': ''.format(proxies['https']),'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        try:
            # UC浏览器
            json_data = json.loads(response.text)
            ids = json_data['data']['items']
            ids = [id for id in ids if len(id['id']) == 20]

            video_datas = [{
                # 视频id
                'id': json_data['data']['articles'][id['id']]['id'],
                # 视频地址
                'url': json_data['data']['articles'][id['id']]['url'],
                # 视频标题
                'title': json_data['data']['articles'][id['id']]['title'],
                # 视频分类
                'category': json_data['data']['articles'][id['id']]['category'][0],
                # 原始分类
                'old_type': json_data['data']['articles'][id['id']]['category'][0],
                # 视频封面地址
                'thumbnails': json_data['data']['articles'][id['id']]['videos'][0]['poster']['url'],
                # 视频宽
                'video_width': json_data['data']['articles'][id['id']]['videos'][0]['video_width'],
                # 视频高
                'video_height': json_data['data']['articles'][id['id']]['videos'][0]['video_height'],
                # 播放量
                'view_cnt': json_data['data']['articles'][id['id']]['videos'][0]['view_cnt'],
                # 评论数
                'cmt_cnt': json_data['data']['articles'][id['id']]['cmt_cnt'],
                'from': 'UC浏览器',
                'spider_time': time.strftime(isotimeformat, time.localtime(time.time())),
            }
                for id in ids if json_data['data']['articles'][id['id']]['videos'][0]['view_cnt'] > item['view_cnt_compare']
                                 or json_data['data']['articles'][id['id']]['cmt_cnt'] > item['cmt_cnt_compare']
            ]

            item['video_datas'] = video_datas

            for gzh_cids in item['video_datas']:
                md = hashlib.md5()  # 构造一个md5
                md.update(str(gzh_cids['url']).encode())
                item['osskey'] = md.hexdigest()

                # 判断视频是否存在
                is_ture = Iduoliao.redis_check(item['osskey'])
                if is_ture is True:
                    time.sleep(3)
                    item['url'] = gzh_cids['url']
                    item['download_url'] = gzh_cids['url']
                    item['like_cnt'] = ''
                    item['cmt_cnt'] = gzh_cids['cmt_cnt']
                    item['sha_cnt'] = ''
                    item['view_cnt'] = gzh_cids['view_cnt']
                    item['thumbnails'] = gzh_cids['thumbnails']
                    item['title'] = gzh_cids['title']
                    item['id'] = gzh_cids['id']
                    item['video_height'] = gzh_cids['video_height']
                    item['video_width'] = gzh_cids['video_width']
                    item['spider_time'] = gzh_cids['spider_time']
                    item['from'] = 'UC浏览器'
                    item['old_type'] = gzh_cids['old_type']

                    self.broser.get(item['url'])
                    try:
                        url = self.broser.find_element_by_xpath('//video').get_attribute("src")
                        Iduoliao.upload(url, item['thumbnails'], item['osskey'], 'UC浏览器', item['title'],item['old_type'])
                    except Exception as f:
                        print(f)
                        pass

            self.broser.quit()

        except Exception as f:
            pprint('UC浏览器爬虫错误:{}'.format(f))
            pass
