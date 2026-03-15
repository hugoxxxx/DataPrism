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

def get_exiftool_path() -> str:
    """
    Get the path to the bundled or local ExifTool executable.
    获取捆绑或本地的 ExifTool 可执行文件路径。
    """
    # 1. Try internal bin directory (Bundled or local dev)
    # 优先尝试内置 bin 目录（打包后或本地开发环境）
    internal_bin = get_resource_path(os.path.join('src', 'resources', 'bin', 'exiftool.exe'))
    if os.path.exists(internal_bin):
        return internal_bin

    # 2. Fallback to system PATH
    # 备选方案：系统环境变量中的 exiftool
    return "exiftool"
