#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON parser for Lightme/Logbook film log files
Lightme/Logbook 胶片记录文件的 JSON 解析器
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FilmLogEntry:
    """
    Single film log entry from JSON
    JSON 中的单条胶片记录
    """
    # Core fields / 核心字段
    timestamp: Optional[datetime] = None  # Shot time / 拍摄时间
    frame_number: Optional[int] = None  # Frame number on roll / 胶卷帧编号
    
    # Camera & Lens / 相机与镜头
    camera: Optional[str] = None  # e.g., "Hasselblad 503CX"
    lens: Optional[str] = None  # e.g., "Carl Zeiss Planar 80mm f/2.8"
    
    # Exposure / 曝光参数
    aperture: Optional[str] = None  # e.g., "2.8"
    shutter_speed: Optional[str] = None  # e.g., "1/125"
    iso: Optional[str] = None  # e.g., "400"
    
    # Film Stock / 胶片型号
    film_stock: Optional[str] = None  # e.g., "Kodak Portra 400"
    
    # Optional fields / 可选字段
    focal_length: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    
    # Raw JSON for custom fields / 原始 JSON 用于自定义字段
    raw_data: Dict[str, Any] = None


class FilmLogParser:
    """
    Parser for Lightme/Logbook JSON exports
    Lightme/Logbook JSON 导出文件解析器
    """
    
    def __init__(self):
        """Initialize parser / 初始化解析器"""
        self.entries: List[FilmLogEntry] = []
    
    def parse_file(self, file_path: str) -> List[FilmLogEntry]:
        """
        Parse JSON file and extract film log entries
        解析 JSON 文件并提取胶片记录
        
        Args:
            file_path: Path to JSON file / JSON 文件路径
        
        Returns:
            List of FilmLogEntry objects / FilmLogEntry 对象列表
        
        Raises:
            ValueError: If JSON format is invalid / 如果 JSON 格式无效
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Try different JSON structures / 尝试不同的 JSON 结构
            if isinstance(data, list):
                # Direct array of entries / 直接的条目数组
                self.entries = [self._parse_entry(entry) for entry in data]
            elif isinstance(data, dict):
                # Wrapped in object / 包装在对象中
                if 'entries' in data:
                    self.entries = [self._parse_entry(entry) for entry in data['entries']]
                elif 'frames' in data:
                    self.entries = [self._parse_entry(entry) for entry in data['frames']]
                elif 'shots' in data:
                    self.entries = [self._parse_entry(entry) for entry in data['shots']]
                else:
                    raise ValueError("Unknown JSON structure")
            else:
                raise ValueError("JSON must be array or object")
            
            logger.info(f"Parsed {len(self.entries)} entries from {file_path}")
            return self.entries
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
    
    def _parse_entry(self, entry: Dict[str, Any]) -> FilmLogEntry:
        """
        Parse single JSON entry
        解析单个 JSON 条目
        
        Args:
            entry: JSON entry dictionary / JSON 条目字典
        
        Returns:
            FilmLogEntry object / FilmLogEntry 对象
        """
        log_entry = FilmLogEntry(raw_data=entry)
        
        # Parse timestamp / 解析时间戳
        timestamp_fields = ['timestamp', 'time', 'date', 'datetime', 'shot_time']
        for field in timestamp_fields:
            if field in entry and entry[field]:
                try:
                    # Try multiple datetime formats / 尝试多种日期时间格式
                    ts_str = entry[field]
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', 
                                '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                        try:
                            log_entry.timestamp = datetime.strptime(ts_str, fmt)
                            break
                        except:
                            continue
                    if log_entry.timestamp is None and isinstance(ts_str, (int, float)):
                        # Unix timestamp / Unix 时间戳
                        log_entry.timestamp = datetime.fromtimestamp(ts_str)
                except Exception as e:
                    logger.warning(f"Could not parse timestamp '{entry[field]}': {e}")
                break
        
        # Parse frame number / 解析帧编号
        frame_fields = ['frame', 'frame_number', 'number', 'shot_number']
        for field in frame_fields:
            if field in entry:
                try:
                    log_entry.frame_number = int(entry[field])
                except:
                    pass
                break
        
        # Parse camera / 解析相机
        camera_fields = ['camera', 'body', 'camera_body', 'camera_model']
        for field in camera_fields:
            if field in entry and entry[field]:
                log_entry.camera = str(entry[field])
                break
        
        # Parse lens / 解析镜头
        lens_fields = ['lens', 'lens_model', 'optic']
        for field in lens_fields:
            if field in entry and entry[field]:
                log_entry.lens = str(entry[field])
                break
        
        # Parse exposure / 解析曝光
        if 'aperture' in entry:
            log_entry.aperture = str(entry['aperture']).replace('f/', '').replace('F', '')
        elif 'f_number' in entry:
            log_entry.aperture = str(entry['f_number'])
        
        if 'shutter_speed' in entry:
            log_entry.shutter_speed = str(entry['shutter_speed'])
        elif 'shutter' in entry:
            log_entry.shutter_speed = str(entry['shutter'])
        elif 'exposure_time' in entry:
            log_entry.shutter_speed = str(entry['exposure_time'])
        
        if 'iso' in entry:
            log_entry.iso = str(entry['iso'])
        elif 'film_speed' in entry:
            log_entry.iso = str(entry['film_speed'])
        
        # Parse film stock / 解析胶片型号
        film_fields = ['film_stock', 'film', 'film_type', 'emulsion']
        for field in film_fields:
            if field in entry and entry[field]:
                log_entry.film_stock = str(entry[field])
                break
        
        # Parse focal length / 解析焦距
        if 'focal_length' in entry:
            log_entry.focal_length = str(entry['focal_length'])
        
        # Parse notes / 解析备注
        if 'notes' in entry:
            log_entry.notes = str(entry['notes'])
        elif 'comment' in entry:
            log_entry.notes = str(entry['comment'])
        
        # Parse location / 解析位置
        if 'location' in entry:
            log_entry.location = str(entry['location'])
        
        return log_entry
    
    def get_entries(self) -> List[FilmLogEntry]:
        """Get parsed entries / 获取已解析的条目"""
        return self.entries
