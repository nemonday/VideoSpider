import time

import pymysql
import schedule
from VideoMatch.settings import User_Agent_list, MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORK, MYSQL_DATABASE

connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )


def match_mysql():
    user_cursor = connection.cursor()
    sql0 = 'update tb_spider_user set work_num=0'
    user_cursor.execute(sql0)
    connection.commit()
    for i in range(3):
        sql = 'SELECT user_id, user_name, small_type, big_type, work_num FROM tb_spider_user where work_num <=3'
        user_cursor.execute(sql)

        video_cursor = connection.cursor()
        for video in user_cursor.fetchall():
            sql = """SELECT match_type, id, video_type FROM tb_spider_video where status = 3 and match_type = '%s' and match_status=0  limit 1"""% (video[2])
            video_cursor.execute(sql)
            video_data = video_cursor.fetchall()

            if video_data:
                match_mysql_keyword(video, video_data[0])
            else:
                match_mysql_notkeyword(video)

    user_cursor.close()
    video_cursor.close()


def match_mysql_keyword(video, video_data):
    video_cursor3 = connection.cursor()
    sql3 = """UPDATE tb_spider_video SET user_name='%s', user_id='%s', match_status=1 where id = '%s'""" % (video[1], video[0], video_data[1])
    video_cursor3.execute(sql3)
    connection.commit()

    sql6 = """UPDATE tb_spider_user SET work_num = '%s' where user_id = '%s'""" % (video[4] + 1, video[0])
    video_cursor3.execute(sql6)
    connection.commit()
    video_cursor3.close()


def match_mysql_notkeyword(video):
    video_cursor4 = connection.cursor()
    sql4 = """SELECT match_type, id, video_type FROM tb_spider_video where status = 3 and match_type = '%s' and match_status=0  limit 1""" % (video[3])
    video_cursor4.execute(sql4)
    video_data = video_cursor4.fetchall()
    if video_data:
        sql5 = """UPDATE tb_spider_video SET user_name='%s', user_id='%s', match_status=1 where id = '%s'""" % (video[1], video[0], video_data[0][1])
        video_cursor4.execute(sql5)
        connection.commit()

        sql6 = """UPDATE tb_spider_user SET work_num = '%s' where user_id = '%s'""" % (video[4] + 1, video[0])
        video_cursor4.execute(sql6)
        connection.commit()
        video_cursor4.close()


schedule.every().day.at("07:30").do(match_mysql)

while True:
    schedule.run_pending()
    time.sleep(1)

