import os
import re
import time
from contextlib import closing
import pymysql
import redis
import requests
from VideoSpider.API.iduoliaotool import IduoliaoTool, Print
from VideoSpider.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE, UPLOADPATH, \
    UPLOADPATH2


class Iduoliao(object):
    def __init__(self):
        self.connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

    @staticmethod
    def upload(url, img_url, filename, videofrom, title, old_type):
        if videofrom == "西瓜视频":
            # 传入视频下载地址，返回新的文件名字
            new_filename = IduoliaoTool.video_download(filename, url, title, old_type, videofrom, ifdewatermark=True)
            # 获取视频的帧宽，帧高， 用于去水印定位
            size_filename, width, height = IduoliaoTool.get_video_size(url)
            # 下载视频的封面地址
            img_filename = IduoliaoTool.img_download(img_url, filename)

            # 当三种东西准备就绪，调用去水印工具
            if new_filename and size_filename and img_filename:
                # 去水印，判断是否成功返回真的视频文件用于oss上传
                dewatermark_name = IduoliaoTool.dewatermark(width, height, 20, 200, 55, 204, new_filename, title, old_type, videofrom)
                if dewatermark_name:
                    # oss上传视频
                    # IduoliaoTool.oss_upload(dewatermark_name, dewatermark_name, UPLOADPATH, de_suffix=True)
                    # oss上传视频封面
                    # IduoliaoTool.oss_upload(img_filename, img_filename, UPLOADPATH2, de_suffix=False)
                    pass
                # 上传完毕，删除文件
                if os.path.exists(img_filename):
                    os.remove(img_filename)

                if os.path.exists(size_filename):
                    os.remove(size_filename)

        if videofrom == "票圈长视频":
            # 获取ffmpeg导出视频名字
            synthesis_filename = re.match(r'https://rescdn.yishihui.com/longvideo/(.*)/(.*)/(.*)/(.*)', url).group(4)
            ffmpeg_filename = re.match(r'(.*)\.m3u8', synthesis_filename).group(1) + '.mp4'

            isotimeformat = '%Y-%m-%d'
            day = time.strftime(isotimeformat, time.localtime(time.time()))

            filename2 = './{}/{}/{}'.format(videofrom, old_type, day)
            if not os.path.exists(filename2):
                os.makedirs(filename2)

            filename = './{}/{}/{}/{}'.format(videofrom, old_type, day, title) + '.mp4'

            # 下载视频
            os.system('ffmpeg -i {} {}'.format(url, filename))

        if videofrom == "UC浏览器":
            IduoliaoTool.video_download(filename, url, title, old_type, videofrom, ifdewatermark=False)

        if videofrom == "糖豆":
            # 获取视频的帧宽，帧高， 用于去水印定位
            size_filename, width, height = IduoliaoTool.get_video_size(url)
            if int(width) > int(height):
                # 传入视频下载地址，返回新的文件名字
                new_filename = IduoliaoTool.video_download(filename, url, title, old_type, videofrom, ifdewatermark=True)

                # 下载视频的封面地址
                img_filename = IduoliaoTool.img_download(img_url, filename)

                # 当三种东西准备就绪，调用去水印工具
                if new_filename and size_filename and img_filename:
                    # 去水印，判断是否成功返回真的视频文件用于oss上传
                    dewatermark_name = IduoliaoTool.dewatermark(width, height, 10, 100, 50, 110, new_filename, title,
                                                                old_type, videofrom)
                    if dewatermark_name:
                        # oss上传视频
                        # IduoliaoTool.oss_upload(dewatermark_name, dewatermark_name, UPLOADPATH, de_suffix=True)
                        # oss上传视频封面
                        # IduoliaoTool.oss_upload(img_filename, img_filename, UPLOADPATH2, de_suffix=False)
                        pass

                    # 上传完毕，删除文件
                    if os.path.exists(img_filename):
                        os.remove(img_filename)

                    if os.path.exists(size_filename):
                        os.remove(size_filename)

        if videofrom == "开眼视频":
            isotimeformat = '%Y-%m-%d'
            day = time.strftime(isotimeformat, time.localtime(time.time()))

            filename2 = 'Z:\\爬虫储存\\爬虫储存1.0\\{}\\{}\\{}'.format(videofrom, old_type, day)
            if not os.path.exists(filename2):
                os.makedirs(filename2)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.3.2.1000 Chrome/30.0.1599.101 Safari/537.36"}
            with closing(requests.get(url, stream=True, headers=headers)) as r:
                chunk_size = 1024
                # content_size = int(r.headers['content-length'])
                filename = 'Z:\\爬虫储存\\爬虫储存1.0\\{}\\{}\\{}\\{}'.format(videofrom, old_type, day, title) + '.mp4'

                with open(filename, "wb") as f:
                    n = 1
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        # loaded = n * 1024.0 / content_size
                        f.write(chunk)
                        n += 1
                    Print.info('下载视频: {}'.format(filename))

        if videofrom == "小年糕":
            # 获取视频的帧宽，帧高， 用于去水印定位
            size_filename, width, height = IduoliaoTool.get_video_size(url)
            # if int(width) > int(height):
                # 传入视频下载地址，返回新的文件名字
            new_filename = IduoliaoTool.video_download(filename, url, title, old_type, videofrom,
                                                       ifdewatermark=True)

            # 下载视频的封面地址
            img_filename = IduoliaoTool.img_download(img_url, filename)

            # 当三种东西准备就绪，调用去水印工具
            if new_filename and size_filename and img_filename:
                # 去水印，判断是否成功返回真的视频文件用于oss上传
                dewatermark_name = IduoliaoTool.dewatermark(width, height, int(height)-70, 100, 50, 120, new_filename, title,
                                                            old_type, videofrom)
                if dewatermark_name:
                    # oss上传视频
                    # IduoliaoTool.oss_upload(dewatermark_name, dewatermark_name, UPLOADPATH, de_suffix=True)
                    # oss上传视频封面
                    # IduoliaoTool.oss_upload(img_filename, img_filename, UPLOADPATH2, de_suffix=False)
                    pass

            # 上传完毕，删除文件
            if os.path.exists(img_filename):
                os.remove(img_filename)

            if os.path.exists(size_filename):
                    os.remove(size_filename)

        if videofrom == "小年糕祝福":
            IduoliaoTool.video_download(filename, url, title, old_type, videofrom, ifdewatermark=False)

        if videofrom == "好看视频":
            # 传入视频下载地址，返回新的文件名字
            new_filename = IduoliaoTool.video_download(filename, url, title, old_type, videofrom,
                                                       ifdewatermark=True)
            # 获取视频的帧宽，帧高， 用于去水印定位
            size_filename, width, height = IduoliaoTool.get_video_size(url)
            # 下载视频的封面地址
            img_filename = IduoliaoTool.img_download(img_url, filename)

            # 当三种东西准备就绪，调用去水印工具
            if new_filename and size_filename and img_filename:
                # 去水印，判断是否成功返回真的视频文件用于oss上传
                dewatermark_name = IduoliaoTool.dewatermark(width, height, 10, 150, 50, 160, new_filename,
                                                            title, old_type, videofrom)
                if dewatermark_name:
                    # oss上传视频
                    # IduoliaoTool.oss_upload(dewatermark_name, dewatermark_name, UPLOADPATH, de_suffix=True)
                    # oss上传视频封面
                    # IduoliaoTool.oss_upload(img_filename, img_filename, UPLOADPATH2, de_suffix=False)
                    pass
                # 上传完毕，删除文件
                if os.path.exists(img_filename):
                    os.remove(img_filename)

                if os.path.exists(size_filename):
                    os.remove(size_filename)

    @staticmethod
    def redis_check(md5_name):
        try:
            redis_db = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
            is_presence = redis_db.zrank('spider', md5_name)
            if is_presence is None:
                mapping = {
                    md5_name: 10
                }
                redis_db.zadd('spider', mapping)
                Print.info('添加 {} 到redis当中'.format(md5_name))
                return True

            else:
                return False

        except Exception as f:
            Print.error(f)

