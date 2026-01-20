#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration example showing how to use the architecture components
展示如何使用架构组件的集成示例
"""

from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget, QPushButton
from src.core.photo_model import PhotoDataModel
from src.core.command_history import CommandHistory
from src.core.exif_worker import ExifToolWorker
from src.core.app_context import AppContext
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PhotoDataController(QWidget):
    """
    Example controller showing integration of all components
    展示所有组件集成的示例控制器
    """
    
    def __init__(self):
        """Initialize controller / 初始化控制器"""
        super().__init__()
        
        # Initialize core components
        # 初始化核心组件
        self.photo_model = PhotoDataModel()
        self.command_history = CommandHistory()
        
        # Register services in AppContext
        # 在 AppContext 中注册服务
        AppContext.register("photo_model", self.photo_model)
        AppContext.register("command_history", self.command_history)
        
        # Setup worker thread for async operations
        # 为异步操作设置工作线程
        self.worker = ExifToolWorker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        # 连接信号
        self.worker.progress.connect(self.on_progress)
        self.worker.result_ready.connect(self.on_exif_loaded)
        self.worker.error_occurred.connect(self.on_error)
        
        self.worker_thread.started.connect(self.on_thread_started)
        self.worker.finished.connect(self.worker_thread.quit)
        
        # Setup UI
        # 设置 UI
        layout = QVBoxLayout(self)
        
        self.table_view = QTableView()
        self.table_view.setModel(self.photo_model)
        layout.addWidget(self.table_view)
        
        import_btn = QPushButton("Import Photos")
        import_btn.clicked.connect(self.on_import_clicked)
        layout.addWidget(import_btn)
        
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.on_undo_clicked)
        layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.on_redo_clicked)
        layout.addWidget(redo_btn)
        
        self.setLayout(layout)
    
    def on_import_clicked(self):
        """
        Handle import button click
        处理导入按钮点击
        """
        # Simulate file selection (in real app, use file dialog)
        # 模拟文件选择（在真实应用中，使用文件对话框）
        file_paths = [
            "D:\\Photos\\photo_1.jpg",
            "D:\\Photos\\photo_2.jpg",
            "D:\\Photos\\photo_3.jpg",
        ]
        
        logger.info(f"Importing {len(file_paths)} photos...")
        
        # Add to model (UI updates immediately with "Loading...")
        # 添加到模型（UI 立即显示"Loading..."）
        self.photo_model.add_photos(file_paths)
        
        # Start worker thread to load EXIF data asynchronously
        # 启动工作线程异步加载 EXIF 数据
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
            self.worker.read_exif(file_paths)
    
    def on_thread_started(self):
        """Called when worker thread starts / 工作线程启动时调用"""
        logger.info("Worker thread started")
    
    def on_progress(self, progress: int):
        """
        Handle progress updates from worker
        处理来自工作线程的进度更新
        """
        logger.info(f"Progress: {progress}%")
    
    def on_exif_loaded(self, results: dict):
        """
        Handle EXIF data loaded from worker
        处理从工作线程加载的 EXIF 数据
        """
        logger.info(f"EXIF loaded for {len(results)} files")
        
        # Update model with loaded EXIF data (with caching)
        # 用加载的 EXIF 数据更新模型（带缓存）
        for file_path, exif_data in results.items():
            self.photo_model.set_exif_data(file_path, exif_data)
    
    def on_error(self, error_msg: str):
        """
        Handle errors from worker
        处理工作线程的错误
        """
        logger.error(f"Worker error: {error_msg}")
    
    def on_undo_clicked(self):
        """Handle undo button click / 处理撤销按钮点击"""
        if self.command_history.undo():
            logger.info("Undo successful")
            self.table_view.update()
        else:
            logger.info("Nothing to undo")
    
    def on_redo_clicked(self):
        """Handle redo button click / 处理重做按钮点击"""
        if self.command_history.redo():
            logger.info("Redo successful")
            self.table_view.update()
        else:
            logger.info("Nothing to redo")


if __name__ == "__main__":
    """
    Usage example - 使用示例
    
    注意：这只是一个示例代码，展示了如何使用这些组件。
    在真实的应用中，应该与 MainWindow 集成。
    """
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    controller = PhotoDataController()
    controller.setWindowTitle("DataPrism - Architecture Example")
    controller.show()
    sys.exit(app.exec())
