# -*- coding:utf-8 -*-
# title           :cook_menu_view.py
# description     :烹饪菜单视图控件
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from controls.tab_input_view import TabInputView
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QTextCursor
from common.app_events import AppEvents
from common.combo_box_utils import select_by_text
from common.json_utils import to_json_items
# from common.openai_libs import OpenAi
from common.ui_mixin import UiMixin
from common.mdi_window_mixin import MdiWindowMixin
from common.ui_utils import find_ui, find_image, find_icon, set_icon, get_html_style
from common.chat_utils import build_my_message, build_openai_message
from common.str_utils import is_empty
from common.message_box import MessageBox


class CookMenuView(TabInputView):
    """
    烹饪菜单视图控件（Tab页签功能）
    """
    def __init__(self, parent, send_message):
        super(CookMenuView, self).__init__(parent)

        self.set_input_style([self.txt_chat_food, self.txt_chat_food_seasoning])
        self.set_placeholder_text([self.txt_chat_food, self.txt_chat_food_seasoning])

        self.btn_food_origin.clicked.connect(lambda: self.on_food_origin_send())
        self.btn_food_skill.clicked.connect(lambda: self.on_food_skill_send())
        self.btn_cooking_method.clicked.connect(lambda: self.on_cooking_method_send())

        self.send_message = send_message

    def on_cooking_method_send(self):
        self.txt_chat_food.prompt = "请告诉我如何烹饪一道完美正宗的“${content}”${seasoning}。需要详细步骤、" \
                                    "所需的所有材料和调料、烹饪时间、操作方式、火候掌握和烹调技巧"
        self.txt_chat_food.no_context = True
        self.on_food_send_with_prompt()

    def on_food_origin_send(self):
        self.txt_chat_food.prompt = "有一道菜叫“${content}”${seasoning}。请给我这道菜的起源/历史/源流/传说/神话"
        self.txt_chat_food.no_context = True
        self.on_food_send_with_prompt()

    def on_food_skill_send(self):
        self.txt_chat_food.prompt = "请告诉我如何烹饪一道完美的“${content}”${seasoning}，重点技巧是什么？"
        self.txt_chat_food.no_context = True
        self.on_food_send_with_prompt()

    def on_food_send_with_prompt(self):
        if not self.check_text_box(self.txt_chat_food, "请输入菜的全名"):
            return

        content = self.txt_chat_food.toPlainText()
        food_seasoning = self.txt_chat_food_seasoning.toPlainText()
        no_context = self.txt_chat_food.no_context

        if is_empty(food_seasoning):
            food_seasoning = ""
        else:
            food_seasoning = f"，这道菜包含材料和调料有：{food_seasoning}"
        # 武汉老通城三鲜豆皮，糯米、黄豆、香菇、笋尖、瘦肉
        # 四川鱼香肉丝、醋、糖、瘦肉、黑木耳
        content = self.txt_chat_food.prompt.replace("${content}", content)
        content = content.replace("${seasoning}", food_seasoning)

        self.send_message(content, no_context)
