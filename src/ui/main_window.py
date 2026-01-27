#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window of DataPrism with macOS aesthetics
DataPrism 的主窗口，采用 macOS 美学设计
"""

from pathlib import Path
from typing import List
import re

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QFileDialog, QTableView, QHeaderView, QFormLayout, QGridLayout,
    QMessageBox, QProgressDialog, QDialog, QLineEdit, QPlainTextEdit,
    QComboBox, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QEvent
from PySide6.QtGui import QFont, QPixmap, QTransform

from src.core.photo_model import PhotoDataModel
from src.core.exif_worker import ExifToolWorker
from src.core.json_parser import FilmLogParser
from src.core.json_matcher import PhotoMatcher
from src.core.metadata_parser import MetadataParser
from src.ui.metadata_editor_dialog import MetadataEditorDialog
from src.ui.settings_dialog import SettingsDialog
from src.utils.i18n import tr, toggle_language, get_current_language
from src.utils.logger import get_logger
from src.ui.style_manager import StyleManager
from src.ui.borderless_delegate import BorderlessDelegate
from src.core.config import get_config
from src.ui.borderless_table_view import BorderlessTableView
from src.ui.borderless_style import BorderlessStyle

logger = get_logger('DataPrism.MainWindow')


class HistoryComboBox(QComboBox):
    """
    Subclass to prevent popup closing when context menu is opened.
    防止上下文菜单打开时关闭弹出窗口的子类。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._skip_hide = False
        # Install event filter on view and viewport to catch clicks early
        # 在视图和视口上安装事件过滤器以尽早捕获点击
        self.view().installEventFilter(self)
        self.view().viewport().installEventFilter(self)
        
    def hidePopup(self):
        if self._skip_hide:
            return
        super().hidePopup()
        
    def set_skip_hide(self, skip: bool):
        self._skip_hide = skip

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                self._skip_hide = True
        return super().eventFilter(obj, event)


class MainWindow(QMainWindow):
    """Main application window / 主应用窗口"""

    start_exif_read = Signal(list)
    start_batch_write = Signal(list)
    start_single_write = Signal(str, dict)

    def __init__(self):
        """Initialize main window / 初始化主窗口"""
        super().__init__()
        self.setWindowTitle("DataPrism")
        self.setGeometry(100, 100, 1200, 800)
        self.model = PhotoDataModel(self)
        self.supported_ext = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng"}
        self.progress_dialog = None  # Progress dialog instance
        self._setup_worker()
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components with macOS aesthetics / 设置 UI 组件，采用 macOS 美学"""
        # Create central widget and main layout
        # 创建中央组件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for clean look
        # 移除边距以获得简洁外观
        
        # Left sidebar - Filters and presets
        # 左侧栏 - 过滤器和预设
        left_widget = QWidget()
        left_widget.setObjectName("Sidebar")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(12, 20, 12, 20)
        left_layout.setSpacing(10)
        
        left_layout.addSpacing(10)
        
        # Metadata Import button (Moved to TOP) / 导入元数据按钮（移至顶部）
        self.json_import_btn = QPushButton(f"{tr('Import Metadata')}")
        self.json_import_btn.setFixedHeight(44)
        self.json_import_btn.setStyleSheet(StyleManager.get_button_style(tier='primary'))
        self.json_import_btn.clicked.connect(self.import_metadata)
        left_layout.addWidget(self.json_import_btn)
        
        left_layout.addSpacing(10)
        
        # Quick Write Section (Now below Import) / 一键写入区域（现在位于导入下方）
        self.sidebar_title = QLabel(tr("Quick Write"))
        self.sidebar_title.setObjectName("SidebarTitle")
        left_layout.addWidget(self.sidebar_title)
        
        self.quick_camera_make = QLineEdit()
        self.quick_camera_make.setPlaceholderText(tr("Camera Make"))
        
        # Smart History Comboboxes / 智能历史组合框
        self.quick_camera_model = HistoryComboBox()
        self.quick_camera_model.setEditable(True)
        self.quick_camera_model.lineEdit().setPlaceholderText(tr("Camera Model"))
        # self.quick_camera_model.setInsertPolicy(QComboBox.NoInsert) # Manually handled / 手动处理
        
        self.quick_lens_make = QLineEdit()
        self.quick_lens_make.setPlaceholderText(tr("Lens Make"))
        
        self.quick_lens_model = HistoryComboBox()
        self.quick_lens_model.setEditable(True)
        self.quick_lens_model.lineEdit().setPlaceholderText(tr("Lens Model"))
        
        self.quick_focal = QLineEdit()
        self.quick_focal.setPlaceholderText(tr("Focal Length"))
        self.quick_focal_35mm = QLineEdit()
        self.quick_focal_35mm.setPlaceholderText(tr("Focal Length (35mm)"))
        
        self.quick_film = HistoryComboBox()
        self.quick_film.setEditable(True)
        self.quick_film.lineEdit().setPlaceholderText(tr("Film Stock"))
        
        # Initialize History / 初始化历史记录
        self._init_quick_write_history()
        
        for edit in [self.quick_camera_make, self.quick_camera_model, self.quick_lens_make, self.quick_lens_model, self.quick_focal, self.quick_focal_35mm, self.quick_film]:
            edit.setStyleSheet(StyleManager.get_input_style().replace("padding: 8px 12px;", "padding: 6px 10px; font-size: 11px;"))
            left_layout.addWidget(edit)

        # Connect auto-fill signals / 连接自动填充信号
        self.quick_camera_model.currentTextChanged.connect(self._on_camera_model_changed)
        self.quick_lens_model.currentTextChanged.connect(self._on_lens_model_changed)
            
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.quick_apply_btn = QPushButton(tr("Apply to All"))
        self.quick_apply_btn.setMinimumHeight(36)
        self.quick_apply_btn.setStyleSheet(StyleManager.get_button_style(tier='secondary'))
        self.quick_apply_btn.clicked.connect(self.on_quick_apply)
        
        self.quick_apply_selected_btn = QPushButton(tr("Apply to Selected"))
        self.quick_apply_selected_btn.setMinimumHeight(36)
        self.quick_apply_selected_btn.setStyleSheet(StyleManager.get_button_style(tier='secondary'))
        self.quick_apply_selected_btn.clicked.connect(self.on_quick_apply_selected)
        
        btn_layout.addWidget(self.quick_apply_btn)
        btn_layout.addWidget(self.quick_apply_selected_btn)
        left_layout.addLayout(btn_layout)
        
        left_layout.addStretch()

        # Bottom Controls (Settings & Language) / 底部控制件（设置与语言）
        bottom_ctrl_layout = QHBoxLayout()
        bottom_ctrl_layout.setSpacing(8)
        
        # Settings button / 设置按钮
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(40, 32)
        self.settings_btn.setStyleSheet(StyleManager.get_button_style(tier='secondary').replace("padding: 10px 18px;", "padding: 0; font-size: 18px;"))
        self.settings_btn.setToolTip(tr("Settings"))
        self.settings_btn.clicked.connect(self.show_settings)
        
        # Language toggle button / 语言切换按钮
        self.lang_btn = QPushButton(tr("EN") if get_current_language() == 'zh' else tr("中"))
        self.lang_btn.setFixedSize(40, 32)
        self.lang_btn.setStyleSheet(StyleManager.get_button_style(tier='primary').replace("padding: 10px 18px;", "padding: 4px 8px;"))
        self.lang_btn.clicked.connect(self.toggle_language)
        
        # About button / 关于按钮
        self.about_btn = QPushButton("ℹ")
        self.about_btn.setFixedSize(40, 32)
        self.about_btn.setStyleSheet(StyleManager.get_button_style(tier='secondary').replace("padding: 10px 18px;", "padding: 0; font-size: 16px; font-weight: bold;"))
        self.about_btn.setToolTip(tr("About"))
        self.about_btn.clicked.connect(self.show_about)
        
        bottom_ctrl_layout.addStretch()
        bottom_ctrl_layout.addWidget(self.settings_btn)
        bottom_ctrl_layout.addWidget(self.lang_btn)
        bottom_ctrl_layout.addWidget(self.about_btn)
        left_layout.addLayout(bottom_ctrl_layout)
        left_widget.setMaximumWidth(220)
        left_widget.setMinimumWidth(180)
        
        # Main content area - Grid/List view
        # 主内容区域 - 网格/列表视图
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Top bar with buttons / 顶部栏按钮
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)
        top_bar.setContentsMargins(0, 5, 0, 15)

        self.browse_btn = QPushButton(tr("Add Photos"))
        self.browse_btn.setMinimumHeight(36)
        self.browse_btn.setStyleSheet(StyleManager.get_button_style())
        self.browse_btn.clicked.connect(self.browse_files)
        top_bar.addWidget(self.browse_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton(f"{tr('Refresh EXIF')}")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setStyleSheet(StyleManager.get_button_style(tier='primary'))
        self.refresh_btn.clicked.connect(self.refresh_exif)
        top_bar.addWidget(self.refresh_btn)
        
        top_bar.addStretch()
        
        center_layout.addLayout(top_bar)
        
        self.table_view = BorderlessTableView()
        self.table_view.setModel(self.model)
        center_layout.addWidget(self.table_view, stretch=0)

        # Placeholder (Below headers when empty) / 占位符（空态时在表头下方）
        self.placeholder = QLabel(tr("Click 'Add Photos' button to import photos"))
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                color: #8e8e93;
                font-size: 14px;
                padding: 40px 100px;
            }
        """)
        center_layout.addWidget(self.placeholder, stretch=1)

        # Log Console (Bottom position) / 日志控制台（底部位置）
        self.console_card = QWidget()
        self.console_card.setObjectName("ConsoleCard")
        self.console_card.setStyleSheet(f"""
            QWidget#ConsoleCard {{
                background-color: #1c1c1e;
                border-top: 1px solid {StyleManager.COLOR_BORDER};
            }}
        """)
        self.console_card.setFixedHeight(180)
        console_layout = QVBoxLayout(self.console_card)
        console_layout.setContentsMargins(15, 10, 15, 10)
        
        console_title = QLabel(tr("Process Status"))
        console_title.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY}; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px;")
        console_layout.addWidget(console_title)
        
        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFrameShape(QPlainTextEdit.Shape.NoFrame)
        self.log_console.setStyleSheet(f"""
            QPlainTextEdit {{
                background: transparent;
                color: #8e8e93;
                font-family: {StyleManager.FONT_FAMILY_MONO};
                font-size: 11px;
                line-height: 1.5;
            }}
        """)
        console_layout.addWidget(self.log_console)
        center_layout.addWidget(self.console_card)

        header = self.table_view.horizontalHeader()
        # Enable interactive column resizing and stretch last section
        # 启用交互式列宽调整并拉伸最后一列
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setHighlightSections(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # CRITICAL: Disable all visual separators / 关键：禁用所有视觉分隔符
        header.setSectionsClickable(False)  # Disable section interaction / 禁用区块交互
        header.setSectionsMovable(False)    # Disable section reordering / 禁用区块重排
        header.setMinimumSectionSize(60)    # Minimum width for readability / 最小宽度以保证可读性
        
        # Industrial Interactive Layout: Enable manual resizing for all columns
        # 工业级交互式布局：允许手动调整所有列宽
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Initial smart sizing: Set sensible starting widths for columns
        # 初始智能调宽：设置合理的起始宽度，防止关键信息被截断
        header.resizeSection(0, 150)  # File / 文件名
        header.resizeSection(10, 160) # Film Stock / 胶卷型号 (Fix truncation)
        header.resizeSection(11, 200) # Location / 位置
        header.resizeSection(12, 140) # Date / 日期
        
        # For technical parameters, use a balanced medium width
        # 对于技术参数，使用均衡的适中宽度
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            header.resizeSection(i, 90)
        
        # Stretch last section to utilize remaining horizontal space
        # 拉伸最后一列以利用剩余的水平空间
        header.setStretchLastSection(True)
        
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.verticalHeader().setDefaultSectionSize(52)  # Breathable row height
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # CRITICAL: Disable frame and all visual artifacts
        self.table_view.setFrameShape(QTableView.Shape.NoFrame)
        self.table_view.setFrameShadow(QTableView.Shadow.Plain)
        self.table_view.setLineWidth(0)
        self.table_view.setMidLineWidth(0)
        
        # Ultra-precision style sync handled via StyleManager CSS
        # 顶级视觉同步已由 StyleManager CSS 统一接管
        self.table_view.setStyleSheet(StyleManager.get_table_style())
        
        # Apply custom style to disable Qt's selection border rendering
        self.table_view.setStyle(BorderlessStyle())
        
        # Apply custom borderless delegate
        self.borderless_delegate = BorderlessDelegate(self)
        self.table_view.setItemDelegate(self.borderless_delegate)
        
        # Connect selection changed / 连接选择变化
        self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        # 右侧检查器面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        
        self.inspector_title = QLabel(tr("Inspector"))
        self.inspector_title.setFont(QFont(StyleManager.FONT_FAMILY_MAIN, 11, QFont.Bold))
        self.inspector_title.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY}; text-transform: uppercase; letter-spacing: 2.5px; padding: 10px 0;")
        right_layout.addWidget(self.inspector_title)
        # 1. Thumbnail Card (置顶 - 强化居中黑盒设计)
        self.thumb_card = QWidget()
        self.thumb_card.setObjectName("CinemaBox")
        self.thumb_card.setFixedSize(280, 190) # Explicit box size
        # Force black background and border / 强制黑色背景与边框
        self.thumb_card.setStyleSheet(f"""
            QWidget#CinemaBox {{
                background-color: #000000;
                border: 1px solid {StyleManager.c("border")};
                border-radius: 4px;
            }}
        """)
        
        thumb_layout = QVBoxLayout(self.thumb_card)
        thumb_layout.setContentsMargins(0, 10, 0, 10) # 10px vertical breath margins / 10px 垂直呼吸边距
        
        self.thumb_label = QLabel()
        # Scale pixmap to fit this area while maintaining aspect ratio
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setStyleSheet("border: none; background: transparent;")
        thumb_layout.addWidget(self.thumb_label)
        
        # Center the box itself in the right layout / 在右侧布局中居中整个盒子
        right_layout.addWidget(self.thumb_card, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 2. Rotation Controls (独立布局 - 移出卡片以获得更多呼吸感)
        rotate_layout = QHBoxLayout()
        rotate_layout.setContentsMargins(0, 5, 0, 10)
        rotate_layout.setSpacing(15)
        
        # Reinforce with injected CSS to override StyleManager defaults
        # 使用注入式 CSS 强制覆盖 StyleManager 的默认字号，确保加粗加大 (Ultra-Bold 900)
        btn_style_base = StyleManager.get_button_style('primary')
        large_icon_css = " QPushButton { font-size: 24px; font-weight: 900; padding: 2px; } "
        
        self.rotate_ccw_btn = QPushButton("↺")
        self.rotate_ccw_btn.setToolTip(tr("Rotate Left"))
        self.rotate_ccw_btn.setFixedSize(48, 34) # Refined minimalist size
        self.rotate_ccw_btn.setStyleSheet(btn_style_base + large_icon_css)
        self.rotate_ccw_btn.clicked.connect(lambda: self.rotate_photo(-90))
        
        self.rotate_cw_btn = QPushButton("↻")
        self.rotate_cw_btn.setToolTip(tr("Rotate Right"))
        self.rotate_cw_btn.setFixedSize(48, 34) # Refined minimalist size
        self.rotate_cw_btn.setStyleSheet(btn_style_base + large_icon_css)
        self.rotate_cw_btn.clicked.connect(lambda: self.rotate_photo(90))
        
        rotate_layout.addStretch()
        rotate_layout.addWidget(self.rotate_ccw_btn)
        rotate_layout.addWidget(self.rotate_cw_btn)
        rotate_layout.addStretch()
        
        right_layout.addLayout(rotate_layout)

        
        




        
        
        # Exposure Section with LCD-style Panels
        exposure_card = QWidget()
        exposure_card.setObjectName("Card")
        exposure_card.setStyleSheet(StyleManager.get_card_style())
        exposure_card_layout = QVBoxLayout(exposure_card)
        
        self.exposure_label = QLabel(tr("Digital Back Display"))
        self.exposure_label.setStyleSheet(f"""
            color: #555557; 
            font-size: 10px; 
            font-weight: 800; 
            text-transform: uppercase; 
            letter-spacing: 1.5px;
            padding: 12px 12px 2px 12px;
        """)
        exposure_card_layout.addWidget(self.exposure_label)
        
        lcd_container = QHBoxLayout()
        lcd_container.setContentsMargins(10, 10, 10, 10)
        lcd_container.setSpacing(8)
        
        def create_lcd_panel(label_text, object_name_suffix):
            panel = QWidget()
            panel.setObjectName("LCDPanel")
            p_layout = QVBoxLayout(panel)
            p_layout.setContentsMargins(12, 10, 12, 10)
            p_layout.setSpacing(4)
            
            lbl = QLabel(label_text)
            lbl.setObjectName(f"LCDLabel_{object_name_suffix}")
            p_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            
            val = QLabel("--")
            val.setObjectName(f"LCDValue_{object_name_suffix}")
            p_layout.addWidget(val, alignment=Qt.AlignmentFlag.AlignCenter)
            return panel, lbl, val

        ap_panel, self.ap_title_label, self.info_aperture = create_lcd_panel(tr("Aperture"), "Ap")
        sh_panel, self.sh_title_label, self.info_shutter = create_lcd_panel(tr("Shutter"), "Sh")
        iso_panel, self.iso_title_label, self.info_iso = create_lcd_panel(tr("ISO"), "Iso")
        
        lcd_container.addWidget(ap_panel, 1)
        lcd_container.addWidget(sh_panel, 1)
        lcd_container.addWidget(iso_panel, 1)
        
        exposure_card_layout.addLayout(lcd_container)
        
        # Apply LCD styles globally to the card for optimal cascading
        # 在 Card 层级统一应用 LCD 样式以获得最佳层叠效果
        exposure_card.setStyleSheet(StyleManager.get_card_style() + StyleManager.get_lcd_style())
        right_layout.addWidget(exposure_card)
        
        # 3. Basic Info Section (底部的元数据细节)
        basic_card = QWidget()
        basic_card.setObjectName("Card")
        basic_card.setStyleSheet(StyleManager.get_card_style())
        basic_card_layout = QVBoxLayout(basic_card)
        basic_card_layout.setContentsMargins(15, 12, 15, 15)
        
        self.basic_label = QLabel(tr("Basic Info"))
        self.basic_label.setStyleSheet(f"color: {StyleManager.COLOR_TEXT_SECONDARY}; font-size: 8px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px;")
        basic_card_layout.addWidget(self.basic_label)
        
        form = QFormLayout()
        form.setVerticalSpacing(8)
        form.setContentsMargins(0, 10, 0, 0)
        # Ensure fields can grow vertically to accommodate wrapped text / 确保字段可以垂直增长以容纳自动换行文本
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        self.info_file = QLabel("--")
        self.info_camera_make = QLabel("--")
        self.info_camera_model = QLabel("--")
        self.info_lens_make = QLabel("--")
        self.info_lens_model = QLabel("--")
        self.info_film = QLabel("--")
        self.info_focal_native = QLabel("--")
        self.info_focal_35mm = QLabel("--")
        self.info_location = QLabel("--")
        self.info_date = QLabel("--")
        self.info_status = QLabel("--")
        
        # High-end technical monospace style / 高端技术等宽字体样式
        value_style = f"color: {StyleManager.COLOR_TEXT_PRIMARY}; font-size: {StyleManager.FONT_SIZE_SMALL}; font-family: {StyleManager.FONT_FAMILY_MONO};"
        for lbl in [self.info_file, self.info_camera_make, self.info_camera_model, self.info_lens_make, self.info_lens_model, self.info_film, self.info_focal_native, self.info_focal_35mm, self.info_location, self.info_date, self.info_status]:
            lbl.setStyleSheet(value_style)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setWordWrap(True)
            # Allow vertical expansion for wrapped text / 允许换行文本垂直扩展
            lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        
        # Label style / 标签样式
        label_style = f"color: {StyleManager.COLOR_TEXT_SECONDARY}; font-size: {StyleManager.FONT_SIZE_TINY}; font-weight: {StyleManager.FONT_WEIGHT_MEDIUM}; letter-spacing: 0.5px;"
        # Use GridLayout instead of FormLayout for better control over wrapping/height
        # 使用网格布局代替表单布局，以更好地控制换行/高度
        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setContentsMargins(0, 10, 0, 0)
        grid.setColumnStretch(1, 1) # Allow value column to expand / 允许值列扩展

        row = 0
        def add_row(label, value):
            nonlocal row
            # Label aligns top-left to handle multi-line string values gracefully
            # 标签左上对齐，以优雅地处理多行字符串值
            grid.addWidget(label, row, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(value, row, 1)
            
            # Apply label style directly here
            label.setStyleSheet(label_style)
            row += 1

        self.file_label = QLabel(tr("File:"))
        self.camera_make_label = QLabel(tr("Camera Make:"))
        self.camera_model_label = QLabel(tr("Camera Model:"))
        self.lens_make_label = QLabel(tr("Lens Make:"))
        self.lens_model_label = QLabel(tr("Lens Model:"))
        self.film_label = QLabel(tr("Film Stock:"))
        self.focal_native_label = QLabel(tr("Focal Length:"))
        self.focal_35mm_label = QLabel(tr("Focal Length (35mm):"))
        self.location_label = QLabel(tr("Location:"))
        self.date_label = QLabel(tr("Date:"))
        self.status_label = QLabel(tr("Status:"))

        add_row(self.file_label, self.info_file)
        add_row(self.camera_make_label, self.info_camera_make)
        add_row(self.camera_model_label, self.info_camera_model)
        add_row(self.lens_make_label, self.info_lens_make)
        add_row(self.lens_model_label, self.info_lens_model)
        add_row(self.film_label, self.info_film)
        add_row(self.focal_native_label, self.info_focal_native)
        add_row(self.focal_35mm_label, self.info_focal_35mm)
        add_row(self.location_label, self.info_location)
        add_row(self.date_label, self.info_date)
        add_row(self.status_label, self.info_status)
        
        basic_card_layout.addLayout(grid)
        right_layout.addWidget(basic_card)
        right_layout.addStretch()
        
        right_widget.setFixedWidth(300)
        
        # Add sections to main layout with splitter for resizing
        # 使用分割条添加到主布局以支持调整大小
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(center_widget)
        splitter.addWidget(right_widget)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)
        
        # Set initial sizes (ratio: 180:800:300)
        # 设置初始尺寸（比例：180:800:300）
        splitter.setSizes([180, 820, 280])
        
        main_layout.addWidget(splitter)
        
        # Apply global styles from StyleManager
        self.setStyleSheet(StyleManager.get_main_style() + StyleManager.get_sidebar_style())

        # Initialize layout state / 初始化布局状态
        self._update_layout_factors()

    def on_files_dropped(self, file_paths: List[str]):
        """Callback when files are imported / 当文件被导入时的回调"""
        unique_files = [p for p in file_paths if p not in {item.file_path for item in self.model.photos}]
        if unique_files:
            self.model.add_photos(unique_files)
            self.queue_exif_read(unique_files)
            self.add_log(tr("Imported {count} file(s).").format(count=len(unique_files)))
        
        # Update layout factors
        self._update_layout_factors()
        logger.info(f"Imported {len(unique_files)} files")

    def _update_layout_factors(self):
        """Adjust stretch based on photo count / 根据照片数量调整拉伸系数"""
        total = self.model.rowCount()
        is_empty = (total == 0)
        self.placeholder.setVisible(is_empty)
        
        layout = self.table_view.parentWidget().layout()
        if is_empty:
            layout.setStretch(1, 0) # table_view
            layout.setStretch(2, 1) # placeholder
            self.table_view.setFixedHeight(self.table_view.horizontalHeader().height() + 2)
        else:
            layout.setStretch(1, 1) # table_view
            layout.setStretch(2, 0) # placeholder
            self.table_view.setMinimumHeight(0)
            self.table_view.setMaximumHeight(16777215)

    # --- File dialog import / 通过对话框导入 ---
    def browse_files(self):
        """Open file dialog to import images / 打开文件对话框导入图像"""
        from src.core.config import get_config
        cfg = get_config()
        last_path = cfg.get('last_import_path', '')
        
        filters = tr("Images (*.jpg *.jpeg *.png *.tif *.tiff *.dng)")
        files, _ = QFileDialog.getOpenFileNames(self, tr("Select photos"), last_path, filters)
        if files:
            # Save the directory of the first file / 保存第一个文件所在的目录
            new_path = str(Path(files[0]).parent)
            cfg.set('last_import_path', new_path)
            self.on_files_dropped(files)

    def show_settings(self):
        """Show settings dialog / 显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Refresh anything that needs immediate update if necessary
            # 如果需要，刷新任何需要立即更新的内容
            self.add_log(tr("Settings updated"))

    def show_about(self):
        """Show about dialog / 显示关于对话框"""
        QMessageBox.about(
            self,
            tr("About DataPrism"),
            tr("DataPrism v1.0.0\nA professional EXIF metadata editor.")
        )

    # --- Worker wiring / 工作者连接 ---
    def _setup_worker(self):
        """Initialize ExifTool worker thread / 初始化 ExifTool 工作线程"""
        self.worker = ExifToolWorker()
        self.worker_thread = QThread(self)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        # Connect signals
        self.worker.read_finished.connect(self.on_exif_read_results)
        self.worker.write_finished.connect(self.on_exif_write_results)
        self.worker.error_occurred.connect(self.on_exif_error)
        self.worker.progress.connect(self.on_exif_progress)
        self.worker.log_message.connect(self.add_log)
        
        self.start_exif_read.connect(self.worker.read_exif)
        self.start_batch_write.connect(self.worker.batch_write_exif)
        self.start_single_write.connect(self.worker.write_exif)
        
        # Connect model signals for inline editing via MainWindow delegator
        # 通过 MainWindow 委托信号连接模型的内联编辑
        self.model.dataChangedForWrite.connect(self.start_single_write)

        # Ensure the thread stops when window closes
        self.destroyed.connect(lambda: self._stop_worker())

    def queue_exif_read(self, file_paths: List[str], show_progress: bool = False):
        """Queue EXIF read in worker thread / 在工作线程中排队读取 EXIF
        
        Args:
            file_paths: List of file paths to read / 要读取的文件路径列表
            show_progress: Whether to show progress dialog / 是否显示进度对话框
        """
        if not file_paths:
            return
        
        # Show progress dialog if requested
        if show_progress:
            self.progress_dialog = QProgressDialog(
                tr("Reading EXIF data..."),
                None,
                0,
                100,
                self
            )
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setWindowTitle(tr("Refresh EXIF"))
            self.progress_dialog.show()
        
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
        # Emit signal to run in worker thread (queued connection)
        self.start_exif_read.emit(file_paths)

    def on_exif_read_results(self, results: dict):
        """Handle EXIF read results / 处理 EXIF 读取结果"""
        for file_path, exif_data in results.items():
            if isinstance(exif_data, dict):
                self.model.set_exif_data(file_path, exif_data)
        
        self._refresh_inspector()
        
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def on_exif_write_results(self, results: dict):
        """Handle EXIF write results (Internal/Single/Batch) / 处理 EXIF 写入结果"""
        if results.get("batch_write"):
            # Batch summary is handled by the temporary connection in execute_metadata_write_tasks or here
            # We'll let MainWindow level logic handle batch status if needed
            pass
        elif "status" in results and results["status"] == "success" and "file" in results:
            # Single write success
            file_path = results["file"]
            logger.info(f"Write successful for {file_path}")
            self.add_log(tr("Successfully wrote metadata to {file}").format(file=file_path))
            # Optional: silent refresh if needed

    def on_exif_progress(self, progress: int):
        """Handle progress update / 处理进度更新
        
        Args:
            progress: Progress percentage (0-100) / 进度百分比 (0-100)
        """
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)

    def on_exif_error(self, error_msg: str):
        """Handle worker errors / 处理工作线程错误"""
        logger.error(f"EXIF worker error: {error_msg}")
        self.add_log(tr("Error: {msg}").format(msg=error_msg))

    def on_selection_changed(self, *_):
        """Update inspector when selection changes / 选择变化时更新检查器"""
        self._refresh_inspector()

    def _refresh_inspector(self):
        """Refresh inspector panel based on current selection / 根据当前选择刷新检查器"""
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            self.info_file.setText("-")
            self.info_camera_make.setText("-")
            self.info_camera_model.setText("-")
            self.info_lens_make.setText("-")
            self.info_lens_model.setText("-")
            self.info_film.setText("-")
            self.info_location.setText("-")
            self.info_date.setText("-")
            self.info_status.setText("-")
            self.info_aperture.setText("-")
            self.info_shutter.setText("-")
            self.info_iso.setText("-")
            self.thumb_label.clear()
            return
        row = selection[0].row()
        photo = self.model.photos[row]
        exif = photo.exif_data or {}
        self.info_file.setText(str(photo.file_name))
        self.info_camera_make.setText(str(exif.get("Make", "--")) if photo.exif_data else "--")
        self.info_camera_model.setText(str(exif.get("Model", "--")) if photo.exif_data else "--")
        self.info_lens_make.setText(str(exif.get("LensMake", "--")) if photo.exif_data else "--")
        self.info_lens_model.setText(str(exif.get("LensModel", "--")) if photo.exif_data else "--")
        self.info_film.setText(str(photo.film_stock or exif.get("Film", "--")))
        def format_focal(val):
            if not val or val == "--": return "--"
            val = str(val).replace('.0 ', ' ').replace('.0', '')
            if val.replace('mm', '').strip().isdigit() and 'mm' not in val.lower():
                val = f"{val.strip()} mm"
            return val

        self.info_focal_native.setText(format_focal(photo.focal_length or exif.get("FocalLength", "--")))
        self.info_focal_35mm.setText(format_focal(photo.focal_length_35mm or exif.get("FocalLengthIn35mmFormat", "--")))
        
        # Prefer cached location; else try GPS; else description
        gps_lat = exif.get("GPSLatitude")
        gps_lon = exif.get("GPSLongitude")
        gps_str = f"{gps_lat}, {gps_lon}" if gps_lat and gps_lon else None
        self.info_location.setText(photo.location or gps_str or exif.get("ImageDescription", "--"))
        self.info_date.setText(photo.exif_data.get("DateTimeOriginal", "--") if photo.exif_data else "--")
        status_display = tr(photo.status) + (tr(" (Modified)") if photo.is_modified else "")
        self.info_status.setText(status_display)
        
        # Exposure data / 曝光数据
        self.info_aperture.setText(f"{photo.aperture}" if photo.aperture else "--")
        
        # Shutter formatting: >= 1s adds 'S', fractions have no suffix
        # 快门格式：1s 及以上带 S，分数不带后缀
        shutter_display = "--"
        if photo.shutter_speed:
            if "/" in photo.shutter_speed:
                shutter_display = photo.shutter_speed
            else:
                try:
                    clean_sh = photo.shutter_speed.replace('S', '').replace('s', '').strip()
                    s_val = float(clean_sh)
                    shutter_display = f"{s_val:.1f}S" if s_val >= 1.0 else f"{s_val}"
                except:
                    shutter_display = photo.shutter_speed
        self.info_shutter.setText(shutter_display)
        self.info_iso.setText(photo.iso or "--")
        
        self._ensure_thumbnail(photo)

    def _ensure_thumbnail(self, photo):
        """Load and cache a thumbnail for inspector / 为检查器加载并缓存缩略图"""
        if photo.thumbnail is None:
            pix = QPixmap(photo.file_path)
            if pix.isNull():
                self.thumb_label.setText("No preview")
                return
            # Use explicit dimensions matching CinemaBox (minus margins) to ensure perfect centering
            # 使用适配 CinemaBox（扣除边距）的明确尺寸，确保完美居中
            photo.thumbnail = pix.scaled(
                280, 170, # 190 - 20 (padding)
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        
        # Apply rotation if needed / 如果需要，应用旋转
        if photo.rotation != 0:
            transform = QTransform().rotate(photo.rotation)
            rotated_pix = photo.thumbnail.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            # Scale again to ensure it fits the box / 再次缩放以适配盒子
            final_pix = rotated_pix.scaled(
                280, 170,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.thumb_label.setPixmap(final_pix)
        else:
            self.thumb_label.setPixmap(photo.thumbnail)

    def rotate_photo(self, angle: int):
        """Rotate the currently selected photo / 旋转当前选中的照片"""
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            return
        
        row = selection[0].row()
        photo = self.model.photos[row]
        
        # Update rotation state (0, 90, 180, 270)
        photo.rotation = (photo.rotation + angle) % 360
        
        # Refresh inspector to show new orientation
        self._refresh_inspector()
        logger.info(f"Rotated photo {photo.file_name} to {photo.rotation} degrees")

    def _stop_worker(self):
        """Gracefully stop worker thread / 优雅停止工作线程"""
        if hasattr(self, "worker_thread") and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(2000)
    
    def toggle_language(self):
        """Toggle UI language between Chinese and English / 在中英文之间切换界面语言"""
        new_lang = toggle_language()
        self.refresh_ui()
        # Header refresh
        self.model.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, self.model.columnCount() - 1)
        self.table_view.horizontalHeader().viewport().update()
        
        # Update language button text / 更新语言按钮文本
        self.lang_btn.setText("中" if new_lang == 'en' else "EN")
    
    def refresh_ui(self):
        """Refresh all UI text with current language / 用当前语言刷新所有 UI 文本"""
        # Update sidebar / 更新侧边栏
        self.sidebar_title.setText(tr("Quick Write"))
        self.json_import_btn.setText(tr("Import Metadata"))
        self.refresh_btn.setText(tr("Refresh EXIF"))
        
        self.quick_camera_make.setPlaceholderText(tr("Camera Make"))
        self.quick_camera_model.lineEdit().setPlaceholderText(tr("Camera Model"))
        self.quick_lens_make.setPlaceholderText(tr("Lens Make"))
        self.quick_lens_model.lineEdit().setPlaceholderText(tr("Lens Model"))
        self.quick_focal.setPlaceholderText(tr("Focal Length"))
        self.quick_focal_35mm.setPlaceholderText(tr("Focal Length (35mm)"))
        self.quick_film.lineEdit().setPlaceholderText(tr("Film Stock"))
        self.quick_apply_btn.setText(tr("Apply to All"))
        self.quick_apply_selected_btn.setText(tr("Apply to Selected"))
        
        # Update content area / 更新内容区域
        self.browse_btn.setText(tr("Add Photos"))
        self.placeholder.setText(tr("Click 'Add Photos' button to import photos"))
        self.console_card.findChild(QLabel).setText(tr("Process Status"))
        
        # Tooltips / 工具提示
        self.settings_btn.setToolTip(tr("Settings"))
        self.about_btn.setToolTip(tr("About"))
        self.rotate_ccw_btn.setToolTip(tr("Rotate Left"))
        self.rotate_cw_btn.setToolTip(tr("Rotate Right"))
        self.lang_btn.setToolTip(tr("Switch to Chinese") if get_current_language() == 'en' else tr("Switch to English"))
        
        # Update inspector / 更新检查器
        self.inspector_title.setText(tr("Inspector"))
        self.basic_label.setText(tr("Basic Info"))
        self.file_label.setText(tr("File:"))
        self.camera_make_label.setText(tr("Camera Make:"))
        self.camera_model_label.setText(tr("Camera Model:"))
        self.lens_make_label.setText(tr("Lens Make:"))
        self.lens_model_label.setText(tr("Lens Model:"))
        self.film_label.setText(tr("Film Stock:"))
        self.location_label.setText(tr("Location:"))
        self.date_label.setText(tr("Date:"))
        self.status_label.setText(tr("Status:"))
        self.focal_native_label.setText(tr("Focal Length:"))
        self.focal_35mm_label.setText(tr("Focal Length (35mm):"))
        
        # Update LCD labels
        self.ap_title_label.setText(tr("Aperture"))
        self.sh_title_label.setText(tr("Shutter"))
        self.iso_title_label.setText(tr("ISO"))
        
        self.exposure_label.setText(tr("Digital Back Display"))
        
        # Re-initialize layout state based on new language text sizes
        # 根据新语言文本大小重新初始化布局状态
        self._update_layout_factors()
        
        # Refresh current selection display
        # 刷新当前选中项显示
        self._refresh_inspector()
    
    def import_metadata(self):
        """Import metadata from JSON/CSV/TXT and show editor dialog / 从 JSON/CSV/TXT 导入元数据并显示编辑对话框"""
        # Check if photos are imported / 检查是否已导入照片
        if self.model.rowCount() == 0:
            QMessageBox.warning(
                self, 
                tr("No photos imported"), 
                tr("Please import photos first")
            )
            return
        
        # Select metadata file / 选择元数据文件
        from src.core.config import get_config
        cfg = get_config()
        last_path = cfg.get('last_import_path', '')
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select metadata file"),
            last_path,
            tr("Metadata Files (*.json *.csv *.txt)")
        )
        
        if not file_path:
            return
            
        # Update last path memory / 更新路径记忆
        cfg.set('last_import_path', str(Path(file_path).parent))
        
        try:
            # Check file type and parse accordingly
            # 根据文件类型选择解析方式
            if file_path.endswith(('.csv', '.txt')):
                from src.core.csv_parser import CSVParser
                
                # Parse CSV file
                csv_parser = CSVParser(file_path)
                headers, rows = csv_parser.parse()
                
                if not headers or not rows:
                    QMessageBox.warning(self, tr("Import Metadata"), tr("No data found in file"))
                    return
                
                # Direct to Unified Editor
                editor = MetadataEditorDialog(self.model.photos, [], headers, rows, self)
                editor.requests_write.connect(self.execute_metadata_write_tasks)
                editor.metadata_written.connect(self.on_metadata_written)
                editor.exec()
                return 
            
            else:
                # JSON import (existing logic)
                # JSON 导入（现有逻辑）
                progress = QProgressDialog(
                    tr("Parsing metadata..."), 
                    None, 
                    0, 
                    0, 
                    self
                )
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                
                parser = MetadataParser()
                metadata_entries = parser.parse_file(file_path)
                
                if not metadata_entries:
                    progress.close()
                    QMessageBox.warning(self, tr("Import Metadata"), "No valid entries found in file")
                    return
                
                progress.close()
            
            # Show editor dialog / 显示编辑对话框
            editor = MetadataEditorDialog(self.model.photos, metadata_entries, parent=self)
            editor.requests_write.connect(self.execute_metadata_write_tasks)
            editor.metadata_written.connect(self.on_metadata_written)
            editor.exec()
                
        except Exception as e:
            QMessageBox.critical(self, tr("Import Metadata"), f"Error: {str(e)}")
            self.add_log(tr("Error importing metadata: {msg}").format(msg=str(e)))
    
    def on_metadata_written(self):
        """Handle metadata written successfully / 处理元数据成功写入"""
        # Mark all photos as modified / 标记所有照片为已修改
        for photo in self.model.photos:
            self.model.mark_modified(photo.file_path)
        
        # Refresh photo data in background / 在后台刷新照片数据
        file_paths = [photo.file_path for photo in self.model.photos]
        self.queue_exif_read(file_paths, show_progress=False)
        
        self.model.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.model.COLUMNS) - 1)
        self.add_log(tr("Metadata written to selected photos."))

    def execute_metadata_write_tasks(self, tasks: list):
        """Execute batch EXIF write tasks with console logging / 在控制台记录下执行批量 EXIF 写入任务"""
        if not tasks: return
        
        # Ensure worker is alive / 确保工作子线程在线
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
            
        self.add_log(tr("Writing metadata..."))
        
        # Connect to the completion handler / 连接到完成处理程序
        self.worker.write_finished.connect(self._on_batch_write_complete)
        self.start_batch_write.emit(tasks)

    def _on_batch_write_complete(self, result):
        """Handle batch write completion in Main Thread / 在主线程处理批量写入完成"""
        if not result.get("batch_write"): return
        
        # Disconnect to prevent double firing on next op
        try: self.worker.write_finished.disconnect(self._on_batch_write_complete)
        except: pass
        
        success = result.get('success', 0)
        QMessageBox.information(self, tr("Write Metadata"), tr("Successfully wrote metadata to {count} file(s)").format(count=success))
        self.on_metadata_written()
    
    def _init_quick_write_history(self):
        """Initialize combobox history from Config / 从配置初始化组合框历史"""
        config = get_config()
        if not config.history:

            return
            
        # Block signals to prevent auto-fill during init
        self.quick_camera_model.blockSignals(True)
        self.quick_lens_model.blockSignals(True)
        
        # Camera Models
        cameras = config.history.get_cameras()

        self.quick_camera_model.clear()
        self.quick_camera_model.addItems(sorted(cameras.keys()))
        self.quick_camera_model.lineEdit().clear()
        
        # Lens Models
        lenses = config.history.get_lenses()

        self.quick_lens_model.clear()
        self.quick_lens_model.addItems(sorted(lenses.keys()))
        self.quick_lens_model.lineEdit().clear()
        
        # Film Stocks
        films = config.history.get_films()

        self.quick_film.clear()
        self.quick_film.addItems(films)
        self.quick_film.lineEdit().clear()
        
        self.quick_camera_model.blockSignals(False)
        self.quick_lens_model.blockSignals(False)
        
        # Setup context menu for removing items / 设置上下文菜单以删除项目
        for combo in [self.quick_camera_model, self.quick_lens_model, self.quick_film]:
            # Must attach to the view() (the popup list) to get right-clicks on items
            view = combo.view()
            view.setContextMenuPolicy(Qt.CustomContextMenu)
            view.customContextMenuRequested.connect(lambda pos, c=combo: self._on_history_context_menu(pos, c))
        
    def _on_camera_model_changed(self, text):
        """Auto-fill camera make when model changes / 当型号改变时自动填充品牌"""
        config = get_config()
        if not config.history: return
        
        make = config.history.get_cameras().get(text)
        if make:
            self.quick_camera_make.setText(make)
            
    def _on_lens_model_changed(self, text):
        """Auto-fill lens make when model changes / 当镜头型号改变时自动填充品牌"""
        config = get_config()
        if not config.history: return
        
        make = config.history.get_lenses().get(text)
        if make:
            self.quick_lens_make.setText(make)
            
    def _on_history_context_menu(self, pos, combo):
        """Show context menu to delete history item / 显示上下文菜单以删除历史项目"""
        view = combo.view()
        # Ensure we clicked on an item / 确保点击了项目
        index = view.indexAt(pos)
        if not index.isValid():
            return
            
        text = combo.itemText(index.row())
        if not text:
            return
            
        # Parent menu to the view to try and keep context / 将菜单父级设置为视图以保持上下文
        menu = QMenu(view)
        delete_action = menu.addAction(tr("Remove '{text}'").format(text=text))
        
        # Prevent popup from closing / 防止弹出窗口关闭
        if hasattr(combo, 'set_skip_hide'):
            combo.set_skip_hide(True)
            
        try:
            action = menu.exec(view.mapToGlobal(pos))
        finally:
            if hasattr(combo, 'set_skip_hide'):
                combo.set_skip_hide(False)
        
        if action == delete_action:
            # Confirm deletion / 确认删除
            reply = QMessageBox.question(
                self, 
                tr("Confirm Deletion"), 
                tr("Are you sure you want to remove '{text}' from history?").format(text=text),
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Remove from UI first
                combo.removeItem(index.row())
                # Clear text if it matches deleted item
                if combo.currentText() == text:
                    combo.setEditText("")
                
                # Remove from config / 从配置中移除
                config = get_config()
                if not config.history: return
                
                if combo == self.quick_camera_model:
                     config.history.remove_camera(text)
                elif combo == self.quick_lens_model:
                    config.history.remove_lens(text)
                elif combo == self.quick_film:
                    config.history.remove_film(text)
                    
                # If deleted item was currently selected, clear related fields
                # 如果删除的项目当前被选中，清除相关字段
                if combo == self.quick_camera_model:
                    self.quick_camera_make.clear()
                elif combo == self.quick_lens_model:
                    self.quick_lens_make.clear()
                    
                # Re-show popup to allow continuous editing/viewing
                # 重新显示弹出窗口以允许连续编辑/查看
                # With HistoryComboBox, the popup might still be open, but we ensure it here
                combo.showPopup()

    def on_quick_apply(self):
        """Batch update Camera, Lens, and Film for all photos / 批量更新所有照片的相机、镜头和胶卷信息"""
        count = len(self.model.photos)
        if count == 0: return
        
        # Ensure worker is alive before signaling / 发送信号前确保工作者线程存活
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
        
        c_make = self.quick_camera_make.text().strip()
        c_model = self.quick_camera_model.currentText().strip()
        l_make = self.quick_lens_make.text().strip()
        l_model = self.quick_lens_model.currentText().strip()
        focal = self.quick_focal.text().strip()
        focal_35 = self.quick_focal_35mm.text().strip()
        film = self.quick_film.currentText().strip()
        
        if not any([c_make, c_model, l_make, l_model, focal, focal_35, film]):
            return
            
        # Update History Logic / 更新历史逻辑
        config = get_config()
        if config.history:
            if c_model: config.history.add_camera(c_model, c_make) # Make can be empty
            if l_model: config.history.add_lens(l_model, l_make)
            if film: config.history.add_film(film)
            
        reply = QMessageBox.question(
            self, 
            tr("Quick Write"), 
            tr("Batch update {count} files?").format(count=count)
        )
        if reply != QMessageBox.Yes: return
        
        # Build batch metadata / 构建批量元数据
        batch_meta = {}
        if c_make: batch_meta["Make"] = c_make
        if c_model: batch_meta["Model"] = c_model
        if l_make: batch_meta["LensMake"] = l_make
        if l_model: batch_meta["LensModel"] = l_model
        if focal: batch_meta["FocalLength"] = focal
        if focal_35: batch_meta["FocalLengthIn35mmFormat"] = focal_35
        if film: batch_meta["Film"] = film
        
        # Prepare synchronous update list / 准备同步更新列表
        metadata_list = [batch_meta] * count
        
        # Apply to model / 应用到模型
        updated = self.model.apply_metadata_sequentially(metadata_list)
        
        if updated > 0:
            QMessageBox.information(self, tr("Quick Write"), tr("Successfully updated {count} photos").format(count=updated))
            self.add_log(tr("Quick write applied to {count} photos.").format(count=updated))
            # Clear fields after success / 成功后清空字段
            # Clear fields after success / 成功后清空字段
            for edit in [self.quick_camera_make, self.quick_camera_model, self.quick_lens_make, self.quick_lens_model, self.quick_focal, self.quick_focal_35mm, self.quick_film]:
                if isinstance(edit, QComboBox):
                    edit.setEditText("")
                else:
                    edit.clear()
        
    def on_quick_apply_selected(self):
        """Batch update Camera, Lens, and Film for selected photos / 批量更新选中照片的相机、镜头和胶卷信息"""
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            QMessageBox.warning(self, tr("No photos selected"), tr("Please select photos first"))
            return
            
        data = {
            "Make": self.quick_camera_make.text().strip(),
            "Model": self.quick_camera_model.currentText().strip(),
            "LensMake": self.quick_lens_make.text().strip(),
            "LensModel": self.quick_lens_model.currentText().strip(),
            "FocalLength": self.quick_focal.text().strip(),
            "FocalLengthIn35mmFormat": self.quick_focal_35mm.text().strip(),
            "Film": self.quick_film.currentText().strip()
        }
        
        # Save History on Apply to Selected too
        c_make = data.get("Make", "")
        c_model = data.get("Model", "")
        l_make = data.get("LensMake", "")
        l_model = data.get("LensModel", "")
        film = data.get("Film", "")
        
        config = get_config()
        if config.history:
            if c_model: config.history.add_camera(c_model, c_make)
            if l_model: config.history.add_lens(l_model, l_make)
            if film: config.history.add_film(film)
        
        # Remove empty values / 移除空值
        data = {k: v for k, v in data.items() if v}
        if not data:
            return

        rows = [idx.row() for idx in selection]
        updated = self.model.apply_metadata_to_rows(rows, data)
        
        if updated > 0:
            QMessageBox.information(self, tr("Quick Write"), tr("Successfully updated {count} photos").format(count=updated))
            self.add_log(tr("Quick write applied to {count} selected photos.").format(count=updated))
            # Clear fields / 清空字段
            # Clear fields / 清空字段
            for edit in [self.quick_camera_make, self.quick_camera_model, self.quick_lens_make, self.quick_lens_model, self.quick_focal, self.quick_focal_35mm, self.quick_film]:
                if isinstance(edit, QComboBox):
                    edit.setEditText("")
                else:
                    edit.clear()
            
    def show_context_menu(self, pos):
        """Show context menu for table view / 显示表格右键菜单"""
        if not self.table_view.selectionModel().hasSelection():
            return
            
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        remove_action = QAction(tr("Remove"), self)
        remove_action.triggered.connect(self.remove_selected_photos)
        menu.addAction(remove_action)
        
        menu.exec_(self.table_view.viewport().mapToGlobal(pos))
        
    def remove_selected_photos(self):
        """Remove selected photos from the list / 从列表中移除选中的照片"""
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            return
            
        reply = QMessageBox.question(
            self,
            tr("Remove"),
            tr("Remove selected photos?"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Sort rows in reverse order to avoid index issues during removal
            rows = sorted([index.row() for index in selection], reverse=True)
            for row in rows:
                self.model.removeRow(row)
            
            # Update placeholder visibility
            self._update_layout_factors()
            
            self.add_log(tr("Removed selected photos."))
    
    def add_log(self, message: str):
        """Add a message to the process console / 向进程控制台添加消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.appendPlainText(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        self.log_console.moveCursor(self.log_console.textCursor().MoveOperation.End)
                
    def refresh_exif(self):
        """Refresh EXIF data for all photos / 刷新所有照片的 EXIF 数据"""
        if not self.model.photos:
            QMessageBox.information(self, tr("Refresh EXIF"), tr("No photos to refresh"))
            return
        
        # Re-read EXIF for all photos with progress dialog / 重新读取所有照片的 EXIF 并显示进度
        file_paths = [photo.file_path for photo in self.model.photos]
        self.queue_exif_read(file_paths, show_progress=True)
