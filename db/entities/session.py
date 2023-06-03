# -*- coding:utf-8 -*-
# title           :session.py
# description     :聊天会话类
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from dataclasses import dataclass


@dataclass
class Session:
    """
    聊天会话
    """
    _id: int = 0
    ts: int = 1551157481034565
    subject: str = ''
    settings: str = ''
    model_id: str = 'gpt-3.5-turbo'
    category_id: int = 0
    order_no: int = 0
    is_top: int = 0
    is_deleted: int = 0


if __name__ == '__main__':
    print(Session())
