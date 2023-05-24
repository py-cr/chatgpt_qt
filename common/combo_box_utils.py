# -*- coding:utf-8 -*-
# title           :combo_box_utils.py
# description     :ComboBox相关工具类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtWidgets import QComboBox


def select_by_text(combo_box: QComboBox, text):
    """
    QComboBox控件，选中指定文本（text）的项
    :param combo_box: QComboBox控件
    :param text: 指定文本
    :return:
    """
    for i in range(combo_box.count()):
        if text == combo_box.itemText(i):
            combo_box.setCurrentIndex(i)
            break


def select_by_value(combo_box: QComboBox, value):
    """
    QComboBox控件，选中指定值（value）的项
    :param combo_box: QComboBox控件
    :param value: 指定值
    :return:
    """
    for i in range(combo_box.count()):
        if value == combo_box.itemData(i):
            combo_box.setCurrentIndex(i)
            break
