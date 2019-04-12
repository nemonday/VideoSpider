from contextlib import closing

import pymysql
import requests

from settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE
from tool import ky_download


class KyDownload(object):
    def __init__(self):
        self.connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

    def get_info(self):
        urls = []
        cursor = self.connection.cursor()
        sql = 'select url, osskey, id, img , video_type, title, video_from, width, height from tb_spider_video where status=1 and video_from= "开眼视频" limit 10'
        cursor.execute(sql)
        for video in cursor.fetchall():
            urls.append([video[0], video[1], video[2], video[3], video[4], video[5], video[6], video[7], video[8]])

        cursor.close()
        return urls

    def update_mysql(self, video_info):

        cursor = self.connection.cursor()
        video_url = 'https://jiuban-image.oss-cn-hangzhou.aliyuncs.com/video_spider/video/'
        img_url = 'https://jiuban-image.oss-cn-hangzhou.aliyuncs.com/video_spider/img/'

        try:
            sql = 'UPDATE tb_spider_video SET status=3, video_oss_url= "%s", img_oss_url="%s" WHERE id="%s"' % (
                video_url + video_info[1] + '.mp4', img_url + video_info[1]+ '.png', video_info[2]
            )

            # sql2 = 'UPDATE tb_spider_video SET status=4" WHERE video_type="%s"' % ('佳品')
            print("""
                上传成功，修改状态,
                video地址: {}
                img地址: {}
            """.format(video_url + video_info[1] + '.mp4', img_url + video_info[1]+ '.png')
                  )

            cursor.execute(sql)
            self.connection.commit()
        except Exception as f:
            print(f)
            self.connection.rollback()

        cursor.close()

    def run(self):
        video_infos = self.get_info()
        if video_infos:
            for video_info in video_infos:
                headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'identity;q=1, *;q=0',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Connection': 'keep-alive',
                    'Host': 'ali.cdn.kaiyanapp.com',
                    'If-Range': '"0FBCD708BAE3DE0D704CA49694141AB5"',
                    'Range': 'bytes=128122880-128141729',
                    'Referer': 'http://ali.cdn.kaiyanapp.com/1554718119916_0fc4696b.mp4?auth_key=1555044507-0-0-61f4f12ee21c1323cc028c73b539cf8b',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                }

                # self.proxy = requests.get('http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=7&fa=20&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson=')

                with closing(requests.get(video_info[0], stream=True, headers=headers)) as r:
                    chunk_size = 1024
                    filename = video_info[1] + '.mp4'
                    with open(filename, "wb") as f:
                        n = 1
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            f.write(chunk)
                            n += 1
                        num = '\r下载视频: {}  '.format(video_info[1])
                        print(num, end='')




if __name__ == '__main__':
    obj = KyDownload()
    obj.run()