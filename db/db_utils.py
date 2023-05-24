# -*- coding:utf-8 -*-
# title           :db_utils.py
# description     :数据库工具类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from common.sqlite_executor import SqliteExecutor
import datetime


def get_timestamp(ts=None):
    """
    获取时间戳（默认当前的时间戳）
    :return: 返回16位整数
    """
    if ts is None:
        ts = datetime.datetime.now().timestamp()
        return int(ts * 1000000)
    else:
        num_len = len(str(int(ts)))
        return int(ts * pow(10, 16 - num_len))


def get_timestamp_str(ts=None, fmt="%Y-%m-%d %H:%M:%S.%f"):
    """
    获取当前时间文本
    :param ts:
    :param fmt:
    :return:
    """
    if ts is None:
        ts = get_timestamp()
    d = datetime.datetime.fromtimestamp(ts / 1000000)
    str1 = d.strftime(fmt)
    return str1


def execute_sql(sql, params=[]):
    """
    执行 SQL，返回数据影响的行数
    :param sql: SQL
    :param params: 参数列表
    :return: 返回数据影响的行数
    """
    executor = SqliteExecutor()
    conn = executor.conn
    result = conn.execute(sql, params)
    conn.commit()
    return result.rowcount


def execute_sqls(sql_params_list):
    """
    执行 SQL 列表，返回数据影响的行数和
    :param sql_params_list: SQL 和参 数的列表
        格式为：(sql, params)
          比如： ("INSERT OR REPLACE INTO ... VALUES(?,?,?)" , [1, 2, 3])
    :return: 返回数据影响的行数和
    """
    executor = SqliteExecutor()
    conn = executor.conn
    rowcount = 0
    for sql, params in sql_params_list:
        result = conn.execute(sql, params)
        rowcount += result.rowcount
    conn.commit()
    return rowcount


def execute_ddl(ddl, params=[]):
    """
    执行 DDL 语句，比如：创建表
    :param ddl:
    :param params:
    :return:
    """
    executor = SqliteExecutor()
    conn = executor.conn
    result = conn.execute(ddl, params)
    conn.commit()
    return result


def select_sql(sql, params=[]):
    """
    查询SQL
    :param sql: SELECT SQL
    :param params: 参数
    :return:
    """
    executor = SqliteExecutor()
    return executor.select_sql(sql, params)


def df_to_entities(df, entity_cls=None):
    """
    DataFrame 转为 指定实体类集合
    :param df: pandas.DataFrame
    :param entity_cls: 指定类型
    :return:
    """
    if entity_cls is None:
        return df

    rows = df.itertuples(index=False)
    my_objs = []  # [entity_cls(*row) for row in rows]

    for row in rows:
        my_obj = entity_cls(*row)
        my_objs.append(my_obj)

    return my_objs


def df_to_entity(df, entity_cls=None):
    """
    DataFrame 转为 指定实体类
    :param df: pandas.DataFrame
    :param entity_cls: 指定类型
    :return:
    """
    if df.empty:
        return None

    if entity_cls is None:
        return df

    entities = df_to_entities(df, entity_cls)
    return entities[0]


def sql_to_entities(sql, params=[], entity_cls=None):
    """
    SQL 转为 指定实体类列表
    :param sql: SELECT SQL
    :param params: 参数
    :param entity_cls: 指定类型
    :return:
    """
    df = select_sql(sql, params)
    return df_to_entities(df, entity_cls)


def sql_to_entity(sql, params=[], entity_cls=None):
    """
    SQL 转为 指定实体类
    :param sql: SELECT SQL
    :param params: 参数
    :param entity_cls: 指定类型
    :return:
    """
    df = select_sql(sql, params)
    return df_to_entity(df, entity_cls)


def insert_return_id(sql, params):
    """
    新增数据，并返回自动编号
    :param sql: INSERT INTO SQL
    :param params: 参数
    :return:
    """
    executor = SqliteExecutor()
    conn = executor.conn
    cursor = conn.cursor()
    cursor.execute(sql, params)
    row_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return row_id


# # import sqlite3
# # from dataclasses import dataclass, field
# # from typing import List
#
#
# # 定义一个使用 @dataclass 装饰器的类
# # @dataclass
# # class Person:
# #     id: int
# #     name: str
# #     age: int
# #     email: str = field(default='')
# #
# #
# # # 数据库文件名
# # db_file = 'example.db'
# #
# # # 连接数据库
# # conn = sqlite3.connect(db_file)
#
#
# 定义一个函数来生成CREATE TABLE语句
def get_create_table_sql(table_name, data_class):
    """
    获取生成表的 DLL 语句
    :param table_name:
    :param data_class:
    :return:
    """
    # 获取类的属性名和类型
    attrs = [(attr, type(getattr(data_class, attr)).__name__) for attr in data_class.__annotations__]
    # 拼接SQL语句
    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join([f'{attr} {attr_type}' for attr, attr_type in attrs])})"
    return sql


#
#
# 定义一个函数来生成INSERT INTO语句
def get_insert_sql(table_name, data):
    """
    获取表的 INSERT INTO 语句
    :param table_name:
    :param data:
    :return:
    """
    # 获取数据类的所有属性名
    attrs = data.__annotations__.keys()
    # 获取数据类的所有属性值
    values = [getattr(data, attr) for attr in attrs]
    # 拼接SQL语句
    sql = f"INSERT INTO `{table_name}` ({', '.join(attrs)}) VALUES ({', '.join(['?' for _ in values])})"
    return sql, values


#
#
# 定义一个函数来生成UPDATE语句
def get_update_sql(table_name, data, id):
    """
    获取表的 UPDATE 语句
    :param table_name:
    :param data:
    :param id:
    :return:
    """
    # 获取数据类的所有属性名
    attrs = data.__annotations__.keys()
    # 获取数据类的所有属性值
    values = [getattr(data, attr) for attr in attrs]
    # 拼接SQL语句
    sql = f"UPDATE `{table_name}` SET {', '.join([f'{attr}=?' for attr in attrs])} WHERE id=?"
    values.append(id)
    return sql, values


# 定义一个函数来生成SELECT语句
def get_select_sql(table_name, id):
    """
    获取表的 SELECT 语句
    :param table_name:
    :param id:
    :return:
    """
    # 拼接SQL语句
    sql = f"SELECT * FROM {table_name} WHERE id=?"
    return sql, (id,)


if __name__ == '__main__':
    # print(get_timestamp_str())
    print(get_timestamp(1684119986386533))
    print(get_timestamp(1684119986386))
    print(get_timestamp(1684119986.386533))
    # from db.entities import Session
    # from db.entities import History
    #
    # sql = get_update_sql('t_session', Session, "_id")
    # print(sql)

#
#

#
#     from db.entities import Session
#     from db.entities import History
#     # from common.sqlite_executor import SqliteExecutor
#     # executor = SqliteExecutor()
# #
# #     sql = create_table_sql('t_session', Session)
#     sql = insert_sql('t_session', Session)
# #
#     # sql = "CREATE TABLE t_history (_id INTEGER primary key autoincrement,session_id INTEGER, ts INTEGER, role varchar(50), content BLOB, content_len int, is_deleted int)"
#     # sql = "CREATE TABLE IF NOT EXISTS t_session (id INTEGER primary key autoincrement, ts INTEGER, subject varchar(100), desc  varchar(500), is_deleted int)"
#     # executor.conn.execute(sql)
#     # executor.conn.commit()
#     # executor.conn.close()
# #
# #
# #     # executor.conn.execute(('INSERT INTO t_history (_id, ts, role, content, content_len, is_deleted) VALUES (?, ?, ?, ?, ?, ?)', [0, 1559091077934358528, '', '', 0, 0]))
#     print(sql)
#
# #
# # # 生成CREATE TABLE语句并执行
# # sql = create_table_sql('person', Person)
# # conn.execute(sql)
# #
# # # 创建一个Person实例并插入到数据库中
# # person = Person(id=1, name='张三', age=18, email='zhangsan@example.com')
# # sql, values = insert_sql('person', person)
# # conn.execute(sql, values)
# #
# # # 更新一个Person实例并更新到数据库中
# # person.age = 20
# # sql, values = update_sql('person', person, 1)
# # conn.execute(sql, values)
# #
# # # 从数据库中查询一个Person实例
# # sql, values = select_sql('person', 1)
# # cursor = conn.execute(sql, values)
# # result = cursor.fetchone()
# # print(result)
# #
# # # 关闭连接
# # conn.close()
