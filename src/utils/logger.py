#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified logging system for DataPrism
DataPrism 统一日志系统
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name='DataPrism', log_file=None, level=logging.INFO, max_bytes=10*1024*1024, backup_count=5):
    """
    Configure unified logging system / 配置统一日志系统
    
    Args:
        name: Logger name / 日志器名称
        log_file: Optional log file path / 可选的日志文件路径
        level: Logging level / 日志级别
        max_bytes: Max size of log file / 日志文件最大容量 (Default 10MB)
        backup_count: Number of backups / 备份数量 (Default 5)
    
    Returns:
        logging.Logger: Configured logger / 配置好的日志器
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers / 避免重复添加处理器
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler / 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter with timestamp / 带时间戳的格式化器
    console_formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional) / 文件处理器（可选）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use RotatingFileHandler instead of FileHandler / 使用 RotatingFileHandler 替代 FileHandler
        file_handler = RotatingFileHandler(
            log_path, 
            maxBytes=max_bytes, 
            backupCount=backup_count, 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File logs are more detailed / 文件日志更详细
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name='DataPrism'):
    return logging.getLogger(name)


def reconfigure_logger(log_file, level=logging.DEBUG, max_size_mb=10, backup_count=5):
    """
    Reconfigure existing logger with new path and limits / 使用新路径和限制重新配置日志器
    """
    # Convert string level to logging level if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger('DataPrism')
    
    # Remove old file handlers / 移除旧的文件处理器
    for handler in logger.handlers[:]:
        if isinstance(handler, RotatingFileHandler) or isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()
            
    # Add new rotating handler / 添加新的循环处理器
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    max_bytes = max_size_mb * 1024 * 1024
    
    new_handler = RotatingFileHandler(
        log_path, 
        maxBytes=max_bytes, 
        backupCount=backup_count, 
        encoding='utf-8'
    )
    new_handler.setLevel(level)
    
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    new_handler.setFormatter(formatter)
    logger.addHandler(new_handler)
    
    logger.info(f"Logger reconfigured: {log_path} (Max {max_size_mb}MB, Backups: {backup_count})")


# Create default logger / 创建默认日志器
default_logger = setup_logger(
    name='DataPrism',
    log_file='dataprism.log',
    level=logging.DEBUG
)
