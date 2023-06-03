# -*- coding:utf-8 -*-
# title           :openai_setting.py
# description     :OpenAI设置窗口
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QApplication
from PyQt5.uic import loadUi

from common.chat_session import ChatSession
from common.message_box import MessageBox
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui
from db.db_ops import ConfigOp


class OpenAiSettingDialog(QDialog, UiMixin):
    """
    OpenAi设置窗口
    """

    def __init__(self, ):
        # call QWidget constructor
        super().__init__()

        # 从 .ui 文件加载 UI
        r = loadUi(find_ui("openai_setting.ui"), self)

        self.setWindowTitle("OpenAI 设置")
        self.setWindowIcon(self.default_icon())
        # 初始化控件
        self.init_controls()
        self.load_config()

    def init_controls(self):
        """
        初始化控件
        :return:
        """
        reg = QRegExp("[a-zA-Z][a-zA-Z0-9-_]+$")
        regVal = QRegExpValidator()
        regVal.setRegExp(reg)
        self.txt_api_key.setValidator(regVal)

        num_reg = QRegExp("[0-9][0-9.]+$")
        num_regVal = QRegExpValidator()
        num_regVal.setRegExp(num_reg)
        self.txt_context_size.setValidator(num_regVal)

        # 获取 QDialogButtonBox 对象
        button_box = self.findChild(QDialogButtonBox, 'buttonBox')

        button_cancel = button_box.button(QDialogButtonBox.Cancel)
        button_cancel.setText('取消')

        self.txt_api_key.setPlaceholderText(self.txt_api_key.toolTip())
        self.txt_api_key.setWhatsThis("请填写 openai 的API Key")

        # 将“OK”按钮的 clicked 信号连接到 validate 函数
        self.button_ok.clicked.connect(self.do_save)
        self.checkBox.clicked.connect(self.checkBox_changed)
        self.btn_test.clicked.connect(self.connect_test)
        self.checkBox_changed()

    def load_config(self):
        """
        加载配置
        :return:
        """
        api_key = ConfigOp.get_sys_config("api_key")
        msg_context_size = ConfigOp.get_sys_config("msg_context_size", 3)

        self.txt_context_size.setText(str(msg_context_size))
        self.txt_api_key.setText(api_key)
        proxy_enabled = ConfigOp.get_sys_config("proxy_enabled")
        proxy_server = ConfigOp.get_sys_config("proxy_server")
        self.checkBox.setChecked(proxy_enabled == "1")
        self.txt_proxy.setEnabled(proxy_enabled == "1")
        self.txt_proxy.setText(proxy_server)

    def connect_test(self):
        """
        连接测试
        :return:
        """

        err_msg, focus_input = self.validate()
        if len(err_msg) > 0:  # 验证失败
            MessageBox.warning(self, '错误', err_msg)
            if hasattr(focus_input, "setFocus"):
                focus_input.setFocus()  # 让用户重新输入
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        session = ChatSession.create()
        ask = "你好，1+1等于几？"

        api_key = self.txt_api_key.text().strip()
        proxy_server = self.txt_proxy.text().strip()
        proxy_enabled = "1" if self.checkBox.checkState() == Qt.Checked else "0"
        content, error_count = session.send_message(ask, api_key=api_key,
                                                    proxy_enabled=proxy_enabled,
                                                    proxy_server=proxy_server)
        QApplication.restoreOverrideCursor()

        if error_count > 0:
            MessageBox.error(self, "连接失败", content)
        else:
            MessageBox.information(self, "连接成功", f"问：{ask} \n答：{content}")
        # print(content)

    def checkBox_changed(self):
        """
        代理
        :return:
        """
        self.txt_proxy.setEnabled(self.checkBox.checkState() == Qt.Checked)

    def save(self):
        """
        保存配置
        :return:
        """
        api_key = self.txt_api_key.text().strip()
        ConfigOp.save_sys_config("api_key", api_key)

        if self.checkBox.checkState() == Qt.Checked:
            proxy_enabled = "1"
        else:
            proxy_enabled = "0"

        proxy = self.txt_proxy.text().strip()
        msg_context_size = self.txt_context_size.text().strip()
        if msg_context_size is None:
            msg_context_size = 2

        ConfigOp.save_sys_config("proxy_enabled", proxy_enabled)
        ConfigOp.save_sys_config("proxy_server", proxy)
        ConfigOp.save_sys_config("msg_context_size", str(msg_context_size))

        # OpenAi.instance().init_config()

    def do_save(self):
        err_msg, focus_input = self.validate()
        if err_msg == '':  # 验证成功，关闭窗口
            self.save()
            self.accept()
        else:  # 验证失败，显示错误消息
            # self.reject()
            MessageBox.warning(self, '错误', err_msg)
            if hasattr(focus_input, "setFocus"):
                focus_input.setFocus()  # 让用户重新输入

    def validate(self):
        """
        保存前验证
        :return:
        """
        api_key = self.txt_api_key.text().strip()
        proxy = self.txt_proxy.text().strip()

        err_msg = ""
        focus_input = None
        if api_key == "":
            err_msg += "- API Key 不能为空\n"
            if focus_input is None:
                focus_input = self.txt_api_key

        if proxy == "" and self.checkBox.checkState() == Qt.Checked:
            err_msg += "- 代理服务器不能为空\n"
            if focus_input is None:
                focus_input = self.txt_proxy

        return err_msg, focus_input
