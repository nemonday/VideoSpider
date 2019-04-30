import contextlib
import json
import os
import re
from pprint import pprint
from contextlib import closing
import requests
import pymysql
import requests
import time
import random
def check(vid):
    # 传入vid, 视频来源

    cursor = connection.cursor()
    try:
        sql = """select vid from tb_spider_video where vid = '%s'""" % (vid)
        data = cursor.execute(sql)

        if data == 0:
            return None
        else:
            return True

    except Exception as f:
        print('查询错误')
        print(f)
        connection.rollback()
    cursor.close()


MYSQL_HOST = 'rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com'
MYSQL_PORT = 3306
MYSQL_USERNAME = 'migration_test'
MYSQL_PASSWORK = 'migrationTest*'
MYSQL_DATABASE = 'db_nt_video'

connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

url = 'https://longvideoapi.qingqu.top/longvideoapi/video/distribute/category/videoList'

headers = {
    'charset': 'utf-8',
    'Accept-Encoding': 'gzip',
    'referer': 'https://servicewechat.com/wx2afa73d47208de10/73/page-frame.html',
    'content-type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; MIX Build/LMY48Z) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Safari/537.36 MicroMessenger/7.0.3.1400(0x2700033C) Process/appbrand0 NetType/WIFI Language/zh_CN',
    'Content-Length': '795',
    'Host': 'longvideoapi.qingqu.top',
    'Connection': 'Keep-Alive',
}

data = r'categoryJson=%7B%22categoryId%22%3A4%7D&pageNo=2&pageSize=6&sortField=0&pageSource=longvideo-pages%2Fcategory&token=&loginUid=&platform=android&versionCode=71&machineCode=weixin_openid_oRAM34waHIG8hQHIRUr1LMmo5C8o&appType=5&system=Android%205.1.1&pageCategoryId=4&rootPageSource=&shareDepth=&rootPageCategoryId=&appId=wx2afa73d47208de10&clientTimestamp={}&machineInfo=%7B%22sdkVersion%22%3A%222.6.6%22%2C%22brand%22%3A%22Xiaomi%22%2C%22language%22%3A%22zh_CN%22%2C%22model%22%3A%22MIX%22%2C%22platform%22%3A%22android%22%2C%22system%22%3A%22Android%205.1.1%22%2C%22weChatVersion%22%3A%227.0.3%22%2C%22screenHeight%22%3A1067%2C%22screenWidth%22%3A600%2C%22pixelRatio%22%3A1.2%2C%22windowHeight%22%3A1013%2C%22windowWidth%22%3A600%2C%22softVersion%22%3A%223.13.11%22%7D&networkType=wifi'.format(int(round(time.time() * 1000)))


res = requests.post(url, headers=headers, data=data)
videos = json.loads(res.text)['data']
item = {}
isotimeformat = '%Y-%m-%d'
cursor = connection.cursor()
pprint(videos)
# for video in videos:
#     donload_dict = {}
#     item['url'] = re.match(r'https://.*.m3u8?', video['videoPath']).group()
#     item['download_url'] = ''
#     item['like_cnt'] = 0
#     item['cmt_cnt'] = 0
#     item['sha_cnt'] = video['shareCount']
#     item['view_cnt'] = video['playCount']
#     item['thumbnails'] = video['coverImg']['coverImgPath']
#     try:
#         item['title'] = video['title']
#     except:
#         item['title'] = video['shareTitle']
#
#     item['id'] = video['id']
#     item['video_height'] = video['height']
#     item['video_width'] = video['width']
#     item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
#     item['from'] = '票圈长视频'
#
#     donload_dict[item['url']]  = re.match(r'https://rescdn.yishihui.com/longvideo/(.*)/(.*)/(.*)/(.*)', item['url']).group(4)
#     synthesis_filename = re.match(r'https://rescdn.yishihui.com/longvideo/(.*)/(.*)/(.*)/(.*)', item['url']).group(4)
#
#     ffmpeg_filename = re.match(r'(.*)\.m3u8', synthesis_filename).group(1)
#     rep = requests.get(item['url']).text
#     file_line = rep.replace('\r\n', '')
#     datas = re.findall(r'(\S*).ts?', file_line)
#
#     os.system('ffmpeg -i {} {}.mp4'.format(item['url'], ffmpeg_filename))



    # item['category'] = item['category']
    # is_ture = check(item['id'])
    # if is_ture is None:
    #     try:
    #         sql = "INSERT INTO tb_spider_video(vid, height, width, video_from, play_volume, comment_volume, title, spidertime, url, img, share_volume, like_volume) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',  '%s')" % (item['id'], item['video_height'], item['video_width'], item['from'],item['view_cnt'], item['cmt_cnt'], item['title'], item['spider_time'],item['url'], item['thumbnails'], item['sha_cnt'], item['like_cnt'])
    #
    #         cursor.execute(sql)
    #         connection.commit()
    #         print('添加id {} 到数据库'.format(item['id']))
    #     except Exception as f:
    #         print('添加错误')
    #         print(f)
    #         connection.rollback()
# cursor.close()
