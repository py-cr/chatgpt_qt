# -*- coding:utf-8 -*-
# title           :history_op.py
# description     :聊天历史记录数据库操作类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from db.db_utils import execute_ddl, execute_sql, insert_return_id, get_timestamp, select_sql


class HistoryOp:
    @classmethod
    def insert(cls, role, content, content_type, session_id, status, create_time=None, role_name=None):
        """
        插入聊天记录数据
        :param role: 角色
        :param content: 聊天内容
        :param content_type: 内容类型（text）
        :param session_id: 一个聊天会话ID
        :param status: 状态（0：正常）
        :param create_time: 创建时间
        :param role_name: 角色名称（可以为空，不为空则直接显示）
        :return:
        """
        if create_time is None:
            create_time = get_timestamp()
        if role_name is None:
            role_name = ''  # 为空
        content_len = len(content)
        row_id = insert_return_id(
            'INSERT INTO `t_history` (`ts`, `role`, `role_name`, `content`,`content_type`, `content_len`,'
            '`session_id`, `is_top`,`order_no`, `status`, `is_deleted`)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 0)',
            (create_time, role, role_name, content, content_type, content_len, session_id, status)
        )
        return row_id

    @classmethod
    def delete(cls, id):
        """
        逻辑删除聊天记录
        :param id: 聊天记录的ID
        :return:
        """
        return execute_sql('UPDATE `t_history` SET is_deleted=? WHERE _id=?', [1, id])

    @classmethod
    def restore(cls, id):
        """
        还原逻辑删除的聊天记录
        :param id: 聊天记录的ID
        :return:
        """
        return execute_sql('UPDATE `t_history` SET is_deleted=? WHERE _id=?', [0, id])

    @classmethod
    def force_delete(cls, id):
        """
        强行删除的聊天记录（无法恢复）
        :param id: 聊天记录的ID
        :return:
        """
        return execute_sql('DELETE FROM `t_history` WHERE _id=?', [id])

    @classmethod
    def topping(cls, id):
        """
        置顶该聊天记录
        :param id: 聊天记录的ID
        :return:
        """
        return execute_sql('UPDATE `t_history` SET is_top=? WHERE _id=?', [1, id])

    @classmethod
    def cancel_topping(cls, id):
        """
        取消该聊天记录的置顶
        :param id: 聊天记录的ID
        :return:
        """
        return execute_sql('UPDATE `t_history` SET is_top=? WHERE _id=?', [0, id])

    @classmethod
    def update_order_no(cls, id, order_no):
        """
        更新聊天记录的排序
        :param id: 聊天记录的ID
        :param order_no: 排序号
        :return:
        """
        return execute_sql('UPDATE `t_history` SET order_no=? WHERE _id=?', [order_no, id])

    @classmethod
    def select(cls, id, entity_cls=None):
        """
        获取指定的聊天记录
        :param id: 聊天记录的ID
        :param entity_cls: 转化后的实体类类型
        :return:
        """
        df = select_sql('SELECT * FROM `t_history` WHERE _id=? AND is_deleted=0', [id])

        if df.empty:
            return None

        if entity_cls is None:
            return df

        rows = df.itertuples(index=False)
        my_objs = [entity_cls(*row) for row in rows]
        return my_objs[0]

    @classmethod
    def select_all(cls, entity_cls=None):
        """
        获取所有的聊天记录
        :param entity_cls: 转化后的实体类类型
        :return:
        """
        df = select_sql(f'SELECT * FROM `t_history` WHERE is_deleted=0 ORDER BY order_no, _id DESC', [])
        if entity_cls is None:
            return df

        rows = df.itertuples(index=False)
        my_objs = [entity_cls(*row) for row in rows]
        return my_objs

    @classmethod
    def select_by_session_id(cls, session_id, order_by=None, entity_cls=None):
        """
        获取指定会话的聊天记录
        :param session_id: 会话ID
        :param order_by: 排序
        :param entity_cls: 转化后的实体类类型
        :return:
        """
        if order_by is None:
            order_by = "order_no, _id DESC"
        df = select_sql(f'SELECT * FROM `t_history` WHERE is_deleted=0 AND session_id=? ORDER BY {order_by}',
                        [session_id])
        if entity_cls is None:
            return df

        rows = df.itertuples(index=False)
        my_objs = [entity_cls(*row) for row in rows]
        return my_objs

    @classmethod
    def create_table(cls):
        """
        创建表
        :return:
        """
        ddl = """CREATE TABLE IF NOT EXISTS `t_history` (
        `_id` INTEGER primary key autoincrement, 
        `ts` INTEGER, 
        `role` varchar(100), 
        `content`  BLOB, 
        `content_type` varchar(50), 
        `content_len` int,
        `session_id` int,
        `order_no` int DEFAULT 0,
        `is_top` int DEFAULT 0,    
        `status` int DEFAULT 0,    
        `is_deleted` int DEFAULT 0,
        `role_name` varchar(100)
        )
        """

        execute_ddl(ddl)
        execute_ddl("CREATE INDEX t_history_session_id_idx ON t_history (session_id)")


if __name__ == '__main__':
    # result = HistoryOp.create_table()
    # row_id = HistoryOp.insert(role="user", content="你好啊", session_id=0)
    #
    #
    # def execute_demo(title, func):
    #     print(f"【{title}】")
    #     print(func())
    #     print(HistoryOp.select(row_id))
    #     print("------------------------------------------------------")
    #
    #
    # print(HistoryOp.select(row_id))
    #
    # execute_demo("topping", lambda: HistoryOp.topping(id=row_id))
    # execute_demo("cancel_topping", lambda: HistoryOp.cancel_topping(id=row_id))
    # execute_demo("update_order_no", lambda: HistoryOp.update_order_no(id=row_id, order_no=10))
    # execute_demo("delete", lambda: HistoryOp.delete(id=row_id))
    # execute_demo("restore", lambda: HistoryOp.restore(id=row_id))
    # execute_demo("force_delete", lambda: HistoryOp.force_delete(id=row_id))
    pass
