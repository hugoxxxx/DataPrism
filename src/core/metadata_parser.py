#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal metadata parser for JSON/CSV/TXT formats
通用元数据解析器，支持 JSON/CSV/TXT 格式
"""

import json
import re
import csv
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MetadataEntry:
    """
    Single metadata entry / 单条元数据条目
    """
    camera: Optional[str] = None  # Camera model / 相机型号
    lens: Optional[str] = None  # Lens model / 镜头型号
    aperture: Optional[str] = None  # f/number / 光圈数值
    shutter_speed: Optional[str] = None  # e.g. "1/125" / 快门速度
    iso: Optional[str] = None  # ISO value / ISO 值
    film_stock: Optional[str] = None  # e.g. "Kodak Portra 400" / 胶片型号
    focal_length: Optional[str] = None  # e.g. "50mm" / 焦距
    timestamp: Optional[datetime] = None  # Shot timestamp / 拍摄时间
    shot_date: Optional[str] = None  # Shot date string / 拍摄日期
    location: Optional[str] = None  # Geographic location / 地理位置
    frame_number: Optional[int] = None  # Frame/shot number / 帧编号
    notes: Optional[str] = None  # Additional notes / 附加备注


class MetadataParser:
    """
    Universal parser for JSON/CSV/TXT metadata files
    JSON/CSV/TXT 元数据文件的通用解析器
    """
    
    def __init__(self):
        """Initialize parser / 初始化解析器"""
        self.entries: List[MetadataEntry] = []
    
    def parse_file(self, file_path: str) -> List[MetadataEntry]:
        """
        Parse metadata file (auto-detect format)
        解析元数据文件（自动检测格式）
        
        Args:
            file_path: Path to metadata file / 元数据文件路径
        
        Returns:
            List of MetadataEntry / MetadataEntry 列表
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.json':
            return self._parse_json(file_path)
        elif file_ext == '.csv':
            return self._parse_csv(file_path)
        elif file_ext == '.txt':
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
    
    def _parse_json(self, file_path: str) -> List[MetadataEntry]:
        """
        Parse JSON metadata file / 解析 JSON 元数据文件
        
        Supports Lightme/Logbook JSON exports
        支持 Lightme/Logbook JSON 导出格式
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.entries = []
            
            # Handle array or object wrapper / 处理数组或对象包装
            if isinstance(data, list):
                entries_data = data
            elif isinstance(data, dict):
                # Try common wrapper keys / 尝试常见的包装键
                if 'entries' in data:
                    entries_data = data['entries']
                elif 'frames' in data:
                    entries_data = data['frames']
                elif 'shots' in data:
                    entries_data = data['shots']
                else:
                    raise ValueError("Unknown JSON structure")
            else:
                raise ValueError("JSON must be array or object")
            
            # Parse entries / 解析条目
            self.entries = [self._parse_entry(entry) for entry in entries_data]
            
            logger.info(f"Parsed {len(self.entries)} entries from JSON: {file_path}")
            return self.entries
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
    
    def _parse_csv(self, file_path: str) -> List[MetadataEntry]:
        """
        Parse CSV metadata file / 解析 CSV 元数据文件
        
        Expected format (header required):
        Camera,Lens,Aperture,Shutter,ISO,FilmStock,Notes
        Canon AE-1,50mm f/1.8,f/2.8,1/125,400,Kodak Portra 400,Portrait
        """
        try:
            self.entries = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if reader.fieldnames is None:
                    raise ValueError("CSV file is empty")
                
                # Map CSV headers to MetadataEntry fields / 映射 CSV 表头到 MetadataEntry 字段
                for row in reader:
                    entry = self._parse_csv_row(row)
                    self.entries.append(entry)
            
            logger.info(f"Parsed {len(self.entries)} entries from CSV: {file_path}")
            return self.entries
        
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise
    
    def _parse_csv_row(self, row: Dict[str, str]) -> MetadataEntry:
        """
        Parse a single CSV row / 解析单行 CSV
        """
        entry = MetadataEntry()
        
        # Field mapping / 字段映射（兼容多种列名）
        camera_fields = ['Camera', 'camera', 'Body', 'body', 'Model', 'model']
        lens_fields = ['Lens', 'lens', 'Lensmodel', 'lensmodel']
        aperture_fields = ['Aperture', 'aperture', 'FNumber', 'fnumber', 'f-stop']
        shutter_fields = ['Shutter', 'shutter', 'ExposureTime', 'exposuretime', 'Speed']
        iso_fields = ['ISO', 'iso', 'Sensitivity', 'sensitivity']
        film_fields = ['Film', 'film', 'FilmStock', 'filmstock', 'Emulsion']
        focal_fields = ['Focal', 'focal', 'FocalLength', 'focallength']
        notes_fields = ['Notes', 'notes', 'Comments', 'comments']
        
        # Try to extract fields / 尝试提取字段
        for field in camera_fields:
            if field in row and row[field]:
                entry.camera = row[field]
                break
        
        for field in lens_fields:
            if field in row and row[field]:
                entry.lens = row[field]
                break
        
        for field in aperture_fields:
            if field in row and row[field]:
                entry.aperture = row[field]
                break
        
        for field in shutter_fields:
            if field in row and row[field]:
                entry.shutter_speed = row[field]
                break
        
        for field in iso_fields:
            if field in row and row[field]:
                entry.iso = row[field]
                break
        
        for field in film_fields:
            if field in row and row[field]:
                entry.film_stock = row[field]
                break
        
        for field in focal_fields:
            if field in row and row[field]:
                entry.focal_length = row[field]
                break
        
        for field in notes_fields:
            if field in row and row[field]:
                entry.notes = row[field]
                break
        
        return entry
    
    def _parse_txt(self, file_path: str) -> List[MetadataEntry]:
        """
        Parse TXT metadata file / 解析 TXT 元数据文件
        
        Expected format (one record per line, fields separated by | or tab):
        Canon AE-1 | 50mm f/1.8 | f/2.8 | 1/125 | 400 | Kodak Portra 400 | Portrait
        or:
        Canon AE-1\t50mm f/1.8\tf/2.8\t1/125\t400\tKodak Portra 400\tPortrait
        """
        try:
            self.entries = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                # Try to split by | or tab / 尝试用 | 或 \t 分割
                if '|' in line:
                    fields = [f.strip() for f in line.split('|')]
                else:
                    fields = [f.strip() for f in line.split('\t')]
                
                entry = self._parse_txt_row(fields)
                self.entries.append(entry)
            
            logger.info(f"Parsed {len(self.entries)} entries from TXT: {file_path}")
            return self.entries
        
        except Exception as e:
            logger.error(f"Error parsing TXT: {e}")
            raise
    
    def _parse_txt_row(self, fields: List[str]) -> MetadataEntry:
        """
        Parse a single TXT row / 解析单行 TXT
        
        Expected field order: Camera, Lens, Aperture, Shutter, ISO, FilmStock, Notes
        预期字段顺序：相机、镜头、光圈、快门、ISO、胶片、备注
        """
        entry = MetadataEntry()
        
        # Assign fields based on position / 基于位置分配字段
        if len(fields) > 0:
            entry.camera = fields[0] or None
        if len(fields) > 1:
            entry.lens = fields[1] or None
        if len(fields) > 2:
            entry.aperture = fields[2] or None
        if len(fields) > 3:
            entry.shutter_speed = fields[3] or None
        if len(fields) > 4:
            entry.iso = fields[4] or None
        if len(fields) > 5:
            entry.film_stock = fields[5] or None
        if len(fields) > 6:
            entry.notes = fields[6] or None
        
        return entry
    
    def _parse_entry(self, entry: Dict[str, Any]) -> MetadataEntry:
        """
        Parse a single JSON entry / 解析单条 JSON 条目
        (Used for JSON parsing - same logic as json_parser.py)
        Supports both Lightme/Logbook and EXIF field names (Lightroom export)
        """
        metadata = MetadataEntry()
        
        # Field mapping with fallbacks / 字段映射和备选项
        # Support both Lightme format and EXIF field names (Lightroom, etc.)
        camera_fields = ['camera', 'body', 'camera_body', 'camera_model', 'Make', 'Model']
        lens_fields = ['lens', 'lensmodel', 'lens_model', 'LensModel', 'LensMake']
        aperture_fields = ['aperture', 'f_stop', 'f-stop', 'fnumber', 'FNumber', 'MaxApertureValue']
        shutter_fields = ['shutter_speed', 'shutter', 'exposure_time', 'exposuretime', 'ExposureTime']
        iso_fields = ['iso', 'sensitivity', 'ISO', 'ISOSpeed']
        film_fields = ['film', 'film_stock', 'filmstock', 'emulsion', 'Description', 'ReelName', 'SpectralSensitivity']
        focal_fields = ['focal_length', 'focallength', 'focal', 'FocalLength', 'FocalLengthIn35mmFormat']
        timestamp_fields = ['timestamp', 'date', 'time', 'datetime', 'DateTimeOriginal']
        shot_date_fields = ['shot_date', 'shot_date_str', 'date_string', 'DateString', 'DateTimeOriginal', 'DateTime', 'CreateDate', 'ModifyDate', 'SubSecDateTimeOriginal']
        location_fields = ['location', 'geo', 'gps', 'GPSInfo', 'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'GPSLatitudeRef', 'GPSLongitudeRef']
        frame_fields = ['frame', 'frame_number', 'number', 'shot_number', 'ImageNumber']
        notes_fields = ['notes', 'comments', 'comment', 'UserComment', 'Notes']
        
        # Extract fields / 提取字段
        for field in camera_fields:
            if field in entry and entry[field]:
                metadata.camera = str(entry[field])
                break
        
        for field in lens_fields:
            if field in entry and entry[field]:
                metadata.lens = str(entry[field])
                break
        
        for field in aperture_fields:
            if field in entry and entry[field]:
                value = entry[field]
                # Handle numeric aperture values (EXIF FNumber/MaxApertureValue) / 处理数字光圈值
                if isinstance(value, (int, float)):
                    metadata.aperture = f"f/{value}"
                else:
                    metadata.aperture = str(value)
                break
        
        for field in shutter_fields:
            if field in entry and entry[field]:
                value = entry[field]
                # Handle numeric shutter speed (EXIF ExposureTime as float) / 处理数字快门速度
                if isinstance(value, (int, float)):
                    if value < 1:
                        # Convert to fraction like 1/125 / 转换为 1/125 的格式
                        denom = round(1 / value)
                        metadata.shutter_speed = f"1/{denom}"
                    else:
                        metadata.shutter_speed = str(value)
                else:
                    metadata.shutter_speed = str(value)
                break
        
        for field in iso_fields:
            if field in entry and entry[field]:
                value = entry[field]
                # Handle numeric ISO values / 处理数字 ISO 值
                if isinstance(value, (int, float)):
                    metadata.iso = str(int(value))
                else:
                    metadata.iso = str(value)
                break
        
        for field in film_fields:
            if field in entry and entry[field]:
                metadata.film_stock = str(entry[field])
                break
        
        for field in focal_fields:
            if field in entry and entry[field]:
                value = entry[field]
                # Handle numeric focal length (EXIF FocalLength) / 处理数字焦距
                if isinstance(value, (int, float)):
                    metadata.focal_length = f"{int(value)}mm"
                else:
                    metadata.focal_length = str(value)
                break
        
        # Parse timestamp / 解析时间戳
        for field in timestamp_fields:
            if field in entry and entry[field]:
                try:
                    ts_str = entry[field]
                    # Try multiple formats / 尝试多种格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y:%m:%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
                               '%Y-%m-%d', '%Y/%m/%d', '%Y:%m:%d']:
                        try:
                            metadata.timestamp = datetime.strptime(ts_str, fmt)
                            break
                        except:
                            continue
                except Exception as e:
                    logger.warning(f"Could not parse timestamp '{entry[field]}': {e}")
                break
        
        # Parse shot date string / 解析拍摄日期字符串
        for field in shot_date_fields:
            if field in entry and entry[field]:
                metadata.shot_date = str(entry[field]).strip()
                break
        
        # Parse location / 解析地理位置（优先拼接 GPS 经纬度并标准化）
        gps_lat = entry.get('GPSLatitude')
        gps_lon = entry.get('GPSLongitude')
        gps_lat_ref = entry.get('GPSLatitudeRef')
        gps_lon_ref = entry.get('GPSLongitudeRef')
        if gps_lat and gps_lon:
            formatted = self._format_gps_pair(gps_lat, gps_lat_ref, gps_lon, gps_lon_ref)
            if formatted:
                metadata.location = formatted
        if not metadata.location:
            # Fallback: first available location-like field
            for field in location_fields:
                if field in entry and entry[field]:
                    value = entry[field]
                    if isinstance(value, dict):
                        metadata.location = ', '.join(f"{k}:{v}" for k, v in value.items())
                    elif isinstance(value, (list, tuple)):
                        metadata.location = ', '.join(str(x) for x in value)
                    else:
                        metadata.location = str(value).strip()
                    break
        
        # Parse frame number / 解析帧编号
        for field in frame_fields:
            if field in entry and entry[field]:
                try:
                    metadata.frame_number = int(entry[field])
                except:
                    pass
                break
        
        # Extract notes / 提取备注
        for field in notes_fields:
            if field in entry and entry[field]:
                metadata.notes = str(entry[field])
                break
        
        return metadata
    
    def get_entries(self) -> List[MetadataEntry]:
        """Get parsed entries / 获取已解析的条目"""
        return self.entries

    @staticmethod
    def _format_gps_pair(lat, lat_ref, lon, lon_ref) -> Optional[str]:
        """Format GPS lat/lon into standardized DMS string without duplicated directions."""

        def _parse_coord(val, ref_hint):
            if val is None:
                return None
            s = str(val).strip()
            # Try DMS with optional direction letter
            m = re.search(r"([0-9.]+)[^0-9]+([0-9.]+)[^0-9]+([0-9.]+)\s*([NSEW])?", s, re.IGNORECASE)
            if m:
                deg, minute, sec, suffix = m.groups()
                suffix = suffix or (ref_hint[:1] if ref_hint else '')
                return float(deg), float(minute), float(sec), suffix.upper() if suffix else None
            # Try plain decimal
            try:
                dec = float(s)
                suffix = ref_hint[:1].upper() if ref_hint else None
                return dec, None, None, suffix
            except:
                return None

        lat_parsed = _parse_coord(lat, str(lat_ref) if lat_ref else None)
        lon_parsed = _parse_coord(lon, str(lon_ref) if lon_ref else None)
        if not lat_parsed or not lon_parsed:
            return None

        def _fmt(parsed):
            deg, minute, sec, suffix = parsed
            if minute is None or sec is None:
                # decimal
                sign = suffix or ''
                return f"{deg:.6f}{sign}"
            suf = suffix or ''
            return f"{deg:.0f}°{minute:.0f}'{sec:.2f}\"{suf}"

        return f"{_fmt(lat_parsed)}, {_fmt(lon_parsed)}"
