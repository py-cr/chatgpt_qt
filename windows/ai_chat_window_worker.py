# -*- coding:utf-8 -*-
# title           :ai_chat_window_worker.py
# description     :AI聊天窗口线程访问worker
# author          :Python超人
# date            :2023-6-10
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================

from PyQt5.QtCore import pyqtSignal, QObject

from common.chat_utils import message_to_html
from windows.ai_chat_window import AiChatWindow


class AiChatWindowWorker(QObject):
    """
    AI聊天窗口线程访问worker
    """
    appendTitleSignal = pyqtSignal(int, bool, str, str, str)
    updateHtmlSignal = pyqtSignal(str)
    chatStatusSignal = pyqtSignal()  # 自定义 聊天状态 信号，停止聊天则调用

    def __init__(self, ui: AiChatWindow):
        super(AiChatWindowWorker, self).__init__()
        self.ui = ui

    def do(self):
        self.ui.ai_converse.start(initial_topic=self.ui.ai_init_subject,
                                  session_id=self.ui.session_id,
                                  sleep_sec=self.ui.spinbox_sleep.value,
                                  repeat_times=-1,
                                  callback=self.ai_chats_callback)

    def ai_chats_callback(self, args):
        """
        AI 聊天回调函数，针对各种 action 进行处理
        :param args:
        :return:
        """
        # print(args)
        action = args["action"]
        params = args["params"]
        if action == "timer":  # 倒计时
            self.ui.lab_timer.setText(str(params["sec"]))
            return
        elif action == "timer_end":  # 倒计时结束
            self.ui.lab_timer.setText("")
            return

        if action == "finish":  # 聊天结束
            self.ui.btn_start.setDisabled(False)
            self.ui.btn_stop.setDisabled(True)
            "i_am_saying"
        elif action == "i_am_saying":  # 我说
            his_id = params['his_id']
            self.appendTitleSignal.emit(his_id, False, "icon_blue.png", "我", "blue")
        elif action == "ai_1_saying":  # 1号 AI  说
            ai1_name = self.ui.txt_ai1_name.text().strip()
            his_id = params['his_id']
            self.appendTitleSignal.emit(his_id, False, "icon_blue.png", ai1_name, "blue")
            self.updateHtmlSignal.emit('<div class="loading"></div>')
        elif action == "ai_2_saying":  # 2号 AI 说
            ai2_name = self.ui.txt_ai2_name.text().strip()
            his_id = params['his_id']
            self.appendTitleSignal.emit(his_id, True, "icon_green.png", ai2_name, "green")
            self.updateHtmlSignal.emit('<div class="loading"></div>')
        elif action in ["ai_1_said", "ai_2_said"]:
            pass
        elif action == "message":  # 1、2号 AI 说的消息
            html = message_to_html(params["content"])
            self.updateHtmlSignal.emit(html)
