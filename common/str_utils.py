# -*- coding:utf-8 -*-
# title           :str_utils.py
# description     :String 工具类
# author          :Python超人
# date            :2023-3-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import os


def is_empty(s: str):
    """
    判断字符串是否为空（去除字符串两边的空格回车）
    :param s:
    :return:
    """
    if s is None:
        return True
    if len(s) == 0:
        return True
    if s.strip() == "":
        return True

    return False
