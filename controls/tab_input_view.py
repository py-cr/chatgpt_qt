# -*- coding:utf-8 -*-
# title           :tab_input_view.py
# description     :Tab输入视图控件基类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QAction, QMenu, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QBrush, QPalette, QPixmap, QCloseEvent
from PyQt5.QtWidgets import QWidget, QMessageBox, QMdiSubWindow, QVBoxLayout, QHBoxLayout, QBoxLayout, QStatusBar
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QHBoxLayout, QBoxLayout, QVBoxLayout
from common.ui_mixin import UiMixin
import os
import sys

from common.ui_utils import find_ui
from windows.session_window import SessionWindow


class TabInputView(QWidget, UiMixin):
    """
    Tab页签功能控件基类
    """

    def __init__(self, parent, ui_name=None):
        # call QWidget constructor
        # QWidget.parentWidget()
        super(TabInputView, self).__init__(parent)
        self.layout_main = None
        self.widget_main = None
        if ui_name is None:
            ui_name = os.path.basename(sys.modules[self.__class__.__module__].__file__)[:-3]

        # 从 .ui 文件加载 UI
        r = loadUi(find_ui(f"ui/{ui_name}.ui"), self)
        self.current_file = None

    def session_window(self):
        widget = self.parentWidget()
        while True:
            if isinstance(widget, SessionWindow):
                return widget
            widget = widget.parentWidget()

        return None

    @property
    def session_events(self):
        session_win = self.session_window()
        if session_win is None:
            return None

        return session_win.session_events

    def find_top_layout(self):
        """
        查找顶级layout（主要用于自动填满整个窗口）
        :return:
        """
        # self.children()[3].children()[0],self.layout_main, isinstance(self.children()[3],QWidget),self.children(),self
        for widget in self.children():
            if type(widget) in [QMenu, QVBoxLayout, QHBoxLayout, QBoxLayout, QStatusBar, QObject]:
                continue
            if type(widget) == QWidget:
                for child in widget.children():
                    if type(child) in [QVBoxLayout, QHBoxLayout, QBoxLayout]:
                        return child

        return None
