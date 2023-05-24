# -*- coding:utf-8 -*-
# title           :history.py
# description     :聊天历史记录类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from dataclasses import dataclass


@dataclass
class History:
    """
    历史记录
    """
    _id: int = 0
    ts: int = 1551157481034565
    role: str = ''
    content: str = ''
    content_type: str = ''
    content_len: int = 0
    session_id: int = 0
    order_no: int = 0
    is_top: int = 0
    status: int = 0
    is_deleted: int = 0
    role_name: str = ''


if __name__ == '__main__':
    print(History())
