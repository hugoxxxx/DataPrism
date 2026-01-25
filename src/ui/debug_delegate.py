#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Delegate - Diagnostic version with extensive logging
调试代理 - 带有详细日志的诊断版本
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from src.utils.logger import get_logger

logger = get_logger('DataPrism.DebugDelegate')


class DebugDelegate(QStyledItemDelegate):
    """
    Debug delegate with extensive logging to diagnose rendering issues.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_main = QColor("#101012")
        self.bg_alternate = QColor("#1D1D21")
        self.text_primary = QColor("#E0E0E0")
        self.accent = QColor("#D15400")
        self.selection_bg = QColor(209, 84, 0, 80)
        self.paint_count = 0
    
    def paint(self, painter, option, index):
        """
        Custom paint with debug logging.
        """
        self.paint_count += 1
        
        # Log every 10th paint call to avoid spam
        if self.paint_count % 10 == 0:
            logger.debug(f"Paint call #{self.paint_count}")
            logger.debug(f"  Row: {index.row()}, Col: {index.column()}")
            logger.debug(f"  Rect: {option.rect}")
            logger.debug(f"  State: {option.state}")
            logger.debug(f"  Selected: {bool(option.state & QStyle.StateFlag.State_Selected)}")
            logger.debug(f"  HasFocus: {bool(option.state & QStyle.StateFlag.State_HasFocus)}")
        
        painter.save()
        
        # Determine colors
        is_selected = option.state & QStyle.StateFlag.State_Selected
        
        if is_selected:
            bg_color = self.selection_bg
            text_color = self.accent
        else:
            if index.row() % 2 == 0:
                bg_color = self.bg_main
            else:
                bg_color = self.bg_alternate
            text_color = self.text_primary
        
        # Fill the ENTIRE rect with background color
        painter.fillRect(option.rect, bg_color)
        
        # Draw a DEBUG border to see the actual cell boundaries
        if is_selected and index.column() == 0:
            # Draw a red border on the first column of selected rows for debugging
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawRect(option.rect.adjusted(1, 1, -1, -1))
        
        # Draw text
        painter.setPen(text_color)
        text_rect = option.rect.adjusted(14, 0, -14, 0)
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
