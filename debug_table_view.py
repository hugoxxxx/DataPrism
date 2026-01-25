#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Table View Debugger - Diagnostic tool to identify rendering issues
表格视图调试器 - 用于识别渲染问题的诊断工具
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, 
                               QVBoxLayout, QWidget, QPushButton, QTextEdit,
                               QStyleFactory)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class SimpleTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.data_list = [
            ["Cell 1-1", "Cell 1-2", "Cell 1-3", "Cell 1-4"],
            ["Cell 2-1", "Cell 2-2", "Cell 2-3", "Cell 2-4"],
            ["Cell 3-1", "Cell 3-2", "Cell 3-3", "Cell 3-4"],
        ]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)
    
    def columnCount(self, parent=QModelIndex()):
        return 4
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data_list[index.row()][index.column()]
        return None


class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table View Debugger")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Info text
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        # Table view
        self.table = QTableView()
        self.table.setModel(SimpleTableModel())
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Control buttons
        btn_default = QPushButton("Test 1: Default Style")
        btn_default.clicked.connect(self.test_default_style)
        layout.addWidget(btn_default)
        
        btn_fusion = QPushButton("Test 2: Fusion Style")
        btn_fusion.clicked.connect(self.test_fusion_style)
        layout.addWidget(btn_fusion)
        
        btn_no_grid = QPushButton("Test 3: No Grid")
        btn_no_grid.clicked.connect(self.test_no_grid)
        layout.addWidget(btn_no_grid)
        
        btn_css = QPushButton("Test 4: CSS Override")
        btn_css.clicked.connect(self.test_css_override)
        layout.addWidget(btn_css)
        
        self.log("Debugger initialized. Select a row and try different tests.")
    
    def log(self, message):
        self.info_text.append(message)
    
    def test_default_style(self):
        QApplication.instance().setStyle(QStyleFactory.create('WindowsVista'))
        self.table.setStyleSheet("")
        self.table.setShowGrid(True)
        self.log("Test 1: Applied default Windows style with grid")
    
    def test_fusion_style(self):
        QApplication.instance().setStyle(QStyleFactory.create('Fusion'))
        self.log("Test 2: Applied Fusion style")
    
    def test_no_grid(self):
        self.table.setShowGrid(False)
        self.table.setGridStyle(Qt.PenStyle.NoPen)
        self.log("Test 3: Disabled grid (setShowGrid=False, gridStyle=NoPen)")
    
    def test_css_override(self):
        css = """
            QTableView {
                gridline-color: transparent;
                border: none;
            }
            QTableView::item {
                border: none;
                outline: none;
            }
            QTableView::item:selected {
                background-color: rgba(209, 84, 0, 0.3);
                border: none;
                outline: none;
            }
        """
        self.table.setStyleSheet(css)
        self.log("Test 4: Applied CSS with transparent gridlines and no borders")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    sys.exit(app.exec())
