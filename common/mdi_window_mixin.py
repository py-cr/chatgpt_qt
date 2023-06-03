# -*- coding:utf-8 -*-
# title           :mdi_window_mixin.py
# description     :MdiWindowMixin
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtWidgets import QAction, QMenu, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QBrush, QPalette, QPixmap, QCloseEvent
from PyQt5.QtWidgets import QWidget, QMessageBox, QMdiSubWindow, QVBoxLayout, QHBoxLayout, QBoxLayout, QStatusBar
from common.ui_utils import find_ui, find_image, find_icon, set_icon
from common.session_events import SessionEvents


class MdiWindowMixin:
    """
    对 MDI 窗口扩展支持
    """

    def dock_fill(self, layout=None):
        """
        将指定的layout填满界面
        :param layout: 如果layout为空，则自动获取顶级layout
        :return:
        """
        if layout is None:
            layout = self.find_top_layout()
        self.widget = QWidget()

        # Set the main layout to the widget
        self.widget.setLayout(layout)

        # Set the widget as the content of the sub-window
        self.setWidget(self.widget)

    def build_session_events(self):
        self.session_events = SessionEvents()

    def find_top_layout(self: QMdiSubWindow):
        """
        查找顶级的 layout
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
