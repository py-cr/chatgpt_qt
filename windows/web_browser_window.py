# -*- coding:utf-8 -*-
# title           :web_browser_window.py
# description     :Web浏览器窗口
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import os

import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from common.ui_mixin import UiMixin
from common.ui_utils import find_file
from common.ui_utils import find_ui, find_image


# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
#
# # from PyQt5.QtCore import *
# # from PyQt5.QtGui import *
# # from PyQt5.QtWidgets import *
# # from PyQt5.QtWebEngineWidgets import *


class WebBrowserWindow(QMdiSubWindow, UiMixin):
    """
    浏览器窗口
    """

    def __init__(self, url_path="index.html"):
        super().__init__()
        self.window_id_url = url_path
        self.init_web(url_path)

    def init_web(self, url_path="index.html"):
        super().__init__()

        if url_path.startswith("http"):
            self.url_path = url_path
        else:
            url_path = find_file(url_path, "docs")
            self.url_path = "file:///" + os.path.abspath(url_path)

        self.setWindowIcon(QIcon(find_image('icons/help.png')))
        loadUi(find_ui("ui/web_browser.ui"), self)
        self.WebBrowser.setControl("Shell.Explorer.2")
        self.WebBrowser.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.WebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.WebBrowser.setObjectName("WebBrowser")

        # self.WebBrowser.dynamicCall("Navigate(const QString&)", "https://www.baidu.com")
        self.WebBrowser.dynamicCall("Navigate(const QString&)", self.url_path)

        # Create a main widget to hold your layout
        self.widget = QWidget()

        # Set the main layout to the widget
        self.widget.setLayout(self.layout_main)
        # self.widget.setLayout(self.splitter)

        # Set the widget as the content of the sub-window
        self.setWidget(self.widget)
        # self.setLayout(self.layout_main)

    def window_id(self):
        return f"WebBrowserWindow_{self.window_id_url}"
