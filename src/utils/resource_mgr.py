import os
import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    获取资源的绝对路径，兼容开发环境和 PyInstaller 环境。
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # PyInstaller 创建一个临时文件夹并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # If not bundled, use the project root (relative to this file)
        # 如果未打包，使用项目根目录（相对于此文件）
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)
