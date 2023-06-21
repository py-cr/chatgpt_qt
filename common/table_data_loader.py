# -*- coding:utf-8 -*-
# title           :table_data_loader.py
# description     :QTableView数据加载器
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QVBoxLayout, QApplication, QWidget, QHeaderView


class TableDataLoader(QWidget):
    """
    QTableView数据加载器
    """

    def __init__(self, table_view, header_labels, data, parent=None):
        super().__init__(parent=parent)
        self.table_view = table_view
        self.header_labels = header_labels
        self.data = data

    def load_data(self, checkbox=True):
        # 设置标题与初始大小
        self.model = QStandardItemModel(self.table_view)
        # 设置数据层次结构，4行4列
        rows = 0
        self.model = QStandardItemModel(rows, len(self.header_labels))
        # self.model.appendRow(QStandardItem('hello'))
        # self.check_box = QCheckBox(self)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(self.header_labels)

        cell_data = []
        for row_idx, row_data in enumerate(self.data):
            if checkbox:
                # cmb = QComboBox()
                # cmb.addItems(["男","女"])
                item_checked = QStandardItem()
                item_checked.setCheckState(Qt.Unchecked)
                item_checked.setCheckable(True)
                self.model.setItem(row_idx, 0, item_checked)

            for col_idx, col_item in enumerate(row_data):
                # if col_idx > len(row_data) - 1:
                #     continue
                item = QStandardItem(col_item)
                if checkbox:
                    self.model.setItem(row_idx, col_idx + 1, item)
                    self.model.item(row_idx, col_idx + 1).setToolTip(self.model.item(row_idx, col_idx + 1).text())
                else:
                    self.model.setItem(row_idx, col_idx, item)
                    self.model.item(row_idx, col_idx).setToolTip(self.model.item(row_idx, col_idx).text())

        # self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.setModel(self.model)
        # # # 设置布局
        # layout = QVBoxLayout()
        # # layout.addWidget(self.check_box)
        # layout.addWidget(self.table_view)
        # self.setLayout(layout)

    def load__(self):
        # 设置标题与初始大小
        self.model = QStandardItemModel(self.table_view)
        # 设置数据层次结构，4行4列
        rows = 0
        self.model = QStandardItemModel(rows, len(self.header_labels))
        # self.model.appendRow(QStandardItem('hello'))
        # self.check_box = QCheckBox(self)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(self.header_labels)

        for row in range(2):
            item_checked = QStandardItem()
            item_checked.setCheckState(Qt.Checked)
            item_checked.setCheckable(True)
            self.model.setItem(row, 0, item_checked)
            for column in range(1, 4):
                item = QStandardItem('row %s,column %s' % (row, column))
                # 设置每个位置的文本值
                self.model.setItem(row, column, item)
                # self.model.item(row, column).setToolTip(self.model.item(row, column).text())
        # self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.table_view.setColumnWidth(0, 1)
        # self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setModel(self.model)
        # 设置布局
        layout = QVBoxLayout()
        # layout.addWidget(self.check_box)
        layout.addWidget(self.table_view)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tableView = QTableView()
    table = TableDataLoader(tableView, ['', '姓名', '身份证', '地址'], [['姓名', '身份证', '地址'], ['姓名', '身份证', '地址']])
    table.load_data()
    table.show()
    sys.exit(app.exec_())
