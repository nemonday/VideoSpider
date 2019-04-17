import pymysql
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import json

app = Flask(__name__)
# api = Api(app)

# MYSQL_HOST = 'rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com'
# MYSQL_PORT = 3306
# MYSQL_USERNAME = 'migration_test'
# MYSQL_PASSWORK = 'migrationTest*'
# MYSQL_DATABASE = 'db_nt_video'

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USERNAME = 'splider'
MYSQL_PASSWORK = 'gz_#@splider@2019'
MYSQL_DATABASE = 'db_nt_video'

connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )


def match_mysql_keyword( video, video_data):
    try:
        connection.ping()

        video_cursor3 = connection.cursor()
        sql3 = """UPDATE tb_spider_video SET user_name='%s', user_id='%s', match_status=1 where id = '%s'""" % (
            video[1], video[0], video_data[1])
        video_cursor3.execute(sql3)
        connection.commit()

        sql6 = """UPDATE tb_spider_user SET work_num = '%s' where user_id = '%s'""" % (video[4] + 1, video[0])
        video_cursor3.execute(sql6)
        connection.commit()
        video_cursor3.close()

        return True
    except:
        connection()


def match_mysql_notkeyword( video):
    try:
        connection.ping()

        video_cursor4 = connection.cursor()
        sql4 = """SELECT match_type, id, video_type FROM tb_spider_video where status = 3 and match_type = '%s' and match_status=0  limit 1""" % (
            video[3])
        video_cursor4.execute(sql4)
        video_data = video_cursor4.fetchall()
        if video_data:
            sql5 = """UPDATE tb_spider_video SET user_name='%s', user_id='%s', match_status=1 where id = '%s'""" % (
                video[1], video[0], video_data[0][1])
            video_cursor4.execute(sql5)
            connection.commit()

            sql6 = """UPDATE tb_spider_user SET work_num = '%s' where user_id = '%s'""" % (video[4] + 1, video[0])
            video_cursor4.execute(sql6)
            connection.commit()
            video_cursor4.close()

        return True
    except:
        connection()

def add(user_id, user_name, add_num):
    try:
        connection.ping()
        user_cursor = connection.cursor()

        for i in range(0, add_num):
            sql = """SELECT user_id, user_name, small_type, big_type, work_num FROM tb_spider_user where user_id = '%s' and user_name = '%s' """ % (
                user_id, user_name)
            user_cursor.execute(sql)
            video_cursor = connection.cursor()
            for video in user_cursor.fetchall():
                sql = """SELECT match_type, id, video_type FROM tb_spider_video where status = 3 and match_type = '%s' and match_status=0  limit 1""" % (
                    video[2])
                video_cursor.execute(sql)
                video_data = video_cursor.fetchall()

                if video_data:
                    is_data = match_mysql_keyword(video, video_data[0])
                    return is_data
                else:
                    is_data = match_mysql_notkeyword(video)
                    return is_data

    except Exception as f:
        print(f)
        connection.rollback()
        connection()

        return False
    
    
@app.route('/python/videos/uid=<int:user_id>/uname=<user_name>/addnum=<int:add_num>', methods=['GET'])
def hello_world(user_id, user_name, add_num):
    is_ture = add(user_id, user_name, add_num)
    if is_ture is True:
        return json.dumps({'status': 1})
    elif is_ture is False:
        return json.dumps({'status': 2})
    elif is_ture is None:
        return json.dumps({'status': 3})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)