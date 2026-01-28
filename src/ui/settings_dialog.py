#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Dialog for DataPrism
DataPrism 设置对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QSpinBox, QCheckBox, QPushButton, QFormLayout, QFileDialog, QWidget, QComboBox
)
from PySide6.QtCore import Qt
from src.core.config import get_config
from src.utils.i18n import tr
from src.ui.style_manager import StyleManager


class SettingsDialog(QDialog):
    """
    Settings dialog to manage application configuration
    管理应用配置的设置对话框
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.setWindowTitle(tr("Settings"))
        self.setMinimumWidth(850) # Increased width for horizontal layout / 增加宽度以适配横屏
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup UI with Hasselblad aesthetics and horizontal layout / 采用哈苏美学与横屏布局设置 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Content content split into two columns / 内容分为左右两栏
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)

        # Style constants / 样式常量
        accent_color = StyleManager.c('accent')
        label_style = f"color: {StyleManager.c('text_secondary')}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;"
        hint_style = f"color: {StyleManager.c('text_secondary')}; font-size: 11px; margin-top: 2px;"
        group_header_style = f"color: {accent_color}; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;"
        input_style = StyleManager.get_input_style()
        
        # Custom CheckBox style
        checkbox_style = f"""
            QCheckBox {{
                color: {StyleManager.c('text_primary')};
                font-size: 12px;
                spacing: 12px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {StyleManager.c('border')};
                border-radius: 4px;
                background-color: #0c0c0e;
            }}
            QCheckBox::indicator:hover {{
                border-color: {accent_color};
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent_color};
                border-color: {accent_color};
            }}
        """
        
        # Helper to add hint labels / 增加提示标签的辅助函数
        def create_form_row(label_text, widget, hint_text=None, has_browse=False):
            lbl = QLabel(tr(label_text))
            lbl.setStyleSheet(label_style)
            lbl.setContentsMargins(0, 8, 0, 0)
            
            field_container = QWidget()
            field_v_layout = QVBoxLayout(field_container)
            field_v_layout.setContentsMargins(0, 0, 0, 0)
            field_v_layout.setSpacing(6)
            
            if has_browse:
                h_layout = QHBoxLayout()
                h_layout.setSpacing(10)
                h_layout.addWidget(widget)
                browse_btn = QPushButton(tr("Browse"))
                browse_btn.setMinimumWidth(80)
                browse_btn.setFixedHeight(34)
                browse_style = StyleManager.get_button_style(tier='primary').replace(
                    "padding: 10px 18px;", 
                    "padding: 0; font-size: 11px; font-weight: 700;"
                )
                browse_btn.setStyleSheet(browse_style)
                browse_btn.clicked.connect(self.browse_exiftool)
                h_layout.addWidget(browse_btn)
                field_v_layout.addLayout(h_layout)
            else:
                field_v_layout.addWidget(widget)
                
            if hint_text:
                hint = QLabel(tr(hint_text))
                hint.setStyleSheet(hint_style)
                hint.setWordWrap(True)
                field_v_layout.addWidget(hint)
            
            return lbl, field_container

        # -- LEFT COLUMN: System & Engine --
        left_column = QWidget()
        left_vbox = QVBoxLayout(left_column)
        left_vbox.setContentsMargins(0, 0, 0, 0)
        
        left_header = QLabel(tr("Engine & System"))
        left_header.setStyleSheet(group_header_style)
        left_vbox.addWidget(left_header)
        
        left_form = QFormLayout()
        left_form.setSpacing(18)
        left_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # ExifTool Path
        self.exiftool_path_edit = QLineEdit()
        self.exiftool_path_edit.setMinimumHeight(34)
        self.exiftool_path_edit.setStyleSheet(input_style)
        left_form.addRow(*create_form_row("ExifTool Path", self.exiftool_path_edit, "Specify the path to exiftool executable", has_browse=True))
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimumHeight(34)
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setSuffix(f" {tr('S')}")
        self.timeout_spin.setStyleSheet(input_style)
        left_form.addRow(*create_form_row("ExifTool Timeout", self.timeout_spin, "Max time to wait for ExifTool (seconds)"))
        
        # Worker Threads
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimumHeight(34)
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setStyleSheet(input_style)
        left_form.addRow(*create_form_row("Worker Threads", self.threads_spin, "Number of parallel worker threads"))

        # Log Level
        self.log_level_combo = QComboBox()
        self.log_level_combo.setMinimumHeight(34)
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setStyleSheet(input_style)
        left_form.addRow(*create_form_row("Log Level", self.log_level_combo, "Detail level of log records"))

        # Log Settings
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setMinimumHeight(34)
        self.log_size_spin.setRange(1, 100)
        self.log_size_spin.setSuffix(" MB")
        self.log_size_spin.setStyleSheet(input_style)
        left_form.addRow(*create_form_row("Log Max Size (MB)", self.log_size_spin, "Maximum size of a single log file in megabytes"))

        self.log_backups_spin = QSpinBox()
        self.log_backups_spin.setMinimumHeight(34)
        self.log_backups_spin.setRange(0, 20)
        self.log_backups_spin.setStyleSheet(input_style)
        left_form.addRow(*create_form_row("Log Backup Count", self.log_backups_spin, "Number of old log files to keep"))

        left_vbox.addLayout(left_form)
        left_vbox.addStretch()

        # -- RIGHT COLUMN: General Behavior --
        right_column = QWidget()
        right_vbox = QVBoxLayout(right_column)
        right_vbox.setContentsMargins(0, 0, 0, 0)

        right_header = QLabel(tr("Workflow & Behavior"))
        right_header.setStyleSheet(group_header_style)
        right_vbox.addWidget(right_header)

        right_form = QFormLayout()
        right_form.setSpacing(12)
        right_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.auto_save_check = QCheckBox(tr("Auto Save Changes"))
        self.auto_save_check.setStyleSheet(checkbox_style)
        right_form.addRow(*create_form_row("", self.auto_save_check, "Automatically save changes to config.json"))
        
        self.confirm_exit_check = QCheckBox(tr("Confirm on Exit"))
        self.confirm_exit_check.setStyleSheet(checkbox_style)
        right_form.addRow(*create_form_row("", self.confirm_exit_check, "Show confirmation dialog before exiting"))
        
        self.show_completion_check = QCheckBox(tr("Show Completion Dialog"))
        self.show_completion_check.setStyleSheet(checkbox_style)
        right_form.addRow(*create_form_row("", self.show_completion_check, "Show summary after batch operations"))
        
        self.overwrite_original_check = QCheckBox(tr("Overwrite Original Files"))
        self.overwrite_original_check.setStyleSheet(checkbox_style)
        right_form.addRow(*create_form_row("", self.overwrite_original_check, "Overwrite photos directly or keep backups"))
        
        self.preserve_date_check = QCheckBox(tr("Preserve File Modify Date"))
        self.preserve_date_check.setStyleSheet(checkbox_style)
        right_form.addRow(*create_form_row("", self.preserve_date_check, "Keep original file system 'Modify Date'"))
        
        self.portable_mode_check = QCheckBox(tr("Portable Mode"))
        self.portable_mode_check.setStyleSheet(checkbox_style)
        right_form.addRow(*create_form_row("", self.portable_mode_check, tr("Store config/history locally next to EXE")))

        right_vbox.addLayout(right_form)
        right_vbox.addStretch()

        # Add columns to content layout / 将两栏加入内容布局
        content_layout.addWidget(left_column, 5) # Left has more complex fields, give more weight
        content_layout.addWidget(right_column, 4)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()
        
        # Buttons / 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.save_btn = QPushButton(tr("Save"))
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setMinimumWidth(100)
        self.save_btn.setStyleSheet(StyleManager.get_button_style(tier='primary'))
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton(tr("Cancel"))
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.setStyleSheet(StyleManager.get_button_style(tier='secondary'))
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(btn_layout)
        self.setStyleSheet(f"background-color: {StyleManager.c('bg_main')};")

    def browse_exiftool(self):
        """Browse for ExifTool executable / 浏览 ExifTool 可执行程序"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("ExifTool Path"), "", "Executable (*.exe);;All Files (*)"
        )
        if file_path:
            self.exiftool_path_edit.setText(file_path)

    def load_settings(self):
        """Load current settings into UI / 将当前设置加载到 UI"""
        self.exiftool_path_edit.setText(self.config.get('exiftool_path', 'exiftool'))
        self.timeout_spin.setValue(self.config.get('exiftool_timeout', 30))
        self.threads_spin.setValue(self.config.get('worker_threads', 2))
        self.auto_save_check.setChecked(self.config.get('auto_save', False))
        self.confirm_exit_check.setChecked(self.config.get('confirm_on_exit', True))
        self.show_completion_check.setChecked(self.config.get('show_completion_dialog', True))
        self.overwrite_original_check.setChecked(self.config.get('overwrite_original', True))
        self.preserve_date_check.setChecked(self.config.get('preserve_modify_date', True))
        self.portable_mode_check.setChecked(self.config.get('portable_mode', False))
        self.log_size_spin.setValue(self.config.get('log_max_size_mb', 10))
        self.log_backups_spin.setValue(self.config.get('log_backup_count', 5))
        
        level = self.config.get('log_level', 'INFO')
        index = self.log_level_combo.findText(level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        
    def save_settings(self):
        """Save UI settings to config / 将 UI 设置保存到配置"""
        self.config.set('exiftool_path', self.exiftool_path_edit.text(), save_immediately=False)
        self.config.set('exiftool_timeout', self.timeout_spin.value(), save_immediately=False)
        self.config.set('worker_threads', self.threads_spin.value(), save_immediately=False)
        self.config.set('auto_save', self.auto_save_check.isChecked(), save_immediately=False)
        self.config.set('confirm_on_exit', self.confirm_exit_check.isChecked(), save_immediately=False)
        self.config.set('show_completion_dialog', self.show_completion_check.isChecked(), save_immediately=False)
        self.config.set('overwrite_original', self.overwrite_original_check.isChecked(), save_immediately=False)
        self.config.set('preserve_modify_date', self.preserve_date_check.isChecked(), save_immediately=False)
        self.config.set('portable_mode', self.portable_mode_check.isChecked(), save_immediately=False)
        self.config.set('log_max_size_mb', self.log_size_spin.value(), save_immediately=False)
        self.config.set('log_backup_count', self.log_backups_spin.value(), save_immediately=False)
        self.config.set('log_level', self.log_level_combo.currentText(), save_immediately=True)
        self.accept()
