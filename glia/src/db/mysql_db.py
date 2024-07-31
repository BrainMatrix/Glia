"""

pip install pymysql

"""

from math import e
import os
import re
import subprocess

from openai import OpenAI
from translate import Translator
import redis
import pymysql


from glia.src.handler.global_exception_handler import exception_handler

class MySQLDatabase:
    def __init__(self, host, database, user, password):
        """
        初始化数据库连接
        :param host: 数据库主机地址
        :param database: 数据库名
        :param user: 数据库用户
        :param password: 数据库密码
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.connect()
        self.cursor = self.connection.cursor()

    @exception_handler.handle_exceptions
    def connect(self):
        """
        建立数据库连接
        """
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        if self.connection.is_connected():
            print("连接成功")

    def close_connection(self):
        """
        关闭数据库连接
        """
        if self.connection.is_connected():
            self.connection.close()
            print("连接已关闭")
        if self.cursor:
            self.cursor.close()

    @exception_handler.handle_exceptions
    def execute_query(self, query):
        """
        执行一个查询并返回结果
        :param query: 要执行的SQL查询
        :return: 查询结果
        """
        self.cursor = self.connection.cursor()

        # 如果是查询语句，则返回结果
        if query.strip().lower().startswith("select"):
            result = self.cursor.fetchall()
            return result
        # 如果是其他语句，则提交更改
        else:
            self.connection.commit()
            return self.cursor.rowcount  # 返回影响的行数


# 使用示例
if __name__ == "__main__":
    db = MySQLDatabase("localhost", "mydatabase", "myuser", "mypassword")

    # 查询示例
    query = "SELECT * FROM mytable"
    results = db.execute_query(query)
    for row in results:
        print(row)

    # 更新示例
    update_query = "UPDATE mytable SET column1='value1' WHERE id=1"
    rows_affected = db.execute_query(update_query)
    print(f"Rows affected: {rows_affected}")

    # 关闭数据库连接
    db.close_connection()
