#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asynchronous thumbnail loader using thread pool to avoid UI blocking
使用线程池的异步缩略图加载器，避免 UI 阻塞
"""

from PySide6.QtCore import QObject, QRunnable, Signal, QSize, Qt
from PySide6.QtGui import QImageReader, QPixmap, QImage
import logging
import time

logger = logging.getLogger('DataPrism.ThumbnailWorker')

class ThumbnailSignals(QObject):
    """Signals for thumbnail loading / 缩略图加载信号"""
    finished = Signal(str, QImage)  # file_path, image
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
        start_t = time.time()
        try:
            reader = QImageReader(self.file_path)
            reader.setAutoTransform(True)
            # Reduced to 512MB to avoid OOM/thrashing while still supporting large files
            reader.setAllocationLimit(512) 
            
            if not reader.canRead():
                logger.error(f"Cannot read: {self.file_path}")
                self.signals.error.emit(self.file_path, "Cannot read image")
                return

            image_size = reader.size()
            if image_size.isValid():
                if image_size.width() > self.target_size.width() or image_size.height() > self.target_size.height():
                    scale_size = image_size.scaled(self.target_size, Qt.AspectRatioMode.KeepAspectRatio)
                    reader.setScaledSize(scale_size)
            
            # Decoding happens here
            image = reader.read()
            if image.isNull():
                self.signals.error.emit(self.file_path, "Decoded image is null")
                return
            
            # Post-decode smooth scaling if setScaledSize wasn't perfect or supported
            if image.width() > self.target_size.width() or image.height() > self.target_size.height():
                image = image.scaled(self.target_size, Qt.AspectRatioMode.KeepAspectRatio, 
                                   Qt.TransformationMode.SmoothTransformation)
            
            duration = (time.time() - start_t) * 1000
            logger.debug(f"Thumbnail decoded in {duration:.1f}ms: {self.file_path}")
            
            self.signals.finished.emit(self.file_path, image)
            
        except Exception as e:
            logger.error(f"Error loading thumbnail for {self.file_path}: {e}")
            self.signals.error.emit(self.file_path, str(e))
