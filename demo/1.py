import base64

import requests
import time
# url = 'https://longvideoapi.qingqu.top/longvideoapi/video/distribute/category/videoList'
#
# headers = {
#     'charset': 'utf-8',
#     'Accept-Encoding': 'gzip',
#     'referer': 'https://servicewechat.com/wx2afa73d47208de10/72/page-frame.html',
#     'content-type': 'application/x-www-form-urlencoded',
#     'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; MIX Build/LMY48Z) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Safari/537.36 MicroMessenger/7.0.3.1400(0x2700033C) Process/appbrand0 NetType/WIFI Language/zh_CN',
#     'Host': 'longvideoapi.qingqu.top',
#     'Connection': 'Keep-Alive',
# }
#
# data = {
#     r'categoryJson=%7B%22categoryId%22%3A5%7D&pageNo=2&pageSize=6&sortField=0&pageSource=longvideo-pages%2Fcategory&token=&loginUid=&platform=android&versionCode=70&machineCode=weixin_openid_oRAM34waHIG8hQHIRUr1LMmo5C8o&appType=5&system=Android%205.1.1&pageCategoryId=5&rootPageSource=&shareDepth=&rootPageCategoryId=&appId=wx2afa73d47208de10&clientTimestamp={}&machineInfo=%7B%22sdkVersion%22%3A%222.6.6%22%2C%22brand%22%3A%22Xiaomi%22%2C%22language%22%3A%22zh_CN%22%2C%22model%22%3A%22MIX%22%2C%22platform%22%3A%22android%22%2C%22system%22%3A%22Android%205.1.1%22%2C%22weChatVersion%22%3A%227.0.3%22%2C%22screenHeight%22%3A1067%2C%22screenWidth%22%3A600%2C%22pixelRatio%22%3A1.2%2C%22windowHeight%22%3A1013%2C%22windowWidth%22%3A600%2C%22softVersion%22%3A%223.13.10%22%7D&networkType=wifi'.format(int(time.time()))
# }
#
# # data
#
#
# res = requests.post(url, headers=headers, data=data, )
#
# print(res.text)
import json
from contextlib import closing
from pprint import pprint

import requests

# url = 'https://rescdn.yishihui.com/longvideo/multitranscode/video/20190121/4901380CvBOEZIP1UFNGgAHgQ-randomIIgAO8z1eA20190411210000042472682-1LD.m3u8?Expires=1556418473&OSSAccessKeyId=LTAIHZz0zdTMC7HN&Signature=jjhyotON8rDckEKiblvInvZp5VM%3D'
#
# def download(osskey, download_url, is_deepimg=False):
#     # 传入oss名称, 下载地址
#     try:
#         # 视频下载
#         with closing(requests.get(download_url, stream=True)) as r:
#             chunk_size = 1024
#             content_size = int(r.headers['content-length'])
#
#             if is_deepimg is False:
#                 filename = osskey + '.mp4'
#             elif is_deepimg is True:
#                 filename = osskey + 'copy' + '.mp4'
#
#             with open(filename, "wb") as f:
#                 n = 1
#                 for chunk in r.iter_content(chunk_size=chunk_size):
#                     loaded = n * 1024.0 / content_size
#                     f.write(chunk)
#                     num = '\r下载视频: {} ,{}% '.format(osskey, int(loaded) * 100)
#                     print(num, end='')
#                     n += 1
#         return filename
#     except:
#         return False

def download(osskey, download_url, is_deepimg=False):
    # 传入oss名称, 下载地址
    try:
        # 视频下载
        with closing(requests.get(download_url, stream=True)) as r:
            chunk_size = 1024
            content_size = int(r.headers['content-length'])

            if is_deepimg is False:
                filename = osskey + '.mp4'
            elif is_deepimg is True:
                filename = osskey + 'copy' + '.mp4'

            with open(filename, "wb") as f:
                n = 1
                for chunk in r.iter_content(chunk_size=chunk_size):
                    loaded = n * 1024.0 / content_size
                    f.write(chunk)
                    num = '\r下载视频: {} ,{}% '.format(osskey, int(loaded) * 100)
                    print(num, end='')
                    n += 1
        return filename
    except:
        return False

url = 'https://wxmini-api.uyouqu.com/rest/wd/wechatApp/hot/photos'

headers = {
'charset': 'utf-8',
'Accept-Encoding': 'gzip',
'referer': 'https://servicewechat.com/wx79a83b1a1e8a7978/23/page-frame.html',
'content-type': 'application/json',
'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; MIX Build/LMY48Z) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Safari/537.36 MicroMessenger/7.0.3.1400(0x2700033C) Process/appbrand1 NetType/WIFI Language/zh_CN',
'Host': 'wxmini-api.uyouqu.com',
'Connection': 'Keep-Alive',

}


for i in range(0, 100001, 20):
    data = {
        r'{"pcursor":%s,"count":20}' % i
    }

    rep = requests.post(url, headers=headers, data=data)

    isotimeformat = '%Y-%m-%d'

    videos = json.loads(rep.text)['feeds']
    time.sleep(5)
    for video in videos:
        item = {}
        # item['url'] = video['mainMvUrls'][0]['url']
        # item['download_url'] = video['mainMvUrls'][0]['url']
        # item['like_cnt'] = video['likeCount']
        # item['cmt_cnt'] = video['commentCount']
        # item['sha_cnt'] = 0
        # item['view_cnt'] = video['viewCount']
        # item['thumbnails'] = video['coverUrls'][0]['url']
        item['title'] = video['caption']
        # item['id'] = video['photoId']
        # item['video_height'] = video['height']
        # item['video_width'] = video['width']
        # item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
        # item['from'] = '快手短视频'
        print(item)
        # download(item['title'], item['url'])
