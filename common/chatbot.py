# -*- coding:utf-8 -*-
# title           :chatbot.py
# description     :聊天机器人基类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================


class Chatbot:
    """
    聊天机器人基类
    """

    def __init__(self):
        if not hasattr(self, "config_inited"):
            self.config_inited = False
        self.init_config()

    def init_config(self):
        if not self.config_inited:
            self.load_config()
        self.config_inited = True

    def load_config(self):
        pass
