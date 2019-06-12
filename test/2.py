import hashlib
import json
import re
from pprint import pprint

import pymysql
import requests
import time
from VideoSpider.settings import pq_headers, pq_spider_dict


class GetPraise(object):
    def __init__(self):

        self.connection = pymysql.connect(
            host='rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com',
            port=3306,
            user='migration_test',
            password='migrationTest*',
            db='db_nt_video',
            charset='utf8'
        )

    def run(self):
        while True:
            try:
                item = {}
                proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=0&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&gm=4'
                proxy = requests.get(proxy_url)
                proxy = json.loads(proxy.text)['data'][0]
                proxies = {
                    'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
                }
                for data, video_infoa in pq_spider_dict.items():
                    url = 'https://longvideoapi.qingqu.top/longvideoapi/video/distribute/category/videoList'

                    res = requests.post(url, headers=pq_headers, data=data, proxies=proxies, timeout=30)
                    videos = json.loads(res.text)['data']

                    for video in videos:
                        item['id'] = video['id']
                        try:
                            item['title'] = video['title']
                        except:
                            item['title'] = '无法获取'
                        item['uid'] = video['user']['uid']
                        item['nickName'] = video['user']['nickName']
                        try:
                            item['vipDesc'] = video['user']['vipDesc']
                        except:
                            item['vipDesc'] = '非优质原创作者'

                        url = 'https://longvideoapi.qingqu.top/longvideoapi/video/reward/getVideoRewardRecordList'

                        data = r'orderBy=1&videoId={}&pageNum=1&pageSize=20&token=98752eb2c48717a915c5d12a05d8e4b9b5806f0d&loginUid=6907157&platform=android&versionCode=91&machineCode=weixin_openid_oRAM34waHIG8hQHIRUr1LMmo5C8o&appType=5&system=Android%205.1.1&pageSource=&pageCategoryId=&rootPageSource=&shareDepth=&rootPageCategoryId=&appId=wx2afa73d47208de10&clientTimestamp=1559551392398&machineInfo=%7B%22sdkVersion%22%3A%222.6.6%22%2C%22brand%22%3A%22Xiaomi%22%2C%22language%22%3A%22zh_CN%22%2C%22model%22%3A%22MIX%22%2C%22platform%22%3A%22android%22%2C%22system%22%3A%22Android%205.1.1%22%2C%22weChatVersion%22%3A%227.0.3%22%2C%22screenHeight%22%3A1067%2C%22screenWidth%22%3A600%2C%22pixelRatio%22%3A1.2%2C%22windowHeight%22%3A1013%2C%22windowWidth%22%3A600%2C%22softVersion%22%3A%223.15.6%22%7D&networkType=wifi'.format(item['id'])

                        headers = {
                            'charset': 'utf-8',
                            'Accept-Encoding': 'gzip',
                            'referer': 'https://servicewechat.com/wx2afa73d47208de10/93/page-frame.html',
                            'content-type': 'application/x-www-form-urlencoded',
                            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; MIX Build/LMY48Z) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Safari/537.36 MicroMessenger/7.0.3.1400(0x2700033C) Process/appbrand0 NetType/WIFI Language/zh_CN',
                            'Host': 'longvideoapi.qingqu.top',
                            'Connection': 'Keep-Alive'
                            }
                        res = requests.post(url, headers=headers, proxies=proxies, data=data)
                        sponsors = json.loads(res.text)['data']
                        try:
                            for sponsor in sponsors:
                                rewardUser = sponsor['rewardUser']
                                item['sponsorname'] = rewardUser['nickName']
                                item['sponsorid'] = rewardUser['uid']
                                item['price'] = sponsor['rewardAmountFormat']

                                md = hashlib.md5()  # 构造一个md5
                                md.update(str(item).encode())
                                id = md.hexdigest()  # 加密结果
                                pprint(item)
                                # cursor = self.connection.cursor()
        #                         try:
        #                             sql = """INSERT INTO tb_pq_rewarduser(id, vid, title, author_id, author, vip_desc, sponsor_id , sponsor_name, sponsor_amount)
        # SELECT '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' FROM DUAL WHERE NOT EXISTS(SELECT id FROM tb_pq_rewarduser WHERE id = '%s')
        # """ % (id, item['id'], item['title'], item['uid'], item['nickName'], item['vipDesc'], item['sponsorid'], item['sponsorname'], item['price'], id)
        #                             cursor.execute(sql)
        #                             self.connection.commit()
        #                             print('添加id {} 到数据库'.format(item['id']))
        #                         except Exception as f:
        #                             print('添加错误')
        #                             print(f)
        #                             self.connection.rollback()
        #
        #                         cursor.close()

                        except Exception as f:
                            print('没有符合条件的作品')
                            pass
                time.sleep(30)

            except Exception as f:
                print(f)
                self.run()
                pass


if __name__ == '__main__':
    obj = GetPraise()
    obj.run()
