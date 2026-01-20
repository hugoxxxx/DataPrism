#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataPrism - A lightweight, high-aesthetic, high-performance ExifTool GUI station
DataPrism - 一款轻量、美学领先、高性能的 ExifTool GUI 工作站
"""

import sys
from src.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication


def main():
    """Main entry point / 主入口"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
