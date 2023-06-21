# -*- coding:utf-8 -*-
# title           :ui_designer.py
# description     :UI设计器
# author          :Python超人
# date            :2023-6-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import os
import sys
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
designer_path = QStandardPaths.findExecutable("designer")
if designer_path:
    os.startfile(designer_path)
else:
    print("Qt Designer 未找到。请安装：\npip install --user -i https://pypi.tuna.tsinghua.edu.cn/simple pyqt5-tools")
    # pip install --user -i https://pypi.tuna.tsinghua.edu.cn/simple pyqt5-tools
