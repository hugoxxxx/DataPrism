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
- **Core Stability / 核心稳定性**: Improved ExifTool robustness and parsing accuracy (增强了 ExifTool 的鲁棒性及元数据解析精度).

## 🆕 What's New in v1.1.0
- **⚡ Supercharged Performance / 性能飞跃**:
  - **21x Speedup**: Multi-core parallel processing for massive batches (多核并发引擎，大批量处理速度提升 21 倍).
  - **Turbo Preview**: Support for 500MB+ TIFF thumbnails (支持亿级像素超大 TIFF 秒开预览).
- **💎 Visual Refinement / 视觉重塑**:
  - **New Icon**: Frameless, transparent "Prism" design (全新无边框透底“棱镜”图标).
  - **UI Polish**: Perfected alignment and "Cinema Padding" (影院级边距与像素级对齐).
- **🔧 Deep Compatibility / 深度兼容**:
  - **JSON Probe**: Recursive parsing for complex log formats (深度递归解析复杂 JSON 结构).
  - **Smart Fixes**: Auto-correction for dates and GPS coordinates (自动纠正日期与 GPS 格式).
- **🎮 Interaction & Usability / 交互与体验**:
  - **Sequence Reordering**: Drag-and-drop to reorder photos in Metadata Studio (支持照片序列自由拖拽重排).
  - **Interactive Columns**: Customizable table column widths and layout memory (全交互式自定义表头列宽与记忆).

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
