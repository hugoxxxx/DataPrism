#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asynchronous thumbnail loader using thread pool to avoid UI blocking
使用线程池的异步缩略图加载器，避免 UI 阻塞
"""

from PySide6.QtCore import QObject, QRunnable, Signal, QSize, Qt
from PySide6.QtGui import QImageReader, QPixmap, QImage
import logging

logger = logging.getLogger('DataPrism.ThumbnailWorker')

class ThumbnailSignals(QObject):
    """Signals for thumbnail loading / 缩略图加载信号"""
    finished = Signal(str, QPixmap)  # file_path, pixmap
    error = Signal(str, str)         # file_path, error_msg

class ThumbnailWorker(QRunnable):
    """
    Worker for decoding images in background / 在后台解码图像的工人
    """
    def __init__(self, file_path: str, target_size: QSize):
        super().__init__()
        self.file_path = file_path
        self.target_size = target_size
        self.signals = ThumbnailSignals()

    def run(self):
        try:
            reader = QImageReader(self.file_path)
            reader.setAutoTransform(True)
            reader.setAllocationLimit(2048) # Allow 2GB RAM for large TIFFs
            
            if not reader.canRead():
                self.signals.error.emit(self.file_path, "Cannot read image")
                return

            # High-quality two-step scaling: 
            # 1. Hardware/Loader-level scaling to 2x target for pixel redundancy
            # 1. 硬件/加载器层级缩放到目标的 2 倍，以保留像素冗余
            image_size = reader.size()
            if image_size.isValid():
                oversample_size = self.target_size * 2
                image_size.scale(oversample_size, Qt.AspectRatioMode.KeepAspectRatio)
                reader.setScaledSize(image_size)
            
            image = reader.read()
            if image.isNull():
                self.signals.error.emit(self.file_path, "Decoded image is null")
                return
            
            # Additional high-quality smooth scaling for final presentation
            # 为最终呈现提供额外的高质量平滑缩放
            if image.width() > self.target_size.width() or image.height() > self.target_size.height():
                image = image.scaled(self.target_size, Qt.AspectRatioMode.KeepAspectRatio, 
                                   Qt.TransformationMode.SmoothTransformation)
            
            pixmap = QPixmap.fromImage(image)
            self.signals.finished.emit(self.file_path, pixmap)
            
        except Exception as e:
            logger.error(f"Error loading thumbnail for {self.file_path}: {e}")
            self.signals.error.emit(self.file_path, str(e))
