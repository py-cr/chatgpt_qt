# -*- coding:utf-8 -*-
# title           :chat_view.py
# description     :聊天视图Web控件
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QAction, QMenu, QPushButton, QTextEdit
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QBrush, QPalette, QPixmap, QCloseEvent, QTextCursor
from PyQt5.QtWidgets import QWidget, QMessageBox, QMdiSubWindow, QVBoxLayout, QHBoxLayout, QBoxLayout, QStatusBar
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QHBoxLayout, QBoxLayout, QVBoxLayout, QFrame
from common.ui_mixin import UiMixin
import os
import sys
import json
from common.ui_utils import find_ui, find_file, find_image
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl

from PyQt5 import QtCore


class DataBridge(QtCore.QObject):
    def __init__(self, required_histories, supported_styles):
        super().__init__(parent=None)
        self.required_histories = required_histories
        self.supported_styles = supported_styles

    @QtCore.pyqtSlot(int, result=bool)
    def onRequiredHistories(self, history_id):
        if callable(self.required_histories):
            self.required_histories(history_id)
        # print("on_required_histories")
        return True

    @QtCore.pyqtSlot(str, result=bool)
    def onSupportedStyles(self, styleNames):
        if callable(self.supported_styles):
            self.supported_styles(styleNames)

        return True


class ConsoleBridge(QtCore.QObject):
    @QtCore.pyqtSlot(str, result=str)
    def log(self, message):
        print(message)
        return ""


class ChatView(QWidget, UiMixin):
    """
    聊天视图Web控件
    """

    def required_histories(self, history_id):
        print("history_id", history_id)

    def supported_styles(self, style_names):
        print("supported_styles", style_names)

    def init_js_bridge(self):
        self.browser.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        channel = QWebChannel(self.browser.page())
        self.browser.page().setWebChannel(channel)
        # self.python_bridge = JsBridge(None)
        self.console_bridge = ConsoleBridge(None)
        self.data_bridge = DataBridge(self.required_histories, self.supported_styles)

        channel.registerObject("dataBridge", self.data_bridge)
        channel.registerObject("consoleBridge", self.console_bridge)

    def __init__(self, parent=None):
        super(ChatView, self).__init__(parent)

        url_path = find_file("chat.html", "docs")
        self.url_path = "file:///" + os.path.abspath(url_path).replace("\\", "/")

        # 创建 QHBoxLayout 对象，并将浏览器添加到它中
        layout = QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建 QWebEngineView 对象
        self.browser = QWebEngineView(self)
        self.init_js_bridge()
        self.browser.setContentsMargins(1, 1, 1, 1)
        self.browser.setAttribute(Qt.WA_StyledBackground)
        self.browser.setStyleSheet("border: 1px solid #b0b0b0;")
        # 加载外部的web界面
        self.browser.load(QUrl(self.url_path))
        self.browser.loadFinished.connect(self.loadFinished)

        layout.addWidget(self.browser)
        # 设置布局
        self.setLayout(layout)

    def loadFinished(self, bool):
        """
        browser 加载 chat.html 结束后会触发
        :param bool:
        :return:
        """
        print(bool)

    def left_title(self, his_id, icon, title, color=None):
        """
        增加左边标题（OpenAI发言）
        :param his_id: 历史记录ID
        :param icon: 图标
        :param title: 名称
        :param color: 字体颜色
        :return:
        """
        if color is None:
            color = ""
        self.runjs(f'leftTitle({his_id},"{icon}","{title}","{color}")')

    def right_title(self, his_id, icon, title, color=None):
        """
        增加右边标题（我发言）
        :param his_id: 历史记录ID
        :param icon: 图标
        :param title: 名称
        :param color: 字体颜色
        :return:
        """
        if color is None:
            color = ""
        self.runjs(f'rightTitle({his_id},"{icon}","{title}","{color}")')

    def append_title(self, his_id, is_left, icon, title, color=None):
        """
        增加标题
        :param his_id: 历史记录ID
        :param is_left: 是否左边
        :param icon: 图标
        :param title: 名称
        :param color: 字体颜色
        :return:
        """
        if is_left:
            self.left_title(his_id, icon, title, color)
        else:
            self.right_title(his_id, icon, title, color)

    def highlightAll(self):
        self.runjs(f'highlightAll();')

    def changeStyle(self, styleName):
        self.runjs(f'changeStyle("{styleName}")')

    def setIsAtTop(self, value: bool):
        self.runjs(f'setIsAtTop({str(value).lower()});')

    def scrollToLastTopElement(self):
        self.runjs(f'scrollToLastTopElement();')

    def formatted_html(self, html):
        _html = json.dumps(html, ensure_ascii=False)
        return _html

    def insert_chat_item(self, his_id, is_left, icon, title, color, html, highlightElement=True):
        """
        更新整个HTML
        :param html:
        :return:
        """
        _html = self.formatted_html(html)

        def js_callback(obj):
            """
            调试用，如果 obj is None 则有问题
            :param obj:
            :return:
            """
            if obj is None:
                print("html", html)
                print("_html", _html)
                print("ERROR, obj为空")
                pass
            else:
                # print("obj", obj)
                pass

        # 运行 chat.html 中的 updateHtml
        self.runjs(
            f'insertChatItem({his_id},{str(is_left).lower()},"{icon}","{title}","{color}",{_html}, '
            f'{str(highlightElement).lower()});',
            js_callback)

    def update_html(self, html, highlightElement=True):
        """
        更新整个HTML
        :param html:
        :return:
        """
        _html = self.formatted_html(html)

        def js_callback(obj):
            """
            调试用，如果 obj is None 则有问题
            :param obj:
            :return:
            """
            if obj is None:
                print("html", html)
                print("_html", _html)
                print("ERROR, obj为空")
                pass
            else:
                # print("obj", obj)
                pass

        # 运行 chat.html 中的 updateHtml
        self.runjs(f'updateHtml({_html}, {str(highlightElement).lower()});', js_callback)

    def scrollBottomEnabled(self):
        self.runjs(f'scrollBottomEnabled();')

    def scrollBottomDisabled(self):
        self.runjs(f'scrollBottomDisabled();')

    def clear(self):
        """
        清空聊天窗口
        :return:
        """
        self.runjs(f'clearHtml()')

    def setLineWrapMode(self, widget_width):
        if QTextEdit.NoWrap == widget_width:
            self.runjs(f'auto_wrap_disable()')
        else:
            self.runjs(f'auto_wrap_enable()')

    def runjs(self, js, callback=None):
        if callback is None:
            self.browser.page().runJavaScript(js)
        else:
            self.browser.page().runJavaScript(js, callback)
