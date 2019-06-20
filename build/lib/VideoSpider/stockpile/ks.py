# -*- coding: utf-8 -*-
import scrapy


class KsSpider(scrapy.Spider):
    name = 'ks'

    def start_requests(self):
        item = {}
        for video_url, video_type in ks_spider_dict.items():
            item['view_cnt_compare'] = video_type[1]
            item['cmt_cnt_compare'] = video_type[2]
            item['category'] = video_type[0]
            item['data'] = video_url

            url = 'https://www.baidu.com/'

            yield scrapy.Request(url, callback=self.parse, meta={'item': deepcopy(item)}, dont_filter=True)

    def parse(self, response):
        pass
