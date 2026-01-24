#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input validators for metadata fields
元数据字段的输入验证器
"""

import re
from typing import Optional


class MetadataValidator:
    """
    Validator for metadata input fields / 元数据输入字段验证器
    Ensures data integrity before writing to EXIF / 确保写入 EXIF 前的数据完整性
    """
    
    @staticmethod
    def validate_aperture(value: str) -> str:
        """
        Validate aperture value / 验证光圈值
        
        Args:
            value: Aperture string (e.g., "f/4", "4", "F4") / 光圈字符串
        
        Returns:
            str: Normalized aperture value / 标准化的光圈值
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("光圈值不能为空 / Aperture value cannot be empty")
        
        # Remove common prefixes / 移除常见前缀
        cleaned = str(value).strip().upper().replace('F/', '').replace('F', '').strip()
        
        try:
            f_num = float(cleaned)
            if f_num < 0.5 or f_num > 64:
                raise ValueError(f"光圈值超出合理范围 (0.5-64): {value}")
            return str(f_num)
        except ValueError:
            raise ValueError(f"无效的光圈值 / Invalid aperture value: {value}")
    
    @staticmethod
    def validate_shutter_speed(value: str) -> str:
        """
        Validate shutter speed / 验证快门速度
        
        Args:
            value: Shutter speed (e.g., "1/125", "2s", "1/125s") / 快门速度
        
        Returns:
            str: Normalized shutter speed / 标准化的快门速度
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("快门速度不能为空 / Shutter speed cannot be empty")
        
        cleaned = str(value).strip().rstrip('s').rstrip('S').strip()
        
        # Support formats: "1/125", "2", "0.5" / 支持格式
        pattern = r'^(\d+/\d+|\d+\.?\d*)$'
        if not re.match(pattern, cleaned):
            raise ValueError(f"无效的快门速度格式 / Invalid shutter speed format: {value}")
        
        # Validate fraction / 验证分数
        if '/' in cleaned:
            parts = cleaned.split('/')
            numerator = int(parts[0])
            denominator = int(parts[1])
            if denominator == 0:
                raise ValueError("快门速度分母不能为0 / Shutter speed denominator cannot be 0")
            if numerator < 1 or denominator < 1:
                raise ValueError(f"无效的快门速度 / Invalid shutter speed: {value}")
        
        return cleaned
    
    @staticmethod
    def validate_iso(value: str) -> int:
        """
        Validate ISO value / 验证 ISO 值
        
        Args:
            value: ISO value / ISO 值
        
        Returns:
            int: Validated ISO value / 验证后的 ISO 值
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("ISO 值不能为空 / ISO value cannot be empty")
        
        try:
            iso = int(str(value).strip())
            if iso < 1 or iso > 409600:
                raise ValueError(f"ISO 值超出合理范围 (1-409600): {value}")
            return iso
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"无效的 ISO 值 / Invalid ISO value: {value}")
            raise
    
    @staticmethod
    def validate_focal_length(value: str) -> str:
        """
        Validate focal length / 验证焦距
        
        Args:
            value: Focal length (e.g., "80mm", "80") / 焦距
        
        Returns:
            str: Normalized focal length / 标准化的焦距
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("焦距不能为空 / Focal length cannot be empty")
        
        # Remove 'mm' suffix / 移除 'mm' 后缀
        cleaned = str(value).strip().lower().replace('mm', '').strip()
        
        try:
            focal = float(cleaned)
            if focal < 1 or focal > 2000:
                raise ValueError(f"焦距超出合理范围 (1-2000mm): {value}")
            return str(int(focal))  # Return as integer string / 返回整数字符串
        except ValueError:
            raise ValueError(f"无效的焦距值 / Invalid focal length: {value}")
    
    @staticmethod
    def validate_datetime(value: str) -> str:
        """
        Validate datetime format / 验证日期时间格式
        
        Args:
            value: DateTime string (EXIF format: "YYYY:MM:DD HH:MM:SS") / 日期时间字符串
        
        Returns:
            str: Validated datetime string / 验证后的日期时间字符串
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("日期时间不能为空 / DateTime cannot be empty")
        
        # EXIF datetime format: YYYY:MM:DD HH:MM:SS
        pattern = r'^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$'
        if not re.match(pattern, str(value).strip()):
            raise ValueError(f"无效的日期时间格式，应为 YYYY:MM:DD HH:MM:SS / Invalid datetime format: {value}")
        
        # Validate ranges / 验证范围
        parts = str(value).strip().split()
        date_parts = parts[0].split(':')
        time_parts = parts[1].split(':')
        
        year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
        hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
        
        if not (1900 <= year <= 2100):
            raise ValueError(f"年份超出范围 (1900-2100): {year}")
        if not (1 <= month <= 12):
            raise ValueError(f"月份超出范围 (1-12): {month}")
        if not (1 <= day <= 31):
            raise ValueError(f"日期超出范围 (1-31): {day}")
        if not (0 <= hour <= 23):
            raise ValueError(f"小时超出范围 (0-23): {hour}")
        if not (0 <= minute <= 59):
            raise ValueError(f"分钟超出范围 (0-59): {minute}")
        if not (0 <= second <= 59):
            raise ValueError(f"秒数超出范围 (0-59): {second}")
        
        return str(value).strip()
    
    @staticmethod
    def validate_camera_model(value: str) -> str:
        """
        Validate camera model name / 验证相机型号名称
        
        Args:
            value: Camera model / 相机型号
        
        Returns:
            str: Validated camera model / 验证后的相机型号
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("相机型号不能为空 / Camera model cannot be empty")
        
        cleaned = str(value).strip()
        
        # Check for reasonable length / 检查合理长度
        if len(cleaned) > 100:
            raise ValueError("相机型号过长 (最多100字符) / Camera model too long (max 100 chars)")
        
        # Check for invalid characters / 检查无效字符
        if re.search(r'[<>:"/\\|?*]', cleaned):
            raise ValueError("相机型号包含非法字符 / Camera model contains invalid characters")
        
        return cleaned
    
    @staticmethod
    def validate_lens_model(value: str) -> str:
        """
        Validate lens model name / 验证镜头型号名称
        
        Args:
            value: Lens model / 镜头型号
        
        Returns:
            str: Validated lens model / 验证后的镜头型号
        
        Raises:
            ValueError: If value is invalid / 如果值无效
        """
        if not value or not str(value).strip():
            raise ValueError("镜头型号不能为空 / Lens model cannot be empty")
        
        cleaned = str(value).strip()
        
        # Check for reasonable length / 检查合理长度
        if len(cleaned) > 150:
            raise ValueError("镜头型号过长 (最多150字符) / Lens model too long (max 150 chars)")
        
        # Check for invalid characters / 检查无效字符
        if re.search(r'[<>:"/\\|?*]', cleaned):
            raise ValueError("镜头型号包含非法字符 / Lens model contains invalid characters")
        
        return cleaned
