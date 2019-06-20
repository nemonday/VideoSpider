# -*- coding: utf-8 -*-
import hashlib
import json
import re
from copy import deepcopy
import requests
import scrapy
from selenium import webdriver
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
        # 获取代理
        proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=0&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        proxy = requests.get(proxy_url)
        proxy = json.loads(proxy.text)['data'][0]
        https_proxies = {
            'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
        }
        self.proxies = https_proxies['https']
        self.opt = webdriver.ChromeOptions()
        # 加入请求头
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.opt.add_argument('--disable-dev-shm-usage')
        # 不加载图片
        self.opt.add_argument('--no-sandbox')
        # 添加代理
        self.opt.add_argument("--proxy-server={}".format(self.proxies))

        # 无头模式
        # self.opt.add_argument('--headless')

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

    def is_visible(self, locator, timeout=10):
        try:
            ui.WebDriverWait(self.broser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except Exception as f:
            return False

    def parse(self, response):
        try:
            isotimeformat = '%Y-%m-%d'
            item = response.meta['item']
            json_data = json.loads(response.text)
            video_info = json_data['data']

            for video in video_info[2:]:
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
                rep = re.search(r'http://toutiao.com/group/(.*)/', url).group(1)
                item['url'] = 'https://www.ixigua.com/i' + rep + '/'

                md = hashlib.md5()  # 构造一个md5
                md.update(str(item['url']).encode())
                item['osskey'] = md.hexdigest()

                if item['view_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']:
                    is_ture = Iduoliao.redis_check(item['osskey'])
                    if is_ture is True:
                        self.broser.get(item['download_url'])
                        exists = self.is_visible('//video')
                        if exists is True:
                            url = self.broser.find_element_by_xpath('//video').get_attribute("src")
                            print(url)
            self.broser.quit()

        except Exception as f:
            Print.error(f)
            print('错误所在的行号：', f.__traceback__.tb_lineno)
            # 判断是否出现解析失败
            exists = self.is_visible('//*[@id="__layout"]/div/div[2]/div/div[2]/div[1]/div[2]')
            if exists is True:
                click_button = self.broser.find_element_by_css_selector('[class="vue-dialog-button"]')
                click_button.click()
            pass

