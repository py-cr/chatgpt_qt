# -*- coding:utf-8 -*-
# title           :chat_history_window.py
# description     :聊天历史查看窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMdiSubWindow, QApplication, QVBoxLayout
from PyQt5.QtWidgets import QTextEdit, QWidget
from PyQt5.uic import loadUi

from common.chat_utils import build_my_message, build_openai_message, message_to_html, required_histories_for_win, \
    get_history_chat_info
from common.mdi_window_mixin import MdiWindowMixin
from common.str_utils import is_empty
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui, get_html_style
from controls.chat_view import ChatView
from db.db_ops import ConfigOp
from db.db_ops import HistoryOp
from db.db_ops import SessionOp
from db.db_utils import get_timestamp_str
from db.entities import History
from db.entities import Session


class ChatHistoryWindow(QMdiSubWindow, UiMixin, MdiWindowMixin):
    """
    聊天历史查看窗口
    """

    def __init__(self, session_id, title="", read_part_data=False):
        super().__init__()
        self.read_part_data = read_part_data
        # 从 .ui 文件加载 UI
        loadUi(find_ui("ui/chat_history.ui"), self)
        self.chat_history = []
        # 加载指定 session_id 的聊天会话
        self.load_session(session_id, title)
        # 初始化控件
        self.init_controls()

        self.setWindowIcon(self.default_icon())

    def load_session(self, session_id, title):
        """
        加载指定 session_id 的聊天会话
        :param session_id: 聊天会话ID
        :param title: 指定的标题
        :return:
        """
        self.session_id = session_id
        session: Session = SessionOp.select(session_id, Session)
        self.session = session
        if is_empty(title):
            if session is not None:
                subject = session.subject
                if is_empty(subject):
                    ts = session.ts
                    subject = "无主题:" + get_timestamp_str(ts, fmt="%m-%d %H:%M")
                else:
                    self.txt_title.setText(subject)
            else:
                subject = "无主题:" + get_timestamp_str(fmt="%m-%d %H:%M")

            self.setWindowTitle("查看历史 >> " + subject)
        else:
            self.setWindowTitle("查看历史 >> " + title)
            self.txt_title.setText(title)

    def init_controls(self):
        """
        初始化控件
        :return:
        """
        self.dock_fill()
        self.init_categories()

        layout_left: QVBoxLayout = self.layout_left
        widget: QWidget = self.txt_main.parent()

        self.txt_main.setParent(None)
        widget.setContentsMargins(0, 0, 0, 0)

        self.txt_main = ChatView(self)
        layout_left.addWidget(self.txt_main)
        layout_left.setSpacing(0)
        self.txt_main.data_bridge.required_histories = self.required_histories
        self.txt_main.browser.loadFinished.connect(self.loadFinished)

        self.chk_auto_wrap.clicked.connect(self.auto_wrap)

    def required_histories(self, history_id):
        required_histories_for_win(self, history_id)

    def loadFinished(self, bool):
        if bool:
            # 初始化历史记录，等待继续聊天，需要等浏览器网页加载完成后，再加载历史消息
            self.init_history_messages(self.read_part_data)

    def window_id(self):
        return f"ChatHistoryWindow_{self.session_id}"

    def init_history_messages(self, read_part_data):
        """
        初始化历史记录，等待继续聊天
        :param read_part_data: 是否读取部分消息
        :return:
        """
        self.all_histories = HistoryOp.select_by_session_id(self.session_id, order_by="order_no, _id",
                                                            entity_cls=History)
        histories = self.all_histories
        if len(histories) == 0:
            self.auto_wrap()
            return

        if read_part_data:
            # 读取部分消息，消息大小的定义在配置中（msg_context_size）定义大小（k）
            msg_context_size = float(ConfigOp.get_sys_config("msg_context_size", 3))
            total_size = 0
            his_len = len(histories)
            for i in range(his_len - 1, 0, -1):
                size = histories[i].content_len
                total_size += size
                if total_size > msg_context_size * 1000:
                    if i < his_len - 1:
                        histories = histories[i + 1:]
                        self.history_point_index = i
                        break

        QApplication.setOverrideCursor(Qt.WaitCursor)

        for history in histories:
            role = history.role
            content = history.content
            content_len = len(content)  # .content_len
            if content_len == 0:
                continue
            status = history.status
            self.chat_history.append((status, {"role": role, "content": content}, content_len))

            is_left = history.role == "assistant"
            icon_name, role_name, color_name, html = get_history_chat_info(history)

            if is_left:
                self.txt_main.left_title(history._id, icon_name, role_name, color_name)
            else:
                self.txt_main.right_title(history._id, icon_name, role_name, color_name)

            self.txt_main.update_html(html, True)

        self.auto_wrap()
        QApplication.restoreOverrideCursor()

    def init_categories(self):
        """
        初始化聊天话题分类下拉框控件
        :return:
        """
        self.cmb_categories.clear()
        self.cmb_categories.addItem("", 0)
        for category in ConfigOp.get_categories():
            self.cmb_categories.addItem(category.cfg_key, category._id)

        session: Session = SessionOp.select(self.session_id, Session)
        if session is not None:
            index = self.cmb_categories.findData(session.category_id)  # 查找值为 20 的选项的索引
            self.cmb_categories.setCurrentIndex(index)  # 将找到的索引设置为当前选中项

        self.cmb_categories.setEnabled(False)

    def on_chat_category_changed(self):
        self.init_categories()

    def auto_wrap(self):
        if self.chk_auto_wrap.checkState() == Qt.Checked:
            self.txt_main.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.txt_main.setLineWrapMode(QTextEdit.NoWrap)
