# -*- coding:utf-8 -*-
# title           :menu_proxy.py
# description     :MenuProxy
# author          :Python超人
# date            :2023-5-1
# link            :https://gitcode.net/pythoncr/
# python_version  :3.8
# ==============================================================================
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory, QFileDialog, QPushButton, QAction
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt

from PyQt5 import QtWidgets, QtGui
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTranslator, QLocale


class MenuProxy(QtWidgets.QProxyStyle):
    """
    菜单对图标文字的支持
    """
    menuHack = False
    alertShown = False

    def useMenuHack(self, element, opt, widget):
        if (element in (self.CT_MenuBarItem, self.CE_MenuBarItem) and
                isinstance(widget, QtWidgets.QMenuBar) and
                opt.icon and not opt.icon.isNull() and opt.text):
            if not self.alertShown:
                if widget.isNativeMenuBar():
                    # this will probably not be shown...
                    print('WARNING: menubar items with icons and text not supported for native menu bars')
                styleName = self.baseStyle().objectName()
                if not 'windows' in styleName and styleName != 'fusion':
                    print('WARNING: menubar items with icons and text not supported for "{}" style'.format(
                        styleName))
                self.alertShown = True
            return True
        return False

    def sizeFromContents(self, content, opt, size, widget=None):
        if self.useMenuHack(content, opt, widget):
            # return a valid size that includes both the icon and the text
            alignment = (QtCore.Qt.AlignCenter | QtCore.Qt.TextShowMnemonic |
                         QtCore.Qt.TextDontClip | QtCore.Qt.TextSingleLine)
            if not self.proxy().styleHint(self.SH_UnderlineShortcut, opt, widget):
                alignment |= QtCore.Qt.TextHideMnemonic

            width = (opt.fontMetrics.size(alignment, opt.text).width() +
                     self.pixelMetric(self.PM_SmallIconSize) +
                     self.pixelMetric(self.PM_LayoutLeftMargin) * 2)

            textOpt = QtWidgets.QStyleOptionMenuItem(opt)
            textOpt.icon = QtGui.QIcon()
            height = super().sizeFromContents(content, textOpt, size, widget).height()

            # return QtCore.QSize(width, height)
            # TODO: 进行了调整
            return QtCore.QSize(width - 10, height)

        return super().sizeFromContents(content, opt, size, widget)

    def drawControl(self, ctl, opt, qp, widget=None):
        if self.useMenuHack(ctl, opt, widget):
            # create a new option with no icon to draw a menubar item; setting
            # the menuHack allows us to ensure that the icon size is taken into
            # account from the drawItemText function
            textOpt = QtWidgets.QStyleOptionMenuItem(opt)
            textOpt.icon = QtGui.QIcon()
            self.menuHack = True
            self.drawControl(ctl, textOpt, qp, widget)
            self.menuHack = False

            # compute the rectangle for the icon and call the default
            # implementation to draw it
            iconExtent = self.pixelMetric(self.PM_SmallIconSize)
            margin = self.pixelMetric(self.PM_LayoutLeftMargin) / 2
            top = opt.rect.y() + (opt.rect.height() - iconExtent) / 2
            iconRect = QtCore.QRect(opt.rect.x() + margin, top, iconExtent, iconExtent)
            pm = opt.icon.pixmap(widget.window().windowHandle(),
                                 QtCore.QSize(iconExtent, iconExtent),
                                 QtGui.QIcon.Normal if opt.state & self.State_Enabled else QtGui.QIcon.Disabled)
            self.drawItemPixmap(qp, iconRect, QtCore.Qt.AlignCenter, pm)
            return
        super().drawControl(ctl, opt, qp, widget)

    def drawItemText(self, qp, rect, alignment, palette, enabled, text, role=QtGui.QPalette.NoRole):
        if self.menuHack:
            margin = (self.pixelMetric(self.PM_SmallIconSize) +
                      self.pixelMetric(self.PM_LayoutLeftMargin))
            # rect = rect.adjusted(margin, 0, 0, 0)
            # TODO: 进行了调整
            rect = rect.adjusted(int(margin / 1.5), 0, 0, 0)
        super().drawItemText(qp, rect, alignment, palette, enabled, text, role)
