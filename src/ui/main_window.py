#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window of DataPrism with macOS aesthetics
DataPrism 的主窗口，采用 macOS 美学设计
"""

from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QFileDialog, QTableView, QHeaderView, QFormLayout,
    QMessageBox, QProgressDialog, QDialog
)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QFont, QPixmap

from src.core.photo_model import PhotoDataModel
from src.core.exif_worker import ExifToolWorker
from src.core.json_parser import FilmLogParser
from src.core.json_matcher import PhotoMatcher
from src.core.metadata_parser import MetadataParser
from src.ui.metadata_editor_dialog import MetadataEditorDialog
from src.utils.i18n import tr, toggle_language, get_current_language
from src.utils.logger import get_logger

logger = get_logger('DataPrism.MainWindow')


class MainWindow(QMainWindow):
    """Main application window / 主应用窗口"""

    start_exif_read = Signal(list)

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
        left_layout = QVBoxLayout(left_widget)
        
        # Language toggle button / 语言切换按钮
        self.lang_btn = QPushButton("中" if get_current_language() == 'en' else "EN")
        self.lang_btn.setFixedSize(40, 32)
        self.lang_btn.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                background-color: #007aff;
                color: white;
                font-size: 11px;
                font-weight: 600;
                border: none;
            }
            QPushButton:hover { background-color: #1a84ff; }
            QPushButton:pressed { background-color: #0062d6; }
        """)
        self.lang_btn.clicked.connect(self.toggle_language)
        left_layout.addWidget(self.lang_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.sidebar_title = QLabel(tr("Filters & Presets"))
        self.sidebar_title.setFont(QFont())
        left_layout.addWidget(self.sidebar_title)
        
        # Placeholder buttons
        # 占位符按钮
        self.camera_btn = QPushButton(f"📷 {tr('Camera')}")
        self.lens_btn = QPushButton(f"🔍 {tr('Lens')}")
        self.film_btn = QPushButton(f"📽️ {tr('Film Stock')}")
        
        for btn in [self.camera_btn, self.lens_btn, self.film_btn]:
            btn.setMinimumHeight(44)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    padding: 10px 14px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #f9f9fb, stop:1 #f0f0f5);
                    border: 1px solid #e5e5ea;
                    font-size: 13px;
                    color: #1d1d1f;
                    text-align: left;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #ffffff, stop:1 #f5f5f7);
                    border: 1px solid #d1d1d6;
                }
                QPushButton:pressed {
                    background: #e8e8ed;
                    border: 1px solid #c7c7cc;
                }
            """)
            left_layout.addWidget(btn)
        
        # JSON Import button / JSON 导入按钮
        left_layout.addSpacing(12)
        self.json_import_btn = QPushButton(f"📄 {tr('Import Metadata')}")
        self.json_import_btn.setMinimumHeight(44)
        self.json_import_btn.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                padding: 10px 14px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #34c759, stop:1 #28a745);
                border: 1px solid #28a745;
                font-size: 13px;
                color: white;
                text-align: left;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #40d865, stop:1 #2fb84f);
            }
            QPushButton:pressed {
                background: #1f8a38;
            }
        """)
        self.json_import_btn.clicked.connect(self.import_metadata)
        left_layout.addWidget(self.json_import_btn)
        
        left_layout.addStretch()
        left_widget.setMaximumWidth(200)
        left_widget.setMinimumWidth(180)
        
        # Main content area - Grid/List view
        # 主内容区域 - 网格/列表视图
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Top bar with title and buttons / 顶部栏包含标题和按钮
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)
        
        self.content_title = QLabel(tr("Imported Photos"))
        self.content_title.setFont(QFont())
        top_bar.addWidget(self.content_title)

        self.browse_btn = QPushButton(tr("Browse files…"))
        self.browse_btn.setMinimumHeight(36)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #007aff;
                color: white;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover { background-color: #1a84ff; }
            QPushButton:pressed { background-color: #0062d6; }
        """)
        self.browse_btn.clicked.connect(self.browse_files)
        top_bar.addWidget(self.browse_btn)
        
        # Refresh button / 刷新按钮
        self.refresh_btn = QPushButton(f"🔄 {tr('Refresh EXIF')}")
        self.refresh_btn.setMinimumHeight(36)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #34c759;
                color: white;
                font-size: 12px;
                border: none;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #40d865; }
            QPushButton:pressed { background-color: #28a745; }
        """)
        self.refresh_btn.clicked.connect(self.refresh_exif)
        top_bar.addWidget(self.refresh_btn)
        
        top_bar.addStretch()
        
        center_layout.addLayout(top_bar)
        
        self.placeholder = QLabel(tr("Click 'Browse files' button to import photos"))
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                color: #8e8e93;
                font-size: 14px;
                padding: 100px;
            }
        """)
        center_layout.addWidget(self.placeholder)

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        header = self.table_view.horizontalHeader()
        # Enable interactive column resizing and stretch last section
        # 启用交互式列宽调整并拉伸最后一列
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        
        # Set initial column widths / 设置初始列宽
        header.resizeSection(0, 150)  # File
        header.resizeSection(1, 100)  # C-Make
        header.resizeSection(2, 120)  # C-Model
        header.resizeSection(3, 100)  # L-Make
        header.resizeSection(4, 150)  # L-Model
        header.resizeSection(5, 70)   # Aperture
        header.resizeSection(6, 80)   # Shutter
        header.resizeSection(7, 60)   # ISO
        header.resizeSection(8, 130)  # Film
        header.resizeSection(9, 250)  # Location
        header.resizeSection(10, 150) # Date
        # Status column (11) will stretch as last section
        
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.verticalHeader().setDefaultSectionSize(52)  # Breathable row height
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)  # Remove grid lines
        self.table_view.setStyleSheet("""
            QTableView {
                border: none;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                selection-background-color: #0051d5;
                selection-color: #ffffff;
                border-radius: 8px;
            }
            QTableView::item {
                padding: 8px;
                border: none;
            }
            QTableView::item:selected {
                background-color: #0051d5;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f5f5f7;
                padding: 8px;
                border: none;
                font-weight: 600;
                color: #333333;
            }
        """)
        self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        center_layout.addWidget(self.table_view)
        
        # Right inspector panel
        # 右侧检查器面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        
        self.inspector_title = QLabel(tr("Inspector"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.inspector_title.setFont(title_font)
        self.inspector_title.setStyleSheet("color: #1d1d1f; padding-bottom: 4px;")
        right_layout.addWidget(self.inspector_title)
        
        # Separator line
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e5e5ea;")
        right_layout.addWidget(separator)
        
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(200, 200)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setStyleSheet("""
            border: 1px solid #d1d1d6;
            border-radius: 8px;
            background: #fafafa;
        """)
        right_layout.addWidget(self.thumb_label)

        # Basic Info Section
        self.basic_label = QLabel(tr("Basic Info"))
        self.basic_label.setStyleSheet("color: #86868b; font-size: 11px; font-weight: 600; margin-top: 8px;")
        right_layout.addWidget(self.basic_label)
        
        form = QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(0, 4, 0, 8)
        
        self.info_file = QLabel("--")
        self.info_camera_make = QLabel("--")
        self.info_camera_model = QLabel("--")
        self.info_lens_make = QLabel("--")
        self.info_lens_model = QLabel("--")
        self.info_film = QLabel("--")
        self.info_location = QLabel("--")
        self.info_date = QLabel("--")
        self.info_status = QLabel("--")
        
        # Style for value labels with monospace font for technical data
        value_style = "color: #1d1d1f; font-size: 12px; font-family: 'Consolas', 'Courier New', monospace;"
        for lbl in [self.info_file, self.info_camera_make, self.info_camera_model, self.info_lens_make, self.info_lens_model, self.info_film, self.info_location, self.info_date, self.info_status]:
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setStyleSheet(value_style)
            lbl.setWordWrap(True)
        
        # Label style
        label_style = "color: #86868b; font-size: 11px;"
        
        self.file_label = QLabel(tr("File:"))
        self.file_label.setStyleSheet(label_style)
        form.addRow(self.file_label, self.info_file)
        
        self.make_label = QLabel(tr("Camera Make:"))
        self.make_label.setStyleSheet(label_style)
        form.addRow(self.make_label, self.info_camera_make)

        self.model_label = QLabel(tr("Camera Model:"))
        self.model_label.setStyleSheet(label_style)
        form.addRow(self.model_label, self.info_camera_model)
        
        self.lens_make_label = QLabel(tr("Lens Make:"))
        self.lens_make_label.setStyleSheet(label_style)
        form.addRow(self.lens_make_label, self.info_lens_make)

        self.lens_model_label = QLabel(tr("Lens Model:"))
        self.lens_model_label.setStyleSheet(label_style)
        form.addRow(self.lens_model_label, self.info_lens_model)

        self.film_label = QLabel(tr("Film Stock:"))
        self.film_label.setStyleSheet(label_style)
        form.addRow(self.film_label, self.info_film)

        self.location_label = QLabel(tr("Location:"))
        self.location_label.setStyleSheet(label_style)
        form.addRow(self.location_label, self.info_location)
        
        self.date_label = QLabel(tr("Date:"))
        self.date_label.setStyleSheet(label_style)
        form.addRow(self.date_label, self.info_date)
        
        self.status_label = QLabel(tr("Status:"))
        self.status_label.setStyleSheet(label_style)
        form.addRow(self.status_label, self.info_status)
        
        right_layout.addLayout(form)
        
        # Exposure Section / 曝光区域
        self.exposure_label = QLabel(tr("Exposure"))
        self.exposure_label.setStyleSheet("color: #86868b; font-size: 11px; font-weight: 600; margin-top: 12px;")
        right_layout.addWidget(self.exposure_label)
        
        exposure_form = QFormLayout()
        exposure_form.setSpacing(8)
        exposure_form.setContentsMargins(0, 4, 0, 8)
        
        self.info_aperture = QLabel("-")
        self.info_shutter = QLabel("-")
        self.info_iso = QLabel("-")
        
        # Monospace font for exposure values / 曝光值使用等宽字体
        exposure_style = "color: #1d1d1f; font-size: 13px; font-family: 'Consolas', 'Courier New', monospace; font-weight: 600;"
        for lbl in [self.info_aperture, self.info_shutter, self.info_iso]:
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setStyleSheet(exposure_style)
        
        self.aperture_label = QLabel(tr("Aperture:"))
        self.aperture_label.setStyleSheet(label_style)
        exposure_form.addRow(self.aperture_label, self.info_aperture)
        
        self.shutter_label = QLabel(tr("Shutter:"))
        self.shutter_label.setStyleSheet(label_style)
        exposure_form.addRow(self.shutter_label, self.info_shutter)
        
        self.iso_label = QLabel(tr("ISO:"))
        self.iso_label.setStyleSheet(label_style)
        exposure_form.addRow(self.iso_label, self.info_iso)
        
        right_layout.addLayout(exposure_form)
        right_layout.addStretch()
        
        right_widget.setMaximumWidth(300)
        right_widget.setMinimumWidth(280)
        
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
        
        # Set window style with macOS Big Sur theme
        # 设置 macOS Big Sur 主题窗口风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QWidget {
                background-color: #f5f5f7;
                color: #1d1d1f;
                font-family: -apple-system, "Segoe UI", sans-serif;
            }
            QLabel {
                color: #1d1d1f;
            }
            QSplitter::handle {
                background-color: #d1d1d6;
                width: 1px;
            }
        """)

    def on_files_dropped(self, file_paths: List[str]):
        """Callback when files are imported / 当文件被导入时的回调"""
        unique_files = [p for p in file_paths if p not in {item.file_path for item in self.model.photos}]
        if unique_files:
            self.model.add_photos(unique_files)
            self.queue_exif_read(unique_files)
        total = self.model.rowCount()
        self.placeholder.setVisible(total == 0)
        if total:
            self.placeholder.setText(
                tr("Imported {count} file(s).", count=total)
            )
        logger.info(f"Imported {len(unique_files)} files")

    # --- File dialog import / 通过对话框导入 ---
    def browse_files(self):
        """Open file dialog to import images / 打开文件对话框导入图像"""
        filters = tr("Images (*.jpg *.jpeg *.png *.tif *.tiff *.dng)")
        files, _ = QFileDialog.getOpenFileNames(self, tr("Select photos"), "", filters)
        if files:
            self.on_files_dropped(files)

    # --- Worker wiring / 工作者连接 ---
    def _setup_worker(self):
        """Initialize ExifTool worker thread / 初始化 ExifTool 工作线程"""
        self.worker = ExifToolWorker()
        self.worker_thread = QThread(self)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker.result_ready.connect(self.on_exif_results)
        self.worker.error_occurred.connect(self.on_exif_error)
        self.worker.progress.connect(self.on_exif_progress)
        self.worker.finished.connect(self.worker_thread.quit)
        self.start_exif_read.connect(self.worker.read_exif)
        
        # Connect model signals for inline editing
        # 连接模型信号以进行内联编辑
        self.model.dataChangedForWrite.connect(self.worker.single_write)

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

    def on_exif_results(self, results: dict):
        """Handle EXIF results / 处理 EXIF 结果"""
        # Distinguish between read results and write results
        # 区分读取结果和写入结果
        if "status" in results and results["status"] == "success" and "file" in results:
            # Single write success - no need to trigger full re-read as model is already updated
            # and marking it as modified/loaded locally is enough for UX.
            # We'll just let the model keep the user's input.
            file_path = results["file"]
            logger.info(f"Write successful for {file_path}")
            return

        for file_path, exif_data in results.items():
            # Skip non-dict data in case of unexpected structure
            if isinstance(exif_data, dict):
                self.model.set_exif_data(file_path, exif_data)
        
        self._refresh_inspector()
        
        # Close progress dialog and show completion message
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

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
        self.info_file.setText(photo.file_name)
        self.info_camera_make.setText(exif.get("Make", "--") if photo.exif_data else "--")
        self.info_camera_model.setText(exif.get("Model", "--") if photo.exif_data else "--")
        self.info_lens_make.setText(exif.get("LensMake", "--") if photo.exif_data else "--")
        self.info_lens_model.setText(exif.get("LensModel", "--") if photo.exif_data else "--")
        self.info_film.setText(photo.film_stock or exif.get("Film", "--"))
        # Prefer cached location; else try GPS; else description
        gps_lat = exif.get("GPSLatitude")
        gps_lon = exif.get("GPSLongitude")
        gps_str = f"{gps_lat}, {gps_lon}" if gps_lat and gps_lon else None
        self.info_location.setText(photo.location or gps_str or exif.get("ImageDescription", "--"))
        self.info_date.setText(photo.exif_data.get("DateTimeOriginal", "--") if photo.exif_data else "--")
        status_display = photo.status + (" (Modified)" if photo.is_modified else "")
        self.info_status.setText(status_display)
        
        # Exposure data / 曝光数据
        self.info_aperture.setText(f"f/{photo.aperture}" if photo.aperture else "--")
        self.info_shutter.setText(f"{photo.shutter_speed}s" if photo.shutter_speed else "--")
        self.info_iso.setText(photo.iso or "--")
        
        self._ensure_thumbnail(photo)

    def _ensure_thumbnail(self, photo):
        """Load and cache a thumbnail for inspector / 为检查器加载并缓存缩略图"""
        if photo.thumbnail is None:
            pix = QPixmap(photo.file_path)
            if pix.isNull():
                self.thumb_label.setText("No preview")
                return
            photo.thumbnail = pix.scaled(
                self.thumb_label.width(),
                self.thumb_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.thumb_label.setPixmap(photo.thumbnail)

    def _stop_worker(self):
        """Gracefully stop worker thread / 优雅停止工作线程"""
        if hasattr(self, "worker_thread") and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(2000)
    
    def toggle_language(self):
        """Toggle UI language between Chinese and English / 在中英文之间切换界面语言"""
        new_lang = toggle_language()
        self.refresh_ui()
        # Update language button text / 更新语言按钮文本
        self.lang_btn.setText("中" if new_lang == 'en' else "EN")
    
    def refresh_ui(self):
        """Refresh all UI text with current language / 用当前语言刷新所有 UI 文本"""
        # Update sidebar / 更新侧边栏
        self.sidebar_title.setText(tr("Filters & Presets"))
        self.camera_btn.setText(f"📷 {tr('Camera')}")
        self.lens_btn.setText(f"🔍 {tr('Lens')}")
        self.film_btn.setText(f"📽️ {tr('Film Stock')}")
        self.json_import_btn.setText(f"📄 {tr('Import Metadata')}")
        self.refresh_btn.setText(f"🔄 {tr('Refresh EXIF')}")
        
        # Update content area / 更新内容区域
        self.content_title.setText(tr("Imported Photos"))
        self.browse_btn.setText(tr("Browse files…"))
        self.placeholder.setText(tr("Drag and drop photos here or click to import"))
        
        # Update inspector / 更新检查器
        self.inspector_title.setText(tr("Inspector"))
        self.basic_label.setText(tr("Basic Info"))
        self.file_label.setText(tr("File:"))
        self.camera_label.setText(tr("Camera:"))
        self.lens_label.setText(tr("Lens:"))
        self.film_label.setText(tr("Film Stock:"))
        self.location_label.setText(tr("Location:"))
        self.date_label.setText(tr("Date:"))
        self.status_label.setText(tr("Status:"))
        
        # Update exposure section / 更新曝光区域
        self.exposure_label.setText(tr("Exposure"))
        self.aperture_label.setText(tr("Aperture:"))
        self.shutter_label.setText(tr("Shutter:"))
        self.iso_label.setText(tr("ISO:"))
    
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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select metadata file"),
            "",
            tr("Metadata Files (*.json *.csv *.txt)")
        )
        
        if not file_path:
            return
        
        try:
            # Check file type and parse accordingly
            # 根据文件类型选择解析方式
            if file_path.endswith(('.csv', '.txt')):
                # CSV/TXT import with field mapping dialog
                # CSV/TXT 导入（带字段映射对话框）
                from src.core.csv_parser import CSVParser
                from src.core.csv_converter import CSVConverter
                from src.ui.field_mapping_dialog import FieldMappingDialog
                
                # Parse CSV file
                csv_parser = CSVParser(file_path)
                headers, rows = csv_parser.parse()
                
                if not headers or not rows:
                    QMessageBox.warning(self, tr("Import Metadata"), tr("No data found in file"))
                    return
                
                # Show field mapping dialog
                # 显示字段映射对话框
                mapping_dialog = FieldMappingDialog(headers, rows[:5], self)
                if mapping_dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                
                # Get user-selected mappings
                mappings = mapping_dialog.get_mappings()
                
                # Convert CSV data to metadata entries (matched by row order)
                # 将 CSV 数据转换为元数据条目（按行序号匹配）
                metadata_entries = CSVConverter.convert_rows(rows, mappings, self.model.photos)
                
                if not metadata_entries:
                    QMessageBox.warning(self, tr("Import Metadata"), tr("No valid entries found"))
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
            editor = MetadataEditorDialog(self.model.photos, metadata_entries, self)
            editor.metadata_written.connect(self.on_metadata_written)
            editor.exec()
                
        except Exception as e:
            QMessageBox.critical(self, tr("Import Metadata"), f"Error: {str(e)}")
    
    def on_metadata_written(self):
        """Handle metadata written successfully / 处理元数据成功写入"""
        # Mark all photos as modified / 标记所有照片为已修改
        for photo in self.model.photos:
            self.model.mark_modified(photo.file_path)
        
        # Refresh photo data with progress dialog / 刷新照片数据并显示进度
        file_paths = [photo.file_path for photo in self.model.photos]
        self.queue_exif_read(file_paths, show_progress=True)
        
        # Trigger model header refresh / 触发模型表头刷新
        self.model.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.model.COLUMNS) - 1)
    
    def refresh_exif(self):
        """Refresh EXIF data for all photos / 刷新所有照片的 EXIF 数据"""
        if not self.model.photos:
            QMessageBox.information(self, tr("Refresh EXIF"), tr("No photos to refresh"))
            return
        
        # Re-read EXIF for all photos with progress dialog / 重新读取所有照片的 EXIF 并显示进度
        file_paths = [photo.file_path for photo in self.model.photos]
        self.queue_exif_read(file_paths, show_progress=True)
