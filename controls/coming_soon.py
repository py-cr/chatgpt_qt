# -*- coding:utf-8 -*-
# title           :coming_soon.py
# description     :敬请期待
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
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QHBoxLayout, QBoxLayout, QVBoxLayout
from common.ui_mixin import UiMixin
import os
import sys

from common.ui_utils import find_ui, find_image, open_url


class ComingSoon(QWidget, UiMixin):
    def __init__(self, parent=None):
        # call QWidget constructor
        super().__init__(parent)
        w, h = int(563 / 1.5), int(840 / 1.5)
        # 从 .ui 文件加载 UI
        r = loadUi(find_ui(f"ui/coming_soon.ui"), self)
        self.link_about.setGeometry(145, 38, 255, 51)
        image_file = find_image("douyin_x.jpg")
        self.graphicsView.setGeometry(20, 20, w+10, h+10)  # QGraphicsView 位置 (20, 20) 和大小 260x200
        scene = QGraphicsScene()  # 加入 QGraphicsScene
        scene.setSceneRect(0, 0, w, h)  # QGraphicsScene 相對位置 (20, 20) 和大小 120x160
        # scene.setSceneRect(0, 0, 840/2, 563/2)  # 设定 QGraphicsScene 位置与大小

        img = QPixmap(image_file)  # 加入图片
        # img = img.scaled(840/2, 563/2)  # 调整图片大小為 120x160
        img = img.scaled(w, h)  # 调整图片大小為 120x160
        scene.addPixmap(img)  # 將图片加入 scene
        self.graphicsView.setScene(scene)  # 设定 QGraphicsView 的场景為 scene

        self.link_about.clicked.connect(self.open_about)

    def open_about(self):
        open_url("https://gitcode.net/pythoncr/index")
