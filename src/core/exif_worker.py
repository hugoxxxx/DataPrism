#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker thread for asynchronous ExifTool operations
异步 ExifTool 操作的工作线程
"""

from PySide6.QtCore import QThread, Signal, QObject
from typing import List, Dict, Any
import subprocess
import json
import logging

logger = logging.getLogger(__name__)


class ExifToolWorker(QObject):
    """
    Worker for async ExifTool operations (non-blocking UI)
    异步 ExifTool 操作的工作线程（不阻塞 UI）
    """
    
    # Signals for communication with main thread
    # 与主线程通信的信号
    progress = Signal(int)  # Current progress (0-100)
    result_ready = Signal(dict)  # Results from ExifTool
    error_occurred = Signal(str)  # Error message
    finished = Signal()  # Operation finished
    
    def __init__(self, exiftool_path: str = "exiftool"):
        """
        Initialize worker
        初始化工作线程
        
        Args:
            exiftool_path: Path to exiftool executable / exiftool 可执行文件路径
        """
        super().__init__()
        self.exiftool_path = exiftool_path
        self.task_queue: List[Dict[str, Any]] = []
        self._is_running = False
    
    def read_exif(self, file_paths: List[str]) -> None:
        """
        Read EXIF data from multiple files asynchronously
        异步读取多个文件的 EXIF 数据
        
        Args:
            file_paths: List of image file paths / 图像文件路径列表
        """
        try:
            total_files = len(file_paths)
            results = {}
            
            for idx, file_path in enumerate(file_paths):
                try:
                    # Execute exiftool command
                    # 执行 exiftool 命令
                    cmd = [self.exiftool_path, "-json", file_path]
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=False,  # handle bytes to avoid codec issues
                        timeout=15
                    )

                    stdout = result.stdout.decode("utf-8", errors="replace")
                    stderr = result.stderr.decode("utf-8", errors="replace")

                    if result.returncode == 0:
                        try:
                            data = json.loads(stdout)
                            results[file_path] = data[0] if data else {}
                        except Exception as e:
                            results[file_path] = {"error": f"JSON parse error: {e}"}
                    else:
                        results[file_path] = {"error": stderr or "exiftool failed"}
                
                except subprocess.TimeoutExpired:
                    results[file_path] = {"error": "Timeout reading EXIF"}
                    logger.warning(f"Timeout reading {file_path}")
                except Exception as e:
                    results[file_path] = {"error": str(e)}
                    logger.error(f"Error reading {file_path}: {e}")
                
                # Emit progress signal
                # 发出进度信号
                progress = int((idx + 1) / total_files * 100)
                self.progress.emit(progress)
            
            self.result_ready.emit(results)
        
        except Exception as e:
            self.error_occurred.emit(f"Batch read failed: {str(e)}")
        finally:
            self.finished.emit()
    
    def write_exif(self, file_path: str, exif_data: Dict[str, Any]) -> None:
        """
        Write EXIF data to file asynchronously
        异步写入 EXIF 数据到文件
        
        Args:
            file_path: Path to image file / 图像文件路径
            exif_data: EXIF tags to write / 要写入的 EXIF 标签
        """
        try:
            # Build exiftool command with tag assignments
            # 使用标签赋值构建 exiftool 命令
            cmd = [self.exiftool_path, "-overwrite_original"]
            
            for tag, value in exif_data.items():
                cmd.append(f"-{tag}={value}")
            
            cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.result_ready.emit({
                    "status": "success",
                    "file": file_path,
                    "message": "EXIF data written successfully"
                })
            else:
                self.error_occurred.emit(f"Write failed: {result.stderr}")
        
        except Exception as e:
            self.error_occurred.emit(f"Write error: {str(e)}")
        finally:
            self.finished.emit()
    
    def batch_write_exif(self, write_tasks: List[Dict[str, Any]]) -> None:
        """
        Batch write EXIF data to multiple files asynchronously
        异步批量写入 EXIF 数据到多个文件
        
        Args:
            write_tasks: List of dicts with 'file_path' and 'exif_data' / 包含 'file_path' 和 'exif_data' 的字典列表
        """
        try:
            total_tasks = len(write_tasks)
            results = []
            
            for idx, task in enumerate(write_tasks):
                file_path = task.get('file_path')
                exif_data = task.get('exif_data', {})
                
                if not file_path or not exif_data:
                    results.append({
                        "status": "error",
                        "file": file_path,
                        "message": "Invalid task data"
                    })
                    continue
                
                try:
                    # Build exiftool command / 构建 exiftool 命令
                    cmd = [self.exiftool_path, "-overwrite_original"]
                    
                    for tag, value in exif_data.items():
                        if value:  # Only write non-empty values
                            cmd.append(f"-{tag}={value}")
                    
                    cmd.append(file_path)
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=False,
                        timeout=10
                    )
                    
                    stdout = result.stdout.decode("utf-8", errors="replace")
                    stderr = result.stderr.decode("utf-8", errors="replace")
                    
                    if result.returncode == 0:
                        results.append({
                            "status": "success",
                            "file": file_path,
                            "message": "EXIF written"
                        })
                    else:
                        results.append({
                            "status": "error",
                            "file": file_path,
                            "message": stderr or "Write failed"
                        })
                
                except subprocess.TimeoutExpired:
                    results.append({
                        "status": "error",
                        "file": file_path,
                        "message": "Timeout"
                    })
                except Exception as e:
                    results.append({
                        "status": "error",
                        "file": file_path,
                        "message": str(e)
                    })
                
                # Emit progress / 发出进度信号
                progress = int((idx + 1) / total_tasks * 100)
                self.progress.emit(progress)
            
            # Emit results / 发出结果
            self.result_ready.emit({
                "batch_write": True,
                "results": results,
                "total": total_tasks,
                "success": sum(1 for r in results if r['status'] == 'success'),
                "failed": sum(1 for r in results if r['status'] == 'error')
            })
        
        except Exception as e:
            self.error_occurred.emit(f"Batch write failed: {str(e)}")
        finally:
            self.finished.emit()

