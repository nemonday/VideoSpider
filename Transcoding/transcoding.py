import json
import time
from pprint import pprint

import schedule
import pymysql
import redis
from aliyunsdkcore import client
from aliyunsdkmts.request.v20140618 import QueryJobListRequest

from Transcoding.settings import ACCESS_KEY, SECRET_KEY, REGION_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, \
    MYSQL_PASSWORK, MYSQL_DATABASE, REDIS_HOST, REDIS_PORT


def transcoding():

    redis_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=3, decode_responses=True)

    # redis_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=3, password='flrjovlOJEROIJ324', decode_responses=True)

    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORK,
        db=MYSQL_DATABASE,
        charset='utf8'
    )

    access_key = ACCESS_KEY
    secret_key = SECRET_KEY
    region_id = REGION_ID
    clt = client.AcsClient(access_key, secret_key, region_id, True, 3, None)

    request = QueryJobListRequest.QueryJobListRequest()
    request.set_accept_format('json')
    request.set_action_name('QueryJobList')

    cur = connection.cursor()
    try:
        sql = 'select job_id, osskey, id from tb_spider_video where status=2 and match_status=0 limit 100'
        cur.execute(sql)

        for info in cur.fetchall():
            request.set_JobIds(info[0])

            result = clt.do_action(request)
            json_data = json.loads(result.decode('utf-8'))

            # 转码状态
            status = json_data['JobList']['Job'][0]['State']
            # 转码完成的标志
            if status == 'TranscodeSuccess':
                # 转码已经完成，添加到redis当中
                transcode = 1
                # 转码中参数，已经转码成功就无视
                transcoding = 1
                # redis_key
                redis_key = 'muk: {0}0'.format(info[1])
                # 转码后的地址
                tcplayurl = 'https://cdn.img1.iduoliao.cn/video/{0}.m3u8'.format(info[1])
                # 文件大小
                totalSize = json_data['JobList']['Job'][0]['Output']['Properties']['FileSize']
                # 播放时长
                seconds = json_data['JobList']['Job'][0]['Output']['Properties']['Duration']
                m, s = divmod(int(seconds), 60)
                h, m = divmod(m, 60)
                duration = "%02d:%02d:%02d" % (h, m, s)
                # 视频长宽
                width = json_data['JobList']['Job'][0]['Output']['Properties']['Width']
                height = json_data['JobList']['Job'][0]['Output']['Properties']['Height']
                # 相关信息
                mediaInfo = json.dumps({
                    "duration": "{}".format(
                        json_data['JobList']['Job'][0]['Output']['Properties']['Format']['Duration']),
                    "width": "{}".format(width),
                    "height": "{}".format(height)
                })
                # 位置参数，暂定为1
                ulid = 1
                cover = 1
                # 上传是否完毕
                upload_done = 1
                # jobid
                tcJobId = info[0]

                # hash类型添加进redis
                redis_db.hset(redis_key, 'transcode', transcode)
                redis_db.hset(redis_key, 'transcoding', transcoding)
                redis_db.hset(redis_key, 'tcplayurl', tcplayurl)
                # redis_db.hset(redis_key, 'duration', duration)
                redis_db.hset(redis_key, 'mediaInfo', mediaInfo)
                redis_db.hset(redis_key, 'totalSize', totalSize)
                redis_db.hset(redis_key, 'tcJobId', tcJobId)
                redis_db.hset(redis_key, 'upload_done', upload_done)
                redis_db.hset(redis_key, 'ulid', ulid)
                redis_db.hset(redis_key, 'cover', cover)

                # 构建视频，图片访问地址
                video_url = 'https://cdn.img1.iduoliao.cn/video/{0}.m3u8'.format(info[1])
                img_url = 'https://cdn.img1.iduoliao.cn/img/{0}.cover'.format(info[1])

                # 把视频时长添加到作品当中
                sql2 = 'update tb_spider_video set status=3, video_oss_url="%s", img_oss_url="%s", duration="%s", width="%s", height="%s" where id="%s" and job_id="%s"' % (video_url, img_url, duration, width, height, info[2], info[0])
                cur.execute(sql2)
                connection.commit()
            else:
                pass
        cur.close()
        connection.close()

    except Exception as f:
        print('添加错误')
        print(f)
        connection.rollback()
    cur.close()


# schedule.every(10).minutes.do(transcoding)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

transcoding()