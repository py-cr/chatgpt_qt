# -*- coding:utf-8 -*-
# title           :session_window.py
# description     :支持会话聊天的窗口
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtWidgets import QMdiSubWindow

from common.mdi_window_mixin import MdiWindowMixin
from common.ui_mixin import UiMixin


class SessionWindow(QMdiSubWindow, UiMixin, MdiWindowMixin):
    """
    聊天窗口
    """

    def __init__(self):
        super().__init__()
        # 构建会话的事件
        self.build_session_events()
