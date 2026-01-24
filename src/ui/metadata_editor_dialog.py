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
import src.utils.gps_utils as gps_utils
from src.utils.i18n import tr
from src.utils.logger import get_logger
from src.utils.validators import MetadataValidator

logger = get_logger('DataPrism.MetadataEditor')


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
        self._completion_handled = False  # Track if completion dialog was handled / 跟踪是否已处理完成对话框
        
        self.setWindowTitle(tr("Metadata Editor"))
        self.setMinimumSize(1200, 700)
        
        # Ensure metadata_entries is large enough to cover all photos
        # 确保元数据列表足够长，以覆盖所有照片
        required_len = len(self.photos) + abs(self.offset) + 20 # Add some buffer
        if len(self.metadata_entries) < required_len:
            missing_count = required_len - len(self.metadata_entries)
            for _ in range(missing_count):
                self.metadata_entries.append(MetadataEntry())
        
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
        # Save current before switching / 切换前保存当前数据
        self._save_current_metadata()
        
        index = item.data(Qt.UserRole)
        self.load_photo(index)

    def _save_current_metadata(self):
        """Save UI values back to current metadata entry / 将 UI 值保存回当前元数据条目"""
        if self.current_index < 0:
            return
            
        metadata_idx = self.current_index + self.offset
        if 0 <= metadata_idx < len(self.metadata_entries):
            entry = self.metadata_entries[metadata_idx]
            
            # Update entry fields from UI
            # 从 UI 更新条目字段
            entry.camera = self.edit_camera.text().strip()
            entry.lens = self.edit_lens.text().strip()
            entry.aperture = self.edit_aperture.text().strip()
            entry.shutter_speed = self.edit_shutter.text().strip()
            entry.iso = self.edit_iso.text().strip()
            entry.focal_length = self.edit_focal_length.text().strip()
            entry.film_stock = self.edit_film_stock.text().strip()
            entry.shot_date = self.edit_shot_date.text().strip()
            entry.location = self.edit_location.text().strip()
            entry.notes = self.edit_notes.text().strip()
            
            # Use getattr for file_name as it's not always present in MetadataEntry
            file_name = getattr(entry, 'file_name', 'Manual Entry')
            logger.debug(f"Saved UI changes to metadata[{metadata_idx}] for {file_name}")
    
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
        # Save current before changing offset / 改变偏移前保存当前数据
        self._save_current_metadata()
        
        self.offset = self.offset_spin.value()
        self.load_photo(self.current_index)
    
    def on_write_metadata(self):
        """Write metadata to all photos / 写入元数据到所有照片"""
        # Save current before writing / 写入前保存当前数据
        self._save_current_metadata()
        
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
            logger.debug(f"Write progress: {val}%")
            progress.setValue(val)

        def _on_result(result):
            logger.debug(f"Write result received: {result}")
            self._on_write_complete(result, progress)

        def _on_error(err):
            logger.error(f"Write error: {err}")
            self._on_write_error(err, progress)

        logger.debug("Connecting write worker signals")
        self.write_worker.progress.connect(_on_progress, Qt.ConnectionType.QueuedConnection)
        self.write_worker.result_ready.connect(_on_result, Qt.ConnectionType.QueuedConnection)
        self.write_worker.error_occurred.connect(_on_error, Qt.QueuedConnection)
        logger.debug("All signals connected")
        # CRITICAL FIX: Don't connect finished signal to quit/deleteLater
        # This causes deadlock when emit() is called from worker thread
        # Instead, use QTimer to poll for completion
        
        
        # Start thread / 启动线程
        logger.info(f"Starting write thread with {len(write_tasks)} tasks")
        
        # Start the thread
        self.write_thread.start()
        
        # Emit signal to trigger write in worker thread
        # This ensures the method runs in the worker's thread context
        self.write_worker.start_write.emit(write_tasks)
        
        # Poll for completion using QTimer
        self._write_check_timer = QTimer(self)
        self._write_check_timer.timeout.connect(lambda: self._check_write_completion(progress))
        self._write_check_timer.start(100)  # Check every 100ms
    
    def _check_write_completion(self, progress):
        """Poll worker for completion / 轮询 worker 是否完成"""
        if not self.write_thread.isRunning():
            # Thread finished
            logger.debug("Write thread finished, stopping timer")
            self._write_check_timer.stop()
            
            if hasattr(self.write_worker, 'last_result') and self.write_worker.last_result:
                logger.debug(f"Retrieved write result: {self.write_worker.last_result}")
                self._on_write_complete(self.write_worker.last_result, progress)
            else:
                logger.warning("No write result found")
                progress.close()
            
            # Clean up
            self.write_thread.quit()
            self.write_thread.wait()
            self.write_worker.deleteLater()
            self.write_thread.deleteLater()
    
    def _build_exif_dict(self, entry: MetadataEntry) -> Dict[str, str]:
        """Build EXIF data dictionary from metadata entry / 从元数据条目构建 EXIF 字典"""
        exif_data = {}
        
        # Camera and lens / 相机和镜头
        if entry.camera:
            try:
                validated_camera = MetadataValidator.validate_camera_model(entry.camera)
                exif_data['Make'] = validated_camera.split()[0] if ' ' in validated_camera else validated_camera
                exif_data['Model'] = validated_camera
            except ValueError:
                # Fallback to raw value / 回退到原始值
                exif_data['Model'] = entry.camera
                if ' ' in entry.camera:
                    exif_data['Make'] = entry.camera.split()[0]
        
        if entry.lens:
            try:
                validated_lens = MetadataValidator.validate_lens_model(entry.lens)
                exif_data['LensModel'] = validated_lens
            except ValueError:
                # Fallback to raw value
                exif_data['LensModel'] = entry.lens
        
        # Exposure settings / 曝光设置
        if entry.aperture:
            try:
                validated_aperture = MetadataValidator.validate_aperture(entry.aperture)
                exif_data['FNumber'] = validated_aperture
            except ValueError:
                # Use raw string directly (ExifTool handles many formats)
                exif_data['FNumber'] = entry.aperture.replace('f/', '').replace('F/', '').replace('f', '').replace('F', '')
        
        if entry.shutter_speed:
            try:
                validated_shutter = MetadataValidator.validate_shutter_speed(entry.shutter_speed)
                exif_data['ExposureTime'] = validated_shutter
            except ValueError:
                exif_data['ExposureTime'] = entry.shutter_speed
        
        if entry.iso:
            try:
                validated_iso = MetadataValidator.validate_iso(entry.iso)
                exif_data['ISO'] = str(validated_iso)
            except ValueError:
                exif_data['ISO'] = entry.iso
        
        if entry.focal_length:
            try:
                validated_focal = MetadataValidator.validate_focal_length(entry.focal_length)
                exif_data['FocalLength'] = validated_focal
            except ValueError:
                exif_data['FocalLength'] = entry.focal_length.replace('mm', '').replace('MM', '')
        
        if entry.shot_date:
            try:
                validated_date = MetadataValidator.validate_datetime(entry.shot_date)
                exif_data['DateTimeOriginal'] = validated_date
                exif_data['CreateDate'] = validated_date
                exif_data['ModifyDate'] = validated_date
            except ValueError:
                # Ensure : format if possible
                date_fixed = entry.shot_date.replace('-', ':').replace('/', ':')
                exif_data['DateTimeOriginal'] = date_fixed
                exif_data['CreateDate'] = date_fixed
                exif_data['ModifyDate'] = date_fixed
        
        # GT23_Workflow Compatibility: Film stock takes priority in ImageDescription
        # GT23_Workflow 兼容性：ImageDescription 优先写入胶卷型号
        if entry.film_stock:
            # 1. Film field (DataPrism standard)
            exif_data['Film'] = entry.film_stock
            
            # 2. ImageDescription (GT23_Workflow auto-detection - PRIORITY)
            #    GT23 主要从这个字段自动识别胶卷型号
            exif_data['ImageDescription'] = entry.film_stock
            
            # 3. UserComment (complete information)
            if entry.location:
                exif_data['UserComment'] = f"Film: {entry.film_stock} | Location: {entry.location}"
            else:
                exif_data['UserComment'] = f"Film: {entry.film_stock}"
        
        # Location: GPS coordinates (preferred) or ImageDescription (fallback)
        # 位置：GPS 坐标（优先）或 ImageDescription（备用）
        if entry.location:
            # Try to parse as GPS coordinates
            gps_parsed = gps_utils.parse_gps_to_exif(entry.location)
            if gps_parsed:
                lat, lat_ref, lon, lon_ref = gps_parsed
                exif_data['GPSLatitude'] = lat
                exif_data['GPSLatitudeRef'] = lat_ref
                exif_data['GPSLongitude'] = lon
                exif_data['GPSLongitudeRef'] = lon_ref
            
            # If no film stock, write location to ImageDescription as fallback
            # 如果没有胶卷型号，才将位置写入 ImageDescription
            if not entry.film_stock:
                exif_data['ImageDescription'] = entry.location
                if 'UserComment' not in exif_data:
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
        logger.debug(f"Write complete callback invoked with result: {result}")
        
        # Mark as handled so fallback doesn't interfere
        self._completion_handled = True
        
        # Close progress dialog first
        try:
            progress.setValue(100)
            progress.close()
        except Exception:
            pass
        
        # Emit metadata_written so main window can refresh
        self.metadata_written.emit()
        
        success_count = result.get('success', 0)
        failed_count = result.get('failed', 0)
        total_count = result.get('total', 0)

        logger.info(f"Write complete: success={success_count}, failed={failed_count}, total={total_count}")
        
        # Build message
        title = tr("Write Metadata")
        if failed_count == 0:
            text = tr("Successfully wrote metadata to {count} file(s)").format(count=success_count)
        else:
            text = tr("Wrote {success}/{total} file(s). {failed} failed.").format(
                success=success_count,
                total=total_count,
                failed=failed_count
            )
        
        # CRITICAL: Use QTimer.singleShot to defer the modal dialog
        # This allows the event loop to process all pending signals (including finished)
        # before blocking with the modal dialog
        def show_completion_dialog():
            logger.debug("Showing completion dialog")
            try:
                QMessageBox.information(self, title, text)
            except Exception as e:
                logger.error(f"Error showing completion dialog: {e}")
            
            # Close the editor after user confirms
            logger.debug("Closing metadata editor")
            try:
                self.accept()
            except Exception as e:
                logger.error(f"Error closing editor: {e}")
        
        # Defer by 100ms to let all signals process
        QTimer.singleShot(100, show_completion_dialog)
    
    def _on_write_error(self, error, progress):
        """Handle write error / 处理写入错误"""
        progress.close()
        QMessageBox.critical(self, tr("Write Metadata"), f"Error: {error}")

    def _on_write_thread_finished(self):
        """Fallback finalizer when write thread finishes: close progress and dialog."""
        logger.debug("Write thread finished (fallback handler)")
        # Close progress dialog if still open
        try:
            if hasattr(self, '_write_progress') and self._write_progress is not None:
                self._write_progress.close()
                self._write_progress = None
        except Exception:
            pass
        # Accept/close the editor if still visible AND not handled
        # If handled, the completion dialog logic takes care of closing
        if not self._completion_handled:
            try:
                if self.isVisible():
                    # Only auto-close if we didn't show the success message
                    # (e.g. if thread finished without result_ready somehow)
                    # But ideally we shouldn't close blindly if the user expects feedback.
                    # For safety, we just log it. If we really want to close on error/silent finish:
                    pass 
                    # QTimer.singleShot(0, self.accept) 
            except Exception:
                pass
    
    def closeEvent(self, event):
        """
        Handle dialog close event / 处理对话框关闭事件
        Ensure proper resource cleanup / 确保正确清理资源
        """
        logger.info("MetadataEditorDialog closing, cleaning up resources")
        
        # Stop timer if running / 停止定时器
        if hasattr(self, '_write_check_timer') and self._write_check_timer.isActive():
            logger.debug("Stopping write check timer")
            self._write_check_timer.stop()
        
        # Wait for thread to finish / 等待线程结束
        if hasattr(self, 'write_thread') and self.write_thread.isRunning():
            logger.debug("Waiting for write thread to finish")
            self.write_thread.quit()
            
            # Wait up to 2 seconds / 最多等待 2 秒
            if not self.write_thread.wait(2000):
                logger.warning("Write thread did not finish in time, terminating")
                self.write_thread.terminate()
                self.write_thread.wait()
        
        # Clean up worker / 清理 worker
        if hasattr(self, 'write_worker'):
            logger.debug("Deleting write worker")
            self.write_worker.deleteLater()
        
        # Clean up thread / 清理线程
        if hasattr(self, 'write_thread'):
            logger.debug("Deleting write thread")
            self.write_thread.deleteLater()
        
        logger.info("Resource cleanup completed")
        super().closeEvent(event)


