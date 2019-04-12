import hashlib
import os
from contextlib import closing
from urllib.request import urlretrieve
import cv2
import jieba
import pymysql
import requests
from PIL import Image
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
import oss2

from settings import ACCESSKEYID, ACCESSKEYSECRET, ENDPOINT, BUCKETNAME, MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, \
    MYSQL_PASSWORK, MYSQL_DATABASE, UPLOADPATH, UPLOADPATH2

connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )


def deeimg(dowonload_url):
    # 传入下载地址

    try:
        video_full_path = dowonload_url
        cap = cv2.VideoCapture(video_full_path)
        if cap.isOpened():  # 正常打开
            rval, frame = cap.read()
        else:
            rval = False

        sign_key = hashlib.md5(str(dowonload_url).encode('utf-8'))
        sign = sign_key.hexdigest()

        size_filename = 'stockpile/' + sign + '.jpg'

        cv2.imwrite(size_filename, frame)
        img = Image.open(size_filename)
        width = img.size[0]
        height = img.size[1]

        return [width, height, size_filename]
    except:
        return False


def oss(key, filename, uploadpath):
    # 传入osskey, 文件路径, oss路径
        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        auth = oss2.Auth(ACCESSKEYID, ACCESSKEYSECRET)
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, ENDPOINT, BUCKETNAME)

        key = uploadpath + key
        filename = filename

        total_size = os.path.getsize(filename)

        # determine_part_size方法用来确定分片大小。
        part_size = determine_part_size(total_size, preferred_size=10240 * 1000)

        # 初始化分片。
        upload_id = bucket.init_multipart_upload(key).upload_id
        parts = []
        # 逐个上传分片。
        with open(filename, 'rb') as fileobj:
            part_number = 1
            offset = 0

            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                # SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                result = bucket.upload_part(key, upload_id, part_number,
                                            SizedFileAdapter(fileobj, num_to_upload, ),
                                            )
                parts.append(PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1


            # 完成分片上传
            bucket.complete_multipart_upload(key, upload_id, parts)


def deep_img_video(width, height, y, w, h, excursion, filename, deepcopy_filename):
    try:
        os.system('''ffmpeg -i {} -filter_complex "delogo=x={}:y={}:w={}:h={}" show=0" {}'''.format(filename, int(width) - excursion,y, w, h, deepcopy_filename))
        return True
    except:
        return False

def download(osskey, download_url, is_deepimg=False):
    # 传入oss名称, 下载地址
    try:
        # 视频下载
        with closing(requests.get(download_url, stream=True)) as r:
            chunk_size = 1024
            content_size = int(r.headers['content-length'])

            if is_deepimg is False:
                filename =  'VideoSpider/stockpile' + osskey + '.mp4'
            elif is_deepimg is True:
                filename =  'VideoSpider/stockpile' + osskey + 'copy' + '.mp4'

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


def ky_download(osskey, download_url):
        # 视频下载
        with closing(requests.get(download_url, stream=True)) as r:
            chunk_size = 1024
            filename = osskey + '.mp4'
            with open(filename, "wb") as f:
                n = 1
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    n += 1
                num = '\r下载视频: {}  '.format(osskey)
                print(num, end='')

        return filename




def download_img(img_url, oss):
    # 传入图片地址, oss名称
    IMAGE_URL = img_url
    img_filename = oss + '.png'
    urlretrieve(IMAGE_URL, img_filename)

    return img_filename


def check(vid, video_from):
    # 传入vid, 视频来源

    cursor = connection.cursor()
    try:
        sql = """select vid from tb_spider_video where vid = '%s' and video_from= '%s'""" % (vid, video_from)
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


def oss_upload(osskey, filename, img_filename):
    if os.path.exists(filename):
        oss(osskey + '.mp4', filename, UPLOADPATH)
        os.remove(filename)

    if os.path.exists(img_filename):
        oss(osskey + '.png', img_filename, UPLOADPATH2)
        os.remove(img_filename)


def update_mysql(item):

    cursor = connection.cursor()
    video_url = 'https://jiuban-image.oss-cn-hangzhou.aliyuncs.com/video_spider/video/'
    img_url = 'https://jiuban-image.oss-cn-hangzhou.aliyuncs.com/video_spider/img/'

    try:
        sql = 'UPDATE tb_spider_video SET status=4, video_oss_url= "%s", img_oss_url="%s" WHERE id="%s"' % (
            video_url + item['osskey'] + '.mp4', img_url + item['osskey']+ '.png', item['id']
        )

        # sql2 = 'UPDATE tb_spider_video SET status=4" WHERE video_type="%s"' % ('佳品')
        print("""
            上传成功，修改状态,
            video地址: {}
            img地址: {}
        """.format(video_url + item['osskey'] + '.mp4', img_url + item['osskey']+ '.png')
              )

        cursor.execute(sql)
        connection.commit()
    except Exception as f:
        print(f)
        connection.rollback()

    cursor.close()


# ky_download('haha', 'http://ali.cdn.kaiyanapp.com/1550720244197_4adc8469.mp4?auth_key=1554261516-0-0-337c723a344e1b7441f8670ce0d8827a')

