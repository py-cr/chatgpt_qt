# -*- coding:utf-8 -*-
# title           :config_window.py
# description     :配置窗口
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QMessageBox, QMdiSubWindow, QAbstractItemView
from PyQt5.QtWidgets import QToolBar, QStyledItemDelegate, QLineEdit
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QColor, QPalette
from PyQt5.uic import loadUi

from common.app_config import DB_NAME
from common.app_events import AppEvents
from common.mdi_window_mixin import MdiWindowMixin
from common.message_box import MessageBox
from common.ui_mixin import UiMixin
from common.ui_utils import find_ui
from db.entities.consts import CFG_KEY_BUTTON_FUNCTION, CFG_KEY_AI_ROLE, CFG_KEY_CHAT_CATEGORY


class ConfigWindowStyledItemDelegate(QStyledItemDelegate):
    """

    """

    def __init__(self, model, parent=None, callback=None):
        super().__init__(parent)
        self.model = model
        self.callback = callback

    def paint(self, painter, option, index):
        is_delete = self.model.data(self.model.index(index.row(), 5))
        if is_delete != 0:
            # 如果是第一行，添加删除线
            color = QColor(180, 180, 180)  # 设置为灰色
            option.palette.setColor(QPalette.Text, color)
            option.font.setStrikeOut(True)  # 添加删除线
        super().paint(painter, option, index)
        if callable(self.callback):
            self.callback()

    def createEditor(self, parent, option, index):
        # 为第一列创建一个 QLineEdit 输入控件
        if index.column() == 2:
            editor = QLineEdit(parent)
            # 检查该单元格是否为空并设置其占位符文本（placeholder text）
            if not index.model().data(index):
                editor.setPlaceholderText("请输入按钮名称")
            return editor
        else:
            return super().createEditor(parent, option, index)


class ConfigWindow(QMdiSubWindow, UiMixin, MdiWindowMixin):
    """
    配置窗口
    """

    def __init__(self, window_title, cfg_category, col_names=['Key', '值', '排序号']):
        super().__init__()

        self.cfg_category = cfg_category
        # # 初始化数据库连接
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(f'data/{DB_NAME}')
        if not self.db.open():
            MessageBox.error(self, '错误', '连接数据库文件失败.')
            return

        loadUi(find_ui("ui/config_setting.ui"), self)

        self.set_icons([self.addButton, self.deleteButton, self.updateButton, self.btn_enabled, self.btn_disabled],
                       ['add.png', 'cross.png', 'disk.png', "star-on.png", "stop.png"])

        self.setWindowTitle(window_title)
        self.label_title.setText(window_title)
        # 初始化表格和模型
        self.init_table_model(col_names)

        self.dock_fill()
        # 初始化按钮
        self.init_buttons()

        self.txt_keyword.textChanged.connect(self.setFilter)

        self.cmb_display_status.addItem("所有", -1)
        self.cmb_display_status.addItem("启用", 0)
        self.cmb_display_status.addItem("禁用", 1)

        self.cmb_display_status.currentIndexChanged.connect(self.setFilter)

        self.setWindowIcon(self.default_icon())

    def setFilter(self):
        from common.str_utils import is_empty
        keyword = self.txt_keyword.text().strip()
        deleted = self.cmb_display_status.itemData(self.cmb_display_status.currentIndex())

        if is_empty(keyword):
            where_clause = f'cfg_category="{self.cfg_category}"'
        else:
            where_clause = f'cfg_category="{self.cfg_category}" AND cfg_key LIKE "%{keyword}%"'

        if deleted >= 0:
            where_clause += f" AND is_deleted={deleted}"

        self.model.setFilter(where_clause)
        self.on_search_keyword_changed(keyword)

    def init_table_model(self, col_names):
        """
        初始化表格和模型
        :param col_names:
        :return:
        """
        self.model = QSqlTableModel()
        self.model.dataChanged.connect(self.on_data_changed)
        # 连接 modelReset() 信号，用于监听数据加载完成事件
        self.model.modelReset.connect(self.handle_data_loaded)
        self.tableView.setModel(self.model)

        table_name = 't_config'
        # where_clause = f'cfg_category="{self.cfg_category}" AND is_deleted=0'
        where_clause = f'cfg_category="{self.cfg_category}"'
        self.model.setTable(table_name)
        self.model.setFilter(where_clause)
        self.model.setSort(self.model.fieldIndex('order_no'), Qt.SortOrder.AscendingOrder)
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()

        # 设置表格的列数和列标签
        self.model.setHeaderData(0, Qt.Horizontal, '_id')
        self.model.setHeaderData(self.model.fieldIndex('cfg_category'), Qt.Horizontal, 'Category')
        self.model.setHeaderData(2, Qt.Horizontal, col_names[0])
        self.model.setHeaderData(3, Qt.Horizontal, col_names[1])
        self.model.setHeaderData(4, Qt.Horizontal, col_names[2])
        self.model.setHeaderData(5, Qt.Horizontal, 'Deleted')


        delegate = ConfigWindowStyledItemDelegate(self.model, callback=self.update_button_status)
        self.tableView.setItemDelegate(delegate)
        # self.tableView.setItemDelegateForColumn(0, delegate)

        self.setColumnsHidden(["_id", "cfg_category", "is_deleted"])
        self.setColumnsWidth(["cfg_key", "cfg_value", "order_no"], [300, 500, 100])
        # self.data_changed = False
        self.tableView.selectionModel().selectionChanged.connect(self.on_row_selected)

    def on_search_keyword_changed(self, keyword):
        pass

    def handle_data_loaded(self):
        pass

    def init_buttons(self):
        """
        初始化按钮
        :return:
        """
        self.toolbar = QToolBar()
        self.layout_left.addWidget(self.toolbar)

        self.btn_enabled.clicked.connect(self.enableRecord)
        self.toolbar.addWidget(self.btn_enabled)

        self.btn_disabled.clicked.connect(self.disableRecord)
        self.toolbar.addWidget(self.btn_disabled)

        self.toolbar.addWidget(self.btn_line)
        # 创建按钮和信号槽连接
        self.addButton.clicked.connect(self.addRecord)
        self.toolbar.addWidget(self.addButton)

        self.updateButton.clicked.connect(self.saveRecord)
        self.toolbar.addWidget(self.updateButton)

        self.deleteButton.clicked.connect(self.deleteRecord)
        self.toolbar.addWidget(self.deleteButton)

    def on_row_selected(self, selected, deselected):
        # for index in selected.indexes():
        #     print('Selected row:', index.row())
        # print("row", self.tableView.currentIndex().row(), "column", self.tableView.currentIndex().column())
        pass

    def setColumnsWidth(self, col_names, width):
        """
        设置列宽
        :param col_names:
        :param width:
        :return:
        """
        for i, col_name in enumerate(col_names):
            col_idx = self.model.fieldIndex(col_name)
            self.tableView.setColumnWidth(col_idx, width[i])

    def setColumnsHidden(self, col_names):
        """
        设置隐藏的列
        :param col_names:
        :return:
        """
        for i, col_name in enumerate(col_names):
            col_idx = self.model.fieldIndex(col_name)
            self.tableView.setColumnHidden(col_idx, True)

    def closeEvent(self, event):
        # 获取窗口中的模型
        model = self.model
        # 如果模型有未提交的更改
        if model.isDirty():
            # 给予提示
            reply = MessageBox.question(self, '数据已修改', '数据已修改，是否保存数据？或者“取消”关闭窗口的操作',
                                        buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                        default_button=QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                # 保存数据
                model.submitAll()
            elif reply == QMessageBox.Cancel:
                # 防止窗口关闭
                event.ignore()
                return True
        super().closeEvent(event)

    def on_data_changed(self, index_top_left, index_bottom_right):
        row = index_top_left.row()
        column = index_top_left.column()
        item = self.model.itemData(index_top_left)

    def window_id(self):
        return f"ConfigWindow_{self.windowTitle()}"

    def addRecord(self):
        """
        插入一条新记录
        :return:
        """
        row_count = self.model.rowCount()
        result = self.model.insertRow(row_count)
        if result:
            # 获取最后一行的记录
            last_record = self.model.record(row_count)
            category_field_index = self.model.fieldIndex('cfg_category')
            last_record.setValue(category_field_index, self.cfg_category)
            self.model.setRecord(row_count, last_record)
            self.model.setData(self.model.index(row_count, category_field_index), self.cfg_category)
            self.model.updateRowInTable(row_count, last_record)
            self.tableView.scrollToBottom()
            bottom_index = self.model.index(row_count, 0)
            self.select_indexes(bottom_index)
            # self.tableView.edit(bottom_index)

    def saveRecord(self):
        """
        提交对当前记录的修改
        :return:
        """
        self.model.submitAll()
        if self.cfg_category == CFG_KEY_BUTTON_FUNCTION:
            AppEvents.on_button_functions_changed()
        elif self.cfg_category == CFG_KEY_AI_ROLE:
            AppEvents.on_ai_roles_changed()
        elif self.cfg_category == CFG_KEY_CHAT_CATEGORY:
            AppEvents.on_chat_category_changed()

    def enableRecord(self):
        """
        启用当前选中的行
        :return:
        """
        indexes = self.tableView.selectionModel().selectedIndexes()
        if len(indexes) == 0:
            return
        self.model.setData(self.model.index(indexes[0].row(), 5), 0)
        # self.saveRecord()
        self.tableView.setFocus()

    def select_indexes(self, index):
        # 设置选中状态并高亮显示
        self.tableView.selectionModel().setCurrentIndex(index,
                                                        QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.tableView.setFocus()

    def disableRecord(self):
        """
        禁用当前选中的行
        :return:
        """
        indexes = self.tableView.selectionModel().selectedIndexes()
        if len(indexes) == 0:
            return
        self.model.setData(self.model.index(indexes[0].row(), 5), 1)
        # self.saveRecord()
        self.tableView.setFocus()

    def deleteRecord(self):
        """
        删除当前选中的行
        :return:
        """
        indexes = self.tableView.selectionModel().selectedIndexes()
        if len(indexes) == 0:
            MessageBox.warning(self, '警告', '没有记录选中')
            return

        # 删除选中的行
        rows = set()
        for index in indexes:
            rows.add(index.row())
        for row in rows:
            self.model.removeRow(row)
        self.tableView.setFocus()

    def update_button_status(self):
        """
        更新按钮的状态（有效、无效）
        :return:
        """
        if self.model.isDirty():
            self.updateButton.setDisabled(False)
        else:
            self.updateButton.setDisabled(True)

        indexes = self.tableView.selectionModel().selectedIndexes()
        if len(indexes) == 0:
            self.btn_enabled.setDisabled(True)
            self.btn_disabled.setDisabled(True)
            # self.addButton.setDisabled(True)
            self.deleteButton.setDisabled(True)
            return

        is_delete = self.model.data(self.model.index(indexes[0].row(), 5))
        if is_delete == 0:
            self.btn_enabled.setDisabled(True)
            self.btn_disabled.setDisabled(False)
        else:
            self.btn_enabled.setDisabled(False)
            self.btn_disabled.setDisabled(True)

        self.deleteButton.setDisabled(False)
