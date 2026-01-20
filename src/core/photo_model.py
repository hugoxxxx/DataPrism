#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data model for managing image metadata with caching
用于管理带缓存的图像元数据的数据模型
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QPixmap, QColor, QPainter, QBrush
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PhotoItem:
    """
    Data structure for a single photo with metadata
    单个照片及其元数据的数据结构
    """
    file_path: str
    file_name: str
    exif_data: Dict[str, Any] = None  # Cached EXIF data
    thumbnail: Optional[QPixmap] = None  # Cached thumbnail
    status: str = "pending"  # Status: pending, loaded, modified, error
    is_modified: bool = False


class PhotoDataModel(QAbstractTableModel):
    """
    Model for managing photo list with efficient data handling
    用于高效管理照片列表的模型
    
    Features:
    - Lazy loading of EXIF data (on demand) / 延迟加载 EXIF 数据
    - Thumbnail caching / 缩略图缓存
    - Batch operations support / 批操作支持
    - Change tracking / 变更追踪
    """
    
    # Column definitions
    # 列定义
    COLUMNS = ["File", "Camera", "Lens", "Date", "Status"]
    
    def __init__(self, parent=None):
        """Initialize model / 初始化模型"""
        super().__init__(parent)
        self.photos: List[PhotoItem] = []
        self.exif_cache: Dict[str, Dict[str, Any]] = {}  # Cache for EXIF data
        self.modified_items: set = set()  # Track which items have changed
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of rows / 返回行数"""
        return len(self.photos)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns / 返回列数"""
        return len(self.COLUMNS)
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        """Return header data / 返回标题数据"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """
        Return data for given index
        返回给定索引的数据
        
        Implements lazy loading: only load EXIF when cell is displayed
        实现延迟加载：仅在显示单元格时加载 EXIF
        """
        if not index.isValid():
            return None
        
        photo = self.photos[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:  # File name
                return photo.file_name
            elif col == 1:  # Camera
                if photo.exif_data is None:
                    return "Loading..."  # Trigger lazy load
                return photo.exif_data.get("Model", "N/A")
            elif col == 2:  # Lens
                if photo.exif_data is None:
                    return "Loading..."
                return photo.exif_data.get("LensModel", "N/A")
            elif col == 3:  # Date
                if photo.exif_data is None:
                    return "Loading..."
                return photo.exif_data.get("DateTimeOriginal", "N/A")
            elif col == 4:  # Status
                # Return empty string - we'll show dot in DecorationRole
                return ""
        
        elif role == Qt.ItemDataRole.DecorationRole and col == 4:
            # Show colored dot based on status
            color_map = {
                "pending": QColor("#999999"),  # Gray
                "loaded": QColor("#34c759"),   # Green
                "modified": QColor("#007aff"), # Blue
                "error": QColor("#ff3b30")     # Red
            }
            status_key = "modified" if photo.is_modified else photo.status
            color = color_map.get(status_key, QColor("#999999"))
            
            # Create a small colored circle pixmap
            pixmap = QPixmap(12, 12)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, 8, 8)
            painter.end()
            return pixmap
        
        elif role == Qt.ItemDataRole.ToolTipRole and col == 4:
            # Tooltip for status column
            status_key = "modified" if photo.is_modified else photo.status
            tooltip_map = {
                "pending": "Pending EXIF read",
                "loaded": "EXIF loaded",
                "modified": "Modified",
                "error": "Error loading EXIF"
            }
            return tooltip_map.get(status_key, "Unknown")
        
        return None
    
    def add_photos(self, file_paths: List[str]) -> None:
        """
        Add photos to model
        将照片添加到模型
        
        Args:
            file_paths: List of image file paths / 图像文件路径列表
        """
        start_row = len(self.photos)
        self.beginInsertRows(QModelIndex(), start_row, start_row + len(file_paths) - 1)
        
        for file_path in file_paths:
            photo = PhotoItem(
                file_path=file_path,
                file_name=Path(file_path).name,
                status="pending"
            )
            self.photos.append(photo)
        
        self.endInsertRows()
    
    def set_exif_data(self, file_path: str, exif_data: Dict[str, Any]) -> None:
        """
        Cache EXIF data for a file (called by worker thread)
        为文件缓存 EXIF 数据（由工作线程调用）
        
        Args:
            file_path: Path to image file / 图像文件路径
            exif_data: EXIF metadata dictionary / EXIF 元数据字典
        """
        # Find and update the photo item
        # 查找并更新照片项
        for idx, photo in enumerate(self.photos):
            if photo.file_path == file_path:
                photo.exif_data = exif_data
                photo.status = "loaded"
                
                # Notify view of data change
                # 通知视图数据已更改
                index = self.index(idx, 0)
                self.dataChanged.emit(index, self.index(idx, len(self.COLUMNS) - 1))
                break
    
    def mark_modified(self, file_path: str) -> None:
        """
        Mark file as having modifications
        标记文件有修改
        
        Args:
            file_path: Path to image file / 图像文件路径
        """
        for idx, photo in enumerate(self.photos):
            if photo.file_path == file_path:
                photo.is_modified = True
                self.modified_items.add(file_path)
                
                index = self.index(idx, len(self.COLUMNS) - 1)
                self.dataChanged.emit(index, index)
                break
    
    def get_modified_files(self) -> List[str]:
        """Get list of modified files / 获取修改过的文件列表"""
        return list(self.modified_items)
    
    def clear(self) -> None:
        """Clear all photos / 清空所有照片"""
        self.beginResetModel()
        self.photos.clear()
        self.exif_cache.clear()
        self.modified_items.clear()
        self.endResetModel()
