#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS Utility functions for parsing and formatting coordinates
GPS 坐标解析和格式化工具函数
"""

import re
from typing import Optional, Tuple, Union

def format_gps_pair(lat: Union[float, str, None], lat_ref: Optional[str], 
                   lon: Union[float, str, None], lon_ref: Optional[str], 
                   strict: bool = True) -> Optional[str]:
    """
    Format GPS lat/lon into standardized DMS string.
    将 GPS 经纬度格式化为标准化的度分秒字符串。
    
    Example output / 输出示例:
    28°31'30.59"N, 119°30'30.44"E
    """
    
    # Check if inputs are effectively None / 检查输入是否为空
    if not lat or not lon:
        return None if strict else None

    # Parse latitude and longitude / 解析经纬度
    lat_parsed = _parse_coordinate(lat, lat_ref)
    lon_parsed = _parse_coordinate(lon, lon_ref)

    if not lat_parsed or not lon_parsed:
        return None if strict else None

    # Format both components / 格式化两个部分
    return f"{_format_coordinate(lat_parsed)}, {_format_coordinate(lon_parsed)}"


def parse_location_string(location_text: str) -> Optional[str]:
    """
    Parse a raw location string and return the standardized formatted string.
    解析原始位置字符串并返回标准化的格式化字符串。
    
    Useful for cleaning up "ugly" strings like "28deg 31' 30.59" N North".
    用于清理诸如 "28deg 31' 30.59" N North" 之类的"丑陋"字符串。
    """
    if not location_text:
        return None
        
    parts = [p.strip() for p in location_text.split(',') if p.strip()]
    if len(parts) < 2:
        return None

    # Try to parse lat and lon from the parts / 尝试从部分中解析经纬度
    # Assuming first part is lat, second is lon / 假设第一部分是纬度，第二部分是经度
    lat_text = parts[0]
    lon_text = parts[1]
    
    # Infer refs from text content if possible / 如果可能，从文本内容推断方向
    lat_ref = 'N' if 'N' in lat_text.upper() else ('S' if 'S' in lat_text.upper() else None)
    lon_ref = 'E' if 'E' in lon_text.upper() else ('W' if 'W' in lon_text.upper() else None)
    
    return format_gps_pair(lat_text, lat_ref, lon_text, lon_ref, strict=True)


def parse_gps_to_exif(location_text: str) -> Optional[Tuple[str, str, str, str]]:
    """
    Parse location string back to EXIF components (lat, lat_ref, lon, lon_ref).
    将位置字符串解析回 EXIF 组件 (lat, lat_ref, lon, lon_ref)。
    
    Used by MetadataEditor to convert display string back to EXIF data.
    被 MetadataEditor 用于将显示字符串转换回 EXIF 数据。
    
    Returns format compatible with ExifTool and 1.json:
    返回与 ExifTool 和 1.json 兼容的格式：
    - Latitude: "28deg 31' 30.59\" N"
    - LatitudeRef: "North"
    - Longitude: "119deg 30' 30.44\" E"
    - LongitudeRef: "East"
    """
    if not location_text:
        return None
        
    parts = [p.strip() for p in location_text.split(',') if p.strip()]
    if len(parts) < 2:
        return None
        
    lat_parsed = _parse_coordinate(parts[0], None)
    lon_parsed = _parse_coordinate(parts[1], None)
    
    if lat_parsed and lon_parsed:
        lat_deg, lat_min, lat_sec, lat_ref = lat_parsed
        lon_deg, lon_min, lon_sec, lon_ref = lon_parsed
        
        # Convert to ExifTool format matching 1.json:
        # "28deg 31' 30.59\" N" and "North"
        # 转换为与 1.json 匹配的 ExifTool 格式
        def _to_exif_format(deg, minute, sec, ref):
            if minute is None or sec is None:
                # Decimal format fallback
                return f"{deg}", ref or "N"
            # DMS format: "28deg 31' 30.59\" N"
            ref_full = "North" if ref == "N" else "South" if ref == "S" else "East" if ref == "E" else "West"
            coord_str = f"{int(deg)}deg {int(minute)}' {sec:.2f}\" {ref}"
            return coord_str, ref_full
            
        # Defaults if ref parsing failed
        final_lat_ref = lat_ref if lat_ref else 'N'
        final_lon_ref = lon_ref if lon_ref else 'E'
        
        lat_str, lat_ref_full = _to_exif_format(lat_deg, lat_min, lat_sec, final_lat_ref)
        lon_str, lon_ref_full = _to_exif_format(lon_deg, lon_min, lon_sec, final_lon_ref)
        
        return (lat_str, lat_ref_full, lon_str, lon_ref_full)
        
    return None


def _parse_coordinate(value, ref_hint) -> Optional[Tuple[float, Optional[float], Optional[float], Optional[str]]]:
    """
    Internal helper to parse a single coordinate string/value.
    内部辅助函数，用于解析单个坐标字符串/值。
    """
    if value is None:
        return None
    
    s = str(value).strip()
    
    # Robust Regex handles:
    # 28deg 31' 30.59" N
    # 28 31 30.59
    # 28deg 31' 30.59" N North
    # Quotes are handled by skipping non-numeric characters between parts
    # [^0-9NSEW]* skips "deg", "'", whitespace, quotes, etc.
    pattern = r"([0-9.]+)[^0-9]+([0-9.]+)[^0-9]+([0-9.]+)[^0-9NSEW]*([NSEW])?"
    
    m = re.match(pattern, s, re.IGNORECASE)
    if m:
        deg, minute, sec, suffix = m.groups()
        suffix = suffix or (ref_hint or "").strip()[:1]
        return float(deg), float(minute), float(sec), suffix.upper() if suffix else None
    
    # Try plain decimal
    try:
        dec = float(s)
        suffix = (ref_hint or "").strip()[:1].upper() if ref_hint else None
        return dec, None, None, suffix
    except:
        return None


def _format_coordinate(parsed) -> str:
    """
    Internal helper to format a single parsed coordinate.
    内部辅助函数，用于格式化单个已解析的坐标。
    """
    deg, minute, sec, suffix = parsed
    if minute is None or sec is None:
        # decimal fallback
        sign = suffix or ""
        return f"{deg:.6f}{sign}"
    
    suf = suffix or ""
    return f"{deg:.0f}°{minute:.0f}'{sec:.0f}\"{suf}"
