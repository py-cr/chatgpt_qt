# -*- coding:utf-8 -*-
# title           :chat_recycle_bin.py
# description     :聊天回收站窗口
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView
from PyQt5.uic import loadUi

from common.chat_utils import CONTENT_SIZE_SO_MUCH
from common.mdi_window_mixin import MdiWindowMixin
from common.message_box import MessageBox
from common.str_utils import is_empty
from common.table_data_loader import TableDataLoader
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui
from db.db_ops import SessionOp
from windows.chat_history_window import ChatHistoryWindow


class ChatRecycleBin(QMdiSubWindow, UiMixin, MdiWindowMixin):
    """
    聊天回收站窗口
    """

    def window_id(self):
        return "RecycleBin"

    def __init__(self, main_window):
        super().__init__()
        # 从 .ui 文件加载 UI
        loadUi(find_ui("ui/chat_recycle_bin.ui"), self)
        # 设置窗口标题和大小
        self.setWindowTitle('回收站')
        self.setWindowIcon(self.icon("bin.png"))
        self.main_window = main_window

        # 绑定事件
        self.bind_events()

        self.set_icons([self.btn_session_delete, self.btn_open_history,
                        self.btn_session_recovery,
                        self.btn_session_refresh],
                       ['cross.png', 'comment.png', 'arrow_undo.png', 'refresh.png'])

        self.dock_fill()

        self.tabview_session.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabview_session.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 加载已经删除的历史聊天
        self.load_deleted_histories()

    def bind_events(self):
        """
        绑定事件
        :return:
        """
        self.btn_session_delete.clicked.connect(self.delete_session)
        self.btn_open_history.clicked.connect(self.open_history_by_index)
        self.btn_session_recovery.clicked.connect(self.recovery_session)
        self.btn_session_refresh.clicked.connect(self.load_deleted_histories)
        self.txt_keyword.textChanged.connect(self.load_deleted_histories)
        self.tabview_session.doubleClicked.connect(self.open_history_by_index)

    def recovery_session(self):
        """
        恢复选中的聊天会话
        :return:
        """
        session_ids = self.selected_session_ids()
        if len(session_ids) > 0:
            SessionOp.restore_ids(tuple(session_ids))
            self.load_deleted_histories()

    def selected_session_ids(self):
        """
        获取选中的 会话 ID 列表
        :return:
        """
        tabview_session: QStandardItemModel = self.tabview_session.model()
        session_ids = []
        for row in range(tabview_session.rowCount()):
            item: QStandardItem = tabview_session.item(row, 0)
            # widget = self.tabview_session.indexWidget(item.index())
            data = tabview_session.itemData(item.index())
            if item.isCheckable() and item.checkState() == Qt.Checked:
                items = []
                for i in range(1, tabview_session.columnCount()):
                    items.append(tabview_session.itemData(tabview_session.item(row, i).index())[0])
                session_ids.append(int(items[3]))

        return session_ids

    def delete_session(self):
        """
        删除选中的聊天会话（无法恢复的删除）
        :return:
        """
        session_ids = self.selected_session_ids()
        if len(session_ids) > 0:
            result = MessageBox.question(self, "删除警告", "注意：一旦删除无法再恢复，\n再次确认是否删除勾选的聊天？")
            if result == QMessageBox.Yes:
                SessionOp.force_delete_ids(tuple(session_ids))
                # print(session_ids)
                self.load_deleted_histories()

    def load_deleted_histories(self):
        """
        加载已经删除的历史聊天
        :return:
        """
        import pandas as pd
        keyword = self.txt_keyword.text()
        df: pd.DataFrame = SessionOp.get_deleted_chat_histories(keyword)
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
            row_data = [subject, row["date_time"][5:-3], row["content"][0:100], str(row["session_id"]),
                        str(row["content_size"])]
            cell_data.append(row_data)

        TableDataLoader(self.tabview_session, ['', '       主题       ', '   时间  ', '   内容        ', '', ''],
                        cell_data).load_data()

        model = self.tabview_session.model()
        for row in range(model.rowCount()):
            for col in range(1, 4):
                item = QStandardItem(str(model.index(row, col).data()))  # 获取当前单元格的值
                font = QFont()
                font.setStrikeOut(True)  # 设置删除线字体
                item.setFont(font)
                color = QColor(100, 100, 100)  # 设置为灰色
                item.setForeground(color)  # 修改字体颜色
                model.setItem(row, col, item)

        # self.tabview_session: QTableView = self.tabview_session
        self.tabview_session.setColumnHidden(4, True)
        self.tabview_session.setColumnHidden(5, True)
        # self.tabview_session.setColumnWidth(0, 10)
        self.tabview_session.resizeColumnToContents(0)
        self.tabview_session.setColumnWidth(1, 280)
        self.tabview_session.setColumnWidth(2, 100)
        self.tabview_session.setToolTipDuration(1)
        self.tabview_session.setColumnWidth(3, 700)

    def open_history_by_index(self):
        """
        打开查看聊天的历史
        :return:
        """
        index = self.tabview_session.currentIndex()
        row = index.row()
        if row < 0:
            return
        # column = index.column()
        model = self.tabview_session.model()
        value = model.data(model.index(row, 4))
        content_size = int(model.data(model.index(row, 5)))

        QApplication.setOverrideCursor(Qt.WaitCursor)
        # session_id, subject
        self.open_chat_history(int(value), None, False, content_size)
        print(int(value))
        # 恢复光标
        QApplication.restoreOverrideCursor()

    def open_chat_history(self, session_id, subject, new_chat_session, content_size):
        """
        打开查看聊天的历史窗口
        :param session_id:
        :param subject:
        :param new_chat_session:
        :param content_size:
        :return:
        """
        window = self.main_window.find_exists_window(f"ChatHistoryWindow_{session_id}")
        if window is not None:
            self.main_window.mdiArea.setActiveSubWindow(window)
            window.showMaximized()
            return
        read_part_data = False
        if content_size > CONTENT_SIZE_SO_MUCH:
            QApplication.restoreOverrideCursor()
            read_part_data = True

            QApplication.setOverrideCursor(Qt.WaitCursor)

        sub_window = ChatHistoryWindow(session_id, subject, read_part_data)
        sub_window.new_chat_session = new_chat_session
        mdi_win = self.main_window.mdiArea.addSubWindow(sub_window)
        self.main_window.menu_window_add(mdi_win)
        sub_window.showMaximized()

    def delete_selected(self):
        """
        删除选中的行
        :return:
        """
        selected_rows = [index.row() for index in self.table.selectedIndexes()]
        for row in selected_rows[::-1]:
            self.table.removeRow(row)

    def restore_selected(self):
        """
        还原选中的行
        :return:
        """
        selected_rows = [index.row() for index in self.table.selectedIndexes()]
        for row in selected_rows[::-1]:
            print(row)

    def search(self, text):
        """
        搜索表格并高亮匹配的内容
        :param text:
        :return:
        """
        items = self.table.findItems(text, Qt.MatchContains)
        for item in items:
            self.table.selectRow(item.row())

    def select_all(self, state):
        """
        全选或全不选
        :param state:
        :return:
        """
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(state)
