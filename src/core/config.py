#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management system for DataPrism
DataPrism 配置管理系统
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger('DataPrism.Config')


class Config:
    """
    Application configuration manager / 应用配置管理器
    Handles loading, saving, and accessing configuration / 处理配置的加载、保存和访问
    """
    
    # Default configuration / 默认配置
    DEFAULT_CONFIG = {
        # ExifTool settings / ExifTool 设置
        'exiftool_path': 'exiftool',
        'exiftool_timeout': 30,
        'exiftool_max_retries': 3,
        
        # UI settings / UI 设置
        'window_width': 1200,
        'window_height': 800,
        'theme': 'dark',
        'language': 'zh_CN',
        
        # Performance settings / 性能设置
        'max_cache_size': 100,
        'worker_threads': 2,
        
        # Behavior settings / 行为设置
        'auto_save': False,
        'confirm_on_exit': True,
        'show_completion_dialog': True,
        
        # Logging settings / 日志设置
        'log_level': 'INFO',
        'log_to_file': True,
        'log_file_path': 'dataprism.log',
    }
    
    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize configuration manager / 初始化配置管理器
        
        Args:
            config_file: Path to configuration file / 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """
        Load configuration from file / 从文件加载配置
        If file doesn't exist, use defaults / 如果文件不存在，使用默认值
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist / 与默认值合并确保所有键存在
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
                    logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                logger.info("Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            logger.info(f"Configuration file not found, using defaults")
            self.config = self.DEFAULT_CONFIG.copy()
            # Save defaults to file / 保存默认配置到文件
            self.save()
    
    def save(self) -> None:
        """
        Save configuration to file / 保存配置到文件
        """
        try:
            # Ensure parent directory exists / 确保父目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value / 获取配置值
        
        Args:
            key: Configuration key / 配置键
            default: Default value if key not found / 键不存在时的默认值
        
        Returns:
            Configuration value / 配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save_immediately: bool = True) -> None:
        """
        Set configuration value / 设置配置值
        
        Args:
            key: Configuration key / 配置键
            value: Configuration value / 配置值
            save_immediately: Whether to save to file immediately / 是否立即保存到文件
        """
        self.config[key] = value
        logger.debug(f"Configuration updated: {key} = {value}")
        
        if save_immediately:
            self.save()
    
    def reset_to_defaults(self) -> None:
        """
        Reset configuration to defaults / 重置配置为默认值
        """
        logger.info("Resetting configuration to defaults")
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values / 获取所有配置值
        
        Returns:
            Dictionary of all configuration / 所有配置的字典
        """
        return self.config.copy()


# Global configuration instance / 全局配置实例
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance / 获取全局配置实例
    
    Returns:
        Config: Global configuration instance / 全局配置实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def init_config(config_file: str = 'config.json') -> Config:
    """
    Initialize global configuration / 初始化全局配置
    
    Args:
        config_file: Path to configuration file / 配置文件路径
    
    Returns:
        Config: Global configuration instance / 全局配置实例
    """
    global _config_instance
    _config_instance = Config(config_file)
    return _config_instance
