# -*- coding:utf-8 -*-
# title           :button_function_window.py
# description     :按钮功能配置窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
import json
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView
from common.str_utils import is_empty
from common.ui_mixin import UiMixin
from controls.function_view import FunctionView, FUNCTION_SAMPLE_TEXT
from db.entities.consts import CFG_KEY_BUTTON_FUNCTION
from windows.config_window import ConfigWindow


class ButtonFunctionWindow(ConfigWindow, UiMixin):
    """
    按钮功能配置窗口
    """

    def __init__(self, window_title, cfg_category=CFG_KEY_BUTTON_FUNCTION, col_names=['Key', '值', '排序号']):
        super().__init__(window_title, cfg_category, col_names)
        #  控制功能视图控件
        function_view = FunctionView()
        function_view.dock_fill(self.layout_right)

        # self.tableView.setColumnHidden(3, True)
        self.setColumnsHidden(["cfg_value"])  # "cfg_value"字段保存的JSON数据，不显示"cfg_value"字段

        function_view.data_changed = self.view_data_changed
        self.function_view = function_view
        self.function_view.setDisabled(True)

    def on_row_selected(self, selected, deselected):
        """
        控制功能视图控件是否有效
        :param selected:
        :param deselected:
        :return:
        """
        _id = self.get_selected_value("_id")
        if _id is None:
            # 如果没有选中任何行，则控制功能视图控件无效
            self.function_view.setDisabled(True)
        else:
            # 选中行后，则控制功能视图控件有效，并更新功能视图控件的数据
            self.function_view.setDisabled(False)
            self.update_view_data()
        # print('Selected row:', _id)

    def handle_data_loaded(self):
        # 处理数据加载完成事件
        self.tableView.clearSelection()
        self.update_view_data()

    def update_view_data(self):
        """
        更新功能视图控件的数据
        :return:
        """
        if not hasattr(self, "function_view"):
            return

        def empty_method():
            pass

        # 功能视图控件的数据发生变化指向一个空方法(即发生变化事件无效，对事件的处理解绑)
        # 因为该代码后面会触发改事件，先暂时忽略数据修改
        self.function_view.data_changed = empty_method
        # 获取当前行的配置数据，并更新到功能视图控件
        key, value = self.get_current_config_kv()
        if len(value) == 0:
            self.function_view.txt_suffix.setText("")
            self.function_view.txt_prefix.setText("")
            self.function_view.txt_message.setText(FUNCTION_SAMPLE_TEXT)
            self.function_view.set_button_style("")
            self.function_view.button_preview.setText("按钮")
        else:
            json_data = json.loads(value)
            suffix = json_data["suffix"]
            prefix = json_data["prefix"]
            if "sample" in json_data:
                sample = json_data["sample"]
            else:
                sample = FUNCTION_SAMPLE_TEXT

            if is_empty(sample):
                sample = FUNCTION_SAMPLE_TEXT
            btn_style = json_data["btn_style"]

            self.function_view.txt_suffix.setText(suffix)
            self.function_view.txt_prefix.setText(prefix)
            self.function_view.txt_message.setText(sample)
            self.function_view.set_button_style(btn_style)
            self.function_view.button_preview.setText(key.split('|')[0].strip())

        # 功能视图控件的数据发生变化事件有效
        self.function_view.data_changed = self.view_data_changed

    def get_selected_value(self, col_name):
        """
        获取选择行和指定列名的值
        :param col_name: 指定列名
        :return:
        """
        col_idx = self.model.fieldIndex(col_name)
        value = self.model.data(self.model.index(self.tableView.currentIndex().row(), col_idx))
        return value

    def on_data_changed(self, index_top_left, index_bottom_right):
        """
        当配置的数据发生修改后触发
        :param index_top_left:
        :param index_bottom_right:
        :return:
        """
        row = index_top_left.row()
        column = index_top_left.column()
        item = self.model.itemData(index_top_left)
        if column == self.model.fieldIndex("cfg_key"):
            # print(row, column, item)  # 0 2 {0: '你好', 2: '你好'}
            button_name = item.get(column, None)
            if button_name == "" or button_name is None:
                button_name = "按钮"

            self.function_view.button_name = button_name
            self.function_view.button_preview.setText(button_name)

    def set_current_config_value(self, value):
        """
        修改当前选中的配置值
        :param value:
        :return:
        """

        def empty_method(index_top_left, index_bottom_right):
            pass

        # 对事件的处理解绑
        self.model.dataChanged.connect(empty_method)
        # 获取当前行号
        row = self.tableView.currentIndex().row()
        # 获取当前行的数据
        current_record = self.model.record(row)
        # 获取字段名为“cfg_value”的列号
        field_index = self.model.fieldIndex('cfg_value')
        # 修改选中 行（row）、指定 列（cfg_value） 的值
        current_record.setValue(field_index, value)
        self.model.setRecord(row, current_record)
        self.model.setData(self.model.index(row, field_index), value)
        # 修改值后，更新到Table
        self.model.updateRowInTable(row, current_record)

        # 对事件的处理重新连接
        self.model.dataChanged.connect(self.on_data_changed)

    def get_current_config_kv(self):
        row = self.tableView.currentIndex().row()
        current_record = self.model.record(row)
        return current_record.value(self.model.fieldIndex('cfg_key')), \
               current_record.value(self.model.fieldIndex('cfg_value'))

    def get_current_config_value(self):
        """
        获取选中行的 cfg_value 值
        :return:
        """
        row = self.tableView.currentIndex().row()
        current_record = self.model.record(row)
        field_index = self.model.fieldIndex('cfg_value')
        value = current_record.value(field_index)
        return value

    def view_data_changed(self):
        """
        功能视图控件的数据发生变化，会触发这里
        :return:
        """
        value = self.get_current_config_value()
        if len(value) == 0:
            print("无数据")
        # 获取功能视图控件的JSON数据
        json_data = self.function_view.to_json_data()
        json_data_str = json.dumps(json_data)
        # 功能视图控件的数据发生变化后，立即修改当前选中的配置值
        self.set_current_config_value(json_data_str)
        self.update_button_status()
