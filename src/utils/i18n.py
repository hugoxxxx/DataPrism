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
            "Browse files…": {"zh": "添加照片...", "en": "Add Photos..."},
            "Add Photos": {"zh": "添加照片", "en": "Add Photos"},
            "Remove": {"zh": "移除", "en": "Remove"},
            "Remove selected photos?": {"zh": "是否移除选中的照片？", "en": "Remove selected photos?"},
            "Browse": {"zh": "浏览", "en": "Browse"},
            "Rotate Left": {"zh": "向左旋转", "en": "Rotate Left"},
            "Rotate Right": {"zh": "向右旋转", "en": "Rotate Right"},
            "Click 'Add Photos' button to import photos": {
                "zh": "点击'添加照片'按钮导入照片",
                "en": "Click 'Add Photos' button to import photos"
            },
            "EN": {"zh": "EN", "en": "EN"},
            "中": {"zh": "中", "en": "中"},
            "Settings": {"zh": "设置中心", "en": "Settings"},
            
            # Sidebar & Inspector Common Fields / 侧边栏与检查器通用字段
            "Camera Make": {"zh": "相机品牌", "en": "Camera Make"},
            "Camera Model": {"zh": "相机型号", "en": "Camera Model"},
            "Lens Make": {"zh": "镜头品牌", "en": "Lens Make"},
            "Lens Model": {"zh": "镜头型号", "en": "Lens Model"},
            "Film Stock": {"zh": "胶卷型号", "en": "Film Stock"},
            "Focal Length": {"zh": "焦距", "en": "Focal Length"},
            "Focal Length (35mm)": {"zh": "等效焦距 (35mm)", "en": "Focal Length (35mm)"},
            "Aperture": {"zh": "光圈", "en": "Ap"},
            "Shutter": {"zh": "快门", "en": "Sh"},
            "ISO": {"zh": "ISO", "en": "ISO"},
            "Location": {"zh": "位置", "en": "Location"},
            "Date": {"zh": "日期", "en": "Date"},
            "Notes": {"zh": "备注", "en": "Notes"},
            
            # Form Label Versions (with colon) / 表单标签版本（带冒号）
            "Camera Make:": {"zh": "相机品牌：", "en": "Camera Make:"},
            "Camera Model:": {"zh": "相机型号：", "en": "Camera Model:"},
            "Lens Make:": {"zh": "镜头品牌：", "en": "Lens Make:"},
            "Lens Model:": {"zh": "镜头型号：", "en": "Lens Model:"},
            "Film Stock:": {"zh": "胶卷型号：", "en": "Film Stock:"},
            "Focal Length:": {"zh": "焦距：", "en": "Focal Length:"},
            "Focal Length (35mm):": {"zh": "等效焦距 (35mm)：", "en": "Focal Length (35mm):"},
            "Aperture:": {"zh": "光圈：", "en": "Aperture:"},
            "Shutter:": {"zh": "快门：", "en": "Shutter:"},
            "ISO:": {"zh": "ISO：", "en": "ISO:"},
            "Film": {"zh": "胶卷", "en": "Film"},
            "FocalLength": {"zh": "焦距", "en": "FocalLength"},
            "Location:": {"zh": "位置：", "en": "Location:"},
            "Date:": {"zh": "日期：", "en": "Date:"},
            "Status:": {"zh": "状态：", "en": "Status:"},
            "File:": {"zh": "文件：", "en": "File:"},
            "Notes:": {"zh": "备注：", "en": "Notes:"},
            "Shot Date:": {"zh": "拍摄日期：", "en": "Shot Date:"},

            # Section Headers & UI Layout / 区域标题与 UI 布局
            "Filters & Presets": {"zh": "过滤器与预设", "en": "Filters & Presets"},
            "Inspector": {"zh": "检查器", "en": "Inspector"},
            "Basic Info": {"zh": "基本信息", "en": "Basic Info"},
            "Gear Info": {"zh": "器材信息", "en": "Gear Info"},
            "Context": {"zh": "环境信息", "en": "Context"},
            "Exposure": {"zh": "曝光参数", "en": "Exposure"},
            "Quick Write": {"zh": "一键写入", "en": "Quick Write"},
            "Batch Modify": {"zh": "批量修改", "en": "Batch Modify"},
            "Apply": {"zh": "应用", "en": "Apply"},
            "Digital Back Display": {"zh": "后背数据屏", "en": "Digital Back Display"},
            "Process Status / Log": {"zh": "执行状态 / 日志", "en": "Process Status / Log"},
            "Process Status": {"zh": "执行状态", "en": "Process Status"},
            "Metadata Studio": {"zh": "元数据工作室", "en": "Metadata Studio"},
            "Records": {"zh": "数据记录", "en": "Records"},
            "Photos": {"zh": "照片", "en": "Photos"},
            "Preview": {"zh": "预览", "en": "Preview"},
            "Time Offset": {"zh": "时间偏移", "en": "Time Offset"},
            "Match Statistics": {"zh": "匹配统计", "en": "Match Statistics"},
            "Mapping Configuration": {"zh": "映射配置", "en": "Mapping Configuration"},
            "Correlate Data": {"zh": "数据关联 / 映射", "en": "Correlate Data / Mapping"},

            # Table Columns / 表格列 (Exact Match with PhotoDataModel.COLUMNS)
            "File": {"zh": "文件", "en": "File"},
            "C-Make": {"zh": "相机品牌", "en": "C-Make"},
            "C-Model": {"zh": "相机型号", "en": "C-Model"},
            "L-Make": {"zh": "镜头品牌", "en": "L-Make"},
            "L-Model": {"zh": "镜头型号", "en": "L-Model"},
            "Focal": {"zh": "焦距", "en": "Focal"},
            "F35mm": {"zh": "等效", "en": "F35mm"},
            "Status": {"zh": "状态", "en": "Status"},
            "Ignore": {"zh": "忽略", "en": "Ignore"},
            "ID Source": {"zh": "ID 来源", "en": "ID Source"},
            
            # Status Messages / 状态消息
            "Loading...": {"zh": "加载中...", "en": "Loading..."},
            "Pending EXIF read": {"zh": "等待读取 EXIF", "en": "Pending EXIF read"},
            "EXIF loaded": {"zh": "EXIF 已加载", "en": "EXIF loaded"},
            "Modified": {"zh": "已修改", "en": "Modified"},
            "Error loading EXIF": {"zh": "加载 EXIF 出错", "en": "Error loading EXIF"},
            "pending": {"zh": "待处理", "en": "Pending"},
            "loaded": {"zh": "已加载", "en": "Loaded"},
            "error": {"zh": "出错", "en": "Error"},
            "modified": {"zh": "已修改", "en": "Modified"},
            
            # Interaction & Logic / 交互与逻辑
            "Apply to All": {"zh": "全部", "en": "All"},
            "Apply to Selected": {"zh": "选中", "en": "Selected"},
            "Cancel": {"zh": "取消", "en": "Cancel"},
            "Save": {"zh": "保存", "en": "Save"},
            "Rematch": {"zh": "重新匹配", "en": "Rematch"},
            "Refresh": {"zh": "刷新", "en": "Refresh"},
            "Refresh EXIF": {"zh": "刷新 EXIF", "en": "Refresh EXIF"},
            "Write All Files": {"zh": "写入全部文件", "en": "Write All Files"},
            "Write Metadata": {"zh": "写入元数据", "en": "Write Metadata"},
            "Match Preview": {"zh": "匹配预览", "en": "Match Preview"},
            "Metadata Editor": {"zh": "元数据编辑器", "en": "Metadata Editor"},
            "Import Metadata": {"zh": "导入元数据", "en": "Import Metadata"},
            "Import JSON": {"zh": "导入 JSON", "en": "Import JSON"},
            "Select photos": {"zh": "选择照片", "en": "Select photos"},
            "Select JSON file": {"zh": "选择 JSON 文件", "en": "Select JSON file"},
            "Select metadata file": {"zh": "选择元数据文件", "en": "Select metadata file"},
            "Sequence Offset": {"zh": "序列偏移", "en": "Sequence Offset"},
            "Adjust by (minutes):": {"zh": "调整 (分钟)：", "en": "Adjust by (minutes):"},

            # Multi-parameter & Template Strings / 带参数与模板字符串
            "Matched: {matched}/{total}": {"zh": "已匹配：{matched}/{total}", "en": "Matched: {matched}/{total}"},
            "Imported {count} file(s).": {"zh": "已导入 {count} 个文件。", "en": "Imported {count} file(s)."},
            "Successfully wrote metadata to {file}": {"zh": "成功将元数据写入 {file}", "en": "Successfully wrote metadata to {file}"},
            "Quick write applied to {count} photos.": {"zh": "一键写入已应用到 {count} 张照片。", "en": "Quick write applied to {count} photos."},
            "Quick write applied to {count} selected photos.": {"zh": "一键写入已应用到 {count} 张选中的照片。", "en": "Quick write applied to {count} selected photos."},
            "Error: {msg}": {"zh": "错误：{msg}", "en": "Error: {msg}"},
            "Successfully loaded EXIF data for {count} file(s)": {"zh": "成功读取了 {count} 个文件的 EXIF 数据", "en": "Successfully loaded EXIF data for {count} file(s)"},
            "Successfully wrote metadata to {count} file(s)": {"zh": "成功写入元数据到 {count} 个文件", "en": "Successfully wrote metadata to {count} file(s)"},
            "This will modify EXIF data in all {count} photos. Continue?": {"zh": "这将修改所有 {count} 张照片的 EXIF 数据。继续吗？", "en": "This will modify EXIF data in all {count} photos. Continue?"},
            "Batch update {count} files?": {"zh": "是否批量修改 {count} 个文件的元数据？", "en": "Batch update {count} files?"},
            "Photo {num}": {"zh": "照片 {num}", "en": "Photo {num}"},
            "{meta} records loaded for {photo} photos": {"zh": "成功加载了 {photo} 张照片的 {meta} 条记录", "en": "{meta} records loaded for {photo} photos"},
            "Warning: Only {meta} records for {photo} photos": {"zh": "仅 {meta} 条记录对 {photo} 张照片", "en": "Warning: Only {meta} records for {photo} photos"},
            "Warning: {meta} records but {photo} photos": {"zh": "记录不匹配：{meta} 记录 / {photo} 照片", "en": "Warning: {meta} records but {photo} photos"},

            # Settings Options / 设置选项
            "ExifTool Path": {"zh": "ExifTool 路径", "en": "ExifTool Path"},
            "ExifTool Timeout": {"zh": "ExifTool 超时", "en": "ExifTool Timeout"},
            "Worker Threads": {"zh": "工作线程数", "en": "Worker Threads"},
            "Auto Save Changes": {"zh": "自动保存修改", "en": "Auto Save Changes"},
            "Confirm on Exit": {"zh": "退出时确认", "en": "Confirm on Exit"},
            "Show Completion Dialog": {"zh": "显示完成对话框", "en": "Show Completion Dialog"},
            "Overwrite Original Files": {"zh": "覆盖原始文件", "en": "Overwrite Original Files"},
            "Preserve File Modify Date": {"zh": "保持文件修改日期", "en": "Preserve File Modify Date"},
            "Log Max Size (MB)": {"zh": "日志最大容量 (MB)", "en": "Log Max Size (MB)"},
            "Log Backup Count": {"zh": "日志备份数量", "en": "Log Backup Count"},
            "Log Level": {"zh": "日志细节级别", "en": "Log Level"},
            "Engine & System": {"zh": "引擎与系统", "en": "Engine & System"},
            "Workflow & Behavior": {"zh": "工作流与行为", "en": "Workflow & Behavior"},
            "S": {"zh": "秒", "en": "S"},
            "Switch to Chinese": {"zh": "切换至中文", "en": "Switch to Chinese"},
            "Switch to English": {"zh": "切换至英文", "en": "Switch to English"},
            "About": {"zh": "关于", "en": "About"},
            "About DataPrism": {"zh": "关于 DataPrism", "en": "About DataPrism"},
            "DataPrism v1.0.0\nA professional EXIF metadata editor.": {
                "zh": "DataPrism v1.0.0\n基于 ExifTool 的元数据编辑器。\n\nGitHub: https://github.com/hugoxxxx/DataPrism\nEmail: xjames007@gmail.com", 
                "en": "DataPrism v1.0.0\nA metadata editor based on ExifTool.\n\nGitHub: https://github.com/hugoxxxx/DataPrism\nEmail: xjames007@gmail.com"
            },

            # Detailed Descriptions / 详细说明
            "Specify the path to exiftool executable": {
                "zh": "若已加入系统环境变量，输入 'exiftool' 即可；否则请点击浏览选择 exiftool.exe 文件。这也是软件读写元数据的核心引擎。", 
                "en": "If in system PATH, 'exiftool' is enough; otherwise browse for exiftool.exe. This is the core engine."
            },
            "Detail level of log records": {
                "zh": "DEBUG(详尽排障), INFO(常规流程), WARNING(潜在问题), ERROR(执行失败)。日常建议设为 INFO。", 
                "en": "DEBUG(Detail), INFO(Normal), WARNING(Warning), ERROR(Failure). INFO is recommended."
            },
            "Max time to wait for ExifTool (seconds)": {"zh": "ExifTool 操作的最大等待时间（秒）", "en": "Max time to wait for ExifTool (seconds)"},
            "Number of parallel worker threads": {"zh": "批量处理时的并行工作线程数", "en": "Number of parallel worker threads"},
            "Automatically save changes to config.json": {"zh": "自动将修改保存至 config.json", "en": "Automatically save changes to config.json"},
            "Show confirmation dialog before exiting": {"zh": "退出程序前弹出确认对话框", "en": "Show confirmation dialog before exiting"},
            "Show summary after batch operations": {"zh": "批量操作完成后显示摘要对话框", "en": "Show summary after batch operations"},
            "Overwrite photos directly or keep backups": {"zh": "直接覆盖照片或保留 .original 备份", "en": "Overwrite photos directly or keep backups"},
            "Keep original file system 'Modify Date'": {"zh": "写入元数据后保持文件的系统修改时间不变", "en": "Keep original file system 'Modify Date'"},
            "Maximum size of a single log file in megabytes": {"zh": "单个日志文件的最大容量（MB）", "en": "Maximum size of a single log file in megabytes"},
            "Number of old log files to keep": {"zh": "保留的历史日志文件数量", "en": "Number of old log files to keep"},
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
