# -*- coding:utf-8 -*-
# title           :chat_window.py
# description     :聊天窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QThread
from PyQt5.QtGui import QTextCursor, QMouseEvent
from PyQt5.QtWidgets import QApplication, QPushButton, QTextEdit, QHBoxLayout
from PyQt5.QtWidgets import QMdiSubWindow, QWidget
from PyQt5.uic import loadUi

from common.app_events import AppEvents
from common.chat_utils import build_my_message, build_openai_message, plain_text_to_html, build_chat_title, \
    message_total_size, get_button_functions
from common.control_init import init_ai_model_combo, init_ai_role_combo, init_categories_combo
from common.mdi_window_mixin import MdiWindowMixin
from common.message_box import MessageBox
from common.str_utils import is_empty
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui, get_html_style
from controls.coming_soon import ComingSoon
from controls.cook_menu_view import CookMenuView
from controls.douyin_video_view import DouyinVideoView
from db.db_ops import ConfigOp
from db.db_ops import HistoryOp
from db.db_ops import SessionOp
from db.db_utils import get_timestamp_str
from db.entities import History
from db.entities import Session
from db.entities.consts import CFG_KEY_TAB_FUNCTION
from db.entities.session_setting import SessionSetting


class ChatWindow(QMdiSubWindow, UiMixin, MdiWindowMixin):
    """
    聊天窗口
    """
    operate = pyqtSignal()

    def __init__(self, session_id, title="", read_part_data=False):
        super().__init__()
        # 从 .ui 文件加载 UI
        loadUi(find_ui("ui/chat.ui"), self)
        self.chat_history = []
        # 加载指定 session_id 的聊天会话
        self.load_session(session_id, title)
        # 初始化控件
        self.init_controls()
        # 初始化聊天会话中的设置项
        self.init_session_settings(self.session)
        # 初始化历史记录，等待继续聊天
        self.init_history_messages(read_part_data)
        # 检查 API Key 是否设置
        self.check_api_key()
        self.setWindowIcon(self.default_icon())
        # 绑定事件
        self.bind_events()
        # 初始化工作线程
        self.init_worker_thread()

    def chat_finished(self):
        """聊天"""
        self.btn_stop.setDisabled(True)

    def append_message(self, text):
        """
        追加消息到聊天文本框
        :param text: 聊天内容
        :return:
        """
        self.txt_main.moveCursor(QTextCursor.End)
        self.txt_main.insertHtml(text)
        self.txt_main.moveCursor(QTextCursor.End)

    def init_worker_thread(self):
        """
        初始化工作线程
        :return:
        """
        from windows.chat_window_worker import ChatWindowWorker
        self.worker = ChatWindowWorker(ui=self)
        self.worker.appendMessageSignal.connect(self.append_message)
        self.worker.finishSignal.connect(self.chat_finished)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        # 一定先把工作对象移动到thread中然后再connect连接工作对象中的循环工作函数
        # 否则会导致主控窗口在工作对象循环时显示不出来
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
        try:
            msg_context_check = self.session_settings.msg_context_check
            ai_role = self.session_settings.ai_role

            if msg_context_check is not None:
                self.chk_msg_context.setCheckState(msg_context_check)
            if ai_role is not None:
                for i in range(self.cmb_ai_role.count()):
                    if ai_role == self.cmb_ai_role.itemText(i):
                        self.cmb_ai_role.setCurrentIndex(i)
                        break
        except Exception as e:
            print(e)

    def init_tab_function(self):
        """
        初始化页签功能
        :return:
        """
        configs = ConfigOp.get_configs(CFG_KEY_TAB_FUNCTION)
        tabs_text = [i.cfg_key for i in configs]
        # self.tab_main.children()[0].children()[4] self.tab_food
        # self.tab_main.widget(i).objectName()
        # print(self.tab_main.count())
        for i in range(self.tab_main.count() - 1, 0, -1):
            if self.tab_main.tabText(i) not in tabs_text:
                # self.tab_main.widget(i).hide()
                self.tab_main.removeTab(i)
        # print(self.tab_main.count())

    def init_controls(self):
        """
        初始化控件
        :return:
        """
        self.dock_fill()
        self.init_ai_role()
        self.init_button_func()
        self.init_categories()

        init_ai_model_combo(self.cmb_ai_model, self.session_id)

        self.splitter.setSizes([600, 400])

        self.tab_text.setLayout(self.layout_text)
        # 工作助理
        self.work_helper_view = ComingSoon(self.tab_oa)
        # self.tab_oa.setLayout(self.work_helper_view.layout_main)
        # 抖音帮手
        self.douyin_video_view = DouyinVideoView(self.tab_douyin, self.send_message)
        self.tab_douyin.setLayout(self.douyin_video_view.layout_main)
        # 家庭厨师
        self.cook_menu_view = CookMenuView(self.tab_food, self.send_message)
        self.tab_food.setLayout(self.cook_menu_view.layout_main)

        # 语音聊天
        self.voice_chat_view = ComingSoon(self.tab_voice_chat)

        self.init_tab_function()

        self.txt_main.setReadOnly(True)
        self.txt_main.setFont(self.default_font())
        self.txt_main.setStyleSheet(get_html_style())

        self.tab_main.setCurrentIndex(0)
        self.chk_md.setVisible(False)

        self.set_input_style([self.txt_chat])
        self.set_placeholder_text([self.txt_chat])
        self.txt_chat.installEventFilter(self)

        self.set_icons([self.btn_send, self.btn_stop], ["comment2.png", "stop.png"])

        self.btn_stop.setDisabled(True)

    def stop_chat(self):
        """
        停止聊天
        :return:
        """
        self.worker.chat_stop = True

    def bind_events(self):
        """
        绑定事件
        :return:
        """
        self.txt_title.textChanged.connect(self.title_changed)
        self.cmb_categories.currentIndexChanged.connect(self.category_changed)
        self.cmb_ai_model.currentIndexChanged.connect(self.model_changed)
        self.chk_auto_wrap.clicked.connect(self.auto_wrap)
        self.chk_msg_context.clicked.connect(self.on_msg_context_changed)
        self.cmb_ai_role.currentIndexChanged.connect(self.ai_role_changed)
        self.btn_send.clicked.connect(self.send_button_clicked)
        self.btn_clear_context.clicked.connect(self.clear_msg_context)
        self.btn_stop.clicked.connect(self.stop_chat)

        AppEvents.on_chat_history_changed_subscription(self.on_chat_history_changed)
        AppEvents.on_ai_roles_changed_subscription(self.on_ai_roles_changed)
        AppEvents.on_button_functions_changed_subscription(self.on_button_functions_changed)
        AppEvents.on_chat_category_changed_subscription(self.on_chat_category_changed)
        AppEvents.on_recieved_message_subscription(self.recieved_message)

    def unbind_events(self):
        """
        解绑事件
        :return:
        """
        self.stop_chat()
        self.worker_thread.exit(0)

        AppEvents.on_chat_history_changed_unsubscription(self.on_chat_history_changed)
        AppEvents.on_ai_roles_changed_unsubscription(self.on_ai_roles_changed)
        AppEvents.on_button_functions_changed_unsubscription(self.on_button_functions_changed)
        AppEvents.on_chat_category_changed_unsubscription(self.on_chat_category_changed)
        AppEvents.on_recieved_message_unsubscription(self.recieved_message)

        self.douyin_video_view.unbind_events()

    def recieved_message(self, status, message):
        layout_right = self.find_layout_by_name(obj_name="layout_right")
        self.set_layout_enabled(layout_right, True)

    def save_settings(self):
        """
        保存设置
        :return:
        """
        msg_context_check = self.chk_msg_context.checkState()
        ai_role = self.cmb_ai_role.currentText()
        if is_empty(ai_role):
            ai_role = ""

        self.session_settings.msg_context_check = msg_context_check
        self.session_settings.ai_role = ai_role
        json_str = self.session_settings.to_json_str()

        SessionOp.update_settings(self.session_id, json_str)

    def ai_role_changed(self):
        """
        AI角色修改后，保存设置
        :return:
        """
        self.save_settings()

    def on_msg_context_changed(self):
        """
        启用消息上下文修改，保存设置
        :return:
        """
        self.save_settings()

    def send_message(self, content, no_context):
        if not self.check_api_key():
            return
        chat_content = build_my_message(content)
        self.append_message(chat_content + "<br>")
        self.run_send_message_thread(content, no_context)

    def eventFilter(self, obj, event):
        if obj is self.txt_chat and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                # 按下 Ctrl+Enter 键，发送文本消息
                # print('发送文本消息:', self.txt_chat.toPlainText())
                self.send_button_clicked()
                return True
        return super().eventFilter(obj, event)

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

    def btn_clear_context_update(self):
        """
        更新缩减上下文按钮的消息大小
        :return:
        """
        self.btn_clear_context.setText(f"缩减上下文({message_total_size(self.chat_history)})")

    def clear_msg_context(self):
        # self.chat_history = self.chat_history[1:]
        msg_context_size = float(ConfigOp.get_sys_config("msg_context_size", 3))
        total_size = 0
        his_len = len(self.chat_history)
        for i in range(his_len - 1, 0, -1):
            _, _, size = self.chat_history[i]
            total_size += size
            if total_size > msg_context_size * 1000:
                if i < his_len - 1:
                    self.chat_history = self.chat_history[i + 1:]
                break

        self.btn_clear_context_update()

    def window_id(self):
        return f"ChatWindow_{self.session_id}"

    def init_history_messages(self, read_part_data):
        """
        初始化历史记录，等待继续聊天
        :param read_part_data: 是否读取部分消息
        :return:
        """
        histories = HistoryOp.select_by_session_id(self.session_id, order_by="order_no, _id", entity_cls=History)
        if len(histories) == 0:
            self.btn_clear_context.setText(f"缩减上下文(0)")
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
                        break

        html = ""
        for history in histories:
            role = history.role
            content = history.content
            content_len = history.content_len
            status = history.status
            self.chat_history.append((status, {"role": role, "content": content}, content_len))
            # AppEvents.on_chat_history_changed()
            if role == "user":
                html += build_my_message(content, role_name=history.role_name)
            elif role == "assistant":
                html += build_openai_message(content, role_name=history.role_name)

        self.clear_msg_context()
        self.btn_clear_context_update()

        self.txt_main.insertHtml(html + "<br>")
        self.txt_main.moveCursor(QTextCursor.End)
        self.auto_wrap()

    def init_categories(self):
        """
        初始化聊天话题分类下拉框控件
        :return:
        """
        init_categories_combo(self.cmb_categories, self.session_id, self.category_changed)

    def title_changed(self):
        """
        标题修改后触发
        :return:
        """
        title = self.txt_title.text().strip()
        if is_empty(title):
            return
        self.setWindowTitle(title)
        self.window_menu_action.setText(title)
        SessionOp.update(self.session_id, title)

    def category_changed(self):
        """
        话题分类修改后触发
        :return:
        """
        category_id = self.cmb_categories.itemData(self.cmb_categories.currentIndex())
        if category_id is not None:
            if category_id > 0:
                SessionOp.update_category(self.session_id, category_id)

    def model_changed(self):
        """
        模型修改后触发
        :return:
        """
        model_id = self.cmb_ai_model.currentText()
        if is_empty(model_id):
            model_id = "gpt-3.5-turbo"
        SessionOp.update_model(self.session_id, model_id)

    def on_chat_history_changed(self):
        """
        当聊天话题分类配置进行了修改，会触发事件
        :return:
        """
        self.btn_clear_context_update()

    def on_ai_roles_changed(self):
        self.init_ai_role()

    def on_button_functions_changed(self):
        self.init_button_func()

    def on_chat_category_changed(self):
        self.init_categories()

    def to_markdown(self):
        # QTextEdit.for
        # QTextEdit.toHtml()
        if self.chk_md.checkState() == Qt.Checked:
            self.txt_main.toMarkdown()
        else:
            self.txt_main.toHtml()

    def auto_wrap(self):

        if self.chk_auto_wrap.checkState() == Qt.Checked:
            self.txt_main.setLineWrapMode(QTextEdit.WidgetWidth)
            self.txt_main.moveCursor(QTextCursor.End)
        else:
            self.txt_main.setLineWrapMode(QTextEdit.NoWrap)

    def init_ai_role(self):
        init_ai_role_combo(self.cmb_ai_role)

    def check_chat_text(self):
        return self.check_text_box(self.txt_chat, "请输入聊天内容")

    def right_clicked_button_func(self, func_name):
        """
        按钮功能点击鼠标右键会触发
        :param func_name:
        :return:
        """
        core_functions = get_button_functions()
        # print(func[func_name])
        func = core_functions[func_name]
        sample = func["Sample"]
        chat_text = self.txt_chat.toPlainText()
        if is_empty(chat_text):
            self.txt_chat.setPlainText(sample)
        elif chat_text.strip() == sample.strip():
            pass
        else:
            self.txt_chat.setPlainText(f"{chat_text}\n{sample}")

    def clicked_button_func(self, func_name):
        """
        按钮功能点击会触发
        :param func_name:
        :return:
        """
        if not self.check_api_key():
            return
        if not self.check_chat_text():
            return
        core_functions = get_button_functions()
        # print(func[func_name])
        func = core_functions[func_name]
        content = self.txt_chat.toPlainText()
        if "Prefix" in func:
            prefix = func["Prefix"]
            if prefix is not None and len(prefix) > 0:
                content = prefix + content
        if "Suffix" in func:
            suffix = func["Suffix"]
            if suffix is not None and len(suffix) > 0:
                content = content + suffix

        chat_content = build_my_message(content)
        self.append_message(chat_content + "<br>")
        self.run_send_message_thread(content)

    def create_prompt_button(self, sample, button_style, mouse_pressed, key):
        """
        创建提示语模板按钮
        :param sample:
        :param button_style:
        :param mouse_pressed:
        :param key:
        :return:
        """
        btn_prompt = QPushButton("?")
        btn_prompt.setToolTip("点击鼠标使用提示语模板")
        btn_prompt.sample = sample
        btn_prompt.setMinimumWidth(13)
        btn_prompt.setMaximumWidth(13)
        btn_prompt.mousePressEvent = mouse_pressed(key)
        # btn_prompt.setFlat(True)
        # btn_prompt.setDefault(True)
        # btn_prompt.setAutoDefault(True)
        # btn_prompt.setAutoFillBackground(True)
        if not is_empty(button_style):
            # button_style = "border-color: rgb(255, 0, 127);" + button_style
            btn_prompt.setStyleSheet(button_style)
        return btn_prompt

    def init_button_func(self):
        """
        初始化按钮功能
        :return:
        """
        grid = self.grid_core_func
        grid.setSpacing(10)

        for i in reversed(range(grid.count())):
            button = grid.itemAt(i).widget()
            # button.clicked.disconnect()
            button.setParent(None)

        func = get_button_functions()

        # 创建多个按钮，并添加到布局中
        buttons = []
        for key in func.keys():
            widget = QWidget()
            button = QPushButton(key)
            button_style = func[key]["ButtonStyle"]
            if not is_empty(button_style):
                button.setStyleSheet(button_style)

            layout = QHBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            # 增加功能按钮
            layout.addWidget(button)

            def clicked(func_name):
                def inner():
                    self.clicked_button_func(func_name)

                return inner

            def mouse_pressed(func_name):
                def inner(mouse_event: QMouseEvent):
                    # print("onRightMouseButtonClicked", mouse_event, func_name)
                    # 判断是否是鼠标右键
                    if mouse_event.button() == Qt.RightButton:
                        self.right_clicked_button_func(func_name)
                    elif mouse_event.button() == Qt.LeftButton:
                        # self.clicked_button_func(func_name)
                        self.right_clicked_button_func(func_name)

                return inner

            sample = func[key]["Sample"]
            if not is_empty(sample):
                # 创建一个提示语按钮
                btn_prompt = self.create_prompt_button(sample, button_style, mouse_pressed, key)
                # 让按钮的文本尽可能居中
                button.setText("  " + button.text())
                # 增加功能按钮对应的提示语按钮
                layout.addWidget(btn_prompt)

            button.clicked.connect(clicked(key))

            widget.setLayout(layout)
            buttons.append(widget)

        # 进行布局
        num_rows = 4
        for i, button in enumerate(buttons):
            row = i // num_rows
            col = i % num_rows
            grid.addWidget(button, row, col)

        # self.function_buttons = buttons

    def send_button_clicked(self):
        """
        按钮发送消息
        :return:
        """
        if not self.check_api_key():
            return
        if not self.check_chat_text():
            return

        content = self.txt_chat.toPlainText()

        chat_title = build_chat_title("[我]", "user.png", "blue")
        self.append_message(chat_title + plain_text_to_html(content) + "<br>")
        self.run_send_message_thread(content)

    def build_messages(self, history_messages, no_context):
        """

        :param history_messages:
        :param no_context: 是否带有上下文
        :return:
        """
        ai_role = self.cmb_ai_role.itemData(self.cmb_ai_role.currentIndex())
        if ai_role == "":
            messages = []
        else:
            messages = [{"role": "system", "content": ai_role}]
        if self.chk_msg_context.checkState() == Qt.Checked or no_context:
            messages = messages + [history_messages[-1][1]]
        else:
            messages = messages + [m[1] for m in history_messages]

        return messages

    def run_send_message_thread(self, message, no_context=False):
        """
        运行发送消息线程
        :param message:
        :param no_context:
        :return:
        """

        if not self.check_api_key():
            return

        layout_right = self.find_layout_by_name(obj_name="layout_right")
        self.set_layout_enabled(layout_right, False)

        what_i_have_asked = {}
        what_i_have_asked["role"] = "user"
        what_i_have_asked["content"] = message

        HistoryOp.insert(role="user",
                         content=message,
                         content_type="text",
                         session_id=self.session_id,
                         status=0)

        self.chat_history.append((0, what_i_have_asked, len(message)))
        AppEvents.on_chat_history_changed()

        messages = self.build_messages(self.chat_history, no_context)

        # print(messages)
        model_id = self.cmb_ai_model.currentText()

        self.model_id = model_id
        self.messages = messages

        # 发送消息前，停止按钮有效，线程聊天停止关闭
        self.btn_stop.setDisabled(False)
        self.worker.chat_stop = False

        self.worker_thread.start()
        self.operate.emit()
