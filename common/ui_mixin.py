# -*- coding:utf-8 -*-
# title           :ui_mixin.py
# description     :UiMixin
# author          :Python超人
# date            :2023-6-3
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtWidgets import QLayout, QLayoutItem, QWidgetItem

from common.message_box import MessageBox
from common.ui_utils import find_icon, set_icon


class UiMixin:
    """
    对窗口 UI 扩展支持
    """

    def window_id(self):
        """
        窗口唯一ID，保证打开的窗口唯一
        :return:
        """
        return ""

    def transparent_icon(self):
        """
        透明图标
        :return:
        """
        return self.icon("transparent.png")

    def default_icon(self):
        """
        默认图标
        :return:
        """
        return self.icon('icon.png')

    def icon(self, icon_file):
        """
        指定图标文件，返回图标对象
        :param icon_file: 图标文件名
        :return:
        """
        return QIcon(find_icon(f'{icon_file}'))

    def set_icon(self, action: [QAction, QMenu], icon_file):
        """
        设置菜单的图标
        :param action: 菜单 action
        :param icon_file: 图标文件名
        :return:
        """
        set_icon(action, icon_file)

    def set_icons(self, actions: [], icon_files: []):
        """
        批量设置菜单集合的图标
        :param actions: 菜单 action 集合
        :param icon_files: 对应菜单 action 的图标文件名集合
        :return:
        """
        for i, action in enumerate(actions):
            set_icon(action, icon_files[i])

    def default_font(self):
        """
        默认字体
        :return:
        """
        font = QFont("微软雅黑", 10)
        return font

    def set_input_style(self, textbox):
        """
        设置输入文本框的样式
        :param textbox: 文本框对象（支持文本框列表）
        :return:
        """
        if isinstance(textbox, list):
            for t in textbox:
                t.setFont(self.default_font())
                t.setStyleSheet("color:blue")
        else:
            textbox.setFont(self.default_font())
            textbox.setStyleSheet("color:blue")

    def set_placeholder_text(self, textbox):
        """
        设置文本框 placeholder 的文本
        :param textbox: 文本框对象（支持文本框列表）
        :return:
        """
        if isinstance(textbox, list):
            for t in textbox:
                t.setPlaceholderText(t.toolTip())
        else:
            textbox.setPlaceholderText(textbox.toolTip())

    def set_layout_enabled(self, layout, enabled):
        """
        设置指定的 layout 是否有效
        :param layout:
        :param enabled:
        :return:
        """
        if layout is None:
            return
        if not hasattr(layout, "count"):
            return
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QWidgetItem):
                item.widget().setEnabled(enabled)
            elif isinstance(item, QLayoutItem):
                self.set_layout_enabled(item.layout(), enabled)

    def find_layout_by_name(self, obj_name):
        """
        根据 objectName 获取 layout 对象
        :param obj_name: objectName
        :return:
        """
        if hasattr(self, f"{obj_name}_parent"):
            return getattr(self, f"{obj_name}_parent")

        parent_obj = self.parentWidget()
        if parent_obj is None:
            return self
        while True:
            if parent_obj.objectName() == obj_name:
                setattr(self, f"{obj_name}_parent", parent_obj)
                return parent_obj
            else:
                obj = parent_obj.findChild(QLayout, obj_name)
                if obj is not None:
                    setattr(self, f"{obj_name}_parent", obj)
                    return obj

            parent_obj = parent_obj.parentWidget()
            if parent_obj is None:
                return self

    def check_text_box(self, textbox, prompt):
        """
        检查文本框内容是否为空，如果为空，提示 prompt
        :param textbox: 文本框对象
        :param prompt: 提示
        :return:
        """
        content: str = textbox.toPlainText()
        content = content.strip()
        if len(content) == 0:
            MessageBox.error(self, "错误", prompt)
            if hasattr(textbox, "setFocus"):
                textbox.setFocus()  # 让用户重新输入
            return False
        return True

    def signal_connected(self, obj, name):
        """
        判断信号是否连接，用于判断事件是否已经绑定
        :param obj:        对象
        :param name:       信号名，如 clicked()
        """
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False

    def reconnect(self, obj, name, method):
        """
        用于事件的重新绑定（先删除绑定，再重新绑定）
        :param obj: 对象
        :param name: 事件名
        :param method: 事件绑定的方法
        :return:
        """
        signal_attr = getattr(obj, name)
        if self.signal_connected(obj, name + "()"):
            signal_attr.disconnect()

        signal_attr.connect(method)
