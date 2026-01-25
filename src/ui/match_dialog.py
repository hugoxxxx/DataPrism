#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Match preview dialog for film log JSON import
胶片日志 JSON 导入的匹配预览对话框
"""

from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QComboBox, QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.core.photo_model import PhotoItem
from src.core.json_parser import FilmLogEntry
from src.core.json_matcher import PhotoMatcher
from src.utils.i18n import tr
from src.ui.style_manager import StyleManager


class MatchPreviewDialog(QDialog):
    """Preview and adjust photo-to-log matching / 预览和调整照片到日志的匹配"""
    
    def __init__(
        self, 
        photos: List[PhotoItem], 
        log_entries: List[FilmLogEntry],
        matches: Dict[int, Optional[int]],
        stats: dict,
        parent=None
    ):
        super().__init__(parent)
        self.photos = photos
        self.log_entries = log_entries
        self.matches = matches.copy()  # Copy to allow modifications
        self.stats = stats
        
        self.setWindowTitle(tr("Match Preview"))
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.populate_table()
    
    def setup_ui(self):
        """Setup UI components / 设置 UI 组件"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Statistics section / 统计部分
        stats_box = QGroupBox(tr("Match Statistics"))
        stats_layout = QHBoxLayout(stats_box)
        
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 13, QFont.Bold))
        self.stats_label.setStyleSheet(f"color: {StyleManager.COLOR_ACCENT};")
        self._update_stats_label()
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        # Rematch button
        rematch_btn = QPushButton(tr("Rematch"))
        rematch_btn.setMinimumHeight(32)
        rematch_btn.clicked.connect(self.rematch_with_offset)
        stats_layout.addWidget(rematch_btn)
        
        layout.addWidget(stats_box)
        
        # Time offset adjustment / 时间偏移调整
        offset_box = QGroupBox(tr("Time Offset"))
        offset_layout = QHBoxLayout(offset_box)
        
        offset_layout.addWidget(QLabel(tr("Adjust by (minutes):")))
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(-180, 180)
        self.offset_spin.setValue(0)
        self.offset_spin.setMinimumWidth(80)
        offset_layout.addWidget(self.offset_spin)
        offset_layout.addStretch()
        
        layout.addWidget(offset_box)
        
        # Match table / 匹配表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            tr("Photo File"),
            tr("Photo Date"),
            tr("→"),
            tr("Log Camera"),
            tr("Log Lens"),
            tr("Log Date")
        ])
        
        # Table styling / 表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setStyleSheet(StyleManager.get_table_style())
        
        layout.addWidget(self.table)
        
        # Buttons / 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton(tr("Cancel"))
        cancel_btn.setMinimumSize(100, 36)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(StyleManager.get_button_style())
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton(f"✅ {tr('Apply to All')}")
        apply_btn.setMinimumSize(140, 38)
        apply_btn.clicked.connect(self.accept)
        apply_btn.setStyleSheet(StyleManager.get_button_style(tier='primary'))
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
        
        # Global Style
        self.setStyleSheet(StyleManager.get_main_style())
        
        for box in [stats_box, offset_box]:
            box.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    color: {StyleManager.COLOR_TEXT_SECONDARY};
                    border: 1px solid {StyleManager.COLOR_BORDER};
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 20px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px;
                }}
            """)
        
        rematch_btn.setStyleSheet(StyleManager.get_button_style(tier='primary').replace("padding: 10px 18px;", "padding: 4px 12px;"))
        self.offset_spin.setStyleSheet(f"border: 1px solid {StyleManager.COLOR_BORDER}; border-radius: 4px; padding: 2px;")
    
    def _update_stats_label(self):
        """Update statistics label / 更新统计标签"""
        matched = self.stats.get('matched', 0)
        total = self.stats.get('total', 0)
        match_rate = self.stats.get('match_rate', 0.0)
        
        text = tr("Matched: {matched}/{total}").format(matched=matched, total=total)
        text += f" ({match_rate:.0%})"
        self.stats_label.setText(text)
    
    def populate_table(self):
        """Populate table with match results / 用匹配结果填充表格"""
        self.table.setRowCount(len(self.photos))
        
        for i, photo in enumerate(self.photos):
            # Photo file / 照片文件
            file_item = QTableWidgetItem(photo.file_name or "—")
            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, file_item)
            
            # Photo date / 照片日期
            date_str = "—"
            if photo.exif_data:
                date_str = photo.exif_data.get('DateTimeOriginal') or photo.exif_data.get('CreateDate') or "—"
            date_item = QTableWidgetItem(date_str)
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, date_item)
            
            # Arrow / 箭头
            arrow_item = QTableWidgetItem("→")
            arrow_item.setFlags(arrow_item.flags() & ~Qt.ItemIsEditable)
            arrow_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, arrow_item)
            
            # Matched log entry / 匹配的日志条目
            log_idx = self.matches.get(i)
            if log_idx is not None and log_idx < len(self.log_entries):
                log_entry = self.log_entries[log_idx]
                
                # Log camera / 日志相机
                camera_item = QTableWidgetItem(log_entry.camera or "—")
                camera_item.setFlags(camera_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 3, camera_item)
                
                # Log lens / 日志镜头
                lens_item = QTableWidgetItem(log_entry.lens or "—")
                lens_item.setFlags(lens_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 4, lens_item)
                
                # Log date / 日志日期
                log_date_str = log_entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log_entry.timestamp else "—"
                log_date_item = QTableWidgetItem(log_date_str)
                log_date_item.setFlags(log_date_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, 5, log_date_item)
            else:
                # No match / 无匹配
                for col in range(3, 6):
                    no_match_item = QTableWidgetItem("—")
                    no_match_item.setFlags(no_match_item.flags() & ~Qt.ItemIsEditable)
                    no_match_item.setForeground(Qt.gray)
                    self.table.setItem(i, col, no_match_item)
        
        self.table.resizeRowsToContents()
    
    def rematch_with_offset(self):
        """Rematch photos with time offset / 用时间偏移重新匹配照片"""
        offset_minutes = self.offset_spin.value()
        
        # Create matcher with adjusted tolerance / 创建调整容差的匹配器
        # Note: This is a simplified approach. For time offset, we adjust the tolerance.
        # A more sophisticated approach would be to adjust photo timestamps in exif_data.
        # 注意：这是简化方法。对于时间偏移，我们调整容差。
        # 更复杂的方法是调整 exif_data 中的照片时间戳。
        
        from datetime import timedelta
        from datetime import datetime
        
        # Temporarily modify photo EXIF dates for matching / 临时修改照片 EXIF 日期用于匹配
        adjusted_photos = []
        for photo in self.photos:
            if photo.exif_data and photo.exif_data.get('DateTimeOriginal'):
                try:
                    # Parse and adjust date / 解析并调整日期
                    date_str = photo.exif_data['DateTimeOriginal']
                    date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    adjusted_date = date_obj + timedelta(minutes=offset_minutes)
                    adjusted_date_str = adjusted_date.strftime('%Y:%m:%d %H:%M:%S')
                    
                    # Create adjusted exif_data / 创建调整后的 exif_data
                    adjusted_exif = photo.exif_data.copy()
                    adjusted_exif['DateTimeOriginal'] = adjusted_date_str
                    if 'CreateDate' in adjusted_exif:
                        adjusted_exif['CreateDate'] = adjusted_date_str
                    
                    # Create new PhotoItem with adjusted EXIF / 创建带调整 EXIF 的新 PhotoItem
                    adjusted_photo = PhotoItem(
                        file_path=photo.file_path,
                        file_name=photo.file_name,
                        exif_data=adjusted_exif,
                        thumbnail=photo.thumbnail,
                        status=photo.status,
                        is_modified=photo.is_modified,
                        aperture=photo.aperture,
                        shutter_speed=photo.shutter_speed,
                        iso=photo.iso,
                        film_stock=photo.film_stock,
                        focal_length=photo.focal_length,
                        serial_number=photo.serial_number
                    )
                    adjusted_photos.append(adjusted_photo)
                except Exception as e:
                    # If parsing fails, use original / 如果解析失败，使用原始数据
                    adjusted_photos.append(photo)
            else:
                adjusted_photos.append(photo)
        
        # Rematch / 重新匹配
        matcher = PhotoMatcher()
        match_tuples = matcher.match_hybrid(adjusted_photos, self.log_entries)
        
        # Convert to index-based dict / 转换为基于索引的字典
        self.matches = {}
        for photo_idx, (photo, log_entry) in enumerate(match_tuples):
            if log_entry:
                log_idx = self.log_entries.index(log_entry)
                self.matches[photo_idx] = log_idx
            else:
                self.matches[photo_idx] = None
        
        self.stats = matcher.get_match_statistics(match_tuples)
        
        # Update UI / 更新 UI
        self._update_stats_label()
        self.populate_table()
    
    def get_confirmed_matches(self) -> Dict[int, Optional[int]]:
        """Get confirmed matches / 获取确认的匹配"""
        return self.matches
