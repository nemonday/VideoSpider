# -*- coding: utf-8 -*-
import base64
import json
import os
import re
from copy import deepcopy
import requests
import scrapy
from VideoSpider.tool import check, jieba_ping, download, download_img, deeimg, oss, deep_img_video, oss_upload
from VideoSpider.settings import *
from random import choice


class HkSpider(scrapy.Spider):
    name = 'hk'

    def start_requests(self):

        item = {}
        for video_url, video_type in hk_spider_dict.items():
            choice_list = [0.5, 0.6, 0.7, 0.8, 0.9, 1]
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['data'] = video_url
            item['match_from'] = video_type[4]

            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        isotimeformat = '%Y-%m-%d'
        item = response.meta['item']
        url = 'https://sv.baidu.com/haokan/api?cmd=feed&log=vhk&tn=1008550k&ctn=1008550k&imei=860288798124814&cuid=74549A5C9851705527AB79A13A5D41DC%7C950679401524948&bdboxcuid=&os=android&osbranch=a0&ua=720_1280_192&ut=OPPO%20R11%20Plus_5.1.1_22_OPPO&apiv=4.6.0.0&appv=412011&version=4.12.1.10&life=1553411253&clife=1553411253&hid=DF2C5C965F584CAEE70171B87FA55FC7&imsi=0&network=1&location=%7B%22prov%22:%22%E4%B8%8A%E6%B5%B7%E5%B8%82%22,%22city%22:%22%E4%B8%8A%E6%B5%B7%E5%B8%82%22,%22county%22:%22%E9%BB%84%E6%B5%A6%E5%8C%BA%22,%22city-code%22:%22289%22,%22street%22:%22%E9%BB%84%E6%B5%A6%E8%B7%AF%22,%22latitude%22:31.24764,%22longitude%22:121.497854%7D&sids=1927_3-1945_2-1967_2-2008_1-2042_4-2055_2-2099_2-2103_2-2105_2-1769_1-2118_1-2122_2-2138_1-2139_1-2144_2-2149_3-2158_4-2146_2-2162_2-2163_1'

        PROXY_URL = 'http://dynamic.goubanjia.com/dynamic/get/822c219bc02c29fe940c1718ccdf89f3.html?sep=3'
        # proxy = requests.get(PROXY_URL)
        # proxies = {
        #     'https': 'http://' + re.search(r'(.*)', proxy.text).group(1)}
        res = requests.post(url, headers=hk_headers, data=item['data'])
        print(res)
        json_data = json.loads(res.text)
        video_info = json_data['feed']['data']['list']

        for video in video_info:
            item['url'] = ''
            item['download_url'] = video['content']['video_src']
            item['like_cnt'] = video['content']['praiseNum']
            item['cmt_cnt'] = video['content']['comment_cnt']
            item['sha_cnt'] = 0
            item['view_cnt'] = video['content']['playcnt']
            item['thumbnails'] = video['content']['thumbnails']
            item['title'] = video['content']['title']
            item['id'] = video['content']['vid']
            item['video_height'] = video['content']['height']
            item['video_width'] = video['content']['width']
            item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
            item['from'] = '好看视频'
            item['category'] = item['category']
            item['osskey'] = base64.b64encode((str(video['content']['vid']) + 'hk').encode('utf-8')).decode('utf-8'),

            result = check(item['from'], item['id'])
            try:
                view_cnt = item['view_cnt']
                cmt_cnt = item['cmt_cnt']
                if (result is None) and (int(view_cnt) >= item['view_cnt_compare'] or int(cmt_cnt) >= item['cmt_cnt_compare']):
                    match_type = jieba_ping(item)
                    item['match_type'] = match_type
                    item['osskey'] = item['osskey'][0]
                    filename = download(item['osskey'], item['download_url'], True)
                    # img_filename = download_img(item['thumbnails'], item['osskey'])
                    if filename:
                        video_size = deeimg(item['download_url'])
                        if not video_size is False and(video_size[0] > video_size[1]):
                            deeimg_filename = 'stockpile/' + item['osskey'] + '.mp4'
                            is_ture = deep_img_video(item['video_width'], item['video_height'], 10, 150, 50, 160, filename, deeimg_filename)
                            if is_ture is True:
                                oss_upload(item['osskey'],deeimg_filename, video_size[2])

                            else:
                                print('去水印失败')
                        else:
                            oss_upload(item['osskey'], filename, video_size[2])

                        if os.path.exists(video_size[2]):
                            os.remove(video_size[2])

                    yield item
            except Exception as f:
                print(f)



