#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata editor dialog for previewing and modifying imported metadata
用于预览和修改导入元数据的编辑对话框
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QFormLayout, QLineEdit, QLabel, QPushButton, QSlider, QSpinBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QProgressDialog, QHeaderView,
    QApplication
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor

import logging

from src.core.photo_model import PhotoItem
from src.core.metadata_parser import MetadataEntry
from src.core.exif_worker import ExifToolWorker
from src.utils.i18n import tr

logger = logging.getLogger(__name__)


class MetadataEditorDialog(QDialog):
    """
    Dialog for editing and applying metadata to photos / 用于编辑和应用元数据到照片的对话框
    """
    
    # Signal emitted when metadata is successfully written / 元数据成功写入时发出的信号
    metadata_written = Signal()
    
    def __init__(
        self,
        photos: List[PhotoItem],
        metadata_entries: List[MetadataEntry],
        parent=None
    ):
        super().__init__(parent)
        self.photos = photos
        self.metadata_entries = metadata_entries
        self.current_index = 0
        self.offset = 0  # Sequence offset / 序列偏移
        
        self.setWindowTitle(tr("Metadata Editor"))
        self.setMinimumSize(1200, 700)
        self.setup_ui()
        self.check_count_match()
        self.load_photo(0)
    
    def setup_ui(self):
        """Setup UI components / 设置 UI 组件"""
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== 左侧：照片列表 ==========
        left_widget = QVBoxLayout()
        
        left_title = QLabel(tr("Photos"))
        left_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_widget.addWidget(left_title)
        
        self.photo_list = QListWidget()
        self.photo_list.setMinimumWidth(200)
        for i, photo in enumerate(self.photos):
            display_text = photo.file_name or f"Photo {i+1}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, i)
            self.photo_list.addItem(item)
        
        self.photo_list.itemClicked.connect(self.on_photo_selected)
        left_widget.addWidget(self.photo_list)
        
        # ========== 右侧：元数据编辑 ==========
        right_widget = QVBoxLayout()
        
        right_title = QLabel(tr("Metadata"))
        right_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        right_widget.addWidget(right_title)
        
        # 编辑表单 / Edit form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.edit_camera = QLineEdit()
        self.edit_lens = QLineEdit()
        self.edit_aperture = QLineEdit()
        self.edit_shutter = QLineEdit()
        self.edit_iso = QLineEdit()
        self.edit_film_stock = QLineEdit()
        self.edit_focal_length = QLineEdit()
        self.edit_shot_date = QLineEdit()
        self.edit_location = QLineEdit()
        self.edit_notes = QLineEdit()
        
        for edit_field in [self.edit_camera, self.edit_lens, self.edit_aperture,
                          self.edit_shutter, self.edit_iso, self.edit_film_stock,
                          self.edit_focal_length, self.edit_shot_date, self.edit_location,
                          self.edit_notes]:
            edit_field.setMinimumHeight(32)
        
        form_layout.addRow(QLabel(tr("Camera:")), self.edit_camera)
        form_layout.addRow(QLabel(tr("Lens:")), self.edit_lens)
        form_layout.addRow(QLabel(tr("Aperture:")), self.edit_aperture)
        form_layout.addRow(QLabel(tr("Shutter:")), self.edit_shutter)
        form_layout.addRow(QLabel(tr("ISO:")), self.edit_iso)
        form_layout.addRow(QLabel(tr("Film Stock:")), self.edit_film_stock)
        form_layout.addRow(QLabel(tr("Focal Length:")), self.edit_focal_length)
        form_layout.addRow(QLabel(tr("Shot Date:")), self.edit_shot_date)
        form_layout.addRow(QLabel(tr("Location:")), self.edit_location)
        form_layout.addRow(QLabel(tr("Notes:")), self.edit_notes)
        
        right_widget.addLayout(form_layout)
        right_widget.addStretch()
        
        # ========== 底部：序列平移 + 警告 + 按钮 ==========
        bottom_widget = QVBoxLayout()
        
        # 数量警告 / Count warning
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        bottom_widget.addWidget(self.warning_label)
        
        # 序列平移滑块 / Sequence offset slider
        offset_layout = QHBoxLayout()
        offset_label = QLabel(tr("Sequence Offset:"))
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(-20, 20)
        self.offset_spin.setValue(0)
        self.offset_spin.setSuffix(" frames")
        self.offset_spin.setMinimumWidth(100)
        self.offset_spin.valueChanged.connect(self.on_offset_changed)
        
        offset_layout.addWidget(offset_label)
        offset_layout.addWidget(self.offset_spin)
        offset_layout.addStretch()
        bottom_widget.addLayout(offset_layout)
        
        # 按钮 / Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(tr("Cancel"))
        cancel_btn.setMinimumSize(100, 36)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                background: #f0f0f5;
                border: 1px solid #e5e5ea;
                font-size: 13px;
            }
            QPushButton:hover { background: #e8e8ed; }
        """)
        button_layout.addWidget(cancel_btn)
        
        write_btn = QPushButton(tr("Write All Files"))
        write_btn.setMinimumSize(140, 36)
        write_btn.clicked.connect(self.on_write_metadata)
        write_btn.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #34c759, stop:1 #28a745);
                border: none;
                color: white;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #40d865, stop:1 #2fb84f);
            }
        """)
        button_layout.addWidget(write_btn)
        
        bottom_widget.addLayout(button_layout)
        
        # 组合左右布局 / Combine layouts
        left_container = QVBoxLayout()
        left_container.addLayout(left_widget)
        left_container.setContentsMargins(0, 0, 0, 0)
        
        right_container = QVBoxLayout()
        right_container.addLayout(right_widget)
        right_container.addLayout(bottom_widget)
        right_container.setContentsMargins(0, 0, 0, 0)
        
        layout.addLayout(left_container, 1)
        layout.addLayout(right_container, 2)
    
    def check_count_match(self):
        """Check if counts match and show warning / 检查数量是否匹配并显示警告"""
        photo_count = len(self.photos)
        metadata_count = len(self.metadata_entries)
        
        if photo_count == metadata_count:
            self.warning_label.setText("")
        else:
            self.warning_label.setText(
                tr("Warning: {meta} records but {photo} photos").format(
                    meta=metadata_count,
                    photo=photo_count
                )
            )
    
    def on_photo_selected(self, item: QListWidgetItem):
        """Handle photo selection / 处理照片选择"""
        index = item.data(Qt.UserRole)
        self.load_photo(index)
    
    def load_photo(self, index: int):
        """Load photo and corresponding metadata / 加载照片和对应的元数据"""
        if 0 <= index < len(self.photos):
            self.current_index = index
            self.photo_list.setCurrentRow(index)
            
            # 获取对应的元数据（考虑偏移） / Get corresponding metadata with offset
            metadata_idx = index + self.offset
            
            logger.debug(f"Loading photo {index}: {self.photos[index].file_name}")
            logger.debug(f"Metadata index (with offset {self.offset}): {metadata_idx}")
            
            # 清空编辑框 / Clear edit fields
            self.edit_camera.clear()
            self.edit_lens.clear()
            self.edit_aperture.clear()
            self.edit_shutter.clear()
            self.edit_iso.clear()
            self.edit_film_stock.clear()
            self.edit_focal_length.clear()
            self.edit_shot_date.clear()
            self.edit_location.clear()
            self.edit_notes.clear()
            
            # 填充数据（如果存在） / Fill data if exists
            if 0 <= metadata_idx < len(self.metadata_entries):
                entry = self.metadata_entries[metadata_idx]
                
                logger.debug(f"Found metadata entry at index {metadata_idx}")
                logger.debug(f"  camera: {entry.camera}")
                logger.debug(f"  lens: {entry.lens}")
                logger.debug(f"  aperture: {entry.aperture}")
                logger.debug(f"  shutter_speed: {entry.shutter_speed}")
                logger.debug(f"  iso: {entry.iso}")
                logger.debug(f"  film_stock: {entry.film_stock}")
                logger.debug(f"  focal_length: {entry.focal_length}")
                logger.debug(f"  shot_date: {entry.shot_date}")
                logger.debug(f"  location: {entry.location}")
                
                self.edit_camera.setText(entry.camera or "")
                self.edit_lens.setText(entry.lens or "")
                self.edit_aperture.setText(entry.aperture or "")
                self.edit_shutter.setText(entry.shutter_speed or "")
                self.edit_iso.setText(entry.iso or "")
                self.edit_film_stock.setText(entry.film_stock or "")
                self.edit_focal_length.setText(entry.focal_length or "")
                self.edit_shot_date.setText(entry.shot_date or "")
                self.edit_location.setText(entry.location or "")
                self.edit_notes.setText(entry.notes or "")
            else:
                logger.warning(f"No metadata found at index {metadata_idx}. "
                              f"Valid range: 0-{len(self.metadata_entries)-1}")
    
    def on_offset_changed(self):
        """Handle offset change / 处理偏移变化"""
        self.offset = self.offset_spin.value()
        self.load_photo(self.current_index)
    
    def on_write_metadata(self):
        """Write metadata to all photos / 写入元数据到所有照片"""
        # Confirm with user / 确认用户
        reply = QMessageBox.question(
            self,
            tr("Write Metadata"),
            tr("This will modify EXIF data in all {count} photos. Continue?").format(
                count=len(self.photos)
            ),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Build write tasks / 构建写入任务
        write_tasks = []
        for i, photo in enumerate(self.photos):
            metadata_idx = i + self.offset
            
            if 0 <= metadata_idx < len(self.metadata_entries):
                entry = self.metadata_entries[metadata_idx]
                exif_data = self._build_exif_dict(entry)
                
                logger.debug(f"Photo {i}: {photo.file_name} → metadata[{metadata_idx}]")
                logger.debug(f"  EXIF data: {exif_data}")
                
                if exif_data:
                    write_tasks.append({
                        'file_path': photo.file_path,
                        'exif_data': exif_data
                    })
            else:
                logger.warning(f"Photo {i}: {photo.file_name} - no metadata at index {metadata_idx}")
        
        if not write_tasks:
            QMessageBox.warning(self, tr("Write Metadata"), "No valid data to write")
            return
        
        # Show progress / 显示进度
        progress = QProgressDialog(
            tr("Writing metadata..."),
            None,
            0,
            100,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # 确保进度条总是显示
        progress.show()
        # keep reference so other slots can close it if needed
        self._write_progress = progress
        
        # Setup worker / 设置工作线程
        self.write_worker = ExifToolWorker()
        self.write_thread = QThread()
        self.write_worker.moveToThread(self.write_thread)

        # Connect signals / 连接信号
        def _on_progress(val):
            try:
                print(f"[MetadataEditor] write progress: {val}")
            except Exception:
                pass
            progress.setValue(val)

        def _on_result(result):
            try:
                print(f"[MetadataEditor] write result_ready emitted: {result}")
            except Exception:
                pass
            self._on_write_complete(result, progress)

        def _on_error(err):
            try:
                print(f"[MetadataEditor] write error emitted: {err}")
            except Exception:
                pass
            self._on_write_error(err, progress)

        self.write_worker.progress.connect(_on_progress)
        self.write_worker.result_ready.connect(_on_result)
        self.write_worker.error_occurred.connect(_on_error)
        self.write_worker.finished.connect(self.write_thread.quit)
        self.write_worker.finished.connect(self.write_worker.deleteLater)
        # Debug: notify when worker finished
        self.write_worker.finished.connect(lambda: print("[MetadataEditor] write_worker.finished emitted"))
        self.write_thread.finished.connect(self.write_thread.deleteLater)
        self.write_thread.finished.connect(lambda: print("[MetadataEditor] write_thread.finished emitted"))
        # Fallback: ensure dialog closes when thread finishes (in case result handler missed)
        self.write_thread.finished.connect(self._on_write_thread_finished)
        self.write_thread.started.connect(lambda: self.write_worker.batch_write_exif(write_tasks))
        
        # Start thread / 启动线程
        try:
            print(f"[MetadataEditor] starting write thread with {len(write_tasks)} tasks")
        except Exception:
            pass
        self.write_thread.start()
    
    def _build_exif_dict(self, entry: MetadataEntry) -> Dict[str, str]:
        """Build EXIF data dictionary from metadata entry / 从元数据条目构建 EXIF 字典"""
        exif_data = {}
        
        if entry.camera:
            # Camera can be "Make Model" format, try to split
            parts = entry.camera.strip().split(None, 1)
            if len(parts) == 2:
                exif_data['Make'] = parts[0]
                exif_data['Model'] = parts[1]
            else:
                exif_data['Make'] = entry.camera
                exif_data['Model'] = entry.camera
        
        if entry.lens:
            exif_data['LensModel'] = entry.lens
        
        if entry.aperture:
            # Convert f/2.8 format to numeric if needed
            aperture_str = entry.aperture.strip()
            if aperture_str.startswith('f/'):
                exif_data['FNumber'] = aperture_str[2:]
            else:
                exif_data['FNumber'] = aperture_str
        
        if entry.shutter_speed:
            # Keep shutter speed as-is (1/60, 1/125, etc)
            exif_data['ExposureTime'] = entry.shutter_speed
        
        if entry.iso:
            # Convert to numeric string
            iso_str = str(entry.iso).strip()
            if iso_str.lower().startswith('iso'):
                exif_data['ISO'] = iso_str[3:].strip()
            else:
                exif_data['ISO'] = iso_str
        
        if entry.focal_length:
            # Convert 80mm format to numeric if needed
            focal_str = entry.focal_length.strip()
            if focal_str.endswith('mm'):
                exif_data['FocalLength'] = focal_str[:-2]
            else:
                exif_data['FocalLength'] = focal_str
        
        if entry.shot_date:
            # Write to multiple date fields
            exif_data['DateTimeOriginal'] = entry.shot_date
            exif_data['CreateDate'] = entry.shot_date
            exif_data['ModifyDate'] = entry.shot_date
        
        if entry.location:
            # Location: write both human-readable description and GPS tags if parsable
            exif_data['ImageDescription'] = entry.location
            gps_parsed = self._parse_gps(entry.location)
            if gps_parsed:
                lat, lat_ref, lon, lon_ref = gps_parsed
                exif_data['GPSLatitude'] = lat
                exif_data['GPSLatitudeRef'] = lat_ref
                exif_data['GPSLongitude'] = lon
                exif_data['GPSLongitudeRef'] = lon_ref
        
        if entry.film_stock:
            # Film stock to UserComment
            if entry.location:
                exif_data['UserComment'] = f"Film: {entry.film_stock} | Location: {entry.location}"
            else:
                exif_data['UserComment'] = f"Film: {entry.film_stock}"
        elif entry.location and 'UserComment' not in exif_data:
            # If only location, put in UserComment as well
            exif_data['UserComment'] = f"Location: {entry.location}"
        
        if entry.notes:
            # Notes can add to UserComment or use XPComment
            if 'UserComment' in exif_data:
                exif_data['UserComment'] = f"{exif_data['UserComment']} | {entry.notes}"
            else:
                exif_data['UserComment'] = entry.notes
        
        return exif_data
    
    def _on_write_complete(self, result, progress):
        """Handle write completion / 处理写入完成"""
        # Ensure progress reaches 100 and close the dialog
        try:
            progress.setValue(100)
        except Exception:
            pass
        try:
            progress.close()
        except Exception:
            pass
        # Force UI to process pending events so the dialog visually updates
        try:
            QApplication.processEvents()
        except Exception:
            pass
        success_count = result.get('success', 0)
        failed_count = result.get('failed', 0)
        total_count = result.get('total', 0)

        logger.info(f"Write complete: success={success_count}, failed={failed_count}, total={total_count}")
        print(f"[MetadataEditor] write complete: success={success_count}, failed={failed_count}, total={total_count}")

        # Emit metadata_written so main window can refresh
        self.metadata_written.emit()

        # Emit metadata_written so main window can refresh before showing confirmation
        self.metadata_written.emit()

        # Show a modal confirmation dialog; wait for the user to click OK,
        # then close the editor. Parent to this dialog (`self`) so the
        # message is centered and modal to the editor window.
        title = tr("Write Metadata")
        if failed_count == 0:
            text = tr("Successfully wrote metadata to {count} file(s)").format(count=success_count)
        else:
            text = tr("Wrote {success}/{total} file(s). {failed} failed.").format(
                success=success_count,
                total=total_count,
                failed=failed_count
            )

        try:
            QMessageBox.information(self, title, text)
        except Exception:
            # If for some reason the modal call fails, fall back to non-modal
            try:
                msg = QMessageBox(self)
                msg.setWindowTitle(title)
                msg.setText(text)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
            except Exception:
                pass

        # Close the editor after the user confirmed
        try:
            self.accept()
        except Exception:
            pass
    
    def _on_write_error(self, error, progress):
        """Handle write error / 处理写入错误"""
        progress.close()
        QMessageBox.critical(self, tr("Write Metadata"), f"Error: {error}")

    def _on_write_thread_finished(self):
        """Fallback finalizer when write thread finishes: close progress and dialog."""
        try:
            print("[MetadataEditor] _on_write_thread_finished called")
        except Exception:
            pass
        # Close progress dialog if still open
        try:
            if hasattr(self, '_write_progress') and self._write_progress is not None:
                self._write_progress.close()
                self._write_progress = None
        except Exception:
            pass
        # Accept/close the editor if still visible
        try:
            if self.isVisible():
                QTimer.singleShot(0, self.accept)
        except Exception:
            pass

    @staticmethod
    def _parse_gps(location_text: str) -> Optional[tuple]:
        """Parse GPS string like "28deg 31' 30.59\" N, 119deg 30' 30.44\" E" to (lat, latRef, lon, lonRef)."""
        if not location_text:
            return None

        def parse_coord(text: str):
            # Try DMS with direction
            m = re.search(r"([0-9.]+)[^0-9]+([0-9.]+)[^0-9]+([0-9.]+)\s*([NSEW])", text, re.IGNORECASE)
            if m:
                deg, minute, sec, ref = m.groups()
                return f"{deg} {minute} {sec}", ref.upper()
            # Try decimal with direction suffix
            m = re.search(r"([-+]?[0-9.]+)\s*([NSEW])", text, re.IGNORECASE)
            if m:
                dec, ref = m.groups()
                return dec, ref.upper()
            # Try pure decimal, infer ref from sign
            m = re.search(r"([-+]?[0-9.]+)", text)
            if m:
                dec = float(m.group(1))
                ref = None
                if dec >= 0:
                    ref = 'N' if 'lat' in text.lower() else ('E' if 'lon' in text.lower() else None)
                else:
                    ref = 'S' if 'lat' in text.lower() else ('W' if 'lon' in text.lower() else None)
                return str(abs(dec)), ref
            return None, None

        parts = [p.strip() for p in location_text.split(',') if p.strip()]
        if len(parts) < 2:
            return None

        lat_val, lat_ref = parse_coord(parts[0])
        lon_val, lon_ref = parse_coord(parts[1])

        if lat_val and lon_val:
            # Default refs if missing but inferable
            if not lat_ref:
                lat_ref = 'N'
            if not lon_ref:
                lon_ref = 'E'
            return lat_val, lat_ref, lon_val, lon_ref
        return None
