# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymysql.cursors
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class NewcgspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class NewspiderImagePipeline(ImagesPipeline):
    # 重写方法可从result中获得图片下载的实际地址
    def item_completed(self, results, item, info):
        for ok,value in results:
            image_file_path = value['path']
        item['img'] =  image_file_path
        return item


class NewspiderMysqlPipeline(object):
    '''
    简版的数据入库方式，有缺陷，同步操作，会造成数据阻塞。
    在数据解析速度更快的时候，数据库中数据越来越多的时候，会阻塞数据入库的速度。
    '''
    # 初始化信息
    def __init__(self):
        self.conn = pymysql.connect(
            host='192.168.30.111',
            database='spiderInc',
            user='root',
            password='123456',
            charset='utf8',
            port=3306,
            use_unicode=True
        )
        self.cursor = self.conn.cursor()

    def process_item(self,item,spider):
        sql_insert = 'replace into NewCG_ae(path,name,time) values (%s,%s,%s);'
        self.cursor.execute(sql_insert,(item['img'],item['tital'],item['time']))
        self.conn.commit()

class MysqlTwistedPipeline(object):

    def __init__(self,dbpool):
        self.dbpool = dbpool

    @staticmethod
    def get_setting(cls, settings):
        '''
        获取setting文件中的信息,加载为异步获取连接池，增加系统的动态扩容性
        :param self:
        :return:
        '''
        db_parms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        # 连接池ConnectionPool
        dbpool = adbapi.ConnectionPool("pymysql", **db_parms)

        return cls(dbpool)

    def process_item(self,item,spider):
        '''
        使用twisted 将mysql插入编程异步执行
        :param item:
        :param spider:
        :return:
        '''
        # 执行数据插入的方法：参数1：执行逻辑，参数2：逻辑数据
        query = self.dbpool.runInteraction(self.do_insert,item)
        # 将异步错误，进行处理
        query.addErrback(self.handle_error,item,spider)


    def handle_error(self,failure,item,spider):
         '''
         将异步执行的异常进行处理
         :param failure: 错误信息
         :param item: 执行错误的数据
         :param spider: 获取的数据信息
         :return:
         '''
         print(failure)

    def do_insert(self,cursor,item):
        '''
        执行具体的插入
        :param cursor: 在dbpool中获得的游标
        :param item: 获取的数据
        :return: 返回数据插入的结果
        '''
        sql_insert = 'replace into NewCG_ae(path,name,time) values (%s,%s,%s);'
        cursor.execute(sql_insert, (item['img'], item['tital'], item['time']))

