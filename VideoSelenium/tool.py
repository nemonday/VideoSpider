import hashlib
import json
import os
from contextlib import closing
from urllib.request import urlretrieve
import cv2
import jieba
import pymysql
import redis
import requests
from PIL import Image
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
import oss2

from settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE, ACCESSKEYID, \
    ACCESSKEYSECRET, ENDPOINT, BUCKETNAME, UPLOADPATH, UPLOADPATH2

from urllib.parse import quote
from aliyunsdkcore.client import AcsClient
from aliyunsdkmts.request.v20140618 import SubmitJobsRequest

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
        print([width, height, size_filename])
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
        os.system('''ffmpeg -i {} -filter_complex "delogo=x={}:y={}:w={}:h={}:show=0" {}'''.format(filename, int(width) - excursion,y, w, h, deepcopy_filename))
        return True
    except:
        return False


def download(osskey, download_url, is_deepimg=False):
    # 传入oss名称, 下载地址
    # try:
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
    # except:
    #     return False


def download_img(img_url, oss):
    # 传入图片地址, oss名称
    with closing(requests.get(img_url, stream=True)) as r:
        chunk_size = 1024
        img_filename = oss + '.cover'
        with open(img_filename, "wb") as f:
            n = 1
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                n += 1

    return img_filename


def oss_upload(osskey, filename, img_filename):
    if os.path.exists(filename):
        oss(osskey, filename, UPLOADPATH)

    if os.path.exists(img_filename):
        oss(osskey + '.cover', img_filename, UPLOADPATH2)


def get_md5_name(vid, filename):
    videoCapture = cv2.VideoCapture()
    videoCapture.open(filename)

    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
    #fps是帧率，意思是每一秒刷新图片的数量，frames是一整段视频中总的图片数量。
    # print("fps=", fps, "frames=",frames)

    images = []
    filename_img = ''
    for i in range(1, int(frames)):
        ret, frame = videoCapture.read()

        if i == int(frames/4):
            filename_img = '{}.{}.jpg'.format(vid, i)
            cv2.imwrite(filename_img, frame)
            images.append(filename_img)

    for i in images:
        bytes = []
        im = Image.open(i)

        width = im.size[0]
        height = im.size[1]

        try:
            for i in range(0, int(width), int(width/10)):
                for j in range(0, int(height), int(height/10)):
                    # 获取像素点颜色
                    color = im.getpixel((j, i))
                    colorsum = color[0] + color[1] + color[2]
                    bytes.append(colorsum)
        except:
            pass

        if os.path.exists(filename_img):
            os.remove(filename_img)

        md = hashlib.md5()  # 构造一个md5
        md.update(str(bytes).encode())
        # print(md.hexdigest())  # 加密后的字符串
        return md.hexdigest()


def redis_check(md5_name):
    redis_db = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    is_presence = redis_db.zrank('spider', md5_name)
    if is_presence is None:
        mapping = {
            md5_name: 10
        }
        redis_db.zadd('spider', mapping)
        print('添加 {} 到redis当中'.format(md5_name))

        return True

    else:
        print('视频已存在')

        return False


def submit_ranscoding(md5_name):
    access_key_id = 'LTAIeSzXuA4O548o'
    access_key_secret = 'gxQTVohHqcOm3SAIPI0NZIVD1iWSUq'
    mps_region_id = 'cn-hangzhou'
    pipeline_id = '264990a3db2b4670812fed84e9d12256'
    template_id = 'fae77e4045aa4fa58185619fcf1d341e'
    oss_location = 'oss-cn-hangzhou'
    oss_bucket = 'jiuban-image'
    oss_input_object = 'video/' + str(md5_name)
    oss_output_object = 'video/' + str(md5_name)


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
        return [True, response['JobResultList']['JobResult'][0]['Job']['JobId']]
    else:
        return [False, response['JobResultList']['JobResult'][0]['Message']]




