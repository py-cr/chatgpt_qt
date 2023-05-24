# -*- coding:utf-8 -*-
# title           :ui_utils.py
# description     :UI工具类
# author          :Python超人
# date            :2023-3-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import os
import time
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory, QFileDialog, QPushButton, QAction, QMenu


def find_file(file_name, parent_dir, raise_exception=True):
    """
    查找文件位置
    :param file_name: 文件名
    :param parent_dir: 父目录
    :param raise_exception: 如果没有找到，是否抛出异常
    :return:
    """
    if parent_dir not in os.path.split(file_name):
        file_path = os.path.join(parent_dir, file_name)
    else:
        file_path = file_name

    if os.path.exists(file_path):
        return file_path

    for i in range(10):
        file_path = os.path.join("..", file_path)
        if os.path.exists(file_path):
            return file_path
    if raise_exception:
        raise Exception(f"文件 {file_name} 未找到")

    return None


def find_image(img_file):
    """
    查找图片（查找的父目录为 images）
    :param img_file: 图片文件名
    :return:
    """
    return find_file(img_file, "images")


def find_icon_file(icon_file):
    """
    查找图标文件（查找的父目录为 images/icons）
    :param icon_file:
    :return:
    """
    fp = find_file(icon_file, os.path.join('images', 'icons'), False)
    if fp is None:
        fp = find_file(icon_file, 'images')
    return fp


def find_icon(icon_file):
    """
    查找图标，并返回图标对象
    :param icon_file: 图标文件名
    :return: 图标对象
    """
    return QIcon(find_icon_file(icon_file))


def set_icon(action: [QAction, QMenu], icon_file):
    """
    设置图标
    :param action: 菜单 action
    :param icon_file: 图标文件
    :return:
    """
    action.setIcon(find_icon(icon_file))


def find_ui(ui_file):
    """
    查找 UI 文件（查找的父目录为 ui）
    :param ui_file: UI 文件名
    :return:
    """
    return find_file(ui_file, "ui")


def get_html_style():
    """
    Html 样式
    :return:
    """
    return """
  body{
    color: green;
  }
  QTextEdit{
    color: green;
  }
  .chat-window {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 300px;
    background-color: #fafafa;
    padding: 10px;
    overflow-y: auto;
  }

  .chat-bubble {
    display: flex;
    flex-direction: column;
    max-width: calc(100% - 60px);
    margin-top: 10px;
    margin-bottom: 10px;
  }

  .left {
    align-items: flex-start;
  }

  .right {
    align-items: flex-end;
  }

  .message {
    padding: 10px;
    background-color: #f3f3f3;
    border-radius: 10px;
    font-size: 14px;
    line-height: 1.4;
  }
  
  .code_s{
    border-style:solid; 
    border-width:1px;
  }

  pre {
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 10px;
    line-height: 1.4;
    overflow-x: auto;
  }

"""


def open_url(url):
    if os.name == 'posix':
        os.system("open " + str(url))
    elif os.name == 'nt':
        os.system("start " + str(url))


# """
# code {
#     font-family: 'Microsoft Yahei', '微软雅黑', 'Courier New', Courier, monospace;
#     color:red;
#     font-size: 14px;
#   }
# """
if __name__ == '__main__':
    print(find_ui('main.ui'))
    open_url("https://gitcode.net/pythoncr/index")
