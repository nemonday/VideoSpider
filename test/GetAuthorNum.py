import pymysql

class GetPraise(object):
    def __init__(self):

        self.connection = pymysql.connect(
            host='rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com',
            port=3306,
            user='migration_test',
            password='migrationTest*',
            db='db_nt_video',
            charset='utf8'
        )

    def run(self):
        cursor = self.connection.cursor()
        try:
            sql = """select author from tb_pq_rewarduser"""
            cursor.execute(sql)
            datas = cursor.fetchall()
            author_list = []
            for data in datas:
                if not data in author_list:
                    author_list.append(data)
                else:
                    pass
            print(len(author_list))
        except Exception as f:
            print('添加错误')
            print(f)
            self.connection.rollback()

        cursor.close()


if __name__ == '__main__':
    obj = GetPraise()
    obj.run()
