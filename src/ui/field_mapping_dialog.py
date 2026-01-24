#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field Mapping Dialog for CSV import
CSV 导入字段映射对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
    QGroupBox, QCheckBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List, Dict
from src.utils.i18n import tr


class FieldMappingDialog(QDialog):
    """
    Field mapping dialog for CSV import
    CSV 导入的字段映射对话框
    """
    
    def __init__(self, csv_headers: List[str], preview_data: List[Dict], parent=None):
        """
        Initialize field mapping dialog
        初始化字段映射对话框
        
        Args:
            csv_headers: CSV column headers / CSV 列标题
            preview_data: Preview data (first 5 rows) / 预览数据（前5行）
            parent: Parent widget / 父组件
        """
        super().__init__(parent)
        self.csv_headers = csv_headers
        self.preview_data = preview_data
        self.mappings = {}  # {csv_column: {'field_combo': QComboBox, 'gps_combo': QComboBox}}
        
        self.setWindowTitle(tr("CSV Field Mapping"))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components / 设置 UI 组件"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(tr("Please map CSV columns to EXIF fields:"))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Mapping section
        mapping_group = QGroupBox(tr("Field Mappings"))
        mapping_layout = QFormLayout()
        
        # EXIF field options
        self.exif_fields = [
            "-- " + tr("Use for sorting (ID)") + " --",
            "-- " + tr("Ignore this column") + " --",
            "DateTimeOriginal",
            "GPSLatitude",
            "GPSLongitude",
            "Make",
            "Model",
            "LensModel",
            "FNumber",
            "ExposureTime",
            "ISO",
            "FocalLength",
            "Film",
            "Notes"
        ]
        
        # Create mapping row for each CSV column
        for csv_col in self.csv_headers:
            row_layout = QHBoxLayout()
            
            # Field selection combo
            field_combo = QComboBox()
            field_combo.addItems(self.exif_fields)
            field_combo.setMinimumWidth(200)
            
            # Smart match default value
            default_mapping = self._smart_match(csv_col)
            if default_mapping in self.exif_fields:
                field_combo.setCurrentText(default_mapping)
            
            row_layout.addWidget(field_combo)
            
            # GPS direction combo (initially hidden)
            gps_combo = QComboBox()
            gps_combo.setMinimumWidth(150)
            gps_combo.hide()
            
            # Setup GPS combo based on field type
            if default_mapping == "GPSLatitude":
                gps_combo.addItems([tr("North (N)"), tr("South (S)")])
                gps_combo.setCurrentText(tr("North (N)"))  # Default
                gps_combo.show()
            elif default_mapping == "GPSLongitude":
                gps_combo.addItems([tr("East (E)"), tr("West (W)")])
                gps_combo.setCurrentText(tr("East (E)"))  # Default
                gps_combo.show()
            
            row_layout.addWidget(gps_combo)
            row_layout.addStretch()
            
            # Connect signal to show/hide GPS combo
            field_combo.currentTextChanged.connect(
                lambda text, col=csv_col: self._on_field_changed(col, text)
            )
            
            # Store references
            self.mappings[csv_col] = {
                'field_combo': field_combo,
                'gps_combo': gps_combo
            }
            
            # Add to form
            label = QLabel(f"{csv_col}  →")
            label.setMinimumWidth(150)
            mapping_layout.addRow(label, row_layout)
        
        mapping_group.setLayout(mapping_layout)
        
        # Make mapping section scrollable
        scroll = QScrollArea()
        scroll.setWidget(mapping_group)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        layout.addWidget(scroll)
        
        # Info label
        info_label = QLabel(
            "ℹ️ " + tr("Tip: ID column is used for photo ordering (row 1 → photo 1)")
        )
        info_label.setStyleSheet("color: #666; padding: 8px; background: #f0f0f0; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Preview section
        preview_group = QGroupBox(tr("Data Preview (first 5 rows)"))
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(len(self.csv_headers))
        self.preview_table.setHorizontalHeaderLabels(self.csv_headers)
        self.preview_table.setRowCount(min(5, len(self.preview_data)))
        
        # Fill preview data
        for row_idx, row_data in enumerate(self.preview_data[:5]):
            for col_idx, header in enumerate(self.csv_headers):
                value = row_data.get(header, '')
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.preview_table.setItem(row_idx, col_idx, item)
        
        self.preview_table.resizeColumnsToContents()
        preview_layout.addWidget(self.preview_table)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Save template checkbox
        self.save_template_cb = QCheckBox(tr("Save this mapping as template (auto-apply next time)"))
        layout.addWidget(self.save_template_cb)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton(tr("OK"))
        ok_button.clicked.connect(self.accept)
        ok_button.setMinimumWidth(100)
        
        cancel_button = QPushButton(tr("Cancel"))
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumWidth(100)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def _smart_match(self, csv_column: str) -> str:
        """
        Smart match CSV column name to EXIF field
        智能匹配 CSV 列名到 EXIF 字段
        
        Args:
            csv_column: CSV column name / CSV 列名
        
        Returns:
            Matched EXIF field / 匹配的 EXIF 字段
        """
        col_lower = csv_column.lower().strip()
        
        # ID column
        if col_lower in ['id', 'no', 'number', '序号', '编号', '#']:
            return "-- " + tr("Use for sorting (ID)") + " --"
        
        # DateTime
        if any(k in col_lower for k in ['datetime', 'date', 'time', '日期', '时间']):
            return 'DateTimeOriginal'
        
        # Latitude
        if any(k in col_lower for k in ['latitude', 'lat', '纬度']):
            return 'GPSLatitude'
        
        # Longitude
        if any(k in col_lower for k in ['longitude', 'lon', 'lng', '经度']):
            return 'GPSLongitude'
        
        # Camera
        if any(k in col_lower for k in ['camera', 'make', '相机', '机身']):
            return 'Model'
        
        # Lens
        if any(k in col_lower for k in ['lens', '镜头']):
            return 'LensModel'
        
        # Aperture
        if any(k in col_lower for k in ['aperture', 'fnumber', 'f-number', '光圈']):
            return 'FNumber'
        
        # Shutter
        if any(k in col_lower for k in ['shutter', 'exposure', '快门', '曝光']):
            return 'ExposureTime'
        
        # ISO
        if 'iso' in col_lower or '感光度' in col_lower:
            return 'ISO'
        
        # Focal length
        if any(k in col_lower for k in ['focal', '焦距']):
            return 'FocalLength'
        
        # Film
        if any(k in col_lower for k in ['film', '胶卷', '胶片']):
            return 'Film'
        
        # Notes
        if any(k in col_lower for k in ['note', 'comment', 'remark', '备注', '注释']):
            return 'Notes'
        
        return "-- " + tr("Ignore this column") + " --"
    
    def _on_field_changed(self, csv_col: str, exif_field: str):
        """
        Handle field selection change
        处理字段选择变化
        
        Args:
            csv_col: CSV column name / CSV 列名
            exif_field: Selected EXIF field / 选择的 EXIF 字段
        """
        mapping = self.mappings[csv_col]
        gps_combo = mapping['gps_combo']
        
        # Hide GPS combo first
        gps_combo.hide()
        gps_combo.clear()
        
        # Show GPS direction combo if GPS field selected
        if exif_field == "GPSLatitude":
            gps_combo.addItems([tr("North (N)"), tr("South (S)")])
            gps_combo.setCurrentText(tr("North (N)"))
            gps_combo.show()
        
        elif exif_field == "GPSLongitude":
            gps_combo.addItems([tr("East (E)"), tr("West (W)")])
            gps_combo.setCurrentText(tr("East (E)"))
            gps_combo.show()
    
    def get_mappings(self) -> Dict:
        """
        Get user-selected field mappings
        获取用户选择的字段映射
        
        Returns:
            {
                'fields': {csv_column: exif_field},
                'gps_refs': {csv_column: 'N'/'S'/'E'/'W'},
                'id_column': csv_column or None
            }
        """
        result = {
            'fields': {},
            'gps_refs': {},
            'id_column': None
        }
        
        for csv_col, mapping in self.mappings.items():
            exif_field = mapping['field_combo'].currentText()
            
            # ID column
            if tr("Use for sorting (ID)") in exif_field:
                result['id_column'] = csv_col
            
            # Regular fields
            elif tr("Ignore this column") not in exif_field:
                result['fields'][csv_col] = exif_field
                
                # GPS direction
                if exif_field == "GPSLatitude":
                    gps_text = mapping['gps_combo'].currentText()
                    result['gps_refs'][csv_col] = 'N' if 'North' in gps_text or '北' in gps_text else 'S'
                
                elif exif_field == "GPSLongitude":
                    gps_text = mapping['gps_combo'].currentText()
                    result['gps_refs'][csv_col] = 'E' if 'East' in gps_text or '东' in gps_text else 'W'
        
        return result
