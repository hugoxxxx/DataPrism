#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Borderless Style - Custom QProxyStyle to disable selection borders
无边框样式 - 自定义 QProxyStyle 以禁用选中边框
"""

from PySide6.QtWidgets import QProxyStyle, QStyle
from PySide6.QtCore import QRect
from PySide6.QtGui import QPalette


class BorderlessStyle(QProxyStyle):
    """
    Custom style that disables the drawing of focus rectangles and selection borders.
    自定义样式，禁用焦点矩形和选中边框的绘制。
    """
    
    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Override to prevent drawing of focus rectangles.
        """
        # Skip drawing focus rectangles
        if element == QStyle.PrimitiveElement.PE_FrameFocusRect:
            return
        
        # Call parent for all other elements
        super().drawPrimitive(element, option, painter, widget)
    
    def drawControl(self, element, option, painter, widget=None):
        """
        Override to customize item view selection rendering.
        """
        # For item view items, we want to prevent the default selection border
        if element == QStyle.ControlElement.CE_ItemViewItem:
            # Let our custom delegate handle all rendering
            # Do NOT call parent to avoid default selection borders
            return
        
        # Call parent for all other elements
        super().drawControl(element, option, painter, widget)
