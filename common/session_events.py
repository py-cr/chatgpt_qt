# -*- coding:utf-8 -*-
# title           :session_events.py
# description     :会话级别的事件订阅和传递
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================


class SessionEvents:
    """
    事件订阅和传递
    """

    def __init__(self):
        # 初始化各类事件的订阅函数列表
        self.on_chat_history_changed_funcs = []
        self.on_recieved_message_funcs = []

    def on_chat_history_changed_subscription(self, fun):
        """
        订阅聊天历史发生改变事件
        :param fun:
        :return:
        """
        # 向on_chat_history_changed_funcs属性中添加函数fun
        self.on_chat_history_changed_funcs.append(fun)

    def on_chat_history_changed_unsubscription(self, fun):
        """
        取消订阅聊天历史发生改变事件
        :param fun:
        :return:
        """
        # 从on_chat_history_changed_funcs属性中删除函数fun
        self.on_chat_history_changed_funcs.remove(fun)

    def on_chat_history_changed(self):
        """
        聊天历史发生改变事件触发
        :return:
        """
        # 触发on_chat_history_changed事件，即遍历on_chat_history_changed_funcs中的每个函数并执行
        for f in self.on_chat_history_changed_funcs:
            f()

    def on_recieved_message_subscription(self, fun):
        """
        订阅收到AI返回的聊天消息事件
        :param fun:
        :return:
        """
        # 向on_recieved_message_funcs属性中添加函数fun
        self.on_recieved_message_funcs.append(fun)

    def on_recieved_message_unsubscription(self, fun):
        """
        取消订阅收到AI返回的聊天消息事件
        :param fun:
        :return:
        """
        # 从on_recieved_message_funcs属性中删除函数fun
        self.on_recieved_message_funcs.remove(fun)

    def on_recieved_message(self, status, message):
        """
        收到AI返回的聊天消息事件触发
        :param message:
        :return:
        """
        # 触发on_recieved_message事件，即遍历on_recieved_message_funcs中的每个函数并执行，将参数message传递给每个函数
        for f in self.on_recieved_message_funcs:
            f(status, message)
