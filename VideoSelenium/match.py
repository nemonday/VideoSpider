import pymysql

from settings import *

connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORK,
            db=MYSQL_DATABASE,
            charset='utf8'
        )


cursor = connection.cursor()

sql = 'select id, big_type from tb_spider_user'

cursor.execute(sql)

for video in cursor.fetchall():
    if video[1] == '1':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (23, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '12':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (40, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '4':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (30, video[0])
        cursor.execute(sql2)
        connection.commit()


    if video[1] == '5':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (36, video[0])
        cursor.execute(sql2)
        connection.commit()


    if video[1] == '15':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (37, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '8':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (31, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '2':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (29, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '6':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (25, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '3':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (27, video[0])
        cursor.execute(sql2)
        connection.commit()


    if video[1] == '14':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (46, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '11':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (38, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '9':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (26, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '13':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (33, video[0])
        cursor.execute(sql2)
        connection.commit()

    if video[1] == '10':
        sql2 = 'update tb_spider_user set big_type="%s" where id="%s"' % (42, video[0])
        cursor.execute(sql2)
        connection.commit()



