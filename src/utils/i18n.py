#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internationalization (i18n) manager for DataPrism
DataPrism 的国际化管理器
"""

import locale
from typing import Dict


class TranslationManager:
    """
    Centralized translation manager with locale detection
    集中式翻译管理器，支持语言环境检测
    """
    
    def __init__(self):
        """Initialize with system locale / 使用系统语言环境初始化"""
        self.current_lang = self._detect_system_language()
        self.translations: Dict[str, Dict[str, str]] = {
            # UI Elements / UI 元素
            "Imported Photos": {"zh": "已导入照片", "en": "Imported Photos"},
            "Browse files…": {"zh": "浏览文件…", "en": "Browse files…"},
            "Drag and drop photos here or click to import": {
                "zh": "拖拽照片到此处或点击导入",
                "en": "Drag and drop photos here or click to import"
            },
            
            # Sidebar / 侧边栏
            "Filters & Presets": {"zh": "过滤器与预设", "en": "Filters & Presets"},
            "Camera": {"zh": "相机", "en": "Camera"},
            "Lens": {"zh": "镜头", "en": "Lens"},
            "Film Stock": {"zh": "胶卷型号", "en": "Film Stock"},
            
            # Inspector / 检查器
            "Inspector": {"zh": "检查器", "en": "Inspector"},
            "Basic Info": {"zh": "基本信息", "en": "Basic Info"},
            "File:": {"zh": "文件：", "en": "File:"},
            "Camera:": {"zh": "相机：", "en": "Camera:"},
            "Lens:": {"zh": "镜头：", "en": "Lens:"},
            "Date:": {"zh": "日期：", "en": "Date:"},
            "Status:": {"zh": "状态：", "en": "Status:"},
            
            # Exposure Section / 曝光区域
            "Exposure": {"zh": "曝光参数", "en": "Exposure"},
            "Aperture:": {"zh": "光圈：", "en": "Aperture:"},
            "Shutter:": {"zh": "快门：", "en": "Shutter:"},
            "ISO:": {"zh": "ISO：", "en": "ISO:"},
            
            # Table Columns / 表格列
            "File": {"zh": "文件", "en": "File"},
            "Aperture": {"zh": "光圈", "en": "Aperture"},
            "Shutter": {"zh": "快门", "en": "Shutter"},
            "ISO": {"zh": "ISO", "en": "ISO"},
            "Date": {"zh": "日期", "en": "Date"},
            "Status": {"zh": "状态", "en": "Status"},
            
            # Status Messages / 状态消息
            "Loading...": {"zh": "加载中...", "en": "Loading..."},
            "Pending EXIF read": {"zh": "等待读取 EXIF", "en": "Pending EXIF read"},
            "EXIF loaded": {"zh": "EXIF 已加载", "en": "EXIF loaded"},
            "Modified": {"zh": "已修改", "en": "Modified"},
            "Error loading EXIF": {"zh": "加载 EXIF 出错", "en": "Error loading EXIF"},
            
            # Import Messages / 导入消息
            "Imported {count} file(s). Drag more to add.": {
                "zh": "已导入 {count} 个文件，可继续拖拽。",
                "en": "Imported {count} file(s). Drag more to add."
            },
            "Select photos": {"zh": "选择照片", "en": "Select photos"},
            "Images (*.jpg *.jpeg *.png *.tif *.tiff *.dng)": {
                "zh": "图像 (*.jpg *.jpeg *.png *.tif *.tiff *.dng)",
                "en": "Images (*.jpg *.jpeg *.png *.tif *.tiff *.dng)"
            },
            
            # JSON Import / JSON 导入
            "Import JSON": {"zh": "导入 JSON", "en": "Import JSON"},
            "Select JSON file": {"zh": "选择 JSON 文件", "en": "Select JSON file"},
            "JSON Files (*.json)": {"zh": "JSON 文件 (*.json)", "en": "JSON Files (*.json)"},
            "Parsing JSON...": {"zh": "解析 JSON...", "en": "Parsing JSON..."},
            "Matching photos...": {"zh": "匹配照片...", "en": "Matching photos..."},
            "Match Preview": {"zh": "匹配预览", "en": "Match Preview"},
            "Apply to All": {"zh": "应用到全部", "en": "Apply to All"},
            "Cancel": {"zh": "取消", "en": "Cancel"},
            "Matched: {matched}/{total}": {"zh": "已匹配：{matched}/{total}", "en": "Matched: {matched}/{total}"},
            "No photos imported": {"zh": "没有导入照片", "en": "No photos imported"},
            "Please import photos first": {"zh": "请先导入照片", "en": "Please import photos first"},
            "Match Statistics": {"zh": "匹配统计", "en": "Match Statistics"},
            "Rematch": {"zh": "重新匹配", "en": "Rematch"},
            "Time Offset": {"zh": "时间偏移", "en": "Time Offset"},
            "Adjust by (minutes):": {"zh": "调整 (分钟)：", "en": "Adjust by (minutes):"},
            "Photo File": {"zh": "照片文件", "en": "Photo File"},
            "Photo Date": {"zh": "照片日期", "en": "Photo Date"},
            "→": {"zh": "→", "en": "→"},
            "Log Camera": {"zh": "日志相机", "en": "Log Camera"},
            "Log Lens": {"zh": "日志镜头", "en": "Log Lens"},
            "Log Date": {"zh": "日志日期", "en": "Log Date"},
            "Writing EXIF data...": {"zh": "写入 EXIF 数据...", "en": "Writing EXIF data..."},
        }
    
    def _detect_system_language(self) -> str:
        """
        Detect system language
        检测系统语言
        
        Returns:
            'zh' for Chinese, 'en' for English / 中文返回 'zh'，英文返回 'en'
        """
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale and system_locale.startswith('zh'):
                return 'zh'
        except:
            pass
        return 'en'
    
    def tr(self, text: str, **kwargs) -> str:
        """
        Translate text to current language
        将文本翻译为当前语言
        
        Args:
            text: Text to translate / 要翻译的文本
            **kwargs: Format parameters / 格式化参数
        
        Returns:
            Translated text / 翻译后的文本
        """
        if text not in self.translations:
            return text.format(**kwargs) if kwargs else text
        
        translation_dict = self.translations[text]
        translated = translation_dict.get(self.current_lang, text)
        
        return translated.format(**kwargs) if kwargs else translated
    
    def set_language(self, lang: str) -> None:
        """
        Set current language
        设置当前语言
        
        Args:
            lang: 'zh' for Chinese, 'en' for English / 'zh' 表示中文，'en' 表示英文
        """
        if lang in ['zh', 'en']:
            self.current_lang = lang
    
    def get_current_language(self) -> str:
        """Get current language / 获取当前语言"""
        return self.current_lang
    
    def toggle_language(self) -> str:
        """
        Toggle between Chinese and English
        在中文和英文之间切换
        
        Returns:
            New language code / 新的语言代码
        """
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        return self.current_lang


# Global instance / 全局实例
_translator = TranslationManager()


def tr(text: str, **kwargs) -> str:
    """
    Global translation function
    全局翻译函数
    
    Args:
        text: Text to translate / 要翻译的文本
        **kwargs: Format parameters / 格式化参数
    
    Returns:
        Translated text / 翻译后的文本
    """
    return _translator.tr(text, **kwargs)


def set_language(lang: str) -> None:
    """Set global language / 设置全局语言"""
    _translator.set_language(lang)


def get_current_language() -> str:
    """Get current language / 获取当前语言"""
    return _translator.get_current_language()


def toggle_language() -> str:
    """Toggle language / 切换语言"""
    return _translator.toggle_language()
