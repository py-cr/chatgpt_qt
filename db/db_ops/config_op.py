# -*- coding:utf-8 -*-
# title           :config_op.py
# description     :配置数据库操作类
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from common.json_utils import to_json_items, to_json_str
from db.db_utils import execute_ddl, execute_sql, execute_sqls, sql_to_entities, select_sql, sql_to_entity
from db.entities.config import Config
from db.entities.consts import CFG_KEY_BUTTON_FUNCTION, CFG_KEY_AI_ROLE, CFG_KEY_CHAT_CATEGORY
from db.entities.consts import CFG_KEY_TAB_FUNCTION


class ConfigOp:
    """

    """

    @classmethod
    def get_sys_config(cls, key, default_val=None):
        """
        获取系统配置
        :param key: 键
        :param default_val: 默认值
        :return:
        """
        df = select_sql(f"SELECT * FROM t_config WHERE `cfg_key`=? AND `cfg_category`=? AND `is_deleted`=0",
                        [key, 'system'])
        if len(df) > 0:
            return df['cfg_value'][0]
        return default_val

    @classmethod
    def save_sys_config(cls, key, value):
        """
        保存系统配置
        :param key: 键
        :param value: 值
        :return:
        """
        sql = f"INSERT OR REPLACE INTO t_config(`cfg_category`,`cfg_key`,`cfg_value`) VALUES(?,?,?)"
        return execute_sql(sql, ['system', key, value])

    @classmethod
    def get_config(cls, category, key, default_val=None):
        """
        获取配置
        :param category: 分类
        :param key: 键
        :param default_val: 默认值
        :return:
        """
        entity = sql_to_entity(f"SELECT * FROM t_config WHERE `cfg_key`=? AND `cfg_category`=? AND `is_deleted`=0",
                               [key, category], Config)
        if entity is None:
            return default_val

        return entity.cfg_value

    @classmethod
    def get_configs(cls, category):
        """
        获取指定分类的配置
        :param category: 分类
        :return:
        """
        entities = sql_to_entities(
            f"SELECT * FROM t_config WHERE `cfg_category`=? AND `is_deleted`=0 ORDER BY order_no",
            [category], Config)
        return entities

    @classmethod
    def save_config(cls, category, key, value, order_no=0, is_deleted=0):
        """
        保存配置
        :param category: 分类
        :param key: 键
        :param value: 值
        :param order_no:
        :param is_deleted: 1 表示删除
        :return:
        """
        sql = "INSERT OR REPLACE INTO t_config(`cfg_category`,`cfg_key`,`cfg_value`,`order_no`,`is_deleted`) " \
              "VALUES(?,?,?,?,?)"
        return execute_sql(sql, [category, key, value, order_no, is_deleted])

    @classmethod
    def save_configs(cls, category, keys, values):
        """
        批量保存配置列表
        :param category: 分类
        :param keys: 键列表
        :param values: 值列表
        :return:
        """
        if len(keys) != len(values):
            raise Exception("keys 和 values 的长度不同")
        sql_params_list = []
        for idx, key in enumerate(keys):
            sql_params = f"INSERT OR REPLACE INTO t_config(`cfg_category`,`cfg_key`,`cfg_value`) VALUES(?,?,?)", \
                         [category, key, values[idx]]

            sql_params_list.append(sql_params)

        return execute_sqls(sql_params_list)

    @classmethod
    def get_categories(cls):
        """
        获取聊天话题分类的配置列表
        :return:
        """
        confs = cls.get_configs(CFG_KEY_CHAT_CATEGORY)
        return confs

    @classmethod
    def get_button_functions(cls):
        """
        获取按钮功能配置列表
        :return:
        """
        confs = cls.get_configs(CFG_KEY_BUTTON_FUNCTION)
        return confs

    @classmethod
    def get_ai_roles(cls):
        """
        获取AI角色配置列表
        :return:
        """
        confs = cls.get_configs(CFG_KEY_AI_ROLE)
        return confs

    @classmethod
    def init_ai_roles(cls):
        """
        初始化AI角色
        :return:
        """
        cls.save_config(CFG_KEY_AI_ROLE, "Python高级工程师", "一个具有10年Python开发经验的资深工程师")
        cls.save_config(CFG_KEY_AI_ROLE, "资深人事部经理", "一个具有10年以上经验丰富的人事部经理，面试经验丰富")

    @classmethod
    def init_tab_funcs(cls):
        """
        初始化AI角色
        :return:
        """
        cls.save_config(CFG_KEY_TAB_FUNCTION, "工作助理", "", order_no=0, is_deleted=1)
        cls.save_config(CFG_KEY_TAB_FUNCTION, "家庭厨师", "", order_no=1)
        cls.save_config(CFG_KEY_TAB_FUNCTION, "语音交流", "", order_no=2, is_deleted=1)
        cls.save_config(CFG_KEY_TAB_FUNCTION, "抖音帮手", "", order_no=3)

    @classmethod
    def init_button_funcs(cls):
        """
        初始化按钮功能
        :return:
        """
        import json

        funcs = cls.get_init_functions()
        order_no = 0
        for key in funcs.keys():
            fun = funcs[key]
            json_data = {
                "prefix": fun["Prefix"],
                "suffix": fun["Suffix"],
                "sample": fun["Sample"],
                "btn_style": fun['ButtonStyle'] if "ButtonStyle" in fun else ""
            }
            json_str = json.dumps(json_data)
            # print(fun)
            order_no += 1
            cls.save_config(CFG_KEY_BUTTON_FUNCTION, key, json_str, order_no=order_no)

    @classmethod
    def init_categories(cls):
        """
        初始化聊天话题分类
        :return:
        """
        for i, key in enumerate(["生活", "工作", "学习", "科学", "闲聊", "其他"]):
            cls.save_config(CFG_KEY_CHAT_CATEGORY, key, "", order_no=i)

    @classmethod
    def create_table(cls):
        """
        创建配置表和唯一键(cfg_category,cfg_key)
        :return:
        """
        ddl = """
        CREATE TABLE `t_config` (
            `_id` INTEGER  PRIMARY KEY autoincrement, 
            `cfg_category`  VARCHAR(50), 
            `cfg_key` VARCHAR(50), 
            `cfg_value` BLOB,
            `order_no` INTEGER DEFAULT 0,
            `is_deleted` INTEGER DEFAULT 0
        )"""
        execute_ddl(ddl)
        execute_ddl("CREATE UNIQUE INDEX t_config_category_key_idx ON t_config (cfg_category,cfg_key)")

    @classmethod
    def get_init_functions_原始(cls):
        """
        获取初始化用的功能按钮
        :return:
        """
        return {
            "英语学术润色": {
                # 前言
                "Prefix": r"Below is a paragraph from an academic paper. Polish the writing to meet the academic style, " +
                          r"improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence. " +
                          r"Furthermore, list all modification and explain the reasons to do so in markdown table." + "\n\n",
                # 后语
                "Suffix": r"",
                "ButtonStyle": "background-color: red",  # 按钮颜色
            },
            "中文学术润色": {
                "Prefix": r"作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，" +
                          r"同时分解长句，减少重复，并提供改进建议。请只提供文本的更正版本，避免包括解释。请编辑以下文本" + "\n\n",
                "Suffix": r"",
                "ButtonStyle": "background-color: red",  # 按钮颜色
            },

            "中译英": {
                "Prefix": r"Please translate following sentence to English:" + "\n\n",
                "Suffix": r"",
                "ButtonStyle": "background-color: red",
            },

            "英译中": {
                "Prefix": r"翻译成地道的中文：" + "\n\n",
                "Suffix": r"",
                "ButtonStyle": "background-color: red",
            },
            # "找图片": {
            #     "Prefix": r"我需要你找一张网络图片。使用Unsplash API(https://source.unsplash.com/960x640/?<英语关键词>)获取图片URL，" +
            #               r"然后请使用Markdown格式封装，并且不要有反斜线，不要用代码块。现在，请按以下描述给我发送图片：" + "\n\n",
            #     "Suffix": r"",
            # },
            "解释代码": {
                "Prefix": r"请解释以下代码：" + "\n```\n",
                "Suffix": "\n```\n",
                "ButtonStyle": "background-color: green; color: white",
            },
            "查找语法错误": {
                "Prefix": r"Can you help me ensure that the grammar and the spelling is correct? " +
                          r"Do not try to polish the text, if no mistake is found, tell me that this paragraph is good." +
                          r"If you find grammar or spelling mistakes, please list mistakes you find in a two-column markdown table, " +
                          r"put the original text the first column, " +
                          r"put the corrected text in the second column and highlight the key words you fixed.""\n"
                          r"Example:""\n"
                          r"Paragraph: How is you? Do you knows what is it?""\n"
                          r"| Original sentence | Corrected sentence |""\n"
                          r"| :--- | :--- |""\n"
                          r"| How **is** you? | How **are** you? |""\n"
                          r"| Do you **knows** what **is** **it**? | Do you **know** what **it** **is** ? |""\n"
                          r"Below is a paragraph from an academic paper. "
                          r"You need to report all grammar and spelling mistakes as the example before."
                          + "\n\n",
                "Suffix": r"",
                "PreProcess": "clear_line_break",  # 预处理：清除换行符
                "ButtonStyle": "background-color: green; color: white",
            },
            "给代码注释": {
                "Prefix": r"请给以下的代码加上完整的中文注释：" + "\n```\n",
                "Suffix": "\n```\n",
                "ButtonStyle": "background-color: green; color: white",
            },
            "学术中英互译": {
                "Prefix": r"I want you to act as a scientific English-Chinese translator, " +
                          r"I will provide you with some paragraphs in one language " +
                          r"and your task is to accurately and academically translate the paragraphs only into the other language. " +
                          r"Do not repeat the original provided paragraphs after translation. " +
                          r"You should use artificial intelligence tools, " +
                          r"such as natural language processing, and rhetorical knowledge " +
                          r"and experience about effective writing techniques to reply. " +
                          r"I'll give you my paragraphs as follows, tell me what language it is written in, and then translate:" + "\n\n",
                "Suffix": "",
                "ButtonStyle": "background-color: red",
            },
        }

    @classmethod
    def get_init_functions(cls):
        """
        获取初始化用的功能按钮。
        使用 ConfigOp.gen_init_functions() 生成的
        :return:
        """
        return {
            "翻译为英文": {
                "Prefix": "Please translate following sentence to English:\n\n",
                "Suffix": "",
                "Sample": "",
                "ButtonStyle": "background-color: red"
            },
            "翻译为中文": {
                "Prefix": "翻译成地道的中文：\n\n",
                "Suffix": "",
                "Sample": "",
                "ButtonStyle": "background-color: red; color: black"
            },
            "中文学术润色": {
                "Prefix": "作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，同时分解长句，减少重复，并提供改进建议。请只提供文本的更正版本，避免包括解释。请编辑以下文本\n\n",
                "Suffix": "",
                "Sample": "",
                "ButtonStyle": "background-color: red; color: black"
            },
            "英语学术润色": {
                "Prefix": "Below is a paragraph from an academic paper. Polish the writing to meet the academic style, improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence. Furthermore, list all modification and explain the reasons to do so in markdown table.\n\n",
                "Suffix": "",
                "Sample": "",
                "ButtonStyle": "background-color: red"
            },
            "查找语法错误": {
                "Prefix": "Can you help me ensure that the grammar and the spelling is correct? Do not try to polish the text, if no mistake is found, tell me that this paragraph is good.If you find grammar or spelling mistakes, please list mistakes you find in a two-column markdown table, put the original text the first column, put the corrected text in the second column and highlight the key words you fixed.\nExample:\nParagraph: How is you? Do you knows what is it?\n| Original sentence | Corrected sentence |\n| :--- | :--- |\n| How **is** you? | How **are** you? |\n| Do you **knows** what **is** **it**? | Do you **know** what **it** **is** ? |\nBelow is a paragraph from an academic paper. You need to report all grammar and spelling mistakes as the example before.\n\n",
                "Suffix": "",
                "Sample": "",
                "ButtonStyle": "background-color: green; color: white"
            },
            "解释代码": {
                "Prefix": "请解释以下代码：\n```\n",
                "Suffix": "\n```\n",
                "Sample": "",
                "ButtonStyle": "background-color: green; color: white"
            },
            "给代码注释": {
                "Prefix": "请给以下的代码加上完整的中文注释：\n```\n",
                "Suffix": "\n```\n",
                "Sample": "",
                "ButtonStyle": "background-color: green; color: white"
            },
            "学术中英互译": {
                "Prefix": "I want you to act as a scientific English-Chinese translator, I will provide you with some paragraphs in one language and your task is to accurately and academically translate the paragraphs only into the other language. Do not repeat the original provided paragraphs after translation. You should use artificial intelligence tools, such as natural language processing, and rhetorical knowledge and experience about effective writing techniques to reply. I'll give you my paragraphs as follows, tell me what language it is written in, and then translate:\n\n",
                "Suffix": "",
                "Sample": "",
                "ButtonStyle": "background-color: green; color: white"
            },
            "提示词生成": {
                "Prefix": "我想让你扮演ChatGPT提示生成器的角色，我会发送一个主题，你要根据主题的内容生成一个ChatGPT提示，提示应该以“我希望你扮演”的话开头，并猜测我可能会做什么，然后根据主题的内容扩展提示，使其有用。",
                "Suffix": "",
                "Sample": "我的主题是[？]",
                "ButtonStyle": "background-color: yellow; color: black"
            },
            "旅游计划": {
                "Prefix": "你现在是一位专业导游，",
                "Suffix": "",
                "Sample": "为我制定一个[三天两晚]在[西安]的旅游计划，行程要有[陕西历史博物馆、大雁塔、芙蓉园]",
                "ButtonStyle": "background-color: yellow; color: black"
            },
            "制作流程图": {
                "Prefix": "我想做一个流程图，需求如下：\n```\n",
                "Suffix": "\n```\n我希望你作为一个经验丰富的人员。帮我梳理一个完整流程，流程节点不少于12个，包含开始和结束节点，包含逻辑判断的分支，要遵循实事是的原则，记住要用Mermaid语法输出。",
                "Sample": "",
                "ButtonStyle": "background-color: yellow; color: black"
            },
            "制作思维导图": {
                "Prefix": "一个典型的思维导图通常应该包含以下内容：\n1. 核心主题或中心思想：思维导图的中心，通常是一个大写的中心节点，代表整个思维导图的主要主题或主要问题，例如：“市场营销战略”、“健康生活方式”等。\n2. 分支节点：中心节点的关联主题或子问题，通常是主题后面的子节点。这些节点可以再次分为多级子节点，形成更详细的子分类，以便更好的理解主题。\n3. 关键词：涉及到重点话题或关键词，方便用户更好地理解思维导图，例如：“数据分析”、“产品优化”等。\n4. 图像：为了更好的参考，一些图片、图表和符号可以用来补充思维导图的内容。\n5. 颜色编码：不同的节点可以具有不同的颜色，颜色编码有助于用户更好地理解主题和节点之间的关系。\n6. 标签和注释：节点可以包含标签和注释来提示关键信息，例如：“60%营收增长”、“市场份额捕获”等。\n7. 连接线：为了更好的理解节点之间的关系，连接线可以用来表示节点之间的层次、行动和其他关系。\n8. 思考过程和想法：思维导图可以记录创意、思考过程和想法。这些节点可以帮助用户更好地处理思考和创意。\n\n现在开始，帮我做一个思维导图，需求如下：\n",
                "Suffix": "，输出为opml代码",
                "Sample": "",
                "ButtonStyle": "background-color: yellow; color: black"
            },
            "健身计划": {
                "Prefix": "你是一位私人教练，",
                "Suffix": "，给我制定一份针对性的训练计划",
                "Sample": "我现在想[减去腿部赘肉]",
                "ButtonStyle": "background-color: blue; color: white"
            },
            "心理咨询": {
                "Prefix": "你现在是一个心理咨询师，我告诉你我的想法，你给我一些建议。",
                "Suffix": "",
                "Sample": "现在我想[和你聊一下关于工作上的问题]",
                "ButtonStyle": "background-color: blue; color: white"
            },
            "周易解梦": {
                "Prefix": "我希望你扮演一位周易解梦专家，并且猜测你可能会解释周易中各种梦境的含义。有很多人梦到了不同的事情，在周易的角度看待这些梦境，或许可以揭示梦中隐含的信息和暗示。我建议您可以通过参考周易中有关梦境的解释和各种象征意义，帮助人们理解梦中的讯息，并为他们提供建议和指引。同时，您可以根据每个人的特殊情况和个性，给出独特的建议，让他们可以更好的把握梦境中的信息，从而更好的应对未来的挑战。\n",
                "Suffix": "\n请开始周易解梦",
                "Sample": "我的梦境是[一个美丽的花园]",
                "ButtonStyle": "background-color: blue; color: white"
            },
            "策划方案": {
                "Prefix": "",
                "Suffix": "，给出一个推广策划方案，并列出具体预算",
                "Sample": "针对公司即将推出的[智能耳机产品]",
                "ButtonStyle": "background-color: blue; color: white"
            },
            "学习计划": {
                "Prefix": "你是我的学习指导老师，",
                "Suffix": "，请为我制定一份详细的学习计划",
                "Sample": "我需要[通过英语四级考试]",
                "ButtonStyle": "background-color: aquamarine; color: black"
            },
            "招聘需求": {
                "Prefix": "你是一位HR，需要发布招聘需求，请你根据对候选人的几个关键要求，设计一份完整的职位描述。",
                "Suffix": "",
                "Sample": "要求为：[大学及以上学历，3年以上小红书账号运营经验。过往有过成功的小红书账号运营案例。有良好的文字策划、视频剪辑和粉丝运营能力。有较好的沟通能力和团队协作能力]",
                "ButtonStyle": "background-color: aquamarine; color: black"
            },
            "委婉拒绝": {
                "Prefix": "",
                "Suffix": "，要求语气委婉、不伤害朋友感情",
                "Sample": "[为拒绝朋友周末的聚餐邀请]给出[3]个借口",
                "ButtonStyle": "background-color: aquamarine; color: black"
            },
            "智囊团建议": {
                "Prefix": "你是我的智囊团，团内有 6 个不同的董事作为教练，分别是乔布斯、伊隆马斯克、马云、柏拉图、维达利和慧能大师。他们都有自己的个性、世界观、价值观，对问题有不同的看法、建议和意见。我会在这里说出我的处境和我的决策。先分别以这 6 个身份，以他们的视角来审视我的决策，给出他们的批评和建议，",
                "Suffix": "",
                "Sample": "我的处境和决策是 [？]",
                "ButtonStyle": "background-color: aquamarine; color: black"
            }
        }

    @classmethod
    def gen_init_functions(cls):
        """
        从数据库中读取，并生成 “获取初始化用的功能按钮”
        :return:
        """
        json_funs = {}
        button_functions = cls.get_button_functions()
        for button_function in button_functions:
            json_str = button_function.cfg_value
            prefix, suffix, sample, btn_style = to_json_items(json_str,
                                                              ["prefix", "suffix", "sample", "btn_style"],
                                                              ["", "", "", ""])
            name = button_function.cfg_key
            json_funs[name] = {}
            json_funs[name]["Prefix"] = prefix
            json_funs[name]["Suffix"] = suffix
            json_funs[name]["Sample"] = sample
            json_funs[name]["ButtonStyle"] = btn_style

        print(to_json_str(json_funs, ensure_ascii=False, indent=4, separators=(',', ': ')))


if __name__ == '__main__':
    # ConfigOp.create_table()
    # print(ConfigOp.get_sys_config("api_key"))
    # print(ConfigOp.get_config("system", "api_key"))
    # print(ConfigOp.get_configs("system"))
    # ConfigOp.init_tab_funcs()
    # ConfigOp.save_config(CFG_KEY_TAB_FUNCTION, "语音交流", "", order_no=2)
    ConfigOp.gen_init_functions()
    pass
