#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataPrism - Professional EXIF Metadata Manager
Entry point / 程序入口
"""

import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger, get_logger
from src.core.config import init_config, get_config

# Setup logger / 设置日志器
config = init_config()  # Initialize config first / 先初始化配置
logger = setup_logger(
    'DataPrism',
    log_file=config.get('log_file_path', 'dataprism.log')
)


def global_exception_handler(exctype, value, tb):
    """
    Global exception handler / 全局异常处理器
    Catches all unhandled exceptions and logs them / 捕获所有未处理的异常并记录
    """
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Unhandled exception:\n{error_msg}")
    
    # Show user-friendly error dialog / 显示用户友好的错误对话框
    try:
        QMessageBox.critical(
            None,
            "程序错误 / Application Error",
            f"程序遇到未处理的错误 / An unhandled error occurred:\n\n{value}\n\n"
            f"详细信息已记录到日志文件 / Details have been logged to dataprism.log"
        )
    except Exception:
        # If GUI fails, at least print to console / 如果 GUI 失败，至少打印到控制台
        print(f"CRITICAL ERROR: {error_msg}")


def main():
    # Install global exception handler / 安装全局异常处理器
    sys.excepthook = global_exception_handler
    
    logger.info("=" * 60)
    logger.info("DataPrism starting...")
    logger.info("=" * 60)
    
    try:
        # Create application / 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("DataPrism")
        app.setApplicationVersion("1.1.0-test")
        app.setOrganizationName("DataPrism")
        
        # CRITICAL: Use Fusion style to eliminate Windows-specific rendering artifacts
        # 使用 Fusion 样式以消除 Windows 特定的渲染问题（如蓝色单元格分隔线）
        from PySide6.QtWidgets import QStyleFactory
        app.setStyle(QStyleFactory.create('Fusion'))
        
        # Initialize Design System / 初始化设计系统
        from src.ui.style_manager import StyleManager
        StyleManager.load_theme("studio_dark")
        
        # Set application metadata / 设置应用程序元数据
        window = MainWindow()
        window.show()
        
        logger.info("Main window displayed successfully")
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)
    
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
