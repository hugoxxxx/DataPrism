#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV to EXIF data converter
CSV 到 EXIF 数据转换器
"""

from typing import Dict, List, Optional
from src.core.metadata_parser import MetadataEntry


class CSVConverter:
    """
    Convert CSV data to EXIF metadata
    将 CSV 数据转换为 EXIF 元数据
    """
    
    @staticmethod
    def convert_rows(csv_rows: List[Dict[str, str]], 
                    mappings: Dict, 
                    photos: List) -> List[MetadataEntry]:
        """
        Convert CSV rows to MetadataEntry list, matching by row order
        将 CSV 行转换为 MetadataEntry 列表，按行序号匹配照片
        
        Args:
            csv_rows: CSV data rows / CSV 数据行
            mappings: Field mappings from dialog / 字段映射关系
            photos: Photo list (PhotoItem) / 照片列表
        
        Returns:
            List of MetadataEntry / MetadataEntry 列表
        """
        metadata_entries = []
        
        for i, row in enumerate(csv_rows):
            # Match by row order
            # 按行序号匹配照片
            if i >= len(photos):
                break  # CSV rows exceed photo count
            
            photo = photos[i]
            entry = MetadataEntry()
            
            # Set file name for matching
            # 设置文件名用于匹配
            entry.file_name = photo.file_name
            
            # Convert fields
            # 转换字段
            for csv_col, exif_field in mappings['fields'].items():
                value = row.get(csv_col, '').strip()
                if not value:
                    continue
                
                if exif_field == 'DateTimeOriginal':
                    # Date format conversion: 2026-01-23 → 2026:01:23
                    # 日期格式转换
                    entry.shot_date = CSVConverter._convert_datetime(value)
                
                elif exif_field == 'GPSLatitude':
                    # Decimal → DMS, generate 2 EXIF fields
                    # 十进制 → DMS，生成 2 个 EXIF 字段
                    lat_ref = mappings['gps_refs'].get(csv_col, 'N')
                    lat_dms = CSVConverter._decimal_to_dms_display(
                        float(value), 'lat', lat_ref
                    )
                    # Store in location field for display
                    # 存储在 location 字段用于显示
                    if not entry.location:
                        entry.location = lat_dms
                    else:
                        entry.location = f"{lat_dms}, {entry.location}"
                
                elif exif_field == 'GPSLongitude':
                    # Decimal → DMS
                    lon_ref = mappings['gps_refs'].get(csv_col, 'E')
                    lon_dms = CSVConverter._decimal_to_dms_display(
                        float(value), 'lon', lon_ref
                    )
                    # Append to location
                    if not entry.location:
                        entry.location = lon_dms
                    else:
                        entry.location = f"{entry.location}, {lon_dms}"
                
                elif exif_field == 'FNumber':
                    entry.aperture = value
                
                elif exif_field == 'ExposureTime':
                    entry.shutter_speed = value
                
                elif exif_field == 'ISO':
                    entry.iso = value
                
                elif exif_field == 'FocalLength':
                    entry.focal_length = value
                
                elif exif_field == 'FocalLengthIn35mmFormat':
                    entry.focal_length_35mm = value
                
                elif exif_field == 'Film':
                    entry.film_stock = value
                
                elif exif_field == 'Make':
                    entry.camera_make = value
                
                elif exif_field == 'Model':
                    entry.camera_model = value
                
                elif exif_field == 'LensModel':
                    entry.lens_model = value
                
                elif exif_field == 'Notes':
                    entry.notes = value
            
            metadata_entries.append(entry)
        
        return metadata_entries
    
    @staticmethod
    def _convert_datetime(datetime_str: str) -> str:
        """
        Convert datetime format to EXIF standard
        转换日期时间格式为 EXIF 标准
        
        Supports:
        - 2026-01-23 17:51:48 → 2026:01:23 17:51:48
        - 2026/01/23 17:51:48 → 2026:01:23 17:51:48
        - 2026.01.23 17:51:48 → 2026:01:23 17:51:48
        """
        result = datetime_str.replace('-', ':').replace('/', ':').replace('.', ':')
        return result
    
    @staticmethod
    def _decimal_to_dms_display(decimal: float, coord_type: str, direction: str) -> str:
        """
        Convert decimal degrees to DMS format for display
        十进制度数转 DMS 格式（用于显示）
        
        Args:
            decimal: Decimal degrees / 十进制度数
            coord_type: 'lat' or 'lon'
            direction: 'N'/'S'/'E'/'W'
        
        Returns:
            "31°08'37\"N" (display format)
        """
        decimal = abs(decimal)
        
        degrees = int(decimal)
        minutes_decimal = (decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60
        
        return f"{degrees}°{minutes:02d}'{seconds:.0f}\"{direction}"
    
    @staticmethod
    def decimal_to_dms_exif(decimal: float, direction: str) -> str:
        """
        Convert decimal degrees to DMS format for ExifTool
        十进制度数转 DMS 格式（用于 ExifTool）
        
        Args:
            decimal: Decimal degrees / 十进制度数
            direction: 'N'/'S'/'E'/'W'
        
        Returns:
            "31deg 8' 37.13\" N" (ExifTool format)
        """
        decimal = abs(decimal)
        
        degrees = int(decimal)
        minutes_decimal = (decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60
        
        return f"{degrees}deg {minutes}' {seconds:.2f}\" {direction}"
    
    @staticmethod
    def get_gps_ref_full(direction: str) -> str:
        """
        Convert direction abbreviation to full name
        转换方向缩写为全称
        
        Args:
            direction: 'N'/'S'/'E'/'W'
        
        Returns:
            "North"/"South"/"East"/"West"
        """
        mapping = {
            'N': 'North',
            'S': 'South',
            'E': 'East',
            'W': 'West'
        }
        return mapping.get(direction, direction)
