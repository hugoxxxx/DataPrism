#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON to photo matching algorithm
JSON 记录与照片文件的匹配算法
"""

from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
import logging

from src.core.json_parser import FilmLogEntry
from src.core.photo_model import PhotoItem

logger = logging.getLogger(__name__)


class PhotoMatcher:
    """
    Match film log entries to photos based on timestamp or sequence
    基于时间戳或顺序将胶片记录匹配到照片
    """
    
    def __init__(self, time_tolerance_minutes: int = 5):
        """
        Initialize matcher
        初始化匹配器
        
        Args:
            time_tolerance_minutes: Tolerance for timestamp matching (±N minutes)
                                   时间戳匹配的容差（±N 分钟）
        """
        self.time_tolerance = timedelta(minutes=time_tolerance_minutes)
    
    def match_by_timestamp(
        self,
        photos: List[PhotoItem],
        log_entries: List[FilmLogEntry]
    ) -> List[Tuple[PhotoItem, Optional[FilmLogEntry]]]:
        """
        Match photos to log entries by timestamp
        通过时间戳将照片匹配到日志条目
        
        Args:
            photos: List of PhotoItem objects / PhotoItem 对象列表
            log_entries: List of FilmLogEntry objects / FilmLogEntry 对象列表
        
        Returns:
            List of (photo, log_entry) tuples / (照片, 日志条目) 元组列表
            log_entry is None if no match found / 如果未找到匹配则 log_entry 为 None
        """
        matches: List[Tuple[PhotoItem, Optional[FilmLogEntry]]] = []
        used_entries = set()
        
        for photo in photos:
            best_match = None
            best_diff = None
            
            # Get photo timestamp / 获取照片时间戳
            photo_time = self._get_photo_timestamp(photo)
            if photo_time is None:
                matches.append((photo, None))
                continue
            
            # Find closest log entry within tolerance / 在容差范围内找到最接近的日志条目
            for idx, entry in enumerate(log_entries):
                if idx in used_entries or entry.timestamp is None:
                    continue
                
                time_diff = abs(photo_time - entry.timestamp)
                
                if time_diff <= self.time_tolerance:
                    if best_diff is None or time_diff < best_diff:
                        best_match = entry
                        best_diff = time_diff
                        best_idx = idx
            
            if best_match:
                used_entries.add(best_idx)
                matches.append((photo, best_match))
                logger.debug(f"Matched {photo.file_name} to entry (diff: {best_diff})")
            else:
                matches.append((photo, None))
                logger.debug(f"No match for {photo.file_name}")
        
        return matches
    
    def match_by_sequence(
        self,
        photos: List[PhotoItem],
        log_entries: List[FilmLogEntry]
    ) -> List[Tuple[PhotoItem, Optional[FilmLogEntry]]]:
        """
        Match photos to log entries by sequence order
        按顺序将照片匹配到日志条目
        
        Assumes both lists are sorted chronologically
        假设两个列表都按时间顺序排序
        
        Args:
            photos: Sorted list of PhotoItem objects / 排序后的 PhotoItem 对象列表
            log_entries: Sorted list of FilmLogEntry objects / 排序后的 FilmLogEntry 对象列表
        
        Returns:
            List of (photo, log_entry) tuples / (照片, 日志条目) 元组列表
        """
        matches: List[Tuple[PhotoItem, Optional[FilmLogEntry]]] = []
        
        # Simple 1:1 sequential matching / 简单的 1:1 顺序匹配
        for idx, photo in enumerate(photos):
            if idx < len(log_entries):
                matches.append((photo, log_entries[idx]))
                logger.debug(f"Sequential match: {photo.file_name} -> entry #{idx+1}")
            else:
                matches.append((photo, None))
                logger.debug(f"No entry for {photo.file_name} (out of bounds)")
        
        return matches
    
    def match_hybrid(
        self,
        photos: List[PhotoItem],
        log_entries: List[FilmLogEntry],
        prefer_timestamp: bool = False
    ) -> List[Tuple[PhotoItem, Optional[FilmLogEntry]]]:
        """
        Hybrid matching: try sequence first, fall back to timestamp if many unmatched
        混合匹配：优先尝试顺序，如果有许多未匹配则回退到时间戳
        
        Default strategy (v0.3.1): Sequence-first approach (prefer_timestamp=False)
        For film photography workflows where photos may be missing or skipped
        默认策略（v0.3.1）：序列优先方法（prefer_timestamp=False）
        用于胶片摄影工作流，其中照片可能被遗漏或跳过
        
        Args:
            photos: List of PhotoItem objects / PhotoItem 对象列表
            log_entries: List of FilmLogEntry objects / FilmLogEntry 对象列表
            prefer_timestamp: If True, prefer timestamp; otherwise prefer sequence (default False for v0.3.1)
                            如果为 True，优先时间戳；否则优先顺序（v0.3.1 默认为 False）
        
        Returns:
            List of (photo, log_entry) tuples / (照片, 日志条目) 元组列表
        """
        if prefer_timestamp:
            matches = self.match_by_timestamp(photos, log_entries)
            
            # Check if we have many unmatched photos / 检查是否有许多未匹配的照片
            unmatched_count = sum(1 for _, entry in matches if entry is None)
            if unmatched_count > len(photos) * 0.5:  # More than 50% unmatched
                logger.warning(f"Timestamp matching failed for {unmatched_count} photos, falling back to sequence")
                matches = self.match_by_sequence(photos, log_entries)
        else:
            # v0.3.1 default: sequence-first strategy
            # For film photography with potential frame skips / 胶片摄影的默认策略，可能跳过帧
            matches = self.match_by_sequence(photos, log_entries)
            
            # Check if we have many unmatched due to sequence / 检查是否因顺序而有许多未匹配
            unmatched_count = sum(1 for _, entry in matches if entry is None)
            if unmatched_count > len(photos) * 0.3 and any(entry.timestamp for entry in log_entries):
                logger.info(f"Sequence matching: {unmatched_count} unmatched photos; timestamp data available in log entries")
                logger.debug("Keeping sequence-first strategy as per v0.3.1 design for film photography")
        
        return matches
    
    def _get_photo_timestamp(self, photo: PhotoItem) -> Optional[datetime]:
        """
        Extract timestamp from photo EXIF data
        从照片 EXIF 数据中提取时间戳
        
        Args:
            photo: PhotoItem object / PhotoItem 对象
        
        Returns:
            datetime object or None / datetime 对象或 None
        """
        if not photo.exif_data:
            return None
        
        # Try multiple EXIF date fields / 尝试多个 EXIF 日期字段
        date_fields = ['DateTimeOriginal', 'CreateDate', 'DateTime', 'DateTimeDigitized']
        
        for field in date_fields:
            if field in photo.exif_data:
                try:
                    date_str = photo.exif_data[field]
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except Exception as e:
                    logger.warning(f"Could not parse date '{date_str}': {e}")
                    continue
        
        return None
    
    def get_match_statistics(
        self,
        matches: List[Tuple[PhotoItem, Optional[FilmLogEntry]]]
    ) -> Dict[str, int]:
        """
        Get matching statistics
        获取匹配统计信息
        
        Args:
            matches: List of matches / 匹配列表
        
        Returns:
            Statistics dictionary / 统计字典
        """
        total = len(matches)
        matched = sum(1 for _, entry in matches if entry is not None)
        unmatched = total - matched
        
        return {
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': matched / total if total > 0 else 0.0
        }
