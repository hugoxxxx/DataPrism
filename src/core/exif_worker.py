#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker thread for asynchronous ExifTool operations
异步 ExifTool 操作的工作线程
"""

from PySide6.QtCore import QThread, Signal, QObject
from typing import List, Dict, Any, Optional
import subprocess
import json
import time
from src.utils.logger import get_logger
from src.core.config import get_config
from src.utils.i18n import tr

logger = get_logger('DataPrism.ExifWorker')
config = get_config()


class ExifToolWorker(QObject):
    """
    Worker for async ExifTool operations (non-blocking UI)
    异步 ExifTool 操作的工作线程（不阻塞 UI）
    """
    
    # Signals for communication with main thread
    # 与主线程通信的信号
    progress = Signal(int)  # Current progress (0-100)
    read_finished = Signal(dict)  # Results from reading EXIF
    write_finished = Signal(dict) # Results from writing metadata
    error_occurred = Signal(str)  # Error message
    finished = Signal()  # Operation finished
    start_write = Signal(list)  # Trigger batch write with tasks / 触发批量写入
    single_write = Signal(str, dict) # Trigger single write (file_path, exif_data)
    log_message = Signal(str)  # Real-time log message for UI / UI 实时日志消息
    
    def __init__(self, exiftool_path: str = None):
        """
        Initialize worker
        初始化工作线程
        
        Args:
            exiftool_path: Path to exiftool executable / exiftool 可执行文件路径
                          If None, uses value from config / 如果为 None，使用配置中的值
        """
        super().__init__()
        
        # Use config values / 使用配置值
        self.exiftool_path = exiftool_path or config.get('exiftool_path', 'exiftool')
        self.MAX_RETRIES = config.get('exiftool_max_retries', 3)
        self.RETRY_DELAY = 0.5  # Fixed delay / 固定延迟
        
        self.task_queue: List[Dict[str, Any]] = []
        self._is_running = False
        self.last_result: Optional[Dict[str, Any]] = None  # Store last batch write result
    
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
                    self.log_message.emit(tr("Reading EXIF: {file_path}").format(file_path=file_path))
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
            
            self.read_finished.emit(results)
        
        except Exception as e:
            self.error_occurred.emit(f"Batch read failed: {str(e)}")
        finally:
            self.finished.emit()
    
    def read_exif_sync(self, file_path: str) -> Dict[str, Any]:
        """
        Read EXIF data from file synchronously / 同步读取文件的EXIF数据
        
        Args:
            file_path: Path to image file / 图像文件路径
            
        Returns:
            Dictionary of EXIF data / EXIF数据字典
        """
        try:
            # Use flat keys (no -G) for consistency with PhotoDataModel
            cmd = [self.exiftool_path, "-j", "-a", file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                timeout=5
            )
            
            stdout = result.stdout.decode("utf-8", errors="replace")
            
            if result.returncode == 0:
                data = json.loads(stdout)
                if data and len(data) > 0:
                    return data[0]
            
            return {}
        
        except Exception as e:
            logger.error(f"Error reading EXIF sync: {e}")
            return {}
    
    def _run_exiftool_with_retry(self, cmd: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Execute exiftool command with retry mechanism / 带重试机制执行 exiftool 命令
        
        Args:
            cmd: Command to execute / 要执行的命令
            timeout: Timeout in seconds / 超时时间（秒）
        
        Returns:
            subprocess.CompletedProcess: Command result / 命令结果
        
        Raises:
            RuntimeError: If all retry attempts fail / 如果所有重试都失败
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"ExifTool attempt {attempt + 1}/{self.MAX_RETRIES}: {' '.join(cmd[:3])}...")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0:
                    if attempt > 0:
                        logger.info(f"ExifTool succeeded on attempt {attempt + 1}")
                    return result
                
                # Command failed, prepare for retry / 命令失败，准备重试
                last_error = result.stderr or "Unknown error"
                logger.warning(f"ExifTool attempt {attempt + 1} failed: {last_error}")
                
                # Wait before retry (exponential backoff) / 重试前等待（指数退避）
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.debug(f"Waiting {delay}s before retry")
                    time.sleep(delay)
            
            except subprocess.TimeoutExpired as e:
                last_error = f"Timeout after {timeout}s"
                logger.warning(f"ExifTool attempt {attempt + 1} timed out")
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"ExifTool failed after {self.MAX_RETRIES} attempts: {last_error}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"ExifTool attempt {attempt + 1} error: {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"ExifTool failed after {self.MAX_RETRIES} attempts: {last_error}")
        
        raise RuntimeError(f"ExifTool failed after {self.MAX_RETRIES} attempts: {last_error}")
    
    def write_exif(self, file_path: str, exif_data: Dict[str, Any]) -> None:
        """
        Write EXIF data to file asynchronously
        异步写入 EXIF 数据到文件
        
        Args:
            file_path: Path to image file / 图像文件路径
            exif_data: EXIF tags to write / 要写入的 EXIF 标签
        """
        try:
            # Build exiftool command / 构建 exiftool 命令
            cmd = [self.exiftool_path, "-charset", "filename=utf8", "-charset", "utf8"]
            
            # Dynamic flags from config / 来自配置的动态标志
            if config.get('overwrite_original', True):
                cmd.append("-overwrite_original")
            if config.get('preserve_modify_date', True):
                cmd.append("-P") # Preserve date/time of original file

            for tag, value in exif_data.items():
                if value is not None:
                    cmd.append(f"-{tag}={value}")

            cmd.append(file_path)

            msg = tr("Writing single EXIF to: {file_path}").format(file_path=file_path)
            logger.info(msg)
            self.log_message.emit(msg)
            # Use retry mechanism / 使用重试机制
            self._run_exiftool_with_retry(cmd, timeout=30)
            
            self.write_finished.emit({
                "status": "success",
                "file": file_path,
                "message": "EXIF data written successfully"
            })
        
        except Exception as e:
            logger.error(f"Failed to write EXIF to {file_path}: {e}")
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

                # Build exiftool command / 构建 exiftool 命令
                cmd = [self.exiftool_path, "-charset", "filename=utf8", "-charset", "utf8"]
                
                # Dynamic flags from config / 来自配置的动态标志
                if config.get('overwrite_original', True):
                    cmd.append("-overwrite_original")
                if config.get('preserve_modify_date', True):
                    cmd.append("-P") # Preserve date/time of original file

                for tag, value in exif_data.items():
                    if value is not None:
                        # Even if string is empty, we might want to clear the tag
                        # 但 ExifTool 写空标签的语法是 -Tag=
                        cmd.append(f"-{tag}={value}")

                cmd.append(file_path)

                try:
                    msg = tr("Writing EXIF to: {file_path}").format(file_path=file_path)
                    logger.info(msg)
                    self.log_message.emit(msg)
                    logger.info(f"Full Command: {' '.join(cmd)}")
                    
                    # Use retry mechanism / 使用重试机制
                    result = self._run_exiftool_with_retry(cmd, timeout=30)
                    
                    results.append({
                        "status": "success",
                        "file": file_path,
                        "message": "EXIF written"
                    })
                    logger.info(f"Successfully wrote EXIF to: {file_path}")
                except RuntimeError as e:
                    # Retry mechanism failed / 重试机制失败
                    results.append({
                        "status": "error",
                        "file": file_path,
                        "message": str(e)
                    })
                    logger.error(f"Failed to write EXIF to {file_path}: {e}")
                except Exception as e:
                    results.append({
                        "status": "error",
                        "file": file_path,
                        "message": str(e)
                    })
                    logger.error(f"Unexpected error writing {file_path}: {e}")
                
                # Emit progress / 发出进度信号
                progress = int((idx + 1) / total_tasks * 100)
                self.progress.emit(progress)
            
            # Emit results / 发出结果
            result_dict = {
                "batch_write": True,
                "results": results,
                "total": total_tasks,
                "success": sum(1 for r in results if r['status'] == 'success'),
                "failed": sum(1 for r in results if r['status'] == 'error')
            }
            # Store result for retrieval in finished handler
            self.last_result = result_dict
            logger.debug(f"Stored batch write result: {result_dict['success']}/{result_dict['total']} successful")
            # Emit write_finished for batch results / 发出批量结果信号
            self.write_finished.emit(result_dict)
        
        except Exception as e:
            logger.critical(f"Exception in batch_write_exif: {e}", exc_info=True)
            self.error_occurred.emit(f"Batch write failed: {str(e)}")
        finally:
            self.finished.emit()

