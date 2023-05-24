# -*- coding:utf-8 -*-
# title           :chat_window_worker.py
# description     :聊天窗口线程访问worker
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================

from PyQt5.QtCore import pyqtSignal, QObject

from common.app_events import AppEvents
from common.chat_utils import build_chat_title, plain_text_to_html, ERR_MSG_MAP
from common.openai_chatbot import OpenAiChatbot
from db.db_ops import HistoryOp
from windows.chat_window import ChatWindow


class ChatWindowWorker(QObject):
    """
    聊天窗口线程访问worker
    """
    appendMessageSignal = pyqtSignal(str)  # 自定义 追加消息到聊天文本框 信号，该信号带参数为（文本）
    finishSignal = pyqtSignal()

    def __init__(self, ui: ChatWindow):
        super(ChatWindowWorker, self).__init__()
        self.ui = ui
        self.chat_stop = False

    def do(self):
        try:
            self._do()
        except Exception as e:
            AppEvents.on_recieved_message(0, str(e))

    def _do(self):
        openai_reply_begin = build_chat_title("[OpenAi]", "icon_16.png", "green")
        self.appendMessageSignal.emit(openai_reply_begin)

        content = ""
        reply_error = 0

        for reply, status, is_error in OpenAiChatbot().chat_messages(self.ui.messages, self.ui.model_id):
            # is_error = 0 没有错误
            # print(status)
            if reply_error != 1:
                reply_error = is_error
            part_content = reply["content"]
            content += part_content
            part_content = plain_text_to_html(part_content)
            # part_content = part_content.replace("\n", "<br>")
            # part_content = part_content.replace(" ", "&nbsp;")
            # print(reply, status, is_error)
            if self.chat_stop:
                break
            self.appendMessageSignal.emit(part_content)

        self.chat_stop = False
        self.finishSignal.emit()

        if reply_error == 1:
            for e_key in ERR_MSG_MAP.keys():
                if e_key in content:
                    self.appendMessageSignal.emit("<br>" + ERR_MSG_MAP[e_key])
                    break

        openai_reply_end = "</div><br><br>"
        self.appendMessageSignal.emit(openai_reply_end)

        # This model's maximum context length is 4097 tokens. However, your messages resulted in 5972 tokens.
        # Please reduce the length of the messages.
        # if "This model's maximum context length is" in content and "Please reduce the length of the messages" in content:
        #     content = "模型上下文消息的长度超限，你可以勾选[停用上下文]或者尝试点击[缩减上下文]按钮后，再重新发送。\n" \
        #               "[缩减上下文]的消息长度可以在菜单[设置]->[OpenAI]进行修改"
        # else:
        #     err_msg = {"role": "user", "content": "请用中文解释以下问题：\n" + content}
        #     status, reply, response = OpenAi.instance().send_messages([err_msg], self.model_id)

        # content = reply["content"]
        content_len = len(content)
        # print("response", status, reply, response)

        if reply_error == 0:
            reply = {"role": "assistant", "content": content}
            self.ui.chat_history.append((reply_error, reply, content_len))
            AppEvents.on_chat_history_changed()
            # 保存回复的消息
            HistoryOp.insert(role="assistant",
                             content=content,
                             content_type="text",
                             session_id=self.ui.session_id,
                             status=0)
        if reply_error == 1:  # 有问题
            pass

        AppEvents.on_recieved_message(0, content)
