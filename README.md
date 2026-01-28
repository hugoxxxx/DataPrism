# DataPrism 📸

DataPrism is a tool for managing photo EXIF metadata (元数据管理工具). It uses ExifTool to help you edit photo information in batches (调用 ExifTool 批量修改照片信息).

## 🖼️ UI Preview / 界面预览

| Chinese / 中文 | English / 英文 |
| :--- | :--- |
| ![CN 1](https://raw.githubusercontent.com/hugoxxxx/photos/main/DataPrism/ScreenShot_1.png) | ![EN 1](https://raw.githubusercontent.com/hugoxxxx/photos/main/DataPrism/ScreenShot_1_en.png) |
| ![CN 2](https://raw.githubusercontent.com/hugoxxxx/photos/main/DataPrism/ScreenShot_2.png) | ![EN 2](https://raw.githubusercontent.com/hugoxxxx/photos/main/DataPrism/ScreenShot_2_en.png) |
| ![CN 3](https://raw.githubusercontent.com/hugoxxxx/photos/main/DataPrism/ScreenShot_3.png) | ![EN 3](https://raw.githubusercontent.com/hugoxxxx/photos/main/DataPrism/ScreenShot_3_en.png) |

## 🌟 Features / 功能特点

- **Metadata Editing / 元数据编辑**: Batch edit Camera, Lens, Film stock, and Exposure data (批量修改相机、镜头、胶卷、曝光等数据).
- **JSON Import / 导入测量数据**: Support importing logs from apps like Lightme or Logbook (支持导入 Lightme、Logbook 等 App 的测量日志).
- **Smart Matching / 智能匹配**: Automatically link logs to photos by time or sequence (按时间或顺序自动将日志匹配到照片).
- **Log Management / 日志管理**: Control log file size and rotation (控制日志文件大小与自动清理).
- **Settings / 灵活配置**: Support for Portable or AppData storage modes (支持便携模式或系统路径存储配置).
- **Bilingual / 双语界面**: Full support for English and Simplified Chinese (完整支持中英文界面).

## 🚀 Getting Started / 快速上手

### Prerequisites / 环境要求
- Python 3.10+
- [ExifTool](https://exiftool.org/) (installed and path set in app / 已安装并在程序中设置好路径).

### Installation / 安装
1. Clone / 克隆: `git clone https://github.com/your-username/DataPrism.git`
2. Venv / 虚拟环境: `python -m venv venv`
3. Activate / 激活: `.\venv\Scripts\activate` (Windows)
4. Dependencies / 依赖: `pip install -r requirements.txt`

### Running / 运行
`python main.py`

## 📄 License
MIT License
