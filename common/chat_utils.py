# -*- coding:utf-8 -*-
# title           :chat_utils.py
# description     :聊天相关工具类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================

from common.str_utils import is_empty
from common.ui_utils import find_icon_file
from db.db_ops import ConfigOp

# import commonmark  # pip install -i https://pypi.douban.com/simple/ markdown2 commonmark

# 历史数据较多 的提示消息
MSG_HISTORY_RECORD_SO_MUCH = '历史数据较多，打开聊天会比较慢，是否只读取最近记录？\n' \
                             '选“是”，则读取最近的记录\n选“否”,则打开全部记录\n或者“取消”操作'

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
    return f"<div style='color:{color}'>{icon_html} {who}</div>{message_begin}"


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


def message_to_html(message):
    """
    消息转 html 格式
    :param message:
    :return:
    """

    html = plain_text_to_html(message)
    # TODO:方法0
    return html

    # message = message.replace("\r\n","\n").replace("\r","\n")
    # message = message.replace("<", "&lt;").replace(">", "&gt;")
    # html = html.replace("\r\n", "\n").replace("\r", "\n").replace("\n\n", "\n").replace("\n\n", "\n")
    # html = html.replace("\n", "<br>")

    # TODO:方法1
    # import commonmark
    # parser = commonmark.Parser()
    # ast = parser.parse(message)
    # renderer = commonmark.HtmlRenderer()
    # html = renderer.render(ast)

    # TODO:方法2
    # from markdown2 import markdown
    # html = markdown(message)

    # TODO:方法3
    # from markdown import markdown
    # html = markdown(message)


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
        icon_file = find_icon_file(icon)
        icon_html = f"<img src='{icon_file}'>"
    else:
        icon_html = ""
    if color is None:
        color = "black"
    # import commonmark
    # message = message.replace("\n\n\n", "\n")
    # message = message.replace("\n\n", "\n")
    # parser = commonmark.Parser()
    # ast = parser.parse(message)
    # renderer = commonmark.HtmlRenderer()
    # message = renderer.render(ast)

    message = message_to_html(message)

    # from markdown import markdown
    # # message = message.replace("\n", "\n\n")
    # message = markdown(message)
    # # message = message.replace("\n", "<br>")
    # # message = message.replace("\r\n", "\n")
    # # message = message.replace("\n\n", "<br>")
    # # message = message.replace("\n", "<br>")

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

    return build_chat_message(f"[{role_name}]", content, "icon_16.png", "green")  # + "<hr>"


def build_my_message(content, role_name=None):
    """
    构建 [我] 的消息
    :param content:
    :param role_name:
    :return:
    """
    if is_empty(role_name):
        role_name = "我"
        icon_name = "user.png"
    else:
        icon_name = "icon_blue.png"
    # return build_send_message(content, "user.png", "blue")
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
        suffix = json_data["suffix"]
        prefix = json_data["prefix"]
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
