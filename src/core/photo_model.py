#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data model for managing image metadata with caching
用于管理带缓存的图像元数据的数据模型
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QPixmap, QColor, QPainter, QBrush
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import re
import src.utils.gps_utils as gps_utils

from src.utils.i18n import tr
from src.utils.validators import MetadataValidator

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
    
    # Extended metadata fields / 扩展元数据字段
    aperture: Optional[str] = None  # e.g., "2.8"
    shutter_speed: Optional[str] = None  # e.g., "1/125"
    iso: Optional[str] = None  # e.g., "400"
    film_stock: Optional[str] = None  # e.g., "Kodak Portra 400"
    focal_length: Optional[str] = None  # e.g., "80mm"
    location: Optional[str] = None  # e.g., "Tokyo, JP"
    serial_number: Optional[str] = None


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
    # Column definitions
    # 列定义
    COLUMNS = ["File", "C-Make", "C-Model", "L-Make", "L-Model", "Aperture", "Shutter", "ISO", "Film Stock", "Location", "Date", "Status"]
    
    # Signal emitted when data changes and needs to be written to EXIF
    # 当数据改变且需要写入 EXIF 时发出的信号
    dataChangedForWrite = Signal(str, dict) # file_path, exif_data
    
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
            return tr(self.COLUMNS[section])
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return item flags / 返回项目标志"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        col = index.column()
        # Columns that can be edited: C-Make(1) to Date(10)
        # 可编辑的列：相机品牌(1) 到 日期(10)
        if 1 <= col <= 10:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """Set data for given index / 为给定索引设置数据"""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        col = index.column()
        photo = self.photos[row]
        
        # New value to write / 要写入的新值
        new_value = str(value).strip()
        
        # Mapping columns to EXIF tags and PhotoItem attributes
        # 将列映射到 EXIF 标签和 PhotoItem 属性
        exif_tag = None
        attr_name = None
        
        try:
            if col == 1: # C-Make
                exif_tag = "Make"
                photo.exif_data["Make"] = new_value
            elif col == 2: # C-Model
                validated = MetadataValidator.validate_camera_model(new_value)
                exif_tag = "Model"
                photo.exif_data["Model"] = validated
            elif col == 3: # L-Make
                exif_tag = "LensMake"
                photo.exif_data["LensMake"] = new_value
            elif col == 4: # L-Model
                validated = MetadataValidator.validate_lens_model(new_value)
                exif_tag = "LensModel"
                photo.exif_data["LensModel"] = validated
            elif col == 5: # Aperture
                validated = MetadataValidator.validate_aperture(new_value)
                # Clean prefix for EXIF
                exif_val = validated.replace('f/', '').replace('F/', '').replace('f', '').replace('F', '')
                exif_tag = "FNumber"
                photo.aperture = validated
            elif col == 6: # Shutter
                validated = MetadataValidator.validate_shutter_speed(new_value)
                exif_tag = "ExposureTime"
                photo.shutter_speed = validated
            elif col == 7: # ISO
                validated = MetadataValidator.validate_iso(new_value)
                exif_tag = "ISO"
                photo.iso = str(validated)
            elif col == 8: # Film
                # Write to both Film and UserComment for best compatibility
                photo.film_stock = new_value
                # Update memory immediately / 立即更新内存
                self.dataChangedForWrite.emit(photo.file_path, {
                    "Film": new_value,
                    "UserComment": f"Film: {new_value}",
                    "ImageDescription": new_value
                })
                self.mark_modified(photo.file_path)
                self.dataChanged.emit(index, index)
                return True
            elif col == 9: # Location
                # Handle GPS or description
                gps_parsed = gps_utils.parse_gps_to_exif(new_value)
                if gps_parsed:
                    lat, lat_ref, lon, lon_ref = gps_parsed
                    exif_data = {
                        "GPSLatitude": lat,
                        "GPSLatitudeRef": lat_ref,
                        "GPSLongitude": lon,
                        "GPSLongitudeRef": lon_ref
                    }
                    photo.location = new_value
                    self.dataChangedForWrite.emit(photo.file_path, exif_data)
                    self.mark_modified(photo.file_path)
                    self.dataChanged.emit(index, index)
                    return True
                else:
                    # Fallback to ImageDescription if not GPS
                    exif_tag = "ImageDescription"
                    photo.location = new_value
            elif col == 10: # Date
                validated = MetadataValidator.validate_datetime(new_value)
                exif_tag = "DateTimeOriginal"
                # Also update CreateDate and ModifyDate
                self.dataChangedForWrite.emit(photo.file_path, {
                    "DateTimeOriginal": validated,
                    "CreateDate": validated,
                    "ModifyDate": validated
                })
                self.mark_modified(photo.file_path)
                self.dataChanged.emit(index, index)
                return True
        except ValueError as e:
            logger.warning(f"Validation failed for column {col}: {e}")
            # If validation fails, we can still try to write raw value or reject
            if col == 5: # Aperture
                exif_tag = "FNumber"
                photo.aperture = new_value.replace('f/', '').replace('F/', '').replace('f', '').replace('F', '')
            elif col == 6: # Shutter
                exif_tag = "ExposureTime"
                photo.shutter_speed = new_value
            elif col == 7: # ISO
                exif_tag = "ISO"
                photo.iso = new_value
            elif col == 10: # Date
                exif_tag = "DateTimeOriginal"
                photo.exif_data["DateTimeOriginal"] = new_value.replace('-', ':').replace('/', ':')
            elif col == 1: # C-Make
                exif_tag = "Make"
                photo.exif_data["Make"] = new_value
            elif col == 2: # C-Model
                exif_tag = "Model"
                photo.exif_data["Model"] = new_value
            elif col == 3: # L-Make
                exif_tag = "LensMake"
                photo.exif_data["LensMake"] = new_value
            elif col == 4: # L-Model
                exif_tag = "LensModel"
                photo.exif_data["LensModel"] = new_value
            else:
                return False

        if exif_tag:
            self.dataChangedForWrite.emit(photo.file_path, {exif_tag: new_value})
            self.mark_modified(photo.file_path)
            self.dataChanged.emit(index, index)
            return True

        return False
    
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
        
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == 0:  # File name
                return photo.file_name
            elif col == 1:  # C-Make
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.exif_data.get("Make", "")
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 2:  # C-Model
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.exif_data.get("Model", "")
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 3:  # L-Make
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.exif_data.get("LensMake", "")
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 4:  # L-Model
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.exif_data.get("LensModel", "")
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 5:  # Aperture
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                if photo.aperture:
                    return (f"f/{photo.aperture}" if role == Qt.ItemDataRole.DisplayRole else photo.aperture)
                return "--" if role == Qt.ItemDataRole.DisplayRole else ""
            elif col == 6:  # Shutter
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                if photo.shutter_speed:
                    return (f"{photo.shutter_speed}s" if role == Qt.ItemDataRole.DisplayRole else photo.shutter_speed)
                return "--" if role == Qt.ItemDataRole.DisplayRole else ""
            elif col == 7:  # ISO
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.iso or ""
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 8:  # Film
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.film_stock or ""
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 9:  # Location
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.location or ""
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 10:  # Date
                if photo.exif_data is None:
                    return tr("Loading...") if role == Qt.ItemDataRole.DisplayRole else ""
                val = photo.exif_data.get("DateTimeOriginal", "")
                return val if val else ("--" if role == Qt.ItemDataRole.DisplayRole else "")
            elif col == 11:  # Status
                # Return empty string - we'll show dot in DecorationRole
                return ""
        
        elif role == Qt.ItemDataRole.DecorationRole and col == 11:
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
        
        elif role == Qt.ItemDataRole.ToolTipRole and col == 9:
            # Tooltip for status column
            status_key = "modified" if photo.is_modified else photo.status
            tooltip_map = {
                "pending": tr("Pending EXIF read"),
                "loaded": tr("EXIF loaded"),
                "modified": tr("Modified"),
                "error": tr("Error loading EXIF")
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
                
                # Parse and cache exposure data / 解析并缓存曝光数据
                self._parse_exposure_data(photo, exif_data)
                
                # Notify view of data change
                # 通知视图数据已更改
                index = self.index(idx, 0)
                self.dataChanged.emit(index, self.index(idx, len(self.COLUMNS) - 1))
                break
    
    def _parse_exposure_data(self, photo: PhotoItem, exif_data: Dict[str, Any]) -> None:
        """
        Parse and format exposure data from EXIF
        从 EXIF 解析并格式化曝光数据
        """
        # Aperture / 光圈
        if "FNumber" in exif_data:
            try:
                f_num = float(exif_data["FNumber"])
                photo.aperture = f"{f_num:.1f}"
            except:
                photo.aperture = str(exif_data["FNumber"])
        elif "Aperture" in exif_data:
            photo.aperture = str(exif_data["Aperture"])
        
        # Shutter Speed / 快门速度
        if "ExposureTime" in exif_data:
            exp_time = exif_data["ExposureTime"]
            if isinstance(exp_time, str) and "/" in exp_time:
                photo.shutter_speed = exp_time
            else:
                try:
                    exp_float = float(exp_time)
                    if exp_float >= 1:
                        photo.shutter_speed = f"{exp_float:.1f}"
                    else:
                        # Convert to fraction
                        denom = int(1 / exp_float)
                        photo.shutter_speed = f"1/{denom}"
                except:
                    photo.shutter_speed = str(exp_time)
        elif "ShutterSpeed" in exif_data:
            photo.shutter_speed = str(exif_data["ShutterSpeed"])
        
        # ISO
        if "ISO" in exif_data:
            photo.iso = str(exif_data["ISO"])
        
        # Focal Length / 焦距
        if "FocalLength" in exif_data:
            focal = exif_data["FocalLength"]
            if isinstance(focal, str) and "mm" in focal:
                photo.focal_length = focal
            else:
                try:
                    focal_float = float(focal)
                    photo.focal_length = f"{focal_float:.0f}mm"
                except:
                    photo.focal_length = str(focal)
        
        # Serial Number / 序列号
        if "SerialNumber" in exif_data:
            photo.serial_number = str(exif_data["SerialNumber"])
        
        
        # Film Stock & Location (Film / ImageDescription / UserComment / GPS)
        # 胶卷型号和位置（Film / ImageDescription / UserComment / GPS）
        
        # First, try to read from Film field (standard EXIF field)
        # 首先尝试从 Film 字段读取（标准 EXIF 字段）
        if "Film" in exif_data:
            photo.film_stock = str(exif_data["Film"])
        
        user_comment = str(exif_data.get("UserComment", "")) if exif_data else ""

        # Prefer GPS coordinates when available (standardized DMS string)
        gps_lat = exif_data.get("GPSLatitude") if exif_data else None
        gps_lon = exif_data.get("GPSLongitude") if exif_data else None
        gps_lat_ref = exif_data.get("GPSLatitudeRef") if exif_data else None
        gps_lon_ref = exif_data.get("GPSLongitudeRef") if exif_data else None
        gps_formatted = gps_utils.format_gps_pair(gps_lat, gps_lat_ref, gps_lon, gps_lon_ref)
        if gps_formatted:
            photo.location = gps_formatted

        if "ImageDescription" in exif_data:
            desc = str(exif_data["ImageDescription"])
            # Keep description as fallback if GPS missing
            if not photo.location and desc:
                photo.location = desc
            
            # If nothing else found, ImageDescription is likely the film stock in this workflow
            # 如果没找到其他信息，ImageDescription 很有可能是这个流中的胶卷型号
            photo.film_stock = photo.film_stock or desc

        # Parse combined user comment patterns like "Film: X | Location: Y | note"
        if user_comment:
            parts = [p.strip() for p in user_comment.split("|") if p.strip()]
            for part in parts:
                if part.lower().startswith("film:"):
                    photo.film_stock = part.split(":", 1)[1].strip() or photo.film_stock
                elif part.lower().startswith("location:"):
                    # Prefer explicit location from comment over description
                    raw_loc = part.split(":", 1)[1].strip()
                    # Improve: try to parse it as standard GPS string if it looks like one
                    # 改进：如果看起来像 GPS 字符串，尝试将其解析为标准 GPS 字符串
                    photo.location = gps_utils.parse_location_string(raw_loc) or raw_loc or photo.location
            # Fallback: if nothing parsed, but comment exists, keep as film if it looks like a film name
            if not photo.film_stock and any(key in user_comment.lower() for key in ["kodak", "fuji", "ilford", "portra", "tri-x"]):
                photo.film_stock = user_comment

        # If still no location, keep any GPS fragments we have (compact)
        if not photo.location and gps_lat and gps_lon:
            fallback = gps_utils.format_gps_pair(gps_lat, gps_lat_ref, gps_lon, gps_lon_ref, strict=False)
            photo.location = fallback or f"{gps_lat}, {gps_lon}"
    
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


