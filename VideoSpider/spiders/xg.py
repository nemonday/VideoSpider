# -*- coding: utf-8 -*-
import hashlib
import json
import re
from copy import deepcopy
from pprint import pprint

import requests
import scrapy
from selenium import webdriver
from contextlib import closing
from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.ui as ui


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
        self.login_url = 'https://miku.tools/tools/toutiao_video_downloader'
        # 登陆获取链接的网站
        self.broser.get(self.login_url)
        # 判断弹窗是否存在
        exists = self.is_visible('//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button')
        # 如果弹窗存在， 就点击close
        if exists is True:
            self.broser.find_element_by_xpath(
                '//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button').click()
            self.url_box = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//input[@placeholder="http://www.365yg.com/a6660790867638373640"]')))

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

    def is_visible(self, locator, timeout=10):
        try:
            ui.WebDriverWait(self.broser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except Exception as f:
            return False

    def parse(self, response):
        # try:
            isotimeformat = '%Y-%m-%d'
            item = response.meta['item']
            json_data = json.loads(response.text)
            video_info = json_data['data']

            for video in video_info[2:]:
                md = hashlib.md5()  # 构造一个md5
                video = json.loads(video['content'])
                item['id'] = video['group_id']
                url = video['display_url']
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
                md.update(str(url).encode())
                item['osskey'] = md.hexdigest()
                rep = re.search(r'http://toutiao.com/group/(.*)/', url).group(1)
                item['url'] = 'https://www.ixigua.com/i' + rep + '/'

                if item['view_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']:
                    # is_ture = redis_check(item['osskey'])
                    # if is_ture is True:
                    # 输入要解析的地址
                    self.url_box.send_keys(item['url'])
                    # 点击解析
                    click_button = self.broser.find_element_by_css_selector('[class="nya-btn"]')
                    click_button.click()

                    # 判断是否出现解析失败
                    exists = self.is_visible('//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button')
                    if exists is True:
                        click_button = self.broser.find_element_by_css_selector('[class="vue-dialog-button"]')
                        click_button.click()
                        self.url_box.clear()

                    # 判断是否获取成功
                    exists = self.is_visible('//*[@id="__layout"]/div/main/div[2]/section[2]/h2/span')
                    if exists is True:
                        url = self.broser.find_element_by_xpath(
                            '//*[@id="__layout"]/div/main/div[2]/section[2]/div/p/a').get_attribute('href')
                        # 开始去水印上传
                        Iduoliao.upload(url, item['thumbnails'], item['osskey'], '西瓜视频', item['title'], item['old_type'])

                        self.url_box.clear()



        # except Exception as f:
        #     Print.error(f)
        #     pass