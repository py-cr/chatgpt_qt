# -*- coding:utf-8 -*-
# title           :session_setting.py
# description     :聊天会话设置
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import json

from common.str_utils import is_empty


class SessionSetting:
    """
    聊天会话的设置信息
    """

    def __init__(self, settings):
        if is_empty(settings):
            session_settings = {}
        else:
            session_settings = json.loads(settings)

        # ChatWindow 配置
        self.msg_context_check = session_settings.get("msg_context_check", None)
        self.ai_role = session_settings.get("ai_role", "")
        # AiChatWindow 配置
        self.ai1_name = session_settings.get("ai1_name", "")
        self.ai1_role = session_settings.get("ai1_role", "")
        self.ai_init_subject = session_settings.get("ai_init_subject", "")
        self.ai2_name = session_settings.get("ai2_name", "")
        self.ai2_role = session_settings.get("ai2_role", "")
        self.code_style = session_settings.get("code_style", "Default")

    def to_json_str(self):
        json_str = json.dumps(self.to_json_obj())
        return json_str

    def to_json_obj(self):
        return {
            "msg_context_check": self.msg_context_check,
            "ai_role": self.ai_role,
            "ai1_name": self.ai1_name,
            "ai1_role": self.ai1_role,
            "ai_init_subject": self.ai_init_subject,
            "ai2_name": self.ai2_name,
            "ai2_role": self.ai2_role,
            "code_style": self.code_style
        }

    def has_ai_chat_settings(self):
        if is_empty(self.ai_init_subject):
            return False

        return True
