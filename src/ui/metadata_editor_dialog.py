#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata editor dialog for previewing and modifying imported metadata
用于预览和修改导入元数据的编辑对话框
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QFormLayout, QLineEdit, QLabel, QPushButton, QSlider, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QProgressDialog, QHeaderView,
    QApplication, QFrame, QWidget, QScrollArea, QSizePolicy, QToolButton
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QThreadPool
from PySide6.QtGui import QFont, QPixmap, QColor, QImageReader, QIcon
from src.core.thumbnail_worker import ThumbnailWorker

import logging

from src.core.photo_model import PhotoItem
from src.core.metadata_parser import MetadataEntry
from src.core.exif_worker import ExifToolWorker
from src.core.csv_converter import CSVConverter
import src.utils.gps_utils as gps_utils
from src.utils.i18n import tr
from src.utils.logger import get_logger
from src.utils.validators import MetadataValidator
from src.ui.style_manager import StyleManager
from src.utils.resource_mgr import get_resource_path

logger = get_logger('DataPrism.MetadataEditor')


class MetadataEditorDialog(QDialog):
    """
    Dialog for editing and applying metadata to photos / 用于编辑和应用元数据到照片的对话框
    """
    
    metadata_written = Signal()
    requests_write = Signal(list)  # Signal to pass tasks to MainWindow / 将任务传递给主窗口的信号
    
    def __init__(
        self,
        photos: List[PhotoItem],
        metadata_entries: List[MetadataEntry],
        raw_headers: List[str] = None,
        raw_rows: List[Dict] = None,
        parent=None
    ):
        super().__init__(parent)
        self.photos = photos
        self.metadata_entries = metadata_entries
        self.raw_headers = raw_headers
        self.raw_rows = raw_rows
        self.mappings = {}  # {csv_column: {'field_combo': QComboBox, 'gps_combo': QComboBox}}
        self.current_index = 0
        self.offset = 0
        self._completion_handled = False
        self.thumb_cache = {} # Local preview cache for performance / 预览缓存提升性能
        self.threadpool = QThreadPool.globalInstance()
        self._loading_thumbnails = {} # {file_path: bool} - tracked for safety
        
        self.setWindowTitle(tr("Metadata Editor"))
        
        # Set Dialog Icon / 设置对话框图标
        icon_path = get_resource_path(os.path.join("src", "resources", "app_icon.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setMinimumSize(1250, 800)
        
        self._current_metadata_idx = None
        
        # Ensure we only show what was imported
        # 不再添加多余的缓冲，严格按导入的元数据量来
        pass
            
        # Initialize UI widget references
        self.photo_list = None
        self.metadata_list = None
        self.preview_label = None
        self.file_info_label = None
        self.warning_label = None
        
        self.setup_ui()
        self.check_count_match()
        self.load_photo(0)
    
    def setup_ui(self):
        """Setup UI components with explicit parenting for stability"""
        main_layout = QVBoxLayout(self) # Changed to Vertical to allow for a header/toolbar
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Top Toolbar ---
        toolbar = QFrame(self)
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet(f"background-color: {StyleManager.COLOR_BG_SIDEBAR}; border-bottom: 1px solid {StyleManager.COLOR_BORDER};")
        tool_layout = QHBoxLayout(toolbar)
        tool_layout.setContentsMargins(20, 0, 20, 0)
        
        self.title_label = QLabel(tr("Metadata Studio"))
        self.title_label.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 16, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_PRIMARY};")
        tool_layout.addWidget(self.title_label)
        tool_layout.addStretch()
        
        if self.raw_headers:
            self.map_toggle = QPushButton(tr("Mapping Configuration"))
            self.map_toggle.setCheckable(True)
            self.map_toggle.setChecked(False)
            self.map_toggle.setStyleSheet(StyleManager.get_button_style(tier='secondary'))
            self.map_toggle.clicked.connect(self.toggle_mapping_pane)
            tool_layout.addWidget(self.map_toggle)
        
        main_layout.addWidget(toolbar)
        
        # --- Content Area ---
        content_widget = QWidget(self)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Mapping Pane (Hidden by default) ---
        self.mapping_pane = QWidget(content_widget)
        self.mapping_pane.setFixedWidth(320)
        self.mapping_pane.setVisible(False)
        map_vbox = QVBoxLayout(self.mapping_pane)
        map_vbox.setContentsMargins(0, 0, 0, 0)
        
        map_title = QLabel(tr("Correlate Data"))
        map_title.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 11, QFont.Bold))
        map_title.setStyleSheet(f"color: {StyleManager.COLOR_ACCENT}; text-transform: uppercase; margin-bottom: 5px;")
        map_vbox.addWidget(map_title)
        
        map_scroll = QScrollArea(self.mapping_pane)
        map_scroll.setWidgetResizable(True)
        map_scroll.setFrameShape(QFrame.Shape.NoFrame)
        map_scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background-color: {StyleManager.COLOR_BG_CARD}; border: 1px solid {StyleManager.COLOR_BORDER}; border-radius: 8px;")
        self.map_form = QFormLayout(scroll_content)
        self.map_form.setSpacing(12)
        
        self.exif_fields = [
            (tr("Ignore"), "IGNORE"),
            (tr("ID Source"), "ID_SOURCE"),
            (tr("DateTimeOriginal"), "DateTimeOriginal"),
            (tr("GPSLatitude"), "GPSLatitude"),
            (tr("GPSLongitude"), "GPSLongitude"),
            (tr("Make"), "Make"),
            (tr("Model"), "Model"),
            (tr("LensModel"), "LensModel"),
            (tr("FNumber"), "FNumber"),
            (tr("ExposureTime"), "ExposureTime"),
            (tr("ISO"), "ISO"),
            (tr("FocalLength"), "FocalLength"),
            (tr("Film"), "Film"),
            (tr("Notes"), "Notes")
        ]
        
        if self.raw_headers:
            for col in self.raw_headers:
                f_combo = QComboBox()
                for label, key in self.exif_fields:
                    f_combo.addItem(label, key)
                
                # Smart Match logic simplified here
                suggested_key = self._smart_match_header(col)
                index = f_combo.findData(suggested_key)
                if index >= 0:
                    f_combo.setCurrentIndex(index)
                
                f_combo.currentIndexChanged.connect(self.on_mapping_changed)
                
                g_combo = QComboBox()
                g_combo.setFixedWidth(80)
                g_combo.hide()
                if suggested_key == "GPSLatitude":
                    g_combo.addItems(["N", "S"])
                    g_combo.show()
                elif suggested_key == "GPSLongitude":
                    g_combo.addItems(["E", "W"])
                    g_combo.show()
                g_combo.currentTextChanged.connect(self.on_mapping_changed)
                
                self.mappings[col] = {'field': f_combo, 'gps': g_combo}
                
                row_w = QWidget()
                row_h = QHBoxLayout(row_w)
                row_h.setContentsMargins(0,0,0,0)
                row_h.addWidget(f_combo)
                row_h.addWidget(g_combo)
                
                lbl = QLabel(f"{col}:")
                lbl.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_PRIMARY};")
                self.map_form.addRow(lbl, row_w)
                
        map_scroll.setWidget(scroll_content)
        map_vbox.addWidget(map_scroll)
        content_layout.addWidget(self.mapping_pane, 2) # Added stretch factor
        
        # --- LEFT: Navigation ---
        left_widget = QWidget(self)
        left_widget.setMinimumWidth(280) # Reduced from 380
        left_vbox = QVBoxLayout(left_widget)
        left_vbox.setContentsMargins(0, 0, 0, 0)
        
        nav_container = QWidget(left_widget)
        nav_hbox = QHBoxLayout(nav_container)
        nav_hbox.setContentsMargins(0, 0, 0, 0)
        
        # Photos list
        photo_box = QWidget(nav_container)
        photo_vbox = QVBoxLayout(photo_box)
        photo_vbox.setContentsMargins(0, 0, 0, 0)
        
        photo_header = QWidget()
        photo_h_layout = QHBoxLayout(photo_header)
        photo_h_layout.setContentsMargins(0, 0, 0, 0)
        photo_title = QLabel(tr("Photos"), photo_header)
        photo_title.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 11, QFont.Bold))
        
        # Add Reverse Order Button / 倒序排列按钮 (更明显的样式)
        self.reverse_btn = QPushButton(f" {tr('Reverse')} ")
        self.reverse_btn.setToolTip(tr("Reverse photo sequence order"))
        self.reverse_btn.setStyleSheet(StyleManager.get_button_style(tier='secondary'))
        self.reverse_btn.clicked.connect(self.reverse_photo_order)
        
        photo_h_layout.addWidget(photo_title)
        photo_h_layout.addStretch()
        photo_h_layout.addWidget(self.reverse_btn)
        
        self.photo_list = QListWidget(photo_box)
        self.photo_list.setStyleSheet(StyleManager.get_list_style())
        
        # Enable Drag and Drop / 开启手动拖拽排序
        self.photo_list.setDragEnabled(True)
        self.photo_list.setAcceptDrops(True)
        self.photo_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        # Sync data when moved / 拖拽后实时同步内存数据
        self.photo_list.model().rowsMoved.connect(self._on_photo_reordered)
        
        for i, photo in enumerate(self.photos):
            item = QListWidgetItem(photo.file_name or tr("Photo {num}").format(num=i+1))
            item.setData(Qt.ItemDataRole.UserRole, i)
            # Store full path for robust synchronization after reordering
            # 存储完整路径，以便重排后进行可靠的数据同步
            item.setData(Qt.ItemDataRole.UserRole + 1, photo.file_path)
            self.photo_list.addItem(item)
        self.photo_list.itemClicked.connect(self.on_photo_selected)
        
        # Add context menu for removal
        self.photo_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.photo_list.customContextMenuRequested.connect(self._on_photo_context_menu)
        
        photo_vbox.addWidget(photo_header)
        photo_vbox.addWidget(self.photo_list)
        
        # Records list
        record_box = QWidget(nav_container)
        record_vbox = QVBoxLayout(record_box)
        record_vbox.setContentsMargins(0, 0, 0, 0)
        record_title = QLabel(tr("Records"), record_box)
        record_title.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 11, QFont.Bold))
        record_title.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY};")
        
        self.metadata_list = QListWidget(record_box)
        self.metadata_list.setStyleSheet(StyleManager.get_list_style())
        for i, entry in enumerate(self.metadata_entries):
            # 仅显示序号，如 #01, #02
            display_text = f"#{i+1:02d}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.metadata_list.addItem(item)
        self.metadata_list.itemClicked.connect(self.on_metadata_selected)
        
        # Add context menu for removal / 添加右键移除功能
        self.metadata_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.metadata_list.customContextMenuRequested.connect(self._on_metadata_context_menu)
        
        record_vbox.addWidget(record_title)
        record_vbox.addWidget(self.metadata_list)
        
        nav_hbox.addWidget(photo_box, 1)
        nav_hbox.addWidget(record_box, 1)
        left_vbox.addWidget(nav_container)
        
        # --- MIDDLE: Form ---
        mid_widget = QWidget(self)
        mid_vbox = QVBoxLayout(mid_widget)
        mid_vbox.setContentsMargins(0, 0, 0, 0)
        
        mid_title = QLabel(tr("Metadata Editor"), mid_widget)
        mid_title.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 16, QFont.Bold))
        mid_title.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_PRIMARY};")
        mid_vbox.addWidget(mid_title)
        
        scroll = QScrollArea(mid_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("ScrollContent")
        scroll_content.setStyleSheet("background: transparent;")
        scroll_vbox = QVBoxLayout(scroll_content)
        scroll_vbox.setContentsMargins(10, 20, 10, 20)
        scroll_vbox.setSpacing(20)
        
        def add_section(title, parent):
            sect = QWidget(parent)
            sect_layout = QVBoxLayout(sect)
            sect_layout.setContentsMargins(0, 10, 0, 10)
            
            lbl = QLabel(title, sect)
            lbl.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 9, QFont.Bold))
            # 提高分类标题亮度
            lbl.setStyleSheet(f"color: {StyleManager.COLOR_ACCENT}; text-transform: uppercase; letter-spacing: 1px;")
            sect_layout.addWidget(lbl)
            
            line = QFrame(sect)
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet(f"background-color: {StyleManager.COLOR_BORDER}; max-height: 1px;")
            sect_layout.addWidget(line)
            
            f = QFormLayout()
            f.setSpacing(12)
            sect_layout.addLayout(f)
            return sect, f

        s1, f1 = add_section(tr("Gear Info"), scroll_content)
        self.edit_make = QLineEdit(s1)
        self.edit_model = QLineEdit(s1)
        self.edit_lens_make = QLineEdit(s1)
        self.edit_lens_model = QLineEdit(s1)
        
        def add_field(form, label_text, widget):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY};")
            form.addRow(lbl, widget)

        add_field(f1, tr("Camera Make:"), self.edit_make)
        add_field(f1, tr("Camera Model:"), self.edit_model)
        add_field(f1, tr("Lens Make:"), self.edit_lens_make)
        add_field(f1, tr("Lens Model:"), self.edit_lens_model)
        scroll_vbox.addWidget(s1)

        s2, f2 = add_section(tr("Exposure"), scroll_content)
        self.edit_aperture = QLineEdit(s2)
        self.edit_shutter = QLineEdit(s2)
        self.edit_iso = QLineEdit(s2)
        self.edit_focal_length = QLineEdit(s2)
        self.edit_focal_35mm = QLineEdit(s2)
        add_field(f2, tr("Aperture:"), self.edit_aperture)
        add_field(f2, tr("Shutter:"), self.edit_shutter)
        add_field(f2, tr("ISO:"), self.edit_iso)
        add_field(f2, tr("Focal Length:"), self.edit_focal_length)
        add_field(f2, tr("Focal Length (35mm):"), self.edit_focal_35mm)
        scroll_vbox.addWidget(s2)

        s3, f3 = add_section(tr("Context"), scroll_content)
        self.edit_film_stock = QLineEdit(s3)
        self.edit_shot_date = QLineEdit(s3)
        self.edit_location = QLineEdit(s3)
        self.edit_notes = QLineEdit(s3)
        add_field(f3, tr("Film Stock:"), self.edit_film_stock)
        add_field(f3, tr("Shot Date:"), self.edit_shot_date)
        add_field(f3, tr("Location:"), self.edit_location)
        add_field(f3, tr("Notes:"), self.edit_notes)
        scroll_vbox.addWidget(s3)
        
        scroll_vbox.addStretch()
        scroll.setWidget(scroll_content)
        mid_vbox.addWidget(scroll)
        
        # Bottom controls
        bottom = QWidget(mid_widget)
        bot_vbox = QVBoxLayout(bottom)
        
        off_cont = QWidget(bottom)
        off_hbox = QHBoxLayout(off_cont)
        off_hbox.setContentsMargins(0, 0, 0, 0)
        off_lbl = QLabel(tr("Sequence Offset"), off_cont)
        off_lbl.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY};")
        self.offset_spin = QSpinBox(off_cont)
        self.offset_spin.setRange(-20, 20)
        self.offset_spin.valueChanged.connect(self.on_offset_changed)
        self.warning_label = QLabel(off_cont)
        self.warning_label.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY}; font-size: 11px;")
        off_hbox.addWidget(off_lbl)
        off_hbox.addWidget(self.offset_spin)
        off_hbox.addSpacing(30)
        off_hbox.addWidget(self.warning_label, 1)
        bot_vbox.addWidget(off_cont)
        
        btn_cont = QWidget(bottom)
        btn_hbox = QHBoxLayout(btn_cont)
        btn_hbox.setContentsMargins(0, 0, 0, 0)
        btn_hbox.addStretch()
        c_btn = QPushButton(tr("Cancel"), btn_cont)
        c_btn.setStyleSheet(StyleManager.get_button_style(tier='ghost'))
        c_btn.clicked.connect(self.reject)
        w_btn = QPushButton(tr("Write All Files"), btn_cont)
        w_btn.clicked.connect(self.on_write_metadata)
        w_btn.setStyleSheet(StyleManager.get_button_style(tier='primary'))
        btn_hbox.addWidget(c_btn)
        btn_hbox.addWidget(w_btn)
        bot_vbox.addWidget(btn_cont)
        
        mid_vbox.addWidget(bottom)
        
        # --- RIGHT: Preview ---
        right_widget = QWidget(self)
        right_widget.setFixedWidth(350)
        right_vbox = QVBoxLayout(right_widget)
        right_vbox.setContentsMargins(10, 30, 10, 0)
        
        p_title = QLabel(tr("Preview"), right_widget)
        p_title.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 11, QFont.Bold))
        right_vbox.addWidget(p_title)
        
        self.preview_label = QLabel(right_widget)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(320, 320)
        self.preview_label.setStyleSheet("background: transparent; border: none;")
        right_vbox.addWidget(self.preview_label)
        
        self.file_info_label = QLabel("", right_widget)
        self.file_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_info_label.setWordWrap(True)
        right_vbox.addWidget(self.file_info_label)
        right_vbox.addStretch()
        
        # Final layout - Adaptive weighting
        content_layout.addWidget(left_widget, 2)
        content_layout.addWidget(mid_widget, 4)   # Highest priority
        content_layout.addWidget(right_widget, 3)
        main_layout.addWidget(content_widget)
        
        # Styles
        self.setStyleSheet(StyleManager.get_main_style())
        for e in [self.edit_make, self.edit_model, self.edit_lens_make, self.edit_lens_model,
                  self.edit_aperture, self.edit_shutter, self.edit_iso, self.edit_focal_length, self.edit_focal_35mm,
                  self.edit_film_stock, self.edit_shot_date, self.edit_location, self.edit_notes]:
            e.setStyleSheet(StyleManager.get_input_style())

        # Initial mapping parse if data exists (Moved to end to ensure widgets exist)
        if self.raw_headers and self.raw_rows:
            self.on_mapping_changed()
            # Restore visibility which might have been set in mapping_pane init
            self.mapping_pane.setVisible(True) 
            if hasattr(self, 'map_toggle'):
                self.map_toggle.setChecked(True)

    def toggle_mapping_pane(self):
        self.mapping_pane.setVisible(self.map_toggle.isChecked())

    def _smart_match_header(self, header: str) -> str:
        h = header.lower().strip()
        if any(k in h for k in ['date', 'time']): return "DateTimeOriginal"
        if 'lat' in h: return "GPSLatitude"
        if any(k in h for k in ['lon', 'lng']): return "GPSLongitude"
        if any(k in h for k in ['camera', 'body', 'model']): return "Model"
        if 'lens' in h: return "LensModel"
        if 'iso' in h: return "ISO"
        if any(k in h for k in ['aperture', 'f-']): return "FNumber"
        if any(k in h for k in ['shutter', 'speed']): return "ExposureTime"
        if '35mm' in h or 'equivalent' in h: return "FocalLengthIn35mmFormat"
        if 'focal' in h: return "FocalLength"
        if 'film' in h: return "Film"
        return "IGNORE"

    def on_mapping_changed(self):
        """Real-time re-processing using industrial-grade CSVConverter"""
        if not self.raw_rows or not self.mappings: return
        
        # Build the mapping dict format expected by CSVConverter
        mappings_dict = {
            'fields': {},
            'gps_refs': {},
            'id_column': None
        }
        
        for col, config in self.mappings.items():
            field_key = config['field'].currentData()
            if field_key == "ID_SOURCE":
                mappings_dict['id_column'] = col
            elif field_key != "IGNORE":
                mappings_dict['fields'][col] = field_key
                # Add GPS Ref if applicable
                if field_key in ["GPSLatitude", "GPSLongitude"]:
                    mappings_dict['gps_refs'][col] = config['gps'].currentText()
        
        # Use existing converter logic for robustness
        self.metadata_entries = CSVConverter.convert_rows(
            self.raw_rows, 
            mappings_dict, 
            self.photos
        )
        
        self._refresh_metadata_list()
        self.load_photo(self.current_index)

    def _refresh_metadata_list(self):
        if not self.metadata_list: return
        self.metadata_list.clear()
        for i, entry in enumerate(self.metadata_entries):
            display_text = f"#{i+1:02d}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.metadata_list.addItem(item)

    def on_photo_selected(self, item):
        if not item: return
        self._save_current_metadata()
        # Row index in QListWidget matches the index in self.photos after reordering
        # QListWidget 中的行索引在重排后与 self.photos 中的索引一致
        idx = self.photo_list.row(item)
        if idx >= 0:
            self.load_photo(idx)

    def on_metadata_selected(self, item):
        self._save_current_metadata()
        idx = item.data(Qt.ItemDataRole.UserRole)
        self.load_metadata(idx)

    def load_photo(self, photo_index):
        try:
            if 0 <= photo_index < len(self.photos):
                self.current_index = photo_index
                self.photo_list.setCurrentRow(photo_index)
                self._update_preview(photo_index)
                
                meta_idx = photo_index + self.offset
                if 0 <= meta_idx < len(self.metadata_entries):
                    self._update_editor_fields(self.metadata_entries[meta_idx], meta_idx)
                    self.metadata_list.setCurrentRow(meta_idx)
                else:
                    self._update_editor_fields(MetadataEntry(), None)
                    self.metadata_list.clearSelection()
        except RuntimeError: pass

    def load_metadata(self, meta_index):
        try:
            if 0 <= meta_index < len(self.metadata_entries):
                self._update_editor_fields(self.metadata_entries[meta_index], meta_index)
                self.metadata_list.setCurrentRow(meta_index)
                
                p_idx = meta_index - self.offset
                if 0 <= p_idx < len(self.photos):
                    # CRITICAL: Sync current_index so async preview worker accepts the result
                    # 关键：同步 current_index，确保异步预览加载器接受返回结果
                    self.current_index = p_idx
                    self.photo_list.setCurrentRow(p_idx)
                    self._update_preview(p_idx)
                else:
                    self.current_index = -1
                    self.photo_list.clearSelection()
                    self._update_preview(None)
        except RuntimeError: pass

    def _update_editor_fields(self, entry, meta_idx):
        self._current_metadata_idx = meta_idx
        self.edit_make.setText(entry.camera_make or "")
        self.edit_model.setText(entry.camera_model or "")
        self.edit_lens_make.setText(entry.lens_make or "")
        self.edit_lens_model.setText(entry.lens_model or "")
        # Formatting for professional display in editor / 编辑器中的专业显示格式化
        ap_val = (entry.aperture or "").replace('f/', '').replace('F/', '')
        self.edit_aperture.setText(ap_val)
        
        sh_val = entry.shutter_speed or ""
        if sh_val and "/" not in sh_val:
            try:
                clean_sh = sh_val.replace('S', '').replace('s', '').strip()
                f_sh = float(clean_sh)
                if f_sh >= 1.0:
                    sh_val = f"{f_sh:.1f}S"
            except: pass
        self.edit_shutter.setText(sh_val)
        self.edit_iso.setText(entry.iso or "")
        self.edit_film_stock.setText(entry.film_stock or "")
        self.edit_focal_length.setText(entry.focal_length or "")
        self.edit_shot_date.setText(entry.shot_date or "")
        self.edit_location.setText(entry.location or "")
        self.edit_focal_35mm.setText(entry.focal_length_35mm or "")
        self.edit_notes.setText(entry.notes or "")

    def _update_preview(self, photo_idx):
        try:
            if photo_idx is not None and 0 <= photo_idx < len(self.photos):
                p = self.photos[photo_idx]
                dpr = self.devicePixelRatio()
                
                # Use cache if available / 如果有缓存则使用缓存
                if p.file_path in self.thumb_cache:
                    cached_pix = self.thumb_cache[p.file_path]
                    # Ensure aspect ratio is preserved and sharp for high DPI
                    scaled_pix = cached_pix.scaled(self.preview_label.width() * dpr, 
                                                 self.preview_label.height() * dpr, 
                                                 Qt.AspectRatioMode.KeepAspectRatio, 
                                                 Qt.TransformationMode.SmoothTransformation)
                    scaled_pix.setDevicePixelRatio(dpr)
                    self.preview_label.setPixmap(scaled_pix)
                    self.file_info_label.setText(f"{p.file_name}")
                    return

                # Async load to keep UI responsive / 异步加载保持 UI 响应
                if p.file_path in self._loading_thumbnails:
                    return
                
                self.preview_label.setText(tr("Loading preview..."))
                self._loading_thumbnails[p.file_path] = True
                
                # Studio-grade preview resolution (Standardized to 1024)
                worker = ThumbnailWorker(p.file_path, QSize(1024, 1024))
                
                # Explicitly connect to slots for main thread safety
                worker.signals.finished.connect(self._on_thumbnail_ready)
                worker.signals.error.connect(self._on_thumbnail_error_handler)
                self.threadpool.start(worker)
                
                self.file_info_label.setText(f"{p.file_name}")
            else:
                self.preview_label.clear()
                self.preview_label.setText(tr("No Photo Linked"))
                self.file_info_label.setText("")
        except RuntimeError: pass

    def _on_thumbnail_ready(self, path, image):
        """Handle thumbnail completion in main thread"""
        self._loading_thumbnails.pop(path, None)
        dpr = self.devicePixelRatio()
        pix = QPixmap.fromImage(image)
        
        # Check if the photo is still selected
        if 0 <= self.current_index < len(self.photos) and self.photos[self.current_index].file_path == path:
            self.thumb_cache[path] = pix
            scaled_pix = pix.scaled(self.preview_label.width() * dpr, 
                                 self.preview_label.height() * dpr, 
                                 Qt.AspectRatioMode.KeepAspectRatio, 
                                 Qt.TransformationMode.SmoothTransformation)
            scaled_pix.setDevicePixelRatio(dpr)
            self.preview_label.setPixmap(scaled_pix)

    def _on_thumbnail_error_handler(self, path, err):
        """Handle thumbnail error in main thread"""
        self._loading_thumbnails.pop(path, None)
        self.preview_label.setText(tr("Preview Failed"))

    def on_offset_changed(self):
        self._save_current_metadata()
        self.offset = self.offset_spin.value()
        self.load_photo(self.current_index)

    def _save_current_metadata(self):
        if self._current_metadata_idx is None: return
        e = self.metadata_entries[self._current_metadata_idx]
        e.camera_make = self.edit_make.text().strip() or None
        e.camera_model = self.edit_model.text().strip() or None
        e.lens_make = self.edit_lens_make.text().strip() or None
        e.lens_model = self.edit_lens_model.text().strip() or None
        e.aperture = self.edit_aperture.text().strip() or None
        e.shutter_speed = self.edit_shutter.text().strip() or None
        e.iso = self.edit_iso.text().strip() or None
        e.film_stock = self.edit_film_stock.text().strip() or None
        
        # Validate and format Focal Lengths / 验证并格式化焦距
        focal_val = self.edit_focal_length.text().strip()
        if focal_val:
            try: e.focal_length = MetadataValidator.validate_focal_length(focal_val)
            except: e.focal_length = focal_val
        else: e.focal_length = None
            
        f35_val = self.edit_focal_35mm.text().strip()
        if f35_val:
            try: e.focal_length_35mm = MetadataValidator.validate_focal_length(f35_val)
            except: e.focal_length_35mm = f35_val
        else: e.focal_length_35mm = None
            
        e.shot_date = self.edit_shot_date.text().strip() or None
        e.location = self.edit_location.text().strip() or None
        e.notes = self.edit_notes.text().strip() or None

    def check_count_match(self):
        p_c = len(self.photos)
        m_c = len([e for e in self.metadata_entries if any(vars(e).values())])
        if p_c <= m_c:
            self.warning_label.setText(tr("Matched: {matched}/{total}").format(matched=m_c, total=p_c))
            self.warning_label.setStyleSheet("color: #4CAF50;")
        else:
            self.warning_label.setText(tr("Warning: {meta} records but {photo} photos").format(meta=m_c, photo=p_c))
            self.warning_label.setStyleSheet("color: #F44336;")

    def on_write_metadata(self):
        self._save_current_metadata()
        reply = QMessageBox.question(self, tr("Write Metadata"), tr("This will modify EXIF data in all {count} photos. Continue?").format(count=len(self.photos)))
        if reply != QMessageBox.Yes: return
        
        tasks = []
        for i, photo in enumerate(self.photos):
            m_idx = i + self.offset
            if 0 <= m_idx < len(self.metadata_entries):
                entry = self.metadata_entries[m_idx]
                exif = self._build_exif_dict(entry)
                if exif:
                    tasks.append({'file_path': photo.file_path, 'exif_data': exif})
                    
        if not tasks: return
        
        # Emit request signal to MainWindow and close / 向主窗口发射请求信号并关闭
        self.requests_write.emit(tasks)
        self.accept()

    def _build_exif_dict(self, entry: MetadataEntry) -> Dict[str, str]:
        exif = {}
        if entry.camera_make: exif['Make'] = entry.camera_make
        if entry.camera_model: exif['Model'] = entry.camera_model
        if entry.lens_make: exif['LensMake'] = entry.lens_make
        if entry.lens_model: exif['LensModel'] = entry.lens_model
        if entry.aperture: 
            exif['FNumber'] = entry.aperture.replace('f/', '').replace('F/', '').strip()
        if entry.shutter_speed: 
            # Strip 'S' or 's' suffix for EXIF writing / 写入 EXIF 时移除 'S' 后缀
            sh_clean = entry.shutter_speed.replace('S', '').replace('s', '').strip()
            exif['ExposureTime'] = sh_clean
        if entry.iso: exif['ISO'] = entry.iso
        if entry.focal_length: 
            # Ensure only number is written to EXIF if needed, but ExifTool handled "X mm" fine
            # We'll just strip for maximum compatibility
            exif['FocalLength'] = entry.focal_length.replace('mm', '').replace('MM', '').strip()
        if entry.focal_length_35mm: 
            exif['FocalLengthIn35mmFormat'] = entry.focal_length_35mm.replace('mm', '').replace('MM', '').strip()
        if entry.film_stock:
            exif['Film'] = entry.film_stock
            exif['ImageDescription'] = entry.film_stock
        if entry.location:
            gps = gps_utils.parse_gps_to_exif(entry.location)
            if gps:
                exif['GPSLatitude'], exif['GPSLatitudeRef'], exif['GPSLongitude'], exif['GPSLongitudeRef'] = gps
        
        # Shot Date - Map to DateTimeOriginal
        if entry.shot_date:
            # Standardize date format for EXIF: Replace -, / with :
            # 将日期格式标准化为 EXIF 要求的 YYYY:MM:DD HH:MM:SS
            d_clean = entry.shot_date.strip().replace('-', ':').replace('/', ':').replace('.', ':')
            # If it's only date without time, append 00:00:00
            if len(d_clean) == 10 and d_clean.count(':') == 2:
                d_clean += " 00:00:00"
            exif['DateTimeOriginal'] = d_clean
            
        if entry.notes: exif['UserComment'] = entry.notes
        return exif

    def _on_photo_context_menu(self, pos):
        item = self.photo_list.itemAt(pos)
        if not item: return
        
        # Use row index for current state
        idx = self.photo_list.row(item)
        menu = StyleManager.create_menu(self)
        remove_act = menu.addAction(tr("Remove Photo"))
        remove_act.triggered.connect(lambda: self.remove_photo(idx))
        menu.exec(self.photo_list.mapToGlobal(pos))

    def _on_metadata_context_menu(self, pos):
        item = self.metadata_list.itemAt(pos)
        if not item: return
        
        idx = item.data(Qt.ItemDataRole.UserRole)
        menu = StyleManager.create_menu(self)
        remove_act = menu.addAction(tr("Remove Record"))
        remove_act.triggered.connect(lambda: self.remove_metadata_record(idx))
        menu.exec(self.metadata_list.mapToGlobal(pos))

    def remove_photo(self, index):
        if len(self.photos) <= 1:
            QMessageBox.warning(self, tr("Remove Photo"), tr("Cannot remove the last photo"))
            return
        
        reply = QMessageBox.question(self, tr("Remove Photo"), 
                                   tr("Exclude '{name}' from this task?").format(name=self.photos[index].file_name))
        if reply == QMessageBox.Yes:
            self.photos.pop(index)
            self._refresh_photo_list()
            # Safety: clamp index
            new_idx = min(index, len(self.photos) - 1)
            self.load_photo(new_idx)
            self.check_count_match()

    def remove_metadata_record(self, index):
        if len(self.metadata_entries) <= 1:
            QMessageBox.warning(self, tr("Remove Record"), tr("Cannot remove the last record"))
            return
            
        reply = QMessageBox.question(self, tr("Remove Record"), tr("Delete this metadata record?"))
        if reply == QMessageBox.Yes:
            self.metadata_entries.pop(index)
            self._refresh_metadata_list()
            # Safety child load
            new_idx = min(index, len(self.metadata_entries) - 1)
            self.load_metadata(new_idx)
            self.check_count_match()

    def _refresh_photo_list(self):
        self.photo_list.blockSignals(True)
        self.photo_list.clear()
        for i, photo in enumerate(self.photos):
            item = QListWidgetItem(photo.file_name or tr("Photo {num}").format(num=i+1))
            item.setData(Qt.ItemDataRole.UserRole, i)
            # Carry path for robust sync
            item.setData(Qt.ItemDataRole.UserRole + 1, photo.file_path)
            self.photo_list.addItem(item)
        self.photo_list.blockSignals(False)

    def reverse_photo_order(self):
        """Reverse the order of photos in the list / 一键倒序排列照片"""
        selected_path = None
        if self.current_index is not None and 0 <= self.current_index < len(self.photos):
            selected_path = self.photos[self.current_index].file_path
            
        self.photos.reverse()
        self._refresh_photo_list()
        
        # Restore selection by path / 按路径恢复选中状态
        if selected_path:
            for i in range(self.photo_list.count()):
                if self.photo_list.item(i).data(Qt.ItemDataRole.UserRole + 1) == selected_path:
                    self.photo_list.setCurrentRow(i)
                    self.current_index = i
                    break
        
        logger.info("Photos order reversed.")
        # Trigger UI update / 触发界面刷新
        current = self.photo_list.currentItem()
        if current:
            self.on_photo_selected(current)
        elif self.photo_list.count() > 0:
            self.photo_list.setCurrentRow(0)
            self.on_photo_selected(self.photo_list.item(0))

    def _on_photo_reordered(self, parent, start, end, destination, row):
        """Handle Drag & Drop completion / 处理拖拽完成"""
        # Small delay to ensure the list model has finished moving items
        QTimer.singleShot(100, self._sync_photos_from_ui_list)

    def _sync_photos_from_ui_list(self):
        """Snapshot current QListWidget order to internal photos list / 同步 UI 顺序到内存列表"""
        photo_map = {p.file_path: p for p in self.photos}
        new_photos = []
        for i in range(self.photo_list.count()):
            item = self.photo_list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole + 1)
            if path in photo_map:
                new_photos.append(photo_map[path])
        
        if len(new_photos) == len(self.photos):
            self.photos = new_photos
            # Sync selection state / 同步当前选中态
            current = self.photo_list.currentItem()
            if current:
                self.current_index = self.photo_list.row(current)
                logger.info(f"Internal photos sequence synced. Primary focus: {self.current_index}")
                self.on_photo_selected(current)
