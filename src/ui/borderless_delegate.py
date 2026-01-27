#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Borderless Table Delegate - Custom cell renderer for DataPrism
无边框表格代理 - DataPrism 的自定义单元格渲染器
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor


class BorderlessDelegate(QStyledItemDelegate):
    """
    Custom delegate that renders table cells without borders.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from src.ui.style_manager import StyleManager
        self.bg_main = QColor(StyleManager.c("bg_main"))
        self.bg_alternate = QColor(StyleManager.c("table_alternate"))
        self.text_primary = QColor(StyleManager.c("text_primary"))
        self.accent = QColor(StyleManager.c("accent"))
        # More opaque selection background for better contrast
        self.selection_bg = QColor(StyleManager.c("table_selection_bg"))
    
    def paint(self, painter, option, index):
        """
        Custom paint with proper selection background.
        自定义绘制，带有适当的选中背景。
        """
        from src.ui.style_manager import StyleManager
        painter.save()
        
        # Enable text anti-aliasing for crisp font rendering
        # 启用文本抗锯齿以获得清晰的字体渲染
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        
        # Determine colors based on selection state
        # 根据选中状态确定颜色
        is_selected = option.state & QStyle.StateFlag.State_Selected
        
        if is_selected:
            bg_color = self.selection_bg
            text_color = self.accent
        else:
            # Alternating row colors / 交替行颜色
            if index.row() % 2 == 0:
                bg_color = self.bg_main
            else:
                bg_color = self.bg_alternate
            text_color = self.text_primary
        
        # Fill the cell background / 填充单元格背景
        painter.fillRect(option.rect, bg_color)
        
        # Set font for text rendering / 设置文本渲染字体
        # Use coordinated font from StyleManager / 使用 StyleManager 中的协调字体
        from PySide6.QtGui import QFont
        
        # Get font name and size from theme
        font_family = StyleManager.t("family_main").strip('"')
        # Use 10px for ultimate "Large smaller" effect as requested by 老大
        font_size = 10
        
        font = QFont(font_family, font_size)
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)
        
        # Draw text / 绘制文字
        painter.setPen(text_color)
        text_rect = option.rect.adjusted(10, 0, -10, 0)  # 进一步减小内边距 / Further reduce padding
        display_text = index.data(Qt.ItemDataRole.DisplayRole)
        if display_text is None:
            display_text = ""
        
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            str(display_text)
        )
        
        painter.restore()
    
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(52)
        return size
