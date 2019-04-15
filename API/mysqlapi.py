import pymysql
from flask import Flask
import json
from flask import request

from flask_restful import reqparse, abort, Api, Resource

from API.setting import *

app = Flask(__name__)

api = Api(app)


# MYSQL_HOST = 'rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com'
# MYSQL_PORT = 3306
# MYSQL_USERNAME = 'migration_test'
# MYSQL_PASSWORK = 'migrationTest*'
# MYSQL_DATABASE = 'db_nt_video'

connection = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USERNAME,
    password=MYSQL_PASSWORK,
    db=MYSQL_DATABASE,
    charset='utf8'
)



def match_mysql_keyword(video, video_data):
    video_cursor3 = connection.cursor()
    sql3 = """UPDATE tb_spider_video SET user_name='%s', user_id='%s', match_status=1 where id = '%s'""" % (video[1], video[0], video_data[1])
    video_cursor3.execute(sql3)
    connection.commit()

    sql6 = """UPDATE tb_spider_user SET work_num = '%s' where user_id = '%s'""" % (video[4] + 1, video[0])
    video_cursor3.execute(sql6)
    connection.commit()
    video_cursor3.close()

    return True


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

    return True


def add_works(user_id, user_name, add_num):
    user_cursor = connection.cursor()
    try:
        for i in range(0, add_num):
            sql = """SELECT user_id, user_name, small_type, big_type, work_num FROM tb_spider_user where user_id = '%s' and user_name = '%s' """ % (
                user_id, user_name)
            user_cursor.execute(sql)
            video_cursor = connection.cursor()
            for video in user_cursor.fetchall():
                sql = """SELECT match_type, id, video_type FROM tb_spider_video where status = 3 and match_type = '%s' and match_status=0  limit 1""" % (video[2])
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
        return False


class MysqlApi(object):

    @app.route("/python/videos/uid=<int:user_id>&uname=<user_name>&addnum=<int:add_num>", methods=['GET'])
    def add_works(user_id, user_name, add_num):
        is_ture = add_works(user_id, user_name, add_num)

        if is_ture is True:
            return json.dumps({'status': 1})
        elif is_ture is False:
            return json.dumps({'status': 2})
        elif is_ture is None:
            return json.dumps({'status': 3})

    @app.after_request
    def after_request(response):
        # response.headers.add("Access-Control-Allow-Origin", "*")
        # response.headers.add("Access-Control-Allow-Methods", "*")
        # 这里不能使用add方法，否则会出现 The 'Access-Control-Allow-Origin' header contains multiple values 的问题
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = '*'
        # response.headers['Access-Control-Allow-Headers'] = 'Origin, No-Cache, X-Requested-With, If-Modified-Since, Pragma, Last-Modified, Cache-Control, Expires, Content-Type, X-E4M-With,userId,token,Access-Control-Allow-Headers'
        # response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    def run(self):
        app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    proxyProvider = MysqlApi()
    proxyProvider.run()




