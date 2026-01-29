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
import os
import platform
import concurrent.futures
from src.utils.argfile_util import ArgfileManager

# Windows-specific flag to hide console window for subprocesses
# Windows 特定的标志，用于隐藏子进程的控制台窗口
CREATE_NO_WINDOW = 0x08000000 if platform.system() == "Windows" else 0

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
        Read EXIF data from multiple files asynchronously using Argfile batching
        使用 Argfile 批量异步读取多个文件的 EXIF 数据
        
        Args:
            file_paths: List of image file paths / 图像文件路径列表
        """
        argfile_path = None
        try:
            total_files = len(file_paths)
            results = {}
            
            if not file_paths:
                self.read_finished.emit({})
                return
                
            self.log_message.emit(tr("Synchronizing metadata for {count} files...").format(count=total_files))
            
            # Create argfile for batch reading
            argfile_path = ArgfileManager.create_read_args(file_paths)
            
            # Execute exiftool command once for all files
            # Added -fast2 to skip MakerNotes for maximum speed
            cmd = [self.exiftool_path, "-fast2", "-@", argfile_path]
            
            self.progress.emit(10) # Start progress
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                timeout=max(30, total_files * 0.5), # Dynamic timeout
                creationflags=CREATE_NO_WINDOW
            )
            
            self.progress.emit(90) # Command finished
            
            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")
            
            if result.returncode == 0:
                try:
                    data = json.loads(stdout)
                    # ExifTool returns a list of dicts. Map them back to file paths.
                    # ExifTool 返回字典列表，将其映射回文件路径。
                    # Note: SourceFile in JSON is usually the normalized path.
                    for entry in data:
                        source_path = entry.get('SourceFile')
                        if source_path:
                            # Try to match original path by normalizing both
                            found = False
                            for original in file_paths:
                                if os.path.abspath(original) == os.path.abspath(source_path):
                                    results[original] = entry
                                    found = True
                                    break
                            if not found:
                                results[source_path] = entry
                except Exception as e:
                    self.error_occurred.emit(f"JSON parse error: {e}")
                    logger.error(f"Failed to parse ExifTool JSON output: {e}")
            else:
                self.error_occurred.emit(f"ExifTool error: {stderr}")
                logger.error(f"ExifTool batch read failed: {stderr}")
            
            self.read_finished.emit(results)
            self.progress.emit(100)
            
        except Exception as e:
            logger.error(f"Batch read failed: {e}", exc_info=True)
            self.error_occurred.emit(f"Batch read failed: {str(e)}")
        finally:
            if argfile_path:
                ArgfileManager.cleanup(argfile_path)
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
                timeout=5,
                creationflags=CREATE_NO_WINDOW
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
                    timeout=timeout,
                    creationflags=CREATE_NO_WINDOW
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
        Batch write EXIF data to multiple files asynchronously using Parallel Argfiles
        使用多核并发 Argfile 异步批量写入 EXIF 数据到多个文件 (终极提速模式)
        
        Args:
            write_tasks: List of dicts with 'file_path' and 'exif_data' / 包含 'file_path' 和 'exif_data' 的字典列表
        """
        temp_files = []
        try:
            total_tasks = len(write_tasks)
            if not write_tasks:
                self.write_finished.emit({})
                return

            self.log_message.emit(tr("Starting parallel batch write for {count} tasks...").format(count=total_tasks))
            self.progress.emit(5)
            
            # 1. Determine concurrency level / 确定并发数
            # Max 4 workers to avoid disk thrashing and high RAM usage
            # 最多 4 个并发进程，平衡磁盘 IO 和内存占用
            cpu_count = os.cpu_count() or 1
            max_workers = min(cpu_count, 4) if total_tasks >= 10 else 1
            
            # 2. Shard tasks into chunks / 将任务分片
            chunk_size = (total_tasks + max_workers - 1) // max_workers
            chunks = [write_tasks[i:i + chunk_size] for i in range(0, total_tasks, chunk_size)]
            
            self.log_message.emit(tr("Using {n} parallel processes for writing...").format(n=len(chunks)))
            
            # 3. Define the worker function for each chunk / 定义每个分片的执行函数
            def process_chunk(chunk_tasks):
                chunk_argfile = None
                try:
                    overwrite = config.get('overwrite_original', True)
                    preserve_date = config.get('preserve_modify_date', True)
                    chunk_argfile = ArgfileManager.create_write_args(chunk_tasks, overwrite, preserve_date)
                    
                    cmd = [self.exiftool_path, "-@", chunk_argfile]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=max(60, len(chunk_tasks) * 2.0),
                        creationflags=CREATE_NO_WINDOW
                    )
                    
                    # Return path for cleanup and status
                    return {
                        "success": result.returncode == 0,
                        "error": result.stderr if result.returncode != 0 else None,
                        "tasks": chunk_tasks,
                        "argfile": chunk_argfile
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "tasks": chunk_tasks,
                        "argfile": chunk_argfile
                    }

            # 4. Execute parallel tasks / 执行并行任务
            results = []
            final_status_list = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_chunk = {executor.submit(process_chunk, c): c for c in chunks}
                
                completed = 0
                for future in concurrent.futures.as_completed(future_to_chunk):
                    res = future.result()
                    temp_files.append(res.get('argfile'))
                    
                    succ = res.get('success', False)
                    err_msg = res.get('error')
                    
                    for t in res.get('tasks', []):
                        final_status_list.append({
                            "status": "success" if succ else "error",
                            "file": t.get('file_path'),
                            "message": "EXIF written" if succ else err_msg
                        })
                    
                    completed += 1
                    self.progress.emit(int(10 + (completed / len(chunks)) * 80))

            # 5. Emit final results / 发送最终结果
            result_dict = {
                "batch_write": True,
                "results": final_status_list,
                "total": total_tasks,
                "success": sum(1 for r in final_status_list if r['status'] == 'success'),
                "failed": sum(1 for r in final_status_list if r['status'] == 'error')
            }
            
            logger.info(tr("Parallel batch write finished: {s}/{t} successful").format(
                s=result_dict['success'], t=total_tasks))
            
            self.last_result = result_dict
            self.write_finished.emit(result_dict)
            self.progress.emit(100)
        
        except Exception as e:
            logger.critical(f"Exception in parallel_batch_write: {e}", exc_info=True)
            self.error_occurred.emit(f"Parallel batch write failed: {str(e)}")
        finally:
            # Cleanup all temp files
            for f in temp_files:
                if f:
                    ArgfileManager.cleanup(f)
            self.finished.emit()

