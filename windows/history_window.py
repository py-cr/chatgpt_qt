# -*- coding:utf-8 -*-
# title           :history_window.py
# description     :历史聊天窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCloseEvent
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView
from PyQt5.uic import loadUi

from common.app_events import AppEvents
from common.message_box import MessageBox
from common.str_utils import is_empty
from common.table_data_loader import TableDataLoader
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui
from db.db_ops import SessionOp, ConfigOp
from db.entities.session_setting import SessionSetting


class HistoryWindow(QDockWidget, UiMixin):
    """
    历史聊天窗口
    """

    def __init__(self, open_chat):
        super().__init__()

        loadUi(find_ui("ui/history.ui"), self)
        # 绑定3个方法
        self.open_chat = open_chat  # 打开一个聊天窗口
        # self.btn_search.setVisible(False)
        # 绑定事件
        self.bind_events()

        self.set_icons([self.btn_delete_chat, self.btn_open_chat, self.btn_refresh],
                       ['cross.png', 'comment.png', 'refresh.png'])
        # bin.png cross.png

        # 初始化控件
        self.init_controls()
        # 加载聊天历史
        self.load_history()

    def bind_events(self):
        """
        绑定事件
        :return:
        """
        self.btn_delete_chat.clicked.connect(self.delete_chat)
        self.btn_open_chat.clicked.connect(self.open_selected_chat)
        self.btn_refresh.clicked.connect(self.load_history)
        self.txt_keyword.textChanged.connect(self.load_history)
        self.tabvw_his.doubleClicked.connect(self.open_chat_by_settings)
        self.cmb_categories.currentIndexChanged.connect(self.load_history)

        AppEvents.on_chat_category_changed_subscription(self.on_chat_category_changed)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.unbind_events()
        super().closeEvent(event)

    def unbind_events(self):
        AppEvents.on_chat_category_changed_unsubscription(self.on_chat_category_changed)

    def init_categories(self):
        """
        话题分类
        :return:
        """
        self.cmb_categories.currentIndexChanged.disconnect()
        category_id = self.cmb_categories.itemData(self.cmb_categories.currentIndex())
        # print(category_id)
        self.cmb_categories.clear()
        self.cmb_categories.addItem("", 0)
        for category in ConfigOp.get_categories():
            self.cmb_categories.addItem(category.cfg_key, category._id)

        if category_id is not None:
            if category_id > 0:
                index = self.cmb_categories.findData(category_id)  # 查找值为 20 的选项的索引
                if index >= 0:
                    self.cmb_categories.setCurrentIndex(index)  # 将找到的索引设置为当前选中项
                else:
                    # 当前的分类删除掉了，则重新加载历史
                    self.load_history()
        else:
            pass

        self.cmb_categories.currentIndexChanged.connect(self.load_history)

    def on_chat_category_changed(self):
        self.init_categories()

    def init_controls(self):
        """
        初始化控件
        :return:
        """
        self.tabvw_his.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabvw_his.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.init_categories()

    def window_id(self):
        return "HistoryWindow"

    def open_selected_chat(self):
        self.open_chat_by_index(self.tabvw_his.currentIndex())

    def open_chat_by_settings(self, index):
        row = index.row()
        if row < 0:
            return
        model = self.tabvw_his.model()
        settings = model.data(model.index(row, 6))

        if is_empty(settings):
            self.open_selected_chat()
        else:
            self.open_selected_chat()

    def open_chat_by_index(self, index, open_chat=None):
        if open_chat is None:
            open_chat = self.open_chat
        row = index.row()
        if row < 0:
            return
        # column = index.column()
        model = self.tabvw_his.model()
        value = model.data(model.index(row, 4))
        content_size = int(model.data(model.index(row, 5)))
        if callable(self.open_chat):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            # session_id, subject
            open_chat(int(value), None, False, content_size)
            # 恢复光标
            QApplication.restoreOverrideCursor()

    def delete_chat(self):
        tabvw_his: QStandardItemModel = self.tabvw_his.model()
        session_ids = []
        for row in range(tabvw_his.rowCount()):
            item: QStandardItem = tabvw_his.item(row, 0)
            # widget = self.tabvw_his.indexWidget(item.index())
            data = tabvw_his.itemData(item.index())
            if item.isCheckable() and item.checkState() == Qt.Checked:
                items = []
                for i in range(1, tabvw_his.columnCount()):
                    items.append(tabvw_his.itemData(tabvw_his.item(row, i).index())[0])
                session_ids.append(int(items[3]))
        if len(session_ids) > 0:
            result = MessageBox.question(self, "确认", "是否删除选中的聊天记录，并放入回收站？")
            if result == QMessageBox.Yes:
                SessionOp.delete_ids(tuple(session_ids))
                # print(session_ids)
                self.load_history()

    def load_history(self):
        """
        加载聊天历史
        :return:
        """
        import pandas as pd
        keyword = self.txt_keyword.text()
        category_id = self.cmb_categories.itemData(self.cmb_categories.currentIndex())
        if category_id == 0:
            category_id = None
        df: pd.DataFrame = SessionOp.get_chat_histories(keyword, category_id)
        cell_data = []

        for idx, row in df.iterrows():
            subject = row["subject"]
            content_size = row["content_size"]
            if content_size < 1000:
                content_size = str(content_size) + "b"
            elif content_size < 1000000:
                content_size = str(round(content_size / 1000, 2)) + "K"
            else:
                content_size = str(round(content_size / 1000000, 2)) + "M"
            if is_empty(subject):
                subject = "无主题"
            subject = f"{subject}({content_size})"
            settings = row["settings"]
            session_setting = SessionSetting(settings)
            row_data = [subject, row["date_time"][5:-3], row["content"][0:30], str(row["session_id"]),
                        str(row["content_size"]), session_setting.ai_init_subject]
            cell_data.append(row_data)

        TableDataLoader(self.tabvw_his, ['', '       主题       ', '   时间  ', '   内容        ', '', '', ''],
                        cell_data).load_data()
        self.tabvw_his: QTableView = self.tabvw_his
        self.tabvw_his.setColumnHidden(4, True)
        self.tabvw_his.setColumnHidden(5, True)
        self.tabvw_his.setColumnHidden(6, True)
        # self.tabvw_his.setColumnWidth(0, 20)
        self.tabvw_his.setColumnWidth(1, 150)
        self.tabvw_his.setColumnWidth(2, 100)
        self.tabvw_his.setToolTipDuration(1)
        self.tabvw_his.setColumnWidth(3, 200)
        self.tabvw_his.resizeColumnToContents(0)
