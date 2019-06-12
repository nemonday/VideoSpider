import os

import pymysql

from VideoSpider.API.iduoliaotool import IduoliaoTool
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
            new_filename = IduoliaoTool.video_download(filename, url, title, old_type, ifdewatermark=True)
            # 获取视频的帧宽，帧高， 用于去水印定位
            size_filename, width, height = IduoliaoTool.get_video_size(url)
            # 下载视频的封面地址
            img_filename = IduoliaoTool.img_download(img_url, filename)

            # 当三种东西准备就绪，调用去水印工具
            if new_filename and size_filename and img_filename:
                # 去水印，判断是否成功返回真的视频文件用于oss上传
                dewatermark_name = IduoliaoTool.dewatermark(width, height, 20, 200, 55, 204, new_filename, title)
                if dewatermark_name:
                    # oss上传视频
                    # IduoliaoTool.oss_upload(dewatermark_name, dewatermark_name, UPLOADPATH, de_suffix=True)
                    # oss上传视频封面
                    # IduoliaoTool.oss_upload(img_filename, img_filename, UPLOADPATH2, de_suffix=False)
                    pass
                # 上传完毕，删除文件
                if os.path.exists(img_filename):
                    os.remove(img_filename)

                # if os.path.exists(dewatermark_name):
                #     os.remove(dewatermark_name)

                if os.path.exists(size_filename):
                    os.remove(size_filename)



