# -*- coding:utf-8 -*-
# title           :main_window.py
# description     :主窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMdiArea
from PyQt5.QtWidgets import QMessageBox, QMdiSubWindow, QAbstractItemView
from PyQt5.uic import loadUi

from common.app_config import DB_NAME
from common.chat_utils import MSG_HISTORY_RECORD_SO_MUCH
from common.message_box import MessageBox
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui
from db.db_ops import ConfigOp
from db.db_ops import HistoryOp
from db.db_ops import SessionOp
from db.entities.consts import CFG_KEY_AI_ROLE, CFG_KEY_CHAT_CATEGORY, CFG_KEY_TAB_FUNCTION
from windows.button_function_window import ButtonFunctionWindow
from windows.chat_recycle_bin import ChatRecycleBin
from windows.chat_window import ChatWindow
from windows.coming_soon_window import ComingSoonWindow
from windows.config_window import ConfigWindow
from windows.history_window import HistoryWindow
from windows.openai_setting import OpenAiSettingDialog


class MainWindow(QMainWindow, UiMixin):
    """
    主窗口
    """

    def __init__(self):
        super().__init__()
        MainWindow.instance = self
        self.setWindowIcon(self.default_icon())
        loadUi(find_ui("ui/main.ui"), self)
        self.setCentralWidget(self.mdiArea)
        self.init_icons()
        # 绑定事件
        self.bind_events()
        # 数据库初始化
        self.db_init()
        # 打开聊天历史
        self.open_chat_history()

    def db_init(self):
        """
        数据库初始化
        :return:
        """
        db_file = os.path.join("data", DB_NAME)
        if not os.path.exists(db_file):
            # 如果数据库不存在，则进行初始化
            ConfigOp.create_table()
            SessionOp.create_table()
            HistoryOp.create_table()

            ConfigOp.init_ai_roles()
            ConfigOp.init_button_funcs()
            ConfigOp.init_categories()
            ConfigOp.init_tab_funcs()

    def init_icons(self):
        self.set_icons([
            self.menu_chat, self.action_new_chat, self.action_chat_history, self.action_exit, self.menu_settings,
            self.action_openai_setting, self.action_roles, self.menu_window, self.action_categories,
            self.action_win_cascade, self.action_win_tile, self.action_recycle_bin, self.action_function,
            self.action_win_min, self.action_win_max, self.action_chatbots,
            self.action_close_others, self.action_close_all_win, self.action_tab_fun
        ], [
            "comment.png", "comment.png", "history.png", "sign-out.png", "settings.png",
            "config.png", "brainstorming.png", "windows.png", "category.png",
            "application_cascade.png", "application_tile_horizontal.png", "bin.png", "button-color-circle.png",
            "application-min.png", "application.png", "bubbles3.png",
            "application_delete.png", "application_cascade_delete.png", "tab.png"
        ])

    def bind_events(self):
        """
        绑定事件
        :return:
        """
        self.action_win_min.setVisible(False)
        self.action_new_chat.triggered.connect(self.new_chat)
        self.action_chatbots.triggered.connect(self.open_coming_soon)
        self.action_chat_history.triggered.connect(self.open_chat_history)
        self.action_exit.triggered.connect(self.quit)
        self.action_openai_setting.triggered.connect(self.openai_setting)
        self.action_roles.triggered.connect(self.roles_settings)
        self.action_tab_fun.triggered.connect(self.tab_function_settings)
        self.action_win_min.triggered.connect(self.sub_win_min)
        self.action_win_max.triggered.connect(self.sub_win_max)
        self.action_win_cascade.triggered.connect(self.sub_win_cascade)
        self.action_win_tile.triggered.connect(self.sub_win_tile)
        self.action_function.triggered.connect(self.function_settings)
        self.action_categories.triggered.connect(self.categories_settings)
        self.action_prompt.triggered.connect(self.open_prompt)
        self.action_recycle_bin.triggered.connect(self.open_recycle_bin)

        self.mdiArea.subWindowActivated.connect(self.handle_subwindow_activated)
        self.action_close_others.triggered.connect(self.close_others_win)
        self.action_close_all_win.triggered.connect(self.close_all_win)

    def handle_subwindow_activated(self, subwindow):
        """
        MDI子窗口被激活会触发
        :param subwindow:
        :return:
        """
        if subwindow is None:
            delattr(self, "activated_subwindow")
        else:
            if hasattr(self, "last_activated_subwindow"):
                if hasattr(self.last_activated_subwindow, "window_menu_action"):
                    self.last_activated_subwindow.window_menu_action.setIcon(self.icon("transparent.png"))

            self.activated_subwindow = subwindow

            if hasattr(self, "activated_subwindow"):
                if hasattr(self.activated_subwindow, "window_menu_action"):
                    # print(self.activated_subwindow.window_menu_action)
                    self.activated_subwindow.window_menu_action.setIcon(self.icon("check.png"))
                    self.last_activated_subwindow = self.activated_subwindow

        # print('SubMdi窗口激活：', subwindow.widget().text())

    def close_all_win(self):
        """
        关闭所有的 MDI子窗口
        :return:
        """
        mdiArea: QMdiArea = self.mdiArea
        if len(mdiArea.subWindowList()) == 0:
            return
        reply = MessageBox.question(self, '确认', '是否关闭所有的窗口？',
                                    buttons=QMessageBox.Yes | QMessageBox.No,
                                    default_button=QMessageBox.No)
        if reply == QMessageBox.No:
            return

        for win in mdiArea.subWindowList():
            win.close()

    def close_others_win(self):
        """
        关闭其他 MDI子窗口（显示在最前面的激活窗口除外）
        :return:
        """
        mdiArea: QMdiArea = self.mdiArea
        if len(mdiArea.subWindowList()) <= 1:
            return

        reply = MessageBox.question(self, '确认', '是否关闭除当前窗口的其他窗口？',
                                    buttons=QMessageBox.Yes | QMessageBox.No,
                                    default_button=QMessageBox.No)
        if reply == QMessageBox.No:
            return

        for win in mdiArea.subWindowList():
            if hasattr(self, "activated_subwindow"):
                if self.activated_subwindow == win:
                    continue
            win.close()
        self.activated_subwindow.showMaximized()

    def open_recycle_bin(self):
        """
        打开回收站
        :return:
        """
        SessionOp.clear_empty_session()
        window = self.find_exists_window("RecycleBin")
        if window is not None:
            self.mdiArea.setActiveSubWindow(window)
            window.showMaximized()
            return
        recycle_bin = ChatRecycleBin(main_window=self)
        mdi_win = self.mdiArea.addSubWindow(recycle_bin)
        # recycle_bin.setWindowTitle("护手掌")
        self.menu_window_add(mdi_win)
        recycle_bin.showMaximized()

    def sub_win_tile(self):
        """
        子窗口排列
        :return:
        """
        mdiArea: QMdiArea = self.mdiArea
        mdiArea.tileSubWindows()

    def sub_win_cascade(self):
        """
        子窗口排列
        :return:
        """
        mdiArea: QMdiArea = self.mdiArea
        mdiArea.cascadeSubWindows()

    def sub_win_max(self):
        """
        子窗口最大化
        :return:
        """
        mdiArea: QMdiArea = self.mdiArea
        for win in mdiArea.subWindowList():
            win.showMaximized()

    def sub_win_min(self):
        """
        子窗口最小化
        :return:
        """
        mdiArea: QMdiArea = self.mdiArea
        for win in mdiArea.subWindowList():
            win.showMinimized()

    def open_coming_soon(self):
        """
        打开一个还没有完成的功能窗口（显示敬请关注）
        :return:
        """
        sub_window = ComingSoonWindow()
        mdi_win = self.mdiArea.addSubWindow(sub_window)
        self.menu_window_add(mdi_win)
        sub_window.showMaximized()

    def new_chat(self):
        """
        新开一个聊天
        :return:
        """
        session_id = SessionOp.insert("")
        self.open_chat_window(session_id, "", True, 0)

    def open_chat_history(self):
        """
        打开聊天历史
        :return:
        """
        history_dock = HistoryWindow(open_chat=self.open_chat_window)
        history_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        history_dock.setWindowTitle("聊天历史")
        history_dock.dockWidgetContents.setLayout(history_dock.layout_main)
        self.addDockWidget(Qt.LeftDockWidgetArea, history_dock)

    def find_exists_window(self, window_id):
        """
        寻找已经存在的窗口对象
        :param window_id: 唯一窗口ID
        :return:
        """
        windows = self.mdiArea.subWindowList()
        for i, window in enumerate(windows):
            # child = window.widget()
            if hasattr(window, "window_id"):
                if window.window_id() == window_id:
                    return window

        return None

    def open_prompt(self):
        """
        打开一个提示语页面
        :return:
        """
        url_path = "index.html"
        window = self.find_exists_window(f"WebBrowserWindow_{url_path}")
        if window is not None:
            self.mdiArea.setActiveSubWindow(window)
            return

        from windows.web_browser_window import WebBrowserWindow
        sub_window = WebBrowserWindow(url_path=url_path)
        mdi_win = self.mdiArea.addSubWindow(sub_window)
        sub_window.setWindowTitle("提示词大全")
        self.menu_window_add(mdi_win)
        sub_window.showMaximized()

    def open_chat_window(self, session_id, subject, new_chat_session, content_size):
        """
        打开一个聊天窗口
        :param session_id:
        :param subject:
        :param new_chat_session:
        :param content_size:
        :return:
        """
        window = self.find_exists_window(f"ChatWindow_{session_id}")
        if window is not None:
            self.mdiArea.setActiveSubWindow(window)
            window.showMaximized()
            return
        read_part_data = False
        if content_size > 200000:
            QApplication.restoreOverrideCursor()
            reply = MessageBox.question(self, '历史数据较多', MSG_HISTORY_RECORD_SO_MUCH,
                                        buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                        default_button=QMessageBox.Yes)
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                read_part_data = True

            QApplication.setOverrideCursor(Qt.WaitCursor)
        sub_window = ChatWindow(session_id, subject, read_part_data)
        sub_window.new_chat_session = new_chat_session
        mdi_win = self.mdiArea.addSubWindow(sub_window)
        self.menu_window_add(mdi_win)
        sub_window.showMaximized()

    def quit(self):
        """
        退出
        :return:
        """
        reply = MessageBox.question(self, '确认', '您确定要关闭窗口吗？')
        if reply == QMessageBox.Yes:
            self.close()
        else:
            pass

    def openai_setting(self):
        """
        打开OpenAI的设置
        :return:
        """
        dialog = OpenAiSettingDialog()
        r = dialog.exec()
        if r == 1:
            print("保存API Key")
        else:
            print(r)

    def function_settings(self):
        """
        打开按钮功能设置
        :return:
        """
        window_title = "按钮功能设置"
        window = self.find_exists_window(f"ConfigWindow_{window_title}")
        if window is not None:
            self.mdiArea.setActiveSubWindow(window)
            return
        col_names = ['按钮名称', '分类说明', '排序号']

        config_window = ButtonFunctionWindow(window_title, col_names=col_names)
        mdi_win = self.mdiArea.addSubWindow(config_window)
        self.menu_window_add(mdi_win)
        config_window.showMaximized()

    def categories_settings(self):
        """
        打开聊天话题分类设置
        :return:
        """

        def init_func(config_window: ConfigWindow):
            config_window.setColumnsHidden(["cfg_value"])

        self.open_config_window("话题分类设置", CFG_KEY_CHAT_CATEGORY, col_names=['分类名称', '分类说明', '排序号'],
                                init_func=init_func)

    def roles_settings(self):
        """
        打开AI角色设置
        :return:
        """
        self.open_config_window("AI角色设置", CFG_KEY_AI_ROLE, col_names=['AI角色名', '提示词', '排序号'])

    def tab_function_settings(self):
        """
        打开页签功能的设置
        :return:
        """

        def init_func(config_window: ConfigWindow):
            config_window.setColumnsHidden(["cfg_value"])
            config_window.addButton.setParent(None)
            config_window.deleteButton.setParent(None)
            # config_window.updateButton.setParent(None)
            # config_window.btn_line.setParent(None)
            config_window.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
            config_window.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.open_config_window("页签功能设置", CFG_KEY_TAB_FUNCTION, col_names=['页签名称', '页签说明', '排序号'],
                                init_func=init_func)

    def open_config_window(self, window_title, cfg_category, col_names=['Key', '值', '排序号'], init_func=None):
        """
        打开配置窗口
        :param window_title:
        :param cfg_category:
        :param col_names:
        :param init_func:
        :return:
        """
        window = self.find_exists_window(f"ConfigWindow_{window_title}")
        if window is not None:
            self.mdiArea.setActiveSubWindow(window)
            return

        # config_window = ConfigWindow("ai_role")
        config_window = ConfigWindow(window_title, cfg_category, col_names=col_names)
        # config_window.new_chat_session = new_chat_session
        mdi_win = self.mdiArea.addSubWindow(config_window)
        self.menu_window_add(mdi_win)
        if callable(init_func):
            init_func(config_window)
        config_window.showMaximized()

    def menu_window_remove(self, mdi_win):
        """
        窗口退出后，从 QMdiArea 中移除，并移除菜单 Action
        :param mdi_win:
        :return:
        """
        menu_window: QMenu = self.menu_window
        open_win_action = mdi_win.window_menu_action
        menu_window.removeAction(open_win_action)
        # QMdiArea
        self.mdiArea.removeSubWindow(mdi_win)
        # self.mdiArea.subWindowList()

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        """

        :param text:
        :param slot:
        :param shortcut:
        :param icon:
        :param tip:
        :param checkable:
        :param signal:
        :return:
        """
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def menu_window_add(self, mdi_win: QMdiSubWindow):
        """
        新开窗口后，新增菜单 Action，并绑定关闭事件
        :param mdi_win:
        :return:
        """
        menu_window: QMenu = self.menu_window
        # win: QWidget = mdi_win.widget()
        win = mdi_win
        if win is None:
            win = mdi_win

        def open_win():
            # print(win.windowTitle())
            self.mdiArea.setActiveSubWindow(mdi_win)

        open_win_action = self.createAction(text=win.windowTitle(), slot=open_win)

        menu_window.addAction(open_win_action)
        mdi_win.window_menu_action = open_win_action
        # 记录
        closeEvent = win.closeEvent

        def close_action(close_event: QCloseEvent):
            if not closeEvent(close_event):
                if hasattr(mdi_win, "new_chat_session"):
                    if mdi_win.new_chat_session:
                        # 删除空的会话(一般为打开聊天窗口，但没有聊天就关闭的窗口)
                        SessionOp.delete_empty_session(mdi_win.session_id)
                if hasattr(mdi_win, "unbind_events"):
                    mdi_win.unbind_events()
                window_state = mdi_win.windowState()
                self.menu_window_remove(mdi_win)
                mdiArea: QMdiArea = self.mdiArea
                activateWindow = mdiArea.activateWindow()
                if activateWindow is not None:
                    activateWindow.setWindowState(window_state)
                else:
                    sub_windows = self.mdiArea.subWindowList()
                    if len(sub_windows) > 0:
                        sub_windows[0].setWindowState(window_state)
                # sub_windows = self.mdiArea.subWindowList()
                # for sub_window in sub_windows:
                #     if sub_window != self:
                #         sub_window.setWindowState(window_state)

        win.closeEvent = close_action
