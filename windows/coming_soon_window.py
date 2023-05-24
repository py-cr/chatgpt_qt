# -*- coding:utf-8 -*-
# title           :coming_soon_window.py
# description     :敬请关注窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtWidgets import QMdiSubWindow, QHBoxLayout

from common.mdi_window_mixin import MdiWindowMixin
from common.ui_mixin import UiMixin
from controls.coming_soon import ComingSoon


class ComingSoonWindow(QMdiSubWindow, UiMixin, MdiWindowMixin):
    """
    敬请关注窗口
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.coming_soon = ComingSoon(self)
        self.layout.addWidget(self.coming_soon)
        self.dock_fill(self.layout)
