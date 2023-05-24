# -*- coding:utf-8 -*-
# title           :douyin_video_view.py
# description     :抖音短视频帮助视图控件
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================

from common.app_events import AppEvents
from controls.tab_input_view import TabInputView


class DouyinVideoView(TabInputView):
    """
    抖音视频视图控件（Tab页签功能）
    """

    def __init__(self, parent, send_message):
        super(DouyinVideoView, self).__init__(parent)

        self.set_input_style([self.txt_chat_subject, self.txt_job_titles])
        self.set_placeholder_text([self.txt_chat_subject, self.txt_job_titles])

        # self.reconnect(self.btn_gen_job, "clicked", self.gen_job)
        self.send_message = send_message

        self.btn_gen_job_title.clicked.connect(lambda: self.gen_job_title())
        self.btn_gen_job.clicked.connect(lambda: self.gen_jobs())

        AppEvents.on_recieved_message_subscription(self.recieved_message)

    def recieved_message(self, status, message):
        """
        接收到消息，会触发
        :param message:
        :return:
        """
        if not hasattr(self, "message_type"):
            return

        if self.message_type == "job_title":
            # 如果消息类型是标题
            # QPlainTextEdit.setPlainText()
            # 将文案标题显示在文案标题的文本框
            self.txt_job_titles.setPlainText(message)
            self.message_type = ""
        elif self.message_type == "job":
            # 如果消息类型是：短视频文案，则根据文案标题批量生成短视频文案
            self.gen_jobs()
            pass

    def gen_jobs(self):
        """
        根据短视频标题批量生成文案内容。
        :return:
        """
        if self.check_text_box(self.txt_job_titles, "请输入关于短视频文案的标题"):
            self.message_type = "job"
            if not hasattr(self, "job_idx"):
                self.job_idx = 0
            else:
                self.job_idx += 1
            # 注意的是：标题以换行符分割
            titles = self.txt_job_titles.toPlainText().split("\n")
            if self.job_idx > len(titles) - 1:
                delattr(self, "job_idx")
                self.message_type = ""
                return

            self.gen_job(titles[self.job_idx])

    def gen_job(self, job_title):
        """
        根据短视频标题生成文案内容
        :param job_title:
        :return:
        """
        job_title = str(job_title).lstrip('1234567890.、) ')
        # 下面根据我提供的标题写出对应的文案：走进未来：人工智能正在改变我们的生活方式
        input_msg = f"下面根据我提供的标题写出对应的短视频文案,大概一到两分钟的视频时间，标题为：{job_title}"
        print(input_msg)  # message, no_context=False
        self.send_message(input_msg, no_context=True)
        self.current_job_status = 1

    def unbind_events(self):
        AppEvents.on_recieved_message_unsubscription(self.recieved_message)

    def gen_job_title(self):
        """
        生成短视频文案的标题
        :return:
        """
        if self.check_text_box(self.txt_chat_subject, "请输入关于短视频文案内容的提示"):
            self.message_type = "job_title"
            job_num = self.spinbox_job_num.value()
            subject = self.txt_chat_subject.toPlainText()
            input_msg = f"生成{job_num}个关于“{subject}”的爆款标题，格式如下：\n"
            for i in range(job_num):
                input_msg += f"{i + 1}. xxxxxx\n"
            print(input_msg)  # message, no_context=False
            self.send_message(input_msg, no_context=True)
