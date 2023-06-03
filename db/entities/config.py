# -*- coding:utf-8 -*-
# title           :config.py
# description     :数据库配置类
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from dataclasses import dataclass


@dataclass
class Config:
    """
    配置
    """
    _id: int
    cfg_category: str = ''
    cfg_key: str = ''
    cfg_value: str = ''
    order_no: int = 0
    is_deleted: int = 0


if __name__ == '__main__':
    print(Config())
