# -*- coding: utf-8 -*-
import hashlib
import json
import re
from copy import deepcopy
import requests
import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from VideoSpider.iduoliao import Print
from VideoSpider.tool import redis_check
from VideoSpider.settings import *


class XgSpider(scrapy.Spider):
    def __init__(self):
        super(XgSpider, self).__init__()
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        # self.opt.add_argument('--disable-dev-shm-usage')
        # self.opt.add_argument('--no-sandbox')

        # display = Display(visible=0, size=(800, 600))
        # display.start()

        self.broser = webdriver.Chrome(options=self.opt)
        self.wait = WebDriverWait(self.broser, 20, 0.5)

    name = 'xg'

    def start_requests(self):
        item = {}
        proxy = requests.get(PROXY_URL)
        proxies = {
            'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}

        for video_url, video_type in xg_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['old_type'] = video_type[4]

            yield scrapy.Request(video_url, headers=video_type[3], callback=self.parse, meta={'proxy': ''.format(proxies['https']),'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        try:
            isotimeformat = '%Y-%m-%d'
            item = response.meta['item']
            json_data = json.loads(response.text)
            video_info = json_data['data']

            for video in video_info[2:]:
                md = hashlib.md5()  # 构造一个md5

                video = json.loads(video['content'])
                item['id'] = video['group_id']
                item['url'] = video['display_url']
                item['download_url'] = video['display_url']
                item['like_cnt'] = video['video_like_count']
                item['cmt_cnt'] = video['comment_count']
                item['sha_cnt'] = video['share_count']
                item['view_cnt'] = video['video_detail_info']['video_watch_count']
                item['thumbnails'] = video['large_image_list'][0]['url']
                item['title'] = video['title']
                item['video_height'] = json.loads(video['video_play_info'])['video_list']['video_1']['vheight']
                item['video_width'] = json.loads(video['video_play_info'])['video_list']['video_1']['vwidth']
                item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                item['from'] = '西瓜视频'
                item['category'] = item['category']
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()

                if item['view_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']:
                    # is_ture = redis_check(item['osskey'])
                    # if is_ture is True:
                    self.broser.get(item['download_url'])
                    time.sleep(5)
                    url = self.broser.find_element_by_xpath('//video').get_attribute("src")

                    print(url)
                    # yield item

        except Exception as f:
            Print.error(f)
            pass