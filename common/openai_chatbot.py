# -*- coding:utf-8 -*-
# title           :openai_chatbot.py
# description     :OpenAi聊天机器人
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import json
import os
import traceback

import openai
import requests

from common.chatbot import Chatbot
from common.str_utils import is_empty
from common.ui_utils import find_file
from db.db_ops import ConfigOp

# TIMEOUT_BOT_MSG = '[Local Message] Request timeout. Network error. Please check proxy settings' + \
#                   '网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。'
TIMEOUT_SECONDS = 30
API_URL = "https://api.openai.com/v1/chat/completions"
MAX_RETRY = 3


class OpenAiChatbot(Chatbot):
    """
    OpenAi聊天机器人
    """

    def __init__(self):
        # self.api_key = ''
        # self.proxy_enabled = 0
        # self.proxy_server = ''
        super().__init__()

    def load_config(self):
        """
        加载 OpenAi 配置（API Key 和 代理）
        :return:
        """
        self.api_key = ConfigOp.get_sys_config("api_key")
        if is_empty(self.api_key):
            return

        self.proxy_enabled = ConfigOp.get_sys_config("proxy_enabled")
        if self.proxy_enabled == "1":
            proxy_server = ConfigOp.get_sys_config("proxy_server")

            self.proxy_server = proxy_server

        # 测试无代理或者错误的代理
        # self.proxy_enabled = "0"
        # self.proxy_server = '127.0.0.1:2000'

        openai.api_key = self.api_key

    def get_model_list(self):
        """
        获取 OpenAi 支持的模型
        :return:
        """
        self.init_config()

        model_file = find_file("model_list.json", "data", raise_exception=False)
        if model_file is None:
            # https://platform.openai.com/docs/api-reference/models/list
            model_list = openai.Model.list()
            with open(os.path.join("data", "model_list.json"), 'w', encoding='UTF-8') as f:
                model_json = json.dumps(model_list)
                f.write(model_json)
        else:
            model_list = json.load(open(model_file, 'r', encoding='UTF-8'))

        model_list = sorted(model_list['data'], key=lambda x: x['id'])

        return model_list

    def generate_payload(self, messages, model_id, api_key):
        """
        根据 messages 的内容，生成 payload（message 携带的内容 ）
        :param messages: 消息列表
        :param model_id: OpenAi支持的模型
        :return: headers 和 payload
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'system', 'content': 'Serve me as a writing and programming assistant.'},
                            {'role': 'user', 'content': 'Excel中的怎么使用chatgpt？'}],
                'temperature': 1,
                'top_p': 1,
                'n': 1,
                'stream': True,
                'presence_penalty': 0,
                frequency_penalty': 0
            }

        """

        if len(api_key) != 51:
            raise AssertionError("你提供了错误的API_KEY。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 1.0,
            "top_p": 1.0,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }
        return headers, payload

    def create_response(self, headers, payload, proxy_enabled, proxy_server):
        """
        创建一个 response
        :param headers: 指定 headers
        :param payload: 指定 payload
        :return:
        """
        if proxy_enabled == "1":
            # make a POST request to the API endpoint, stream=True
            proxies = {
                #          [协议]://  [地址]  :[端口]
                "http": proxy_server,
                "https": proxy_server,
            }
            response = requests.post(API_URL, headers=headers, proxies=proxies,
                                     json=payload, stream=True, timeout=TIMEOUT_SECONDS)
        else:
            response = requests.post(API_URL, headers=headers,
                                     json=payload, stream=True, timeout=TIMEOUT_SECONDS)
        return response

    def chat_messages(self, input_messages, model_id, api_key=None, proxy_enabled=None, proxy_server=None):
        """
        消息聊天
        :param input_messages: 输入消息
            格式为： [{'role': 'system', 'content': 'Serve me as a writing and programming assistant.'},
                     {'role': 'user', 'content': 'Excel中的怎么使用chatgpt？'}]
        :param model_id: 默认：gpt-3.5-turbo
        :return:
        """
        if model_id is None:
            model_id = "gpt-3.5-turbo"

        if api_key is None:
            api_key = self.api_key

        if proxy_enabled is None:
            proxy_enabled = self.proxy_enabled

        if proxy_server is None:
            proxy_server = self.proxy_server

        headers, payload = self.generate_payload(input_messages, model_id, api_key)

        retry = 0
        while True:
            try:
                response = self.create_response(headers, payload, proxy_enabled, proxy_server)
                break
            except requests.exceptions.ProxyError as pe:
                retry += 1
                proxy_error = f"代理服务器配置错误：{pe}"
                if retry > MAX_RETRY:
                    return
                    # raise requests.exceptions.ProxyError(proxy_error)
                yield {"role": "assistant", "content": proxy_error}, "error", 1
            except requests.exceptions.ReadTimeout as te:
                retry += 1
                traceback.print_exc()
                if retry > MAX_RETRY:
                    return
                    # raise TimeoutError
                    yield {"role": "assistant", "content": str(te)}, "error", 1
                if MAX_RETRY != 0:
                    print(f'请求超时，正在重试 ({retry}/{MAX_RETRY}) ……')
            except Exception as e:
                retry += 1
                traceback.print_exc()
                if retry > MAX_RETRY:
                    return
                    # raise e
                yield {"role": "assistant", "content": str(e)}, "error", 1

        if response is None:
            raise ConnectionError

        is_head_of_the_stream = True
        # 获取迭代行数据，可以通过循环 iter_lines 获取每次接收的文字
        iter_lines = response.iter_lines()
        # 是否出现错误
        is_error = False
        # 如果出现错误，记录错误的JSON内容
        error_json = ""
        # 获取返回的所有消息内容
        content = ""
        while True:
            # 循环获取Open回复的消息流，直到消息结束
            try:
                # 获取当前行文字块的内容（字节流）
                chunk = next(iter_lines)
                # 转为JSON数据字符串
                json_data = chunk.decode()
            except StopIteration as s:
                break
            except Exception as e:
                # 出现异常，则返回
                is_error = True
                # traceback.print_exc()
                # print(str(e))
                err_msg = str(e)
                error_json = f'{{"error": {{ "message": "{err_msg}", "code": "error" }} }}'
                break

            if is_head_of_the_stream:
                error_json = json_data
                # 数据流的第一帧不携带content
                is_head_of_the_stream = False
                continue

            if chunk:
                try:
                    # 判断有错误的消息
                    if str(json_data).lstrip(" '\"").startswith("error"):
                        is_error = True
                    if is_error:
                        error_json += json_data
                        # 虽然已经有错误，但是消息还不完整，需要进行反复构建完整的错误消息
                        continue
                    try:
                        chunkjson = json.loads(json_data[6:])
                    except Exception as e:
                        is_error = True
                        continue
                    choices_data = chunkjson['choices']
                    # 获取消息
                    delta = choices_data[0]["delta"]
                    if len(delta) == 0:
                        # 判定为数据流的结束，终止循环
                        break
                    if "content" not in delta.keys():
                        continue
                    # 处理数据流的样本内容如下：
                    # {
                    #   'id': 'chatcmpl-7CeyA9atmRjO1PrYWjJneBzA0jt3Q',
                    #   'object': 'chat.completion.chunk',
                    #   'created': 1683251778, 'model': 'gpt-3.5-turbo-0301',
                    #   'choices': [{'delta': {'content': '如果'}, 'index': 0, 'finish_reason': None}]
                    # }

                    status_text = f"finish_reason: {choices_data[0]['finish_reason']}"
                    # 如果这里抛出异常，一般是文本过长，详情见get_full_error的输出
                    reply = {"role": "assistant", "content": delta["content"]}
                    content += delta["content"]

                    # 回复的消息, 状态信息，状态值(0：正常)
                    yield reply, status_text, 0

                except Exception as e:
                    traceback.print_exc()
                    is_error = True
                    continue

        if is_error:
            # print(error_json) # {"error": "", "message": "", "code": ""}
            print(error_json)
            error_obj = json.loads(error_json)["error"]
            # 回复的消息, error_obj["code"]错误状态信息，状态值(1：错误)
            yield {"role": "assistant", "content": error_obj["message"]}, error_obj["code"], 1

        return


# import time
# import datetime  # 引入datetime模块
#
#
# def chat_to_opanai_self(initial_topic):
#     chatbot = OpenAiChatbot()
#
#     answer_init_messages = [{"role": "system", "content": '你是一个小白，有个问题不懂，你要根据我提的话题提出问题，'
#                                                           '然后再来问我，字数越少越好，一次只问一个的问题，'
#                                                           '每次问题不要超过100字，也不要总是提问，就当和我聊天一样，你也不要说好的'}]
#     reply_init_messages = [{"role": "system", "content": '你是一个专家，上知天文下知地理，没有什么问题能难倒你，'
#                                                          '但是回答问题也要实事求是，字数越少越好，如果我没有说明白，'
#                                                          '你要能反问我，和我聊天一样，不要超过200字'}]
#
#     history_messages = []
#
#     repeat_times = 10
#     chat_message = initial_topic
#     while True:
#         repeat_times -= 1
#         if repeat_times <= 0:
#             break
#         if len(history_messages) == 0:
#             answer_messages = answer_init_messages + [{"role": "user", "content": chat_message}]
#         else:
#             answer_messages = answer_init_messages
#             for role, history_message in history_messages:
#                 if role == "answer":
#                     role = "assistant"
#                 else:
#                     role = "user"
#                 answer_messages.append({"role": role, "content": history_message})
#
#         time_str = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
#         print(f"小白机器人[{time_str}]：")
#         answer_message = ""
#         for reply, status, is_error in chatbot.chat_messages(answer_messages, None):
#             answer_message += reply["content"]
#             if is_error != 0:
#                 if "context_length_exceeded" in answer_message:
#                     print("ERROR", answer_message, status)
#                     exit(0)
#
#         print(answer_message.replace("\n\n", "\n"))
#
#         history_messages.append(("answer", answer_message))
#         answer_bot_messages = reply_init_messages
#         for role, history_message in history_messages:
#             if role == "answer":
#                 role = "user"
#             else:
#                 role = "assistant"
#             answer_bot_messages.append({"role": role, "content": history_message})
#
#         # Rate limit reached for default-gpt-3.5-turbo in organization org-ItuVH8h8JDDhOVHJehbSn0Lj on requests per min. Limit: 3 / min. Please try again in 20s. Contact us through our help center at help.openai.com if you continue to have issues. Please add a payment method to your account to increase your rate limit. Visit https://platform.openai.com/account/billing to add a payment method
#         time.sleep(20)
#         time_str = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
#         print(f"专家机器人[{time_str}]：")
#
#         reply_message = ""
#         for reply, status, is_error in chatbot.chat_messages(answer_bot_messages, None):
#             reply_message += reply["content"]
#             if is_error != 0:
#                 print("ERROR", answer_message, status)
#                 exit(0)
#
#         print(reply_message.replace("\n\n", "\n"))
#
#         history_messages.append(("reply", reply_message))
#
#         chat_message = reply_message
#
#         time.sleep(20)
#
#
# def openai_test_chat():
#     histories = HistoryOp.select_by_session_id(39, order_by="order_no, _id", entity_cls=History)
#     # histories = histories[-18:]
#     histories = histories[-20:]
#     chatbot = OpenAiChatbot()
#     print(chatbot.get_model_list())
#     # input_messages = [{"role": "assistant", "content": 'reply'},{"role": "user", "content": '请问你能做什么？'}]
#     # input_messages = [{"role": "system", "content": 'you are my assistant'}, {"role": "user", "content": '请问你能做什么？'}
#     input_messages = [{"role": "system", "content": 'you are my assistant'}]
#
#     for history in histories:
#         input_messages.append({"role": history.role, "content": history.content})
#
#     model_id = None
#
#     for reply, status, is_error in chatbot.chat_messages(input_messages, model_id):
#         # is_error = 0 没有错误
#         # print(status)
#         print(reply)


# error =  { "error": {    "message": "This model's maximum context length is 4097 tokens. However, your messages
# resulted in 13966 tokens. Please reduce the length of the messages.",    "type": "invalid_request_error",
# "param": "messages",    "code": "context_length_exceeded"  }}
if __name__ == '__main__':
    # chat_to_opanai_self("话题是关于人工智能对未来10年的有哪些危险和机会")
    pass
