# -*- coding:utf-8 -*-
# title           :db_utils.py
# description     :数据库工具类
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import os

from common.app_config import DB_NAME
from db.db_ops import ConfigOp, SessionOp, HistoryOp

CURRENT_DB_VERSION = "1.0"


def create_db():
    ConfigOp.create_table()
    SessionOp.create_table()
    HistoryOp.create_table()

    ConfigOp.init_ai_roles()
    ConfigOp.init_button_funcs()
    ConfigOp.init_categories()
    ConfigOp.init_tab_funcs()


def get_db_version():
    """
    0.9 初始版本（简单的聊天功能、体验不好）
    1.0 体验做了很多改进：1）样式进行调整；2）对于历史记录过多会分页展开

    """
    v = ConfigOp.get_sys_config("version", "0.9")
    return v


def db_0_9_to_1_0():
    """
    0.9 -> 1.0 升级
    """
    ConfigOp.save_sys_config("version", "1.0")


def db_version_check():
    db_file = os.path.join("data", DB_NAME)
    if os.path.exists(db_file):
        # 检查版本
        db_ver = get_db_version()
        if db_ver < CURRENT_DB_VERSION:
            db_0_9_to_1_0()
    else:
        # 如果数据库不存在，则进行初始化
        create_db()
        db_0_9_to_1_0()


if __name__ == '__main__':
    os.chdir("../")
    print(db_version_check())
