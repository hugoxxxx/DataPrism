#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility for managing ExifTool Argfiles
用于管理 ExifTool Argfile 的工具类
"""

import os
import tempfile
from typing import List, Dict, Any

class ArgfileManager:
    """
    Manager for temporary ExifTool argument files
    ExifTool 临时参数文件的管理器
    """
    
    @staticmethod
    def create_read_args(file_paths: List[str]) -> str:
        """
        Create an argfile for reading metadata from multiple files
        创建用于批量读取元数据的 argfile
        
        Args:
            file_paths: List of file paths to read / 待读取的文件路径列表
            
        Returns:
            Path to the temporary argfile / 临时参数文件的路径
        """
        # Create a temporary file that persists after closing
        # 创建一个关闭后依然存在的临时文件
        fd, path = tempfile.mkstemp(suffix='.args', prefix='dp_read_', text=True)
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                # Basic read flags
                f.write("-json\n")
                f.write("-charset\n")
                f.write("filename=utf8\n")
                f.write("-charset\n")
                f.write("utf8\n")
                
                # Add each file path
                for p in file_paths:
                    # Escape '#' if necessary (though ExifTool handles paths on newlines well)
                    f.write(f"{p}\n")
            return path
        except Exception:
            os.remove(path)
            raise

    @staticmethod
    def create_write_args(write_tasks: List[Dict[str, Any]], overwrite: bool = True, preserve_date: bool = True) -> str:
        """
        Create a complex argfile for batch writing metadata to multiple files
        创建用于批量写入元数据的复杂 argfile
        
        Args:
            write_tasks: List of {'file_path': str, 'exif_data': dict} / 写入任务列表
            overwrite: Whether to overwrite original file / 是否覆盖原文件
            preserve_date: Whether to preserve file modification date / 是否保留修改日期
            
        Returns:
            Path to the temporary argfile / 临时参数文件的路径
        """
        fd, path = tempfile.mkstemp(suffix='.args', prefix='dp_write_', text=True)
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                # Global flags / 全局标志
                if overwrite:
                    f.write("-overwrite_original\n")
                if preserve_date:
                    f.write("-P\n")
                
                f.write("-charset\n")
                f.write("filename=utf8\n")
                f.write("-charset\n")
                f.write("utf8\n")
                
                # Per-file tasks / 每个文件的任务
                # Format: -Tag=Value
                #         Filepath
                #         -execute
                for task in write_tasks:
                    file_path = task.get('file_path')
                    exif_data = task.get('exif_data', {})
                    
                    if not file_path:
                        continue
                        
                    for tag, value in exif_data.items():
                        if value is not None:
                            # Use -Tag=Value format
                            # Note: ExifTool handles the escaping if we put them on separate lines
                            f.write(f"-{tag}={value}\n")
                    
                    f.write(f"{file_path}\n")
                    f.write("-execute\n")
                    
            return path
        except Exception:
            os.remove(path)
            raise
    
    @staticmethod
    def cleanup(path: str):
        """Clean up the temporary file / 清理临时文件"""
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
