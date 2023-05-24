# -*- coding:utf-8 -*-
# title           :session_op.py
# description     :聊天会话数据库操作类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from db.db_utils import execute_ddl, execute_sql, insert_return_id, get_timestamp, select_sql
from common.str_utils import is_empty


class SessionOp:
    @classmethod
    def insert(cls, subject, model_id='gpt-3.5-turbo', create_time=None):
        """
        插入数据
        :param subject: 聊天会话标题
        :param model_id: 聊天会话使用的模型ID
        :param create_time: 创建时间
        :return:
        """
        if create_time is None:
            create_time = get_timestamp()
        row_id = insert_return_id(
            'INSERT INTO `t_session` (`ts`, `subject`, `model_id`, `order_no`, `category_id`, `is_top`, `is_deleted`) '
            'VALUES (?, ?, ?, 0, 0, 0, 0)', (create_time, subject, model_id)
        )
        return row_id

    @classmethod
    def delete(cls, id):
        """
        逻辑删除指定的聊天会话
        :param id: 聊天会话ID
        :return:
        """
        return execute_sql('UPDATE `t_session` SET is_deleted=? WHERE _id=?', [1, id])

    @classmethod
    def delete_ids(cls, ids):
        """
        批量逻辑删除指定的聊天会话
        :param ids: 聊天会话ID集合
        :return:
        """
        sql = 'UPDATE `t_session` SET is_deleted=? WHERE _id in ({})'.format(','.join(['?'] * len(ids)))  # , [1] + ids
        return execute_sql(sql, [1] + list(ids))

    @classmethod
    def force_delete_ids(cls, ids):
        """
        批量强制删除指定的聊天会话
        :param ids: 聊天会话ID集合
        :return:
        """
        sql = 'DELETE FROM `t_session` WHERE is_deleted=? AND _id in ({})'.format(
            ','.join(['?'] * len(ids)))  # , [1] + ids
        return execute_sql(sql, [1] + list(ids))

    @classmethod
    def restore(cls, id):
        """
        还原逻辑删除的聊天会话
        :param id: 聊天会话ID
        :return:
        """
        return execute_sql('UPDATE `t_session` SET is_deleted=? WHERE _id=?', [0, id])

    @classmethod
    def restore_ids(cls, ids):
        """
        批量还原逻辑删除的聊天会话
        :param ids: 聊天会话ID集合
        :return:
        """
        sql = 'UPDATE `t_session` SET is_deleted=? WHERE is_deleted=? AND _id in ({})'.format(
            ','.join(['?'] * len(ids)))  # , [1] + ids
        return execute_sql(sql, [0, 1] + list(ids))

    @classmethod
    def force_delete(cls, id):
        """
        强行删除指定的聊天会话
        :param id: 聊天会话ID
        :return:
        """
        return execute_sql('DELETE FROM `t_session` WHERE _id=?', [id])

    @classmethod
    def update(cls, id, subject, desc=None):
        """
        修改指定的聊天会话
        :param id: 聊天会话ID
        :param subject: 聊天会话标题
        :param desc: 聊天会话描述
        :return:
        """
        if desc is None:
            return execute_sql('UPDATE `t_session` SET subject=? WHERE _id=?', (subject, id))

        return execute_sql('UPDATE `t_session` SET subject=?, `desc`=? WHERE _id=?', (subject, desc, id))

    @classmethod
    def update_category(cls, id, category_id):
        """
        修改聊天会话的类别
        :param id: 聊天会话ID
        :param category_id: 聊天话题类别ID
        :return:
        """
        return execute_sql('UPDATE `t_session` SET category_id=? WHERE _id=?', [category_id, id])

    @classmethod
    def update_settings(cls, id, settings):
        """
        修改聊天会话的设置信息
        :param id: 聊天会话ID
        :param settings: 设置信息
        :return:
        """
        return execute_sql('UPDATE `t_session` SET settings=? WHERE _id=?', [settings, id])

    @classmethod
    def update_model(cls, id, model_id):
        """
        修改聊天会话的模型
        :param id: 聊天会话ID
        :param model_id: 模型ID
        :return:
        """
        return execute_sql('UPDATE `t_session` SET model_id=? WHERE _id=?', [model_id, id])

    @classmethod
    def topping(cls, id):
        """
        置顶聊天会话
        :param id: 聊天会话ID
        :return:
        """
        return execute_sql('UPDATE `t_session` SET is_top=? WHERE _id=?', [1, id])

    @classmethod
    def cancel_topping(cls, id):
        """
        取消聊天会话的置顶
        :param id: 聊天会话ID
        :return:
        """
        return execute_sql('UPDATE `t_session` SET is_top=? WHERE _id=?', [0, id])

    @classmethod
    def update_order_no(cls, id, order_no):
        """
        更新聊天会话的排序
        :param id: 聊天会话ID
        :param order_no: 排序号
        :return:
        """
        return execute_sql('UPDATE `t_session` SET order_no=? WHERE _id=?', [order_no, id])

    @classmethod
    def select(cls, id, entity_cls=None):
        """
        获取指定的聊天会话
        :param id: 聊天会话ID
        :param entity_cls:
        :return:
        """
        df = select_sql('SELECT * FROM `t_session` WHERE _id=?', [id])

        if df.empty:
            return None

        if entity_cls is None:
            return df

        rows = df.itertuples(index=False)
        my_objs = []  # [entity_cls(*row) for row in rows]

        for row in rows:
            my_obj = entity_cls(*row)
            my_objs.append(my_obj)

        return my_objs[0]

    @classmethod
    def clear_empty_session(cls):
        """
        清除空会话，没有历史记录的，为了防止删除刚刚新建的会话，指定了删除条件：days=1.5 就是36个小时内的不清除
        :return:
        """
        """
SELECT s._id, datetime(s.ts/1000000,'unixepoch','localtime'),CAST((julianday('now') - 2440587.5)*86400 AS INTEGER)
FROM t_session s
WHERE _id NOT IN (SELECT session_id FROM t_history) AND s.ts<CAST((julianday('now') - 2440587.5-1)*86400000000 AS INTEGER)
        """
        days = 1.5  # 清除空会话，days=1.5就是36个小时内的不清除
        sql = f"""
DELETE FROM t_session
WHERE _id NOT IN (SELECT session_id FROM t_history) 
    AND ts<CAST((julianday('now') - 2440587.5-?)*86400000000 AS INTEGER)
        """
        execute_sql(sql, [days])

    @classmethod
    def get_chat_histories(cls, keyword=None, category_id=None):
        """
        根据关键字搜索聊天历史
        :param keyword: 关键字
        :return:
        """
        if is_empty(keyword):
            keyword_search = ""
        else:
            keyword_search = f" AND t.content LIKE '%{keyword}%'"

        if category_id is not None:
            where_string = f" AND s.category_id={category_id}"
        else:
            where_string = ""

        sql = f"""
SELECT 
        MAX(h_id) history_id,datetime(ts/1000000, 'unixepoch', 'localtime') date_time,
        session_id,subject,content,SUM(content_len) content_size,settings
FROM (
	SELECT h._id h_id, h.session_id,h.ts, s.subject,s.settings, h.content, h.content_len
	FROM (SELECT t.*,t.content_len FROM t_history t WHERE t.is_deleted=0 {keyword_search}) h 
	    INNER JOIN t_session s ON h.session_id=s._id AND s.is_deleted=0 {where_string}
) t GROUP BY session_id ORDER BY ts DESC"""
        df = select_sql(sql)
        # print(df)
        return df

    @classmethod
    def get_deleted_chat_histories(cls, keyword=None):
        """
        根据关键字搜索已经逻辑删除的聊天历史
        :param keyword: 关键字
        :return:
        """
        if is_empty(keyword):
            keyword_search = ""
        else:
            keyword_search = f" WHERE t.content LIKE '%{keyword}%'"
        sql = f"""
SELECT 
        MAX(h_id) history_id,datetime(ts/1000000, 'unixepoch', 'localtime') date_time,
        session_id,subject,content,SUM(content_len) content_size
FROM (
    SELECT h._id h_id, h.session_id,h.ts, s.subject, h.content, h.content_len
    FROM (SELECT t.*,t.content_len FROM t_history t{keyword_search}) h 
        INNER JOIN t_session s ON h.session_id=s._id AND s.is_deleted=1 
) t GROUP BY session_id ORDER BY ts DESC"""
        df = select_sql(sql)
        # print(df)
        return df

    @classmethod
    def delete_empty_session(cls, id):
        """
        删除空的会话(一般为打开聊天窗口，但没有聊天就关闭的窗口)
        :param id: 聊天会话ID
        :return:
        """
        # df = select_sql('SELECT * FROM `t_session` WHERE _id=?', [id])
        sql = 'SELECT ? session_id, COUNT(1) his_count FROM `t_history` WHERE session_id=?'
        sql = f'SELECT session_id FROM ({sql}) t WHERE t.his_count=0'
        sql = f'DELETE FROM `t_session` WHERE _id IN ({sql})'
        execute_sql(sql, [id, id])

    @classmethod
    def create_table(cls):
        """
        创建表
        :return:
        """
        ddl = """CREATE TABLE IF NOT EXISTS `t_session` (
        `_id` INTEGER primary key autoincrement, 
        `ts` INTEGER, 
        `subject` varchar(100), 
        `settings` BLOB, 
        `model_id`  varchar(100), 
        `category_id` int,
        `order_no` int DEFAULT 0,
        `is_top` int DEFAULT 0,        
        `is_deleted` int DEFAULT 0
        )
        """
        return execute_ddl(ddl)


if __name__ == '__main__':
    # SessionOp.delete_empty_session(2)
    # print(SessionOp.get_chat_histories("数学"))
    # result = SessionOp.create_table()
    # row_id = SessionOp.insert(subject="标题", desc="描述")
    #
    #
    # def execute_demo(title, func):
    #     print(f"【{title}】")
    #     print(func())
    #     print(SessionOp.select(row_id))
    #     print("------------------------------------------------------")
    #
    #
    # print(SessionOp.select(row_id))
    # execute_demo("update", lambda: SessionOp.update(id=row_id, subject="标题2", desc="描述2"))
    # execute_demo("topping", lambda: SessionOp.topping(id=row_id))
    # execute_demo("cancel_topping", lambda: SessionOp.cancel_topping(id=row_id))
    # execute_demo("update_order_no", lambda: SessionOp.update_order_no(id=row_id, order_no=10))
    # execute_demo("update_category", lambda: SessionOp.update_category(id=row_id, category_id=1))
    # execute_demo("delete", lambda: SessionOp.delete(id=row_id))
    # execute_demo("restore", lambda: SessionOp.restore(id=row_id))
    # execute_demo("force_delete", lambda: SessionOp.force_delete(id=row_id))
    pass
