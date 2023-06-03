# -*- coding:utf-8 -*-
# title           :app_events.py
# description     :事件订阅和传递
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================


class AppEvents:
    """
    事件订阅和传递
    """

    @staticmethod
    def init():
        # 如果已经存在 on_chat_history_changed_funcs(其中一个) 属性，则不进行初始化
        if hasattr(AppEvents, "on_chat_history_changed_funcs"):
            return

        # 初始化各类事件的订阅函数列表
        # AppEvents.on_chat_history_changed_funcs = []
        # AppEvents.on_recieved_message_funcs = []
        AppEvents.on_button_functions_changed_funcs = []
        AppEvents.on_ai_roles_changed_funcs = []
        AppEvents.on_chat_category_changed_funcs = []

    # @staticmethod
    # def on_chat_history_changed_subscription(fun):
    #     """
    #     订阅聊天历史发生改变事件
    #     :param fun:
    #     :return:
    #     """
    #     # 向on_chat_history_changed_funcs属性中添加函数fun
    #     AppEvents.on_chat_history_changed_funcs.append(fun)
    #
    # @staticmethod
    # def on_chat_history_changed_unsubscription(fun):
    #     """
    #     取消订阅聊天历史发生改变事件
    #     :param fun:
    #     :return:
    #     """
    #     # 从on_chat_history_changed_funcs属性中删除函数fun
    #     AppEvents.on_chat_history_changed_funcs.remove(fun)
    #
    # @staticmethod
    # def on_chat_history_changed():
    #     """
    #     聊天历史发生改变事件触发
    #     :return:
    #     """
    #     # 触发on_chat_history_changed事件，即遍历on_chat_history_changed_funcs中的每个函数并执行
    #     for f in AppEvents.on_chat_history_changed_funcs:
    #         f()
    #
    # @staticmethod
    # def on_recieved_message_subscription(fun):
    #     """
    #     订阅收到AI返回的聊天消息事件
    #     :param fun:
    #     :return:
    #     """
    #     # 向on_recieved_message_funcs属性中添加函数fun
    #     AppEvents.on_recieved_message_funcs.append(fun)
    #
    # @staticmethod
    # def on_recieved_message_unsubscription(fun):
    #     """
    #     取消订阅收到AI返回的聊天消息事件
    #     :param fun:
    #     :return:
    #     """
    #     # 从on_recieved_message_funcs属性中删除函数fun
    #     AppEvents.on_recieved_message_funcs.remove(fun)
    #
    # @staticmethod
    # def on_recieved_message(status, message):
    #     """
    #     收到AI返回的聊天消息事件触发
    #     :param message:
    #     :return:
    #     """
    #     # 触发on_recieved_message事件，即遍历on_recieved_message_funcs中的每个函数并执行，将参数message传递给每个函数
    #     for f in AppEvents.on_recieved_message_funcs:
    #         f(status, message)

    @staticmethod
    def on_button_functions_changed_subscription(fun):
        """
        订阅功能按钮发生修改的消息事件
        :param fun:
        :return:
        """
        # 向on_button_functions_changed_funcs属性中添加函数fun
        AppEvents.on_button_functions_changed_funcs.append(fun)

    @staticmethod
    def on_button_functions_changed_unsubscription(fun):
        """
        取消订阅功能按钮发生修改的消息事件
        :param fun:
        :return:
        """
        # 从on_button_functions_changed_funcs属性中删除函数fun
        AppEvents.on_button_functions_changed_funcs.remove(fun)

    @staticmethod
    def on_button_functions_changed():
        """
        功能按钮发生修改的消息事件触发
        :return:
        """
        # 触发on_button_functions_changed事件，即遍历on_button_functions_changed_funcs中的每个函数并执行
        for f in AppEvents.on_button_functions_changed_funcs:
            f()

    @staticmethod
    def on_ai_roles_changed_subscription(fun):
        """
        订阅AI角色配置发生修改的消息事件
        :param fun:
        :return:
        """
        # 向on_ai_roles_changed_funcs属性中添加函数fun
        AppEvents.on_ai_roles_changed_funcs.append(fun)

    @staticmethod
    def on_ai_roles_changed_unsubscription(fun):
        """
        取消订阅AI角色配置发生修改的消息事件
        :param fun:
        :return:
        """
        # 从on_ai_roles_changed_funcs属性中删除函数fun
        AppEvents.on_ai_roles_changed_funcs.remove(fun)

    @staticmethod
    def on_ai_roles_changed():
        """
        AI角色配置发生修改的消息事件触发
        :return:
        """
        # 触发on_ai_roles_changed事件，即遍历on_ai_roles_changed_funcs中的每个函数并执行
        for f in AppEvents.on_ai_roles_changed_funcs:
            f()

    @staticmethod
    def on_chat_category_changed_subscription(fun):
        """
        订阅聊天主题分类配置发生修改的消息事件
        :param fun:
        :return:
        """
        # 向on_chat_category_changed_funcs属性中添加函数fun
        AppEvents.on_chat_category_changed_funcs.append(fun)

    @staticmethod
    def on_chat_category_changed_unsubscription(fun):
        """
        取消订阅聊天主题分类配置发生修改的消息事件
        :param fun:
        :return:
        """
        # 从on_chat_category_changed_funcs属性中删除函数fun
        AppEvents.on_chat_category_changed_funcs.remove(fun)

    @staticmethod
    def on_chat_category_changed():
        """
        聊天主题分类配置发生修改的消息事件触发
        :return:
        """
        # 触发on_chat_category_changed事件，即遍历on_chat_category_changed_funcs中的每个函数并执行
        for f in AppEvents.on_chat_category_changed_funcs:
            f()


# 初始化AppEvents类
AppEvents.init()
