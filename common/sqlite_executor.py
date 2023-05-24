# -*- coding:utf-8 -*-
# title           :sqlite_executor.py
# description     :SqliteExecutor
# author          :Python超人
# date            :2023-3-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import sqlite3
import pandas as pd

from common.app_config import DB_NAME
from common.ui_utils import find_file
import os


class SqliteExecutor:
    """
    SqliteExecutor
    """

    def find_data_dir(self):
        """
        查找数据库文件的目录 data
        :return:
        """
        data_dir = "data"
        if os.path.exists(data_dir):
            return os.path.normpath(data_dir)

        for i in range(3):
            data_dir = os.path.join("..", data_dir)
            if os.path.exists(data_dir):
                return os.path.normpath(data_dir)

        return None

    def __init__(self, db_file=None):
        """

        :param db_file: 默认内存
        """
        # db_file = ':memory:'
        if db_file is None:
            db_file = find_file(DB_NAME, "data", raise_exception=False)
            if db_file is None:
                # db_file = os.path.join("data", DB_NAME)
                data_dir = self.find_data_dir()
                if data_dir is None:
                    raise Exception(f"data目录没有找到")
                db_file = os.path.join(data_dir, DB_NAME)
                # os.path.realpath(db_file)
        # 创建与数据库的连接
        # 连接到SQLite数据库

        # 数据库文件是 chatgpt.db，如果文件不存在，会自动在当前目录创建
        self.conn = sqlite3.connect(db_file)

    def select_sql(self, sql, params=[]):
        """
        查询SQL
        :param sql: SELECT SQL
        :param params: 参数
        :return:
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        # result1 = cursor.fetchone()  # 使用fetchone()方法查询一条数据
        # print(result1)
        #
        # result2 = cursor.fetchmany(2)  # 使用fetchmany()方法查询多条数据
        # print(result2)
        #
        # result3 = cursor.fetchall()  # 使用fetchall(方法查询全部数据
        # print(result3)

        cols = []

        for col in cursor.description:
            cols.append(col[0])

        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=cols)

        # 关闭游标
        cursor.close()

        # 关闭Connection
        # self.conn.close()
        return df

    def insert(self, sql):
        self.conn.execute(sql)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


if __name__ == '__main__':

    executor = SqliteExecutor(f"../data/{DB_NAME}")
    # executor.create_table()
