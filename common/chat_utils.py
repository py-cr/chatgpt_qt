# -*- coding:utf-8 -*-
# title           :chat_utils.py
# description     :聊天相关工具类
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================

from common.str_utils import is_empty
from common.ui_utils import find_icon_file
from db.db_ops import ConfigOp

# import commonmark  # pip install -i https://pypi.douban.com/simple/ markdown2 commonmark

# 历史数据认为 > CONTENT_SIZE_SO_MUCH 就较多，提示
CONTENT_SIZE_SO_MUCH = 10000

# Please reduce the length of the messages
# Rate limit reached for default-gpt-3.5-turbo in organization org-ItuVH8h8JDDhOVHJehbSn0Lj on requests per min. Limit: 3 / min. Please try again in 20s. Contact us through our help center at help.openai.com if you continue to have issues. Please add a payment method to your account to increase your rate limit. Visit https://platform.openai.com/account/billing to add a payment method.
ERR_MSG_MAP = {
    "This model's maximum context length is":
        "模型上下文消息的长度超限，你可以勾选[停用上下文]或者尝试点击[缩减上下文]按钮后，再重新发送。\n[缩减上下文]的消息长度可以在菜单[设置]->[OpenAI]进行修改",
    "Rate limit reached for": "发送频率达到请求限制，可以稍后重试"
}


def build_chat_title(who, icon=None, color=None):
    """
    构建聊天的标题（图标+发言者名称）
    :param who:发言者名称 [OpenAI]、[我]、[发言者名称]
    :param icon: 图标
    :param color: 文字颜色
    :return:
    """
    if icon is not None:
        icon_file = find_icon_file(icon)
        icon_html = f"<img src='{icon_file}'>"
    else:
        icon_html = ""
    if color is None:
        color = "black"
    message_begin = f"""<div style='color:{color}'>"""
    html = f"<div style='color:{color}'>{icon_html} {who}</div>{message_begin}"
    # print("build_chat_title", html)
    return html


def build_send_message(message, icon=None, color=None):
    """
    构建发送的消息，发言者为[我]
    :param message: 消息内容
    :param icon: 图标
    :param color: 文字颜色
    :return:
    """
    if icon is not None:
        icon_file = find_icon_file(icon)
        icon_html = f"<img src='{icon_file}'>"
    else:
        icon_html = ""
    if color is None:
        color = "black"

    from markdown import markdown
    message = message.replace("\n", "\n\n")
    message = markdown(message)

    message = f"""<div style='color:{color}'>{message}</div>"""
    # print(icon_html)
    # print(message)
    return f"<div style='color:{color}'>{icon_html} [我]</div>{message}"


def plain_text_to_html(plain_text):
    """
    纯文本转 html 格式
    :param plain_text:
    :return:
    """
    # print("plain_text",plain_text)
    # plain_text = plain_text.replace("\r\n", "\n")
    plain_text = plain_text.replace("\r", "")
    html = plain_text.replace("<", "&lt;").replace(">", "&gt;")
    html = html.replace("\n", "<br>")
    html = html.replace(" ", "&nbsp;")
    # print("html",html)
    return html


def get_history_chat_info(history):
    """

    :param history:
    :return:
    """
    role_name = history.role_name
    if history.role == "user":
        color_name = "blue"
        if is_empty(role_name):
            role_name = "我"
            icon_name = "me.png"
        else:
            icon_name = "icon_blue.png"
    elif history.role == "assistant":
        color_name = "green"
        icon_name = "icon_green.png"
        if is_empty(role_name):
            role_name = "OpenAi"
    else:
        color_name = "green"
        icon_name = ""
    html = message_to_html(history.content)
    return icon_name, role_name, color_name, html


def required_histories_for_win(win_self, history_id):
    # print("OK", history_id)
    if not hasattr(win_self, "history_point_index") or not hasattr(win_self, "all_histories"):
        return
    # print(self.all_histories[self.history_point_index])
    for i in range(10):
        # len() = 3   index= 2
        # if self.history_point_index < 0:
        #     # 最后一条数据，已经到顶了
        #     return

        history = (win_self.all_histories[win_self.history_point_index])
        # insert_chat_item(self, his_id, is_left, icon, title, color, html, highlightElement=True)
        is_left = history.role == "assistant"
        icon_name, title, color_name, html = get_history_chat_info(history)

        if not is_empty(title):
            win_self.txt_main.insert_chat_item(history._id, is_left, icon_name, title,
                                               color_name, html, highlightElement=True)

        if win_self.history_point_index == 0:
            # 最后一条数据，已经到顶了
            win_self.txt_main.setIsAtTop(True)
            win_self.txt_main.scrollToLastTopElement()
            return
        win_self.history_point_index -= 1

    win_self.txt_main.scrollToLastTopElement()
    win_self.txt_main.setIsAtTop(False)


def message_to_html(message):
    """
    消息转 html 格式
    :param message:
    :return:
    """
    # TODO:方法0
    # html = plain_text_to_html(message)
    # return html

    # message = message.replace("\r\n","\n").replace("\r","\n")
    # message = message.replace("<", "&lt;").replace(">", "&gt;")
    # html = html.replace("\r\n", "\n").replace("\r", "\n").replace("\n\n", "\n").replace("\n\n", "\n")
    # html = html.replace("\n", "<br>")

    # TODO:方法1
    import commonmark
    parser = commonmark.Parser()
    ast = parser.parse(message)
    renderer = commonmark.HtmlRenderer()
    html = renderer.render(ast)
    return html

    # # TODO:方法2
    # from markdown2 import markdown
    # exts = ['extra', 'codehilite', 'tables', 'toc', 'nl2br']
    # html = markdown(message, html4tags=False, extras=exts)
    # return html

    # # TODO:方法3
    # from markdown import markdown
    # exts = ['extra', 'abbr', 'attr_list', 'def_list', 'fenced_code', 'footnotes', 'md_in_html',
    #         'admonition', 'legacy_attrs', 'legacy_em', 'meta', 'sane_lists', 'smarty', 'wikilinks',
    #         'codehilite', 'tables', 'toc', 'nl2br']
    # # exts = ['extra', 'codehilite', 'tables', 'toc', 'nl2br']
    # html = markdown(message, extensions=exts)
    # return html


# def check_code(pre_html: str):
#     code = ["python", "js"]
#     for c in code:
#         if pre_html.startswith(c):
#             return f"<pre class='{c}'>[{c}]<br>", pre_html[len(c):]
#     return "<pre>", pre_html


# def replace_as_pre(html):
#     pre_start = True
#     if '```' in html:
#         while True:
#             if '```' not in html:
#                 break
#             find_pre_idx = html.index('```')
#             if find_pre_idx < 0:
#                 break
#
#             if pre_start:
#                 pre, suffix = check_code(html[find_pre_idx + 3:])
#                 html = html[:find_pre_idx] + pre + suffix
#                 pre_start = False
#             else:
#                 html = html[:find_pre_idx] + "</pre>" + html[find_pre_idx + 3:]
#                 pre_start = True
#     # html = html.replace("\n", "<br>")
#     return html


def build_chat_message(who, message, icon=None, color=None):
    """
    构建聊天消息
    :param who: 发言者名称 [OpenAI]、[我]、[发言者名称]
    :param message: 聊天的消息
    :param icon: 图标
    :param color: 文字颜色
    :return:
    """
    if icon is not None:
        icon_file = find_icon_file(icon).replace("\\", "/")
        icon_html = f"<img src='{icon_file}'>"
    else:
        icon_html = ""
    if color is None:
        color = "black"
    message = message_to_html(message)

    message = f"""<div style='color:{color}'>{message}</div>"""
    # print(icon_html)
    # print(message)
    return f"<div style='color:{color}'>{icon_html} {who}</div>{message}"


def build_openai_message(content, role_name=None):
    """
    构建 OpenAI（发言者）的消息
    :param content: 消息内容
    :param role_name: 发言者角色名称
    :return:
    """
    if is_empty(role_name):
        role_name = "OpenAi"
        color = "green"
    else:
        color = "green"

    return build_chat_message(f"[{role_name}]", content, "icon_green.png", "green")  # + "<hr>"


def build_my_message(content, role_name=None):
    """
    构建 [我] 的消息
    :param content:
    :param role_name:
    :return:
    """
    if is_empty(role_name):
        role_name = "我"
        icon_name = "user24.png"
    else:
        icon_name = "icon_blue.png"
    # return build_send_message(content, "user24.png", "blue")
    return build_chat_message(f"[{role_name}]", content, icon_name, "blue")


def message_total_size(chat_history):
    total_size = 0
    for status, message, size in chat_history:
        total_size += size

    if total_size < 1000:
        total_size = f"{total_size}b"
    elif total_size < 1000000:
        total_size = f"{round(total_size / 1000, 2)}K"
    else:
        total_size = f"{round(total_size / 1000000, 2)}M"
    return total_size


def get_button_functions():
    """
    获取按钮功能
    :return:
    """
    import json
    functions = {}

    for config in ConfigOp.get_button_functions():
        fun_name = config.cfg_key
        json_str = config.cfg_value
        if is_empty(json_str):
            json_data = {"suffix": "", "prefix": "", "btn_style": ""}
        else:
            json_data = json.loads(json_str)

        if "suffix" in json_data:
            suffix = json_data["suffix"]
        else:
            suffix = ""

        if "prefix" in json_data:
            prefix = json_data["prefix"]
        else:
            prefix = ""

        btn_style = json_data["btn_style"]
        if "sample" in json_data:
            sample = json_data["sample"]
        else:
            sample = ""
        functions[fun_name] = {}
        functions[fun_name]["Suffix"] = suffix
        functions[fun_name]["Prefix"] = prefix
        functions[fun_name]["Sample"] = sample
        functions[fun_name]["PreProcess"] = ""
        functions[fun_name]["ButtonStyle"] = btn_style

    return functions
