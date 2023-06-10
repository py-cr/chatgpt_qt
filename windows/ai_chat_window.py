# -*- coding:utf-8 -*-
# title           :ai_chat_window.py
# description     :AI聊天窗口
# author          :Python超人
# date            :2023-6-10
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import json

import pandas.io.clipboard as cb
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QSplitter, \
    QTextEdit, QVBoxLayout, QWidget
from PyQt5.uic import loadUi

from common.ai_converse import AiConverse
from common.app_events import AppEvents
from common.chat_utils import get_history_chat_info, required_histories_for_win
from common.control_init import init_ai_model_combo, init_categories_combo
from common.message_box import MessageBox
from common.str_utils import is_empty
from common.ui_utils import find_ui
from controls.chat_view import ChatView
from db.db_ops import ConfigOp
from db.db_ops import HistoryOp
from db.db_ops import SessionOp
from db.db_utils import get_timestamp_str
from db.entities import History
from db.entities import Session
from db.entities.session_setting import SessionSetting
from windows.session_window import SessionWindow


class AiChatWindow(SessionWindow):
    """
    AI聊天窗口
    """
    operate = pyqtSignal()

    def __init__(self, session_id, title="", read_part_data=False, new_ai_chat=None, settings=None):
        super().__init__()
        # 从 .ui 文件加载 UI
        loadUi(find_ui("ui/ai_chat.ui"), self)
        self.read_part_data = read_part_data
        self.chat_history = []
        # 加载指定 session_id 的聊天会话
        self.load_session(session_id, title)
        # 初始化控件
        self.init_controls()
        # 初始化聊天会话中的设置项
        self.init_session_settings(self.session)
        # 检查 API Key 是否设置
        self.check_api_key()

        self.setWindowIcon(self.default_icon())
        # 绑定事件
        self.bind_events()
        # 两AI聊天类
        self.ai_converse = AiConverse()
        # 传入的 main.py 的函数，可以打开一个新的AI聊天对话窗口
        self.new_ai_chat = new_ai_chat

        if settings is not None:
            # 初始化设置
            self.init_settings(settings)

        # 初始化工作线程
        self.init_worker_thread()

    def init_worker_thread(self):
        """
        初始化工作线程
        :return:
        """
        from windows.ai_chat_window_worker import AiChatWindowWorker
        self.worker = AiChatWindowWorker(ui=self)

        self.worker.updateHtmlSignal.connect(self.txt_main.update_html)
        self.worker.appendTitleSignal.connect(self.txt_main.append_title)

        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.operate.connect(self.worker.do)

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

            self.setWindowTitle(subject)
        else:
            self.setWindowTitle(title)
            self.txt_title.setText(title)

    def init_session_settings(self, session: Session):
        """
        初始化聊天会话中的设置项
        :param session:
        :return:
        """
        self.session_settings = SessionSetting(session.settings)
        if not is_empty(self.session_settings.ai1_name):
            self.txt_ai1_name.setText(self.session_settings.ai1_name)

        if not is_empty(self.session_settings.ai2_name):
            self.txt_ai2_name.setText(self.session_settings.ai2_name)

        self.txt_ai1_role.setPlainText(self.session_settings.ai1_role)
        self.txt_ai2_role.setPlainText(self.session_settings.ai2_role)
        self.txt_ai_init_subject.setPlainText(self.session_settings.ai_init_subject)

    def init_controls(self):
        """
        初始化控件
        :return:
        """

        self.dock_fill()
        self.init_categories()
        init_ai_model_combo(self.cmb_ai_model, self.session_id)
        self.group_ai1.setLayout(self.form_ai1)
        self.group_ai2.setLayout(self.form_ai2)
        splitter: QSplitter = self.splitter
        splitter.setSizes([600, 400])

        layout_left: QVBoxLayout = self.layout_left
        widget: QWidget = self.txt_main.parent()

        self.txt_main.setParent(None)
        widget.setContentsMargins(0, 0, 0, 0)

        self.txt_main = ChatView(self)
        self.txt_main.data_bridge.required_histories = self.required_histories
        self.txt_main.data_bridge.supported_styles = self.supported_styles
        layout_left.addWidget(self.txt_main)
        layout_left.setSpacing(0)
        # self.txt_main.browser.loadFinished.connect(self.loadFinished)

        self.btn_stop.setDisabled(True)

        self.set_placeholder_text([self.txt_ai1_name, self.txt_ai2_name,
                                   self.txt_ai1_role, self.txt_ai2_role, self.txt_ai_init_subject])

        self.set_icons([self.btn_copy, self.btn_paste, self.btn_stop, self.btn_start, self.btn_new_chat],
                       ["page-copy.png", "page-paste.png", "stop.png", "comment2.png", "comment_add.png"])

    # def loadFinished(self, bool):
    #     if bool:
    #         # 初始化历史记录，等待继续聊天，需要等浏览器网页加载完成后，再加载历史消息
    #         self.init_history_messages(self.read_part_data)

    def stop_chat(self):
        self.ai_converse.chat_stop = True

    def copy_to_clipboard(self):
        """
        复制信息到剪切板
        :return:
        """
        data = self.get_settings()
        cb.copy(json.dumps(data, ensure_ascii=False))  # 复制到剪切板

    def get_settings(self):
        ai1_name = self.txt_ai1_name.text().strip()
        ai2_name = self.txt_ai2_name.text().strip()
        ai1_role = self.txt_ai1_role.toPlainText().strip()
        ai2_role = self.txt_ai2_role.toPlainText().strip()
        ai_init_subject = self.txt_ai_init_subject.toPlainText().strip()

        data = {
            "ai1_name": ai1_name,
            "ai2_name": ai2_name,
            "ai1_role": ai1_role,
            "ai2_role": ai2_role,
            "ai_init_subject": ai_init_subject
        }
        return data

    def paste_from_clipboard(self):
        json_data = cb.paste()
        try:
            data = json.loads(json_data)
            self.init_settings(data)
        except Exception as e:
            return

    def init_settings(self, settings):
        if settings is None:
            return
        ai1_name = self.txt_ai1_name.text().strip()
        ai2_name = self.txt_ai2_name.text().strip()
        ai1_role = self.txt_ai1_role.toPlainText().strip()
        ai2_role = self.txt_ai2_role.toPlainText().strip()
        ai_init_subject = self.txt_ai_init_subject.toPlainText().strip()

        if len(ai1_role) > 0:
            ai1_role += "\n"
        if len(ai2_role) > 0:
            ai2_role += "\n"
        if len(ai_init_subject) > 0:
            ai_init_subject += "\n"

        if "ai1_name" in settings:
            if not is_empty(settings["ai1_name"]):
                ai1_name = settings["ai1_name"]

        if "ai2_name" in settings:
            if not is_empty(settings["ai2_name"]):
                ai2_name = settings["ai2_name"]

        self.txt_ai1_name.setText(ai1_name)
        self.txt_ai2_name.setText(ai2_name)

        if "ai1_role" in settings:
            self.txt_ai1_role.setPlainText(ai1_role + settings["ai1_role"])
        if "ai2_role" in settings:
            self.txt_ai2_role.setPlainText(ai2_role + settings["ai2_role"])
        if "ai_init_subject" in settings:
            self.txt_ai_init_subject.setPlainText(ai_init_subject + settings["ai_init_subject"])

    def bind_events(self):

        self.txt_title.textChanged.connect(self.title_changed)
        self.cmb_categories.currentIndexChanged.connect(self.category_changed)
        self.cmb_ai_model.currentIndexChanged.connect(self.model_changed)
        self.chk_auto_wrap.clicked.connect(self.auto_wrap)
        self.chk_auto_scroll.clicked.connect(self.auto_scroll)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.btn_paste.clicked.connect(self.paste_from_clipboard)
        self.btn_new_chat.clicked.connect(self.open_new_ai_chat)
        self.btn_stop.clicked.connect(lambda: self.stop_chat())
        self.txt_ai1_name.textChanged.connect(self.save_settings)
        self.txt_ai2_name.textChanged.connect(self.save_settings)
        self.txt_ai1_role.textChanged.connect(self.save_settings)
        self.txt_ai2_role.textChanged.connect(self.save_settings)
        self.txt_ai_init_subject.textChanged.connect(self.save_settings)

        AppEvents.on_chat_category_changed_subscription(self.on_chat_category_changed)

    def open_new_ai_chat(self):
        if callable(self.new_ai_chat):
            settings = self.get_settings()
            self.new_ai_chat(settings)

    def unbind_events(self):
        self.stop_chat()
        self.worker_thread.exit(0)
        AppEvents.on_chat_category_changed_unsubscription(self.on_chat_category_changed)

    def save_settings(self):

        self.session_settings.ai1_name = self.txt_ai1_name.text().strip()
        self.session_settings.ai2_name = self.txt_ai2_name.text().strip()

        self.session_settings.ai1_role = self.txt_ai1_role.toPlainText().strip()
        self.session_settings.ai2_role = self.txt_ai2_role.toPlainText().strip()
        self.session_settings.ai_init_subject = self.txt_ai_init_subject.toPlainText().strip()

        code_style = self.cmb_style.itemData(self.cmb_style.currentIndex())
        self.session_settings.code_style = code_style

        json_str = self.session_settings.to_json_str()

        SessionOp.update_settings(self.session_id, json_str)

    def check_api_key(self, show_window=True):
        """
        检查 API Key 是否设置
        :return:
        """
        from windows.main_window import MainWindow
        api_key = ConfigOp.get_sys_config("api_key")
        if is_empty(api_key):
            if not show_window:
                return False
            QApplication.restoreOverrideCursor()
            MessageBox.warning(self, "设置 APIKey", "请先设置 OpenAI 提供的 API Key")
            MainWindow.instance.openai_setting()
            return False
        return True

    def window_id(self):
        return f"AiChatWindow_{self.session_id}"

    def required_histories(self, history_id):
        required_histories_for_win(self, history_id)

    def supported_styles(self, style_names):
        self.cmb_style.addItem("默认", "Default")
        style_names = style_names.split("\n")
        for style_name in style_names:
            if not is_empty(style_name):
                self.cmb_style.addItem(style_name, style_name)

        self.cmb_style.currentIndexChanged.connect(self.chat_view_style_changed)

        code_style = self.session_settings.code_style
        if code_style != "Default":
            for i in range(self.cmb_style.count()):
                if code_style == self.cmb_style.itemText(i):
                    self.cmb_style.setCurrentIndex(i)
                    break
            # self.txt_main.changeStyle(code_style)

        # 初始化历史记录，等待继续聊天，需要等浏览器网页加载完成后，再加载历史消息
        self.init_history_messages(self.read_part_data)

    def init_history_messages(self, read_part_data):
        self.all_histories = HistoryOp.select_by_session_id(self.session_id, order_by="order_no, _id",
                                                            entity_cls=History)
        histories = self.all_histories
        # read_part_data =False
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

            self.txt_main.update_html(html, False)

        self.txt_main.highlightAll()
        self.auto_wrap()
        QApplication.restoreOverrideCursor()

    def is_auto_scroll(self):
        if not hasattr(self, "chk_auto_scroll"):
            return True
        return self.chk_auto_scroll.checkState() == Qt.Checked

    def chat_view_style_changed(self):
        styleName = self.cmb_style.itemData(self.cmb_style.currentIndex())
        self.txt_main.changeStyle(styleName)
        self.save_settings()

    def init_categories(self):
        init_categories_combo(self.cmb_categories, self.session_id, self.category_changed)

    def title_changed(self):
        title = self.txt_title.text().strip()
        if is_empty(title):
            return
        self.setWindowTitle(title)
        self.window_menu_action.setText(title)
        SessionOp.update(self.session_id, title)

    def category_changed(self):
        category_id = self.cmb_categories.itemData(self.cmb_categories.currentIndex())
        if category_id is not None:
            if category_id > 0:
                SessionOp.update_category(self.session_id, category_id)

    def model_changed(self):
        model_id = self.cmb_ai_model.currentText()
        if is_empty(model_id):
            model_id = "gpt-3.5-turbo"
        SessionOp.update_model(self.session_id, model_id)

    def on_chat_category_changed(self):
        self.init_categories()

    def auto_scroll(self):
        """
        自动滚动
        :return:
        """
        if self.chk_auto_scroll.checkState() == Qt.Checked:
            self.txt_main.scrollBottomEnabled()
        else:
            self.txt_main.scrollBottomDisabled()

    def auto_wrap(self):

        if self.chk_auto_wrap.checkState() == Qt.Checked:
            self.txt_main.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.txt_main.setLineWrapMode(QTextEdit.NoWrap)

    def check_chat_text(self):
        return self.check_text_box(self.txt_ai_init_subject, "请输入一个聊天的初始话题")

    def on_start(self):
        if not self.check_api_key():
            return

        self.ai_converse.chat_stop = False
        if not self.check_chat_text():
            return

        self.btn_start.setDisabled(True)
        self.btn_stop.setDisabled(False)

        self.ai_converse.ai1_name = self.txt_ai1_name.text().strip()
        self.ai_converse.ai2_name = self.txt_ai2_name.text().strip()
        sleep_sec = int(self.spinbox_sleep.value())

        self.ai_converse.ai1_role = self.txt_ai1_role.toPlainText().strip()
        self.ai_converse.ai2_role = self.txt_ai2_role.toPlainText().strip()
        self.ai_init_subject = self.txt_ai_init_subject.toPlainText().strip()

        self.worker_thread.start()
        self.operate.emit()
        # self.worker.do()
