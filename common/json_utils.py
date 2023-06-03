# -*- coding:utf-8 -*-
# title           :json_utils.py
# description     :JSON 相关工具类
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import json


def to_json_obj(json_str: str, default_val=None):
    """
    JSON字符串转为对象
    :param json_str: JSON字符串
    :param default_val: 默认值
    :return:
    """
    try:
        obj = json.loads(json_str)
        return obj
    except Exception as e:
        print(e)
        return default_val


def to_json_items(json_str: str, item_names: [], default_item_values: [] = None):
    """
    JSON字符串转为项目列表
    :param json_str: JSON字符串
    :param item_names: 项目名称列表
    :param default_item_values: 项目列表的默认值
    :return:
    """
    obj = to_json_obj(json_str)
    if obj is None:
        return [None] * len(item_names)
    items = []
    for idx, item_name in enumerate(item_names):
        if item_name in obj:
            items.append(obj[item_name])
        else:
            if default_item_values is None or idx > len(default_item_values) + 1:
                items.append(None)
            else:
                items.append(default_item_values[idx])
    return items


def to_json_str(obj, default_val=None, ensure_ascii=True, indent=None, separators=None):
    """
    JSON对象转为字符串
    :param obj: JSON对象
    :param default_val: 默认值
    :return:
    """
    try:
        s = json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent, separators=separators)
        return s
    except Exception as e:
        return default_val
