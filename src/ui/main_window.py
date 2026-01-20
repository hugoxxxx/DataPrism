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
    QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QFont, QPixmap

from src.core.photo_model import PhotoDataModel
from src.core.exif_worker import ExifToolWorker
from src.core.json_parser import FilmLogParser
from src.core.json_matcher import PhotoMatcher
from src.utils.i18n import tr, toggle_language, get_current_language


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
        self.json_import_btn = QPushButton(f"📄 {tr('Import JSON')}")
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
        self.json_import_btn.clicked.connect(self.import_json)
        left_layout.addWidget(self.json_import_btn)
        
        left_layout.addStretch()
        left_widget.setMaximumWidth(200)
        left_widget.setMinimumWidth(180)
        
        # Main content area - Grid/List view
        # 主内容区域 - 网格/列表视图
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        self.content_title = QLabel(tr("Imported Photos"))
        self.content_title.setFont(QFont())
        center_layout.addWidget(self.content_title)

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
        center_layout.addWidget(self.browse_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.placeholder = QLabel(tr("Drag and drop photos here or click to import"))
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # File
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Camera
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Lens
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Aperture
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Shutter
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # ISO
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Status
        header.resizeSection(3, 90)  # Aperture width
        header.resizeSection(4, 90)  # Shutter width
        header.resizeSection(5, 70)  # ISO width
        header.resizeSection(7, 60)  # Status width
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
        
        self.info_file = QLabel("-")
        self.info_camera = QLabel("-")
        self.info_lens = QLabel("-")
        self.info_date = QLabel("-")
        self.info_status = QLabel("-")
        
        # Style for value labels with monospace font for technical data
        value_style = "color: #1d1d1f; font-size: 12px; font-family: 'Consolas', 'Courier New', monospace;"
        for lbl in [self.info_file, self.info_camera, self.info_lens, self.info_date, self.info_status]:
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setStyleSheet(value_style)
            lbl.setWordWrap(True)
        
        # Label style
        label_style = "color: #86868b; font-size: 11px;"
        
        self.file_label = QLabel(tr("File:"))
        self.file_label.setStyleSheet(label_style)
        form.addRow(self.file_label, self.info_file)
        
        self.camera_label = QLabel(tr("Camera:"))
        self.camera_label.setStyleSheet(label_style)
        form.addRow(self.camera_label, self.info_camera)
        
        self.lens_label = QLabel(tr("Lens:"))
        self.lens_label.setStyleSheet(label_style)
        form.addRow(self.lens_label, self.info_lens)
        
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

        # Enable drag-and-drop on the main window / 启用窗口拖拽导入
        self.setAcceptDrops(True)

    # --- Drag & Drop handlers / 拖拽处理 ---
    def dragEnterEvent(self, event):
        """Accept drag if it contains supported image files / 如果包含支持的图像文件则接受拖拽"""
        if self._has_supported_files(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle dropped files / 处理拖入的文件"""
        paths = self._extract_files(event.mimeData())
        if not paths:
            event.ignore()
            return
        self.on_files_dropped(paths)
        event.acceptProposedAction()

    def _has_supported_files(self, mime_data) -> bool:
        """Check mime data for at least one supported file / 检查是否含有至少一个支持的文件"""
        if not mime_data.hasUrls():
            return False
        for url in mime_data.urls():
            ext = Path(url.toLocalFile()).suffix.lower()
            if ext in self.supported_ext:
                return True
        return False

    def _extract_files(self, mime_data) -> List[str]:
        """Extract supported file paths / 提取支持的文件路径"""
        if not mime_data.hasUrls():
            return []
        paths: List[str] = []
        for url in mime_data.urls():
            file_path = Path(url.toLocalFile())
            if file_path.is_file() and file_path.suffix.lower() in self.supported_ext:
                paths.append(str(file_path))
        return paths

    def on_files_dropped(self, file_paths: List[str]):
        """Callback when files are dropped / 当文件被拖入时的回调"""
        unique_files = [p for p in file_paths if p not in {item.file_path for item in self.model.photos}]
        if unique_files:
            self.model.add_photos(unique_files)
            self.queue_exif_read(unique_files)
        total = self.model.rowCount()
        self.placeholder.setVisible(total == 0)
        if total:
            self.placeholder.setText(
                tr("Imported {count} file(s). Drag more to add.", count=total)
            )
        print("Imported files:", unique_files)

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
        self.worker.finished.connect(self.worker_thread.quit)
        self.start_exif_read.connect(self.worker.read_exif)

        # Ensure the thread stops when window closes
        self.destroyed.connect(lambda: self._stop_worker())

    def queue_exif_read(self, file_paths: List[str]):
        """Queue EXIF read in worker thread / 在工作线程中排队读取 EXIF"""
        if not file_paths:
            return
        if not self.worker_thread.isRunning():
            self.worker_thread.start()
        # Emit signal to run in worker thread (queued connection)
        self.start_exif_read.emit(file_paths)

    def on_exif_results(self, results: dict):
        """Handle EXIF results / 处理 EXIF 结果"""
        for file_path, exif_data in results.items():
            self.model.set_exif_data(file_path, exif_data)
        self._refresh_inspector()

    def on_exif_error(self, error_msg: str):
        """Handle worker errors / 处理工作线程错误"""
        # For now, just log to console; can surface in UI later
        print("EXIF worker error:", error_msg)

    def on_selection_changed(self, *_):
        """Update inspector when selection changes / 选择变化时更新检查器"""
        self._refresh_inspector()

    def _refresh_inspector(self):
        """Refresh inspector panel based on current selection / 根据当前选择刷新检查器"""
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            self.info_file.setText("-")
            self.info_camera.setText("-")
            self.info_lens.setText("-")
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
        self.info_camera.setText(exif.get("Model", "Loading..." if photo.exif_data is None else "--"))
        self.info_lens.setText(exif.get("LensModel", "Loading..." if photo.exif_data is None else "--"))
        self.info_date.setText(exif.get("DateTimeOriginal", "Loading..." if photo.exif_data is None else "--"))
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
        self.json_import_btn.setText(f"📄 {tr('Import JSON')}")
        
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
        self.date_label.setText(tr("Date:"))
        self.status_label.setText(tr("Status:"))
        
        # Update exposure section / 更新曝光区域
        self.exposure_label.setText(tr("Exposure"))
        self.aperture_label.setText(tr("Aperture:"))
        self.shutter_label.setText(tr("Shutter:"))
        self.iso_label.setText(tr("ISO:"))
    
    def import_json(self):
        """Import film log JSON and match with photos / 导入胶片日志 JSON 并与照片匹配"""
        # Check if photos are imported / 检查是否已导入照片
        if self.model.rowCount() == 0:
            QMessageBox.warning(
                self, 
                tr("No photos imported"), 
                tr("Please import photos first")
            )
            return
        
        # Select JSON file / 选择 JSON 文件
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select JSON file"),
            "",
            tr("JSON Files (*.json)")
        )
        
        if not file_path:
            return
        
        try:
            # Parse JSON / 解析 JSON
            progress = QProgressDialog(
                tr("Parsing JSON..."), 
                None, 
                0, 
                0, 
                self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            parser = FilmLogParser()
            log_entries = parser.parse_file(file_path)
            
            if not log_entries:
                progress.close()
                QMessageBox.warning(self, tr("Import JSON"), "No valid entries found in JSON")
                return
            
            # Store log entries for later use / 存储日志条目供后续使用
            self.log_entries = log_entries
            
            # Update progress / 更新进度
            progress.setLabelText(tr("Matching photos..."))
            
            # Match photos with log entries / 匹配照片与日志条目
            matcher = PhotoMatcher()
            match_tuples = matcher.match_hybrid(self.model.photos, log_entries)
            
            # Convert to index-based dict / 转换为基于索引的字典
            matches = {}
            for photo_idx, (photo, log_entry) in enumerate(match_tuples):
                if log_entry:
                    log_idx = log_entries.index(log_entry)
                    matches[photo_idx] = log_idx
                else:
                    matches[photo_idx] = None
            
            stats = matcher.get_match_statistics(match_tuples)
            
            progress.close()
            
            # Show match preview dialog / 显示匹配预览对话框
            from src.ui.match_dialog import MatchPreviewDialog
            dialog = MatchPreviewDialog(self.model.photos, log_entries, matches, stats, self)
            
            if dialog.exec():
                # Apply matches / 应用匹配
                confirmed_matches = dialog.get_confirmed_matches()
                self._apply_json_matches(confirmed_matches)
                
        except Exception as e:
            QMessageBox.critical(self, tr("Import JSON"), f"Error: {str(e)}")
    
    def _apply_json_matches(self, matches):
        """Apply matched JSON data to photos / 将匹配的 JSON 数据应用到照片"""
        # Build write tasks / 构建写入任务
        write_tasks = []
        
        for photo_idx, log_idx in matches.items():
            if log_idx is None:
                continue
            
            photo = self.model.photos[photo_idx]
            log_entry = self.log_entries[log_idx]
            
            # Build EXIF data dict from log entry / 从日志条目构建 EXIF 数据字典
            exif_data = {}
            
            if log_entry.camera:
                exif_data['Make'] = log_entry.camera.split()[0] if ' ' in log_entry.camera else log_entry.camera
                exif_data['Model'] = log_entry.camera
            
            if log_entry.lens:
                exif_data['LensModel'] = log_entry.lens
            
            if log_entry.aperture:
                exif_data['FNumber'] = log_entry.aperture
            
            if log_entry.shutter_speed:
                exif_data['ExposureTime'] = log_entry.shutter_speed
            
            if log_entry.iso:
                exif_data['ISO'] = log_entry.iso
            
            if log_entry.focal_length:
                exif_data['FocalLength'] = log_entry.focal_length
            
            if log_entry.film_stock:
                exif_data['UserComment'] = f"Film: {log_entry.film_stock}"
            
            if log_entry.timestamp:
                date_str = log_entry.timestamp.strftime("%Y:%m:%d %H:%M:%S")
                exif_data['DateTimeOriginal'] = date_str
                exif_data['CreateDate'] = date_str
            
            if exif_data:
                write_tasks.append({
                    'file_path': photo.file_path,
                    'exif_data': exif_data
                })
        
        if not write_tasks:
            QMessageBox.information(self, tr("Import JSON"), "No data to write")
            return
        
        # Store log entries for later use / 存储日志条目供后续使用
        self.log_entries = [log_entry for _, log_entry in 
                           [(matches.get(i), self.log_entries[matches[i]]) 
                            for i in range(len(self.model.photos)) if matches.get(i) is not None]]
        
        # Show progress dialog / 显示进度对话框
        progress = QProgressDialog(
            tr("Writing EXIF data..."),
            None,
            0,
            100,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Setup worker for batch write / 设置批量写入工作线程
        write_worker = ExifToolWorker()
        write_thread = QThread()
        write_worker.moveToThread(write_thread)
        
        # Connect signals / 连接信号
        write_worker.progress.connect(progress.setValue)
        write_worker.result_ready.connect(
            lambda result: self._on_batch_write_complete(result, progress, write_thread)
        )
        write_worker.error_occurred.connect(
            lambda error: self._on_batch_write_error(error, progress, write_thread)
        )
        write_worker.finished.connect(write_thread.quit)
        write_thread.started.connect(lambda: write_worker.batch_write_exif(write_tasks))
        
        # Start thread / 启动线程
        write_thread.start()
    
    def _on_batch_write_complete(self, result, progress, thread):
        """Handle batch write completion / 处理批量写入完成"""
        progress.close()
        
        success_count = result.get('success', 0)
        failed_count = result.get('failed', 0)
        total_count = result.get('total', 0)
        
        # Show completion message / 显示完成消息
        if failed_count == 0:
            QMessageBox.information(
                self,
                tr("Import JSON"),
                f"Successfully wrote EXIF to {success_count} file(s)"
            )
        else:
            QMessageBox.warning(
                self,
                tr("Import JSON"),
                f"Wrote {success_count}/{total_count} file(s). {failed_count} failed."
            )
        
        # Refresh photo data / 刷新照片数据
        file_paths = [photo.file_path for photo in self.model.photos]
        self._read_exif_async(file_paths)
        
        # Cleanup / 清理
        thread.wait()
    
    def _on_batch_write_error(self, error, progress, thread):
        """Handle batch write error / 处理批量写入错误"""
        progress.close()
        QMessageBox.critical(self, tr("Import JSON"), f"Error: {error}")
        thread.quit()
        thread.wait()

        
        
        # Trigger model header refresh / 触发模型表头刷新
        self.model.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.model.COLUMNS) - 1)
