#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management system for DataPrism
DataPrism 配置管理系统
"""

import os
import shutil
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from src.utils.logger import get_logger

logger = get_logger('DataPrism.Config')

def get_app_data_path() -> Path:
    """Get the standard AppData path for the application / 获取应用程序的标准 AppData 路径"""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA')
        if not base:
            base = str(Path.home() / "AppData" / "Roaming")
    elif sys.platform == 'darwin':
        base = str(Path.home() / "Library" / "Application Support")
    else:
        base = str(Path.home() / ".config")
        
    path = Path(base) / "DataPrism"
    return path

class HistoryManager:
    """
    Manager for history data (Cameras, Lenses, Film)
    历史记录管理器（相机、镜头、胶卷）
    """
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.history_file = storage_dir / 'history.json'
        self.data = {
            'camera_history': {},
            'lens_history': {},
            'film_history': []
        }
        self.load()

    def load(self):
        """Load history from file or initialize from defaults / 从文件加载历史或从默认值初始化"""
        if self.history_file.exists():
            try:
                logger.info(f"Loading history from: {self.history_file}")
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        loaded = {}
                    else:
                        loaded = json.loads(content)
                    
                    self.data = loaded # Direct load / 直接加载
                    
                # Auto-seed if empty / 如果为空自动填充
                cam_count = len(self.data.get('camera_history', {}))
                lens_count = len(self.data.get('lens_history', {}))
                film_count = len(self.data.get('film_history', []))
                
                logger.info(f"Loaded history stats: Cameras={cam_count}, Lenses={lens_count}, Films={film_count}")
                
                is_empty = (cam_count == 0 and lens_count == 0 and film_count == 0)
                
                if is_empty:
                    logger.info("History file is empty, seeding from template...")
                    self._load_from_template()
                    
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
                self._load_from_template() # Fallback only on error / 仅在错误时回退
        else:
            logger.info("History file not found, initializing from template...")
            self._load_from_template()

    def _load_from_template(self):
        """Initialize data from default template and save / 从默认模板初始化数据并保存"""
        try:
            base_dir = Path(__file__).parent.parent 
            template_path = base_dir / 'resources' / 'default_history.json'
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    logger.info("Initialized history from template")
            self.save() # Create the file immediately / 立即创建文件
        except Exception as e:
             logger.warning(f"Failed to load history template: {e}")

    def save(self):
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            
    # ... (add methods)

    def add_camera(self, model: str, make: str):
        if model and make:
            # Ensure dicts exist if file was corrupted/empty
            if 'camera_history' not in self.data: self.data['camera_history'] = {}
            self.data['camera_history'][model] = make
            self.save()

    def add_lens(self, model: str, make: str):
        if model and make:
            if 'lens_history' not in self.data: self.data['lens_history'] = {}
            self.data['lens_history'][model] = make
            self.save()

    def add_film(self, film: str):
        if film:
            if 'film_history' not in self.data: self.data['film_history'] = []
            if film not in self.data['film_history']:
                self.data['film_history'].insert(0, film)
                self.data['film_history'] = self.data['film_history'][:50]
                self.save()

    def remove_camera(self, model: str):
        if model and 'camera_history' in self.data:
            if model in self.data['camera_history']:
                del self.data['camera_history'][model]
                self.save()

    def remove_lens(self, model: str):
        if model and 'lens_history' in self.data:
            if model in self.data['lens_history']:
                del self.data['lens_history'][model]
                self.save()

    def remove_film(self, film: str):
        if film and 'film_history' in self.data:
            if film in self.data['film_history']:
                self.data['film_history'].remove(film)
                self.save()

    def get_cameras(self) -> Dict[str, str]:
        return self.data.get('camera_history', {})

    def get_lenses(self) -> Dict[str, str]:
        return self.data.get('lens_history', {})

    def get_films(self) -> List[str]:
        return self.data.get('film_history', [])


class Config:
    """
    Application configuration manager / 应用配置管理器
    """
    
    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize configuration manager / 初始化配置管理器
        """
        self.local_config_path = Path(config_file)
        self.appdata_config_dir = get_app_data_path()
        self.appdata_config_path = self.appdata_config_dir / config_file
        
        # Determine active config file / 确定活动配置文件
        self.config_file = self.local_config_path
        self.storage_dir = Path('.')
        self.config: Dict[str, Any] = {}
        self.history: Optional[HistoryManager] = None
        
        # Path resolution logic
        if self.local_config_path.exists():
            # Portable mode detected
            logger.info("Found local config, starting in PORTABLE mode")
        elif self.appdata_config_path.exists():
            # AppData mode detected
            self.config_file = self.appdata_config_path
            self.storage_dir = self.appdata_config_dir
            logger.info("Starting in STANDARD (AppData) mode")
        else:
            # First run: Default to Standard (AppData)
            self.config_file = self.appdata_config_path
            self.storage_dir = self.appdata_config_dir
            logger.info("Fresh install, defaulting to STANDARD (AppData) mode")

        self.load()
        self.history = HistoryManager(self.storage_dir)

    def load(self) -> None:
        """
        Load configuration from file or template / 从文件或模板加载配置
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self._load_from_template()
        else:
            self._load_from_template()
            
    def _load_from_template(self):
        """Initialize config from default template and save / 从默认模板初始化配置并保存"""
        try:
            base_dir = Path(__file__).parent.parent 
            template_path = base_dir / 'resources' / 'default_config.json'
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    logger.info("Initialized configuration from template")
            else:
                self.config = {} # Should ideally not happen if installation is correct
                logger.warning("Default config template missing!")
            
            self.save()
        except Exception as e:
            logger.error(f"Failed to load config template: {e}")
            self.config = {}

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
            
        # Handle portable mode change
        if key == 'portable_mode':
            self.migrate_storage(value)

    def migrate_storage(self, portable: bool):
        """Migrate configuration and history between AppData and Local / 在 AppData 和本地目录之间迁移配置和历史记录"""
        target_dir = Path('.') if portable else self.appdata_config_dir
        source_dir = self.appdata_config_dir if portable else Path('.')
        
        if target_dir == source_dir:
            return
            
        logger.info(f"Migrating storage to {'PORTABLE' if portable else 'STANDARD'} mode...")
        
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Migrate config.json
            target_config = target_dir / 'config.json'
            with open(target_config, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Migrate history.json
            source_history = source_dir / 'history.json'
            target_history = target_dir / 'history.json'
            if source_history.exists():
                shutil.copy2(source_history, target_history)
            
            # Update internal state
            self.config_file = target_config
            self.storage_dir = target_dir
            if self.history:
                self.history.storage_dir = target_dir
                self.history.history_file = target_history
            
            # Delete old files (optional, but keep for now until user confirms)
            # if (source_dir / 'config.json').exists():
            #     (source_dir / 'config.json').unlink()
            
            logger.info("Migration successful")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
    
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
