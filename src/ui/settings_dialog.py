#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Dialog for DataPrism
DataPrism 设置对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QSpinBox, QCheckBox, QPushButton, QFormLayout, QFileDialog, QWidget
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
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup UI with Hasselblad aesthetics / 采用哈苏美学设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Style constants / 样式常量
        accent_color = StyleManager.c('accent')
        label_style = f"color: {StyleManager.c('text_secondary')}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;"
        hint_style = f"color: {StyleManager.c('text_secondary')}; font-size: 11px; margin-top: 2px;"
        input_style = StyleManager.get_input_style()
        
        # Custom CheckBox style - Cleaner and warning-free / 自定义复选框样式 - 更简洁且无警告
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
        
        # Form layout for settings / 设置的表单布局
        form = QFormLayout()
        form.setSpacing(20)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Helper to add hint labels / 增加提示标签的辅助函数
        def add_setting_row(label_text, widget, hint_text=None, has_browse=False):
            lbl = QLabel(tr(label_text))
            lbl.setStyleSheet(label_style)
            # Add top margin to align with input field
            lbl.setContentsMargins(0, 8, 0, 0)
            
            # Container for the field + hint to ensure perfect alignment
            # 使用容器包裹字段和提示，确保绝对对齐
            field_container = QWidget()
            field_v_layout = QVBoxLayout(field_container)
            field_v_layout.setContentsMargins(0, 0, 0, 0)
            field_v_layout.setSpacing(6)
            
            if has_browse:
                h_layout = QHBoxLayout()
                h_layout.setSpacing(10)
                h_layout.addWidget(widget)
                browse_btn = QPushButton(tr("Browse"))
                browse_btn.setMinimumWidth(90)
                browse_btn.setFixedHeight(34)
                # Use Primary style for maximum visibility / 使用 Primary 风格以获得最大可见度
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
            
            form.addRow(lbl, field_container)

        # ExifTool Path / ExifTool 路径
        self.exiftool_path_edit = QLineEdit()
        self.exiftool_path_edit.setMinimumHeight(34)
        self.exiftool_path_edit.setStyleSheet(input_style)
        add_setting_row("ExifTool Path", self.exiftool_path_edit, "Specify the path to exiftool executable", has_browse=True)
        
        # Timeout / 超时
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimumHeight(34)
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setSuffix(f" {tr('S')}")
        self.timeout_spin.setStyleSheet(input_style)
        add_setting_row("ExifTool Timeout", self.timeout_spin, "Max time to wait for ExifTool (seconds)")
        
        # Worker Threads / 工作线程
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimumHeight(34)
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setStyleSheet(input_style)
        add_setting_row("Worker Threads", self.threads_spin, "Number of parallel worker threads")
        
        # Behavior Checkboxes / 行为复选框
        self.auto_save_check = QCheckBox(tr("Auto Save Changes"))
        self.auto_save_check.setStyleSheet(checkbox_style)
        add_setting_row("", self.auto_save_check, "Automatically save changes to config.json")
        
        self.confirm_exit_check = QCheckBox(tr("Confirm on Exit"))
        self.confirm_exit_check.setStyleSheet(checkbox_style)
        add_setting_row("", self.confirm_exit_check, "Show confirmation dialog before exiting")
        
        self.show_completion_check = QCheckBox(tr("Show Completion Dialog"))
        self.show_completion_check.setStyleSheet(checkbox_style)
        add_setting_row("", self.show_completion_check, "Show summary after batch operations")
        
        self.overwrite_original_check = QCheckBox(tr("Overwrite Original Files"))
        self.overwrite_original_check.setStyleSheet(checkbox_style)
        add_setting_row("", self.overwrite_original_check, "Overwrite photos directly or keep backups")
        
        self.preserve_date_check = QCheckBox(tr("Preserve File Modify Date"))
        self.preserve_date_check.setStyleSheet(checkbox_style)
        add_setting_row("", self.preserve_date_check, "Keep original file system 'Modify Date'")
        
        self.portable_mode_check = QCheckBox(tr("Portable Mode"))
        self.portable_mode_check.setStyleSheet(checkbox_style)
        add_setting_row("", self.portable_mode_check, tr("Store config/history locally next to EXE"))
        
        layout.addLayout(form)
        layout.addStretch()
        
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
        
        layout.addLayout(btn_layout)
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
        self.config.set('portable_mode', self.portable_mode_check.isChecked(), save_immediately=True)
        self.accept()
