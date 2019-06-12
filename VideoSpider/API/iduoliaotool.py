import json
import os
import re
import time
from pprint import pprint

import oss2
import redis
import cv2
from PIL import Image
import hashlib
from oss2 import determine_part_size, SizedFileAdapter
from oss2.models import PartInfo
import pymysql
from contextlib import closing
import requests
from VideoSpider.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE, ACCESSKEYID, \
    ACCESSKEYSECRET, ENDPOINT, BUCKETNAME
from urllib.parse import quote
from aliyunsdkcore.client import AcsClient
from aliyunsdkmts.request.v20140618 import SubmitJobsRequest


class Print(object):
    @staticmethod
    def info(message):
        out_message =  Print.timeStamp() + '  ' + 'INFO: ' +str(message)
        Print.write(out_message)
        print(out_message)

    @staticmethod
    def error(message):
        out_message = Print.timeStamp() + '  ' + 'ERROR: ' + str(message)
        Print.write(out_message)
        print(out_message)

    @staticmethod
    def write(message):
        LOG_DIRECTORY = "./"
        log_path = os.path.join(LOG_DIRECTORY, 'log.txt')
        with open(log_path,'a+') as f:
            f.write(message)
            f.write('\n')

    @staticmethod
    def timeStamp():
        local_time = time.localtime(time.time())
        return time.strftime("%Y_%m_%d-%H_%M_%S", local_time)


class IduoliaoTool(object):
    def __int__(self):
        self.connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

    @staticmethod
    def video_download(filename, download_url, title, old_type, ifdewatermark=False,):
        # 传入oss名称, 下载地址
        # 视频下载
        try:
            with closing(requests.get(download_url, stream=True)) as r:
                chunk_size = 1024
                content_size = int(r.headers['content-length'])

                # 不需要遮挡水印文件地址
                if ifdewatermark is False:
                    filename = title + '.mp4'

                # 需要遮挡水印文件地址
                elif ifdewatermark is True:
                    filename = 'Z:\\爬虫储存\\西瓜视频2\\{}\\{}'.format(old_type, title) + 'dewatermark' + '.mp4'

                with open(filename, "wb") as f:
                    n = 1
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        loaded = n * 1024.0 / content_size
                        f.write(chunk)
                        n += 1
                    Print.info('下载视频: {}'.format(filename))

            if os.path.exists(filename):
                return filename
            else:
                return None

        except Exception as f:
            Print.error(f)

    @staticmethod
    def img_download(img_url, imgfilename):
        try:
            # 传入图片地址, oss名称
            with closing(requests.get(img_url, stream=True)) as r:
                chunk_size = 1024
                # 文件格式
                img_filename = imgfilename + '.cover'
                with open(img_filename, "wb") as f:
                    n = 1
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        n += 1
            return img_filename

        except Exception as f:
            Print.error(f)

    @staticmethod
    def dewatermark(width, height, y, w, h, excursion, filename, dewatermarkname):
        try:
            # 分别传入: 视频帧宽，帧高，水印位置定位的：y值，w值，h值，w偏移值，去水印视频，去水印后的视频文件名字
            dewatermarkname = dewatermarkname + '.mp4'
            os.system('''C:\\Users\\nemo\\Desktop\\VideoSpider\\deeimg2\\bin\\ffmpeg -i {} -filter_complex "delogo=x={}:y={}:w={}:h={}:show=0" {}'''.
                      format(filename, int(width) - excursion, y, w, h, dewatermarkname))

            # if os.path.exists(dewatermarkname):
            #     os.remove(filename)
            return dewatermarkname
            # else:
            #     return None

        except Exception as f:
            Print.error(f)

    @staticmethod
    def oss_upload(osskey, filename, uploadpath, de_suffix=True):
        try:
            # 当 de_suffix 是Ture，使用正则把文件的后缀去掉
            if de_suffix is True:
                osskey = re.match(r'\w+', filename).group()

            # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
            auth = oss2.Auth(ACCESSKEYID, ACCESSKEYSECRET)
            # Endpoint以杭州为例，其它Region请按实际情况填写。
            bucket = oss2.Bucket(auth, ENDPOINT, BUCKETNAME)

            key = uploadpath + osskey
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

        except Exception as f:
            Print.error(f)

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

    @staticmethod
    def get_video_size(dowonload_url):
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

            size_filename = sign + '.jpg'

            cv2.imwrite(size_filename, frame)
            img = Image.open(size_filename)
            width = img.size[0]
            height = img.size[1]

            return size_filename, width, height

        except Exception as f:
            Print.error(f)
            return False

    @staticmethod
    def submit_ranscoding(filename):
        access_key_id = 'LTAI2aU1LjHOWKZf'
        access_key_secret = 'fe1L3bkeucrrEFnaJbDC5woepupNAv'
        mps_region_id = 'cn-hangzhou'
        pipeline_id = '264990a3db2b4670812fed84e9d12256'
        template_id = 'fae77e4045aa4fa58185619fcf1d341e'
        oss_location = 'oss-cn-hangzhou'
        oss_bucket = 'jiuban-image'
        oss_input_object = 'video/' + str(filename)
        oss_output_object = 'video/' + str(filename)

        # 创建AcsClient实例
        client = AcsClient(access_key_id, access_key_secret, mps_region_id)

        # 创建request，并设置参数
        request = SubmitJobsRequest.SubmitJobsRequest()
        request.set_accept_format('json')
        # # Input
        job_input = {'Location': oss_location,
                     'Bucket': oss_bucket,
                     'Object': quote(oss_input_object)}
        #
        request.set_Input(json.dumps(job_input))

        # # Output
        output = {'OutputObject': quote(oss_output_object)}

        # Ouput->TemplateId
        output['TemplateId'] = template_id
        outputs = [output]
        request.set_Outputs(json.dumps(outputs))
        request.set_OutputBucket(oss_bucket)
        request.set_OutputLocation(oss_location)

        # PipelineId
        request.set_PipelineId(pipeline_id)

        # 发起API请求并显示返回值
        response_str = client.do_action_with_exception(request)
        response = json.loads(response_str)
        if response['JobResultList']['JobResult'][0]['Success']:
            print(response['JobResultList']['JobResult'][0]['Job']['JobId'])
            return [True, response['JobResultList']['JobResult'][0]['Job']['JobId']]
        else:
            print(response['JobResultList']['JobResult'][0]['Message'])
            return [False, response['JobResultList']['JobResult'][0]['Message']]



# obj = IduoliaoTool()
# obj.submit_ranscoding('videoaddtest3')








