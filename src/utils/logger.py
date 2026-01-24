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


def setup_logger(name='DataPrism', log_file=None, level=logging.INFO):
    """
    Configure unified logging system / 配置统一日志系统
    
    Args:
        name: Logger name / 日志器名称
        log_file: Optional log file path / 可选的日志文件路径
        level: Logging level / 日志级别
    
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
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # File logs are more detailed / 文件日志更详细
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name='DataPrism'):
    """
    Get logger instance / 获取日志器实例
    
    Args:
        name: Logger name / 日志器名称
    
    Returns:
        logging.Logger: Logger instance / 日志器实例
    """
    return logging.getLogger(name)


# Create default logger / 创建默认日志器
default_logger = setup_logger(
    name='DataPrism',
    log_file='dataprism.log',
    level=logging.DEBUG
)
