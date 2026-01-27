from PySide6.QtWidgets import QTableView, QStyleOptionViewItem, QStyle
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen


class BorderlessTableView(QTableView):
    """
    Custom QTableView that completely overrides paintEvent to eliminate all grid lines.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Disable all grid-related features
        self.setShowGrid(False)
        self.setGridStyle(Qt.PenStyle.NoPen)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Disable frame
        self.setFrameShape(QTableView.Shape.NoFrame)
        self.setFrameShadow(QTableView.Shadow.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        
        # Set selection behavior
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Disable vertical header
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(52)
    
    def paintEvent(self, event):
        """
        COMPLETE override of paintEvent - we manually draw everything.
        完全覆盖 paintEvent - 我们手动绘制所有内容。
        """
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Fill viewport background
        from src.ui.style_manager import StyleManager
        painter.fillRect(event.rect(), QColor(StyleManager.c("bg_main")))
        
        # Get visible range
        first_row = self.rowAt(event.rect().top())
        last_row = self.rowAt(event.rect().bottom())
        if first_row == -1:
            first_row = 0
        if last_row == -1:
            last_row = self.model().rowCount() - 1
        
        first_col = self.columnAt(event.rect().left())
        last_col = self.columnAt(event.rect().right())
        if first_col == -1:
            first_col = 0
        if last_col == -1:
            last_col = self.model().columnCount() - 1
        
        # Draw each visible cell using the delegate
        for row in range(first_row, last_row + 1):
            for col in range(first_col, last_col + 1):
                index = self.model().index(row, col)
                option = QStyleOptionViewItem()
                option.rect = self.visualRect(index)
                
                # Set selection state - FIXED: use correct enum path
                if self.selectionModel().isSelected(index):
                    option.state |= QStyle.StateFlag.State_Selected
                
                # Let the delegate paint
                delegate = self.itemDelegate(index)
                if delegate:
                    delegate.paint(painter, option, index)
        
        # DO NOT call super().paintEvent() - this prevents Qt from drawing anything else
        # 不调用 super().paintEvent() - 这阻止了 Qt 绘制任何其他东西

