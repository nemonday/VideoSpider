import jieba
import pymysql

from VideoSpider.settings import *

connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )

cursor = connection.cursor()

def jieba_ping():
    # 传入爬虫item
    sql = 'select title, video_type, match_type, id from tb_spider_video'
    cursor.execute(sql)

    for videos in cursor.fetchall():
        sql3 = """update tb_spider_video set match_type='%s' where id='%s'""" % (videos[1], videos[3])
        cursor.execute(sql3)
        connection.commit()


jieba_ping()