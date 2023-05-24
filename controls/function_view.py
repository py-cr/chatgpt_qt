# -*- coding:utf-8 -*-
# title           :function_view.py
# description     :功能视图控件
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QComboBox, QMainWindow, QApplication, QHBoxLayout, QBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
import os
import sys

from common.ui_utils import find_ui

FUNCTION_SAMPLE_TEXT = "[在这里输入你的内容]"


class FunctionView(QWidget):
    """
    按钮功能视图
    """

    def __init__(self):
        # call QWidget constructor
        super().__init__()
        self.layout_main = None
        self.widget_main = None
        self.txt_prefix = None
        self.txt_suffix = None
        self.txt_message = None
        self.cmb_btn_style = None
        self.txt_preview = None
        self.button_preview = None
        self.button_name = "按钮"

        # 从 .ui 文件加载 UI
        r = loadUi(find_ui(f"ui/function_view.ui"), self)
        self.current_file = None
        self.data_changed = None

        self.init_controls()

    def bind_events(self):
        """
        绑定事件
        :return:
        """
        self.txt_prefix.textChanged.connect(self.on_data_changed)
        self.txt_suffix.textChanged.connect(self.on_data_changed)
        self.txt_message.textChanged.connect(self.on_data_changed)
        self.cmb_btn_style.currentIndexChanged.connect(self.on_data_changed)

    def init_controls(self):
        """
        初始化控件
        :return:
        """
        self.button_preview.setText(self.button_name)
        self.txt_message.setText(FUNCTION_SAMPLE_TEXT)

        #  TODO：使用 windows/color_demo.py 查看颜色
        self.cmb_btn_style.addItem("默认", "")
        self.cmb_btn_style.addItem("白字红底", "background-color: red; color: white")
        self.cmb_btn_style.addItem("白字绿底", "background-color: green; color: white")
        self.cmb_btn_style.addItem("白字蓝底", "background-color: blue; color: white")
        self.cmb_btn_style.addItem("白字黑底", "background-color: black; color: white")

        self.cmb_btn_style.addItem("白字中蓝底", "background-color: mediumblue; color: white")
        self.cmb_btn_style.addItem("白字藏蓝底", "background-color: navy; color: white")
        self.cmb_btn_style.addItem("白字深红底", "background-color: darkred; color: white")

        self.cmb_btn_style.addItem("黑字红底", "background-color: red; color: black")
        self.cmb_btn_style.addItem("黑字黄底", "background-color: yellow; color: black")
        self.cmb_btn_style.addItem("黑字粉底", "background-color: pink; color: black")

        self.cmb_btn_style.addItem("黑字浅绿底", "background-color: lightgreen; color: black")
        self.cmb_btn_style.addItem("黑字橘黄底", "background-color: bisque; color: black")
        self.cmb_btn_style.addItem("黑字米黄底", "background-color: beige; color: black")
        self.cmb_btn_style.addItem("黑字麦色底", "background-color: wheat; color: black")
        self.cmb_btn_style.addItem("黑字蓝绿底", "background-color: aquamarine; color: black")

        #
        '''
        天依蓝 #66ccff
        初音绿 #66ffcc
        言和绿 #99ffff
        阿绫红 #ee0000
        双子黄 #ffff00
        '''
        if hasattr(self, "right_widget"):
            self.right_widget.setStyleSheet('''QWidget{background-color:#66CCFF;}''')

        self.txt_preview.setStyleSheet("background-color:#aaeeff")
        self.txt_prefix.setStyleSheet("color: blue")
        self.txt_suffix.setStyleSheet("color: blue")

        self.bind_events()

    def setEnabled(self, value):
        """
        设置是否有效
        :param value:
        :return:
        """
        self.cmb_btn_style.setEnabled(value)
        self.txt_prefix.setEnabled(value)
        self.txt_suffix.setEnabled(value)
        self.txt_message.setEnabled(value)
        self.button_preview.setEnabled(value)

    def setDisabled(self, value):
        """
        设置是否无效
        :param value:
        :return:
        """
        self.cmb_btn_style.setDisabled(value)
        self.txt_prefix.setDisabled(value)
        self.txt_suffix.setDisabled(value)
        self.txt_message.setDisabled(value)
        self.button_preview.setDisabled(value)

    def on_data_changed(self):
        """
        该控件视图中的数据发生变动后，会触发
        :return:
        """
        if self.data_changed is not None:
            # 该控件视图中的数据发生变动后，传递事件到外部
            self.data_changed()

        self.button_preview.setText(self.button_name)
        btn_style = self.cmb_btn_style.itemData(self.cmb_btn_style.currentIndex())
        if len(btn_style) > 0:
            self.button_preview.setStyleSheet(btn_style)
        else:
            self.button_preview.setStyleSheet("")

        preview_text = self.txt_prefix.toPlainText() + self.txt_message.toPlainText() + self.txt_suffix.toPlainText()

        self.txt_preview.setText(preview_text)

    def set_button_style(self, style):
        try:
            for i in range(self.cmb_btn_style.count()):
                if style in self.cmb_btn_style.itemData(i):
                    self.cmb_btn_style.setCurrentIndex(i)
                    break
        except Exception as e:
            print(e)

    def to_json_data(self):
        """

        :return:
        """
        btn_style = self.cmb_btn_style.itemData(self.cmb_btn_style.currentIndex())
        sample = self.txt_message.toPlainText()
        if sample == FUNCTION_SAMPLE_TEXT:
            sample = ""
        json_data = {
            "prefix": self.txt_prefix.toPlainText(),
            "suffix": self.txt_suffix.toPlainText(),
            "sample": sample,
            "btn_style": btn_style
        }

        return json_data

    def dock_fill(self, container):
        self.container = container
        # if self.layout_main is not None:
        container.setLayout(self.widget_main)
        # elif self.widget_main is not None:
        #     # h_layout = QHBoxLayout()
        #     container.addWidget(self.widget_main)
        # container.setLayout(h_layout)
