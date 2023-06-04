# -*- coding:utf-8 -*-
# title           :chatgpt_main.py
# description     :ChatGPT程序入口
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import sys

from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QStyleFactory

from common.menu_proxy import MenuProxy
from windows.main_window import MainWindow

if __name__ == '__main__':
    # ['windowsvista', 'Windows', 'Fusion']
    app = QApplication(sys.argv)
    # # 加载翻译文件
    translation_file = './qm/qt_zh_CN.qm'
    translator = QTranslator()

    if translator.load(translation_file):
        print("翻译器加载成功：", translation_file)
        app.installTranslator(translator)
    else:
        print("翻译器加载失败：", translation_file)

    print("支持样式：", QStyleFactory.keys())
    app.setStyle(MenuProxy(QStyleFactory.create('Fusion')))

    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = MainWindow()
    # window.setGeometry(191, 143, 1538, 830)  # 设置窗口位置和宽高大小
    # window.resize(1600, 900)  # 设置窗口宽高大小
    # window.show()
    window.showMaximized()

    sys.exit(app.exec_())
