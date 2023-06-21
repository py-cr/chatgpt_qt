# -*- coding:utf-8 -*-
# title           :message_box.py
# description     :消息框工具类
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QApplication


class MessageBox:
    """
    消息框工具类
    """

    def __init__(self):
        pass

    @staticmethod
    def show(widget, title, text, buttons, default_button, window_icon=None, icon=None):
        """
        显示消息框
        :param widget: 指定当前的窗口的 widget
        :param title: 消息框标题
        :param text: 消息框内容
        :param buttons: 消息框支持的按钮
        :param default_button: 消息框默认按钮
        :param window_icon: 消息框窗口图标
        :param icon: 消息的图标
        @return:

        """
        locales = QLocale.matchingLocales(QLocale.Chinese, QLocale.AnyScript, QLocale.China)
        locale = locales[0]

        msgbox = QMessageBox()

        msgbox.setLocale(locale)

        if window_icon is None and widget is not None:
            window_icon = QIcon(widget.windowIcon())

        if window_icon is not None:
            msgbox.setWindowIcon(window_icon)

        if icon is not None:
            msgbox.setIcon(icon)

        msgbox.setWindowTitle(title)

        if len(text) < 30:
            text = text.ljust(30, " ")

        msgbox.setText(text)
        # QMessageBox.setWindowTitle(msgbox, title)
        # QMessageBox.setText(msgbox, text)
        msgbox.setStandardButtons(buttons)

        if default_button is not None:
            msgbox.setDefaultButton(default_button)

        MessageBox.set_button_text(msgbox, QMessageBox.Yes, "是(&Y)")
        MessageBox.set_button_text(msgbox, QMessageBox.No, "否(&N)")
        MessageBox.set_button_text(msgbox, QMessageBox.Ok, "确定(&O)")
        MessageBox.set_button_text(msgbox, QMessageBox.Cancel, "取消(&C)")
        MessageBox.set_button_text(msgbox, QMessageBox.Close, "关闭(&C)")
        MessageBox.set_button_text(msgbox, QMessageBox.NoAll, "非全部(&N)")
        MessageBox.set_button_text(msgbox, QMessageBox.NoToAll, "全否(&N)")

        MessageBox.set_button_text(msgbox, QMessageBox.Discard, "放弃(&D)")
        MessageBox.set_button_text(msgbox, QMessageBox.Save, "保存(&S)")
        MessageBox.set_button_text(msgbox, QMessageBox.SaveAll, "保存所有(&S)")

        MessageBox.set_button_text(msgbox, QMessageBox.Abort, "中止(&A)")

        MessageBox.set_button_text(msgbox, QMessageBox.Apply, "应用(&A)")
        MessageBox.set_button_text(msgbox, QMessageBox.Help, "帮助(&H)")
        MessageBox.set_button_text(msgbox, QMessageBox.Ignore, "忽略(&I)")

        MessageBox.set_button_text(msgbox, QMessageBox.Reset, "重置(&R)")

        MessageBox.set_button_text(msgbox, QMessageBox.Reset, "重置(&R)")
        MessageBox.set_button_text(msgbox, QMessageBox.Retry, "重试(&R)")
        MessageBox.set_button_text(msgbox, QMessageBox.YesToAll, "所有全是(&A)")

        # MessageBox.set_button_text(msgbox, QMessageBox.Rejected, "拒绝(&R)")
        # MessageBox.set_button_text(msgbox, QMessageBox.Accepted, "接受(&A)")
        # msgbox.setMinimumWidth(100000)

        # msgbox.setMinimumSize()
        reply = msgbox.exec()
        return reply

    @staticmethod
    def set_button_text(msgbox, button, text):
        """
        修改按钮的文本
        :param msgbox: 消息框对象
        :param button: 消息框按钮对象
        :param text: 文本
        :return:
        """
        msg_button = msgbox.button(button)
        if msg_button is not None:
            msg_button.setText(text)

    @staticmethod
    def question(widget, title, text, buttons=QMessageBox.Yes | QMessageBox.No, default_button=QMessageBox.No):
        """
        确认框
        :param widget: 指定当前的窗口的 widget
        :param title: 消息框标题
        :param text: 消息框内容
        :param buttons: 消息框支持的按钮
        :param default_button: 消息框默认按钮
        @return:

        """
        return MessageBox.show(widget, title, text,
                               buttons=buttons,
                               default_button=default_button, icon=QMessageBox.Icon.Question)

    @staticmethod
    def information(widget, title, text):
        """
        确认框
        :param widget: 指定当前的窗口的 widget
        :param title: 消息框标题
        :param text: 消息框内容
        @return:
        """
        return MessageBox.show(widget, title, text,
                               buttons=QMessageBox.Ok,
                               default_button=None, icon=QMessageBox.Icon.Information)

    @staticmethod
    def error(widget, title, text):
        """
        确认框
        :param widget: 指定当前的窗口的 widget
        :param title: 消息框标题
        :param text: 消息框内容
        @return:
        """
        return MessageBox.show(widget, title, text,
                               buttons=QMessageBox.Ok,
                               default_button=None, icon=QMessageBox.Icon.Critical)

    @staticmethod
    def warning(widget, title, text):
        """
        确认框
        :param widget: 指定当前的窗口的 widget
        :param title: 消息框标题
        :param text: 消息框内容
        @return:
        """
        return MessageBox.show(widget, title, text,
                               buttons=QMessageBox.Ok,
                               default_button=None, icon=QMessageBox.Icon.Warning)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    msgbox = MessageBox.warning(None, "提醒", "1111111111111")
    msgbox.exec_()
    sys.exit()
