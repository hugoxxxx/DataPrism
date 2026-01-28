# DataPrism User Guide / 使用手册 📖

## 1. ExifTool Setup / 准备工作
- **Path / 路径**: DataPrism needs ExifTool to work (程序需要 ExifTool 才能读写数据).
- **Settings / 设置**: Go to settings and select your `exiftool.exe` (在设置中指定 `exiftool.exe` 的存放路径).

## 2. Basic Use / 基本用法
1. **Import / 导入**: Click "Add Photos" to select images (点击“添加照片”按钮选择文件).
2. **Edit / 编辑**: Click a photo and change its information on the right (点击照片，在右侧修改信息).
3. **Quick Apply / 一键写入**: Use **All** or **Selected** buttons in the sidebar to batch update basic info (使用侧边栏的“全部”或“选中”按钮批量更新基础信息).
4. **Refresh / 刷新**: Click **Refresh EXIF** to reload data from files (点击“刷新 EXIF”从文件重新读取数据).

## 3. JSON/CSV/TXT Import / 导入元数据
1. **Import Photos / 导入照片**: Click "Add Photos" first (先点击“添加照片”导入扫描件).
2. **Select File / 选择文件**: Click **📄 Import Metadata**, choose a JSON, CSV, or TXT file (点击“导入元数据”，选择对应的日志文件).
3. **Mapping (CSV/TXT only) / 映射配置**:
   - If importing CSV/TXT, click **Mapping Configuration** (如果是 CSV/TXT，点击“映射配置”按钮)。
   - Match your file columns (e.g., "Body") to DataPrism tags (e.g., "Model") (将文件中的列名与程序标签进行关联).
   - For GPS, select the correct direction (N/S/E/W) (如果是经纬度，选择正确的方向).
4. **Time Offset / 时间偏移**: Adjust the slider to sync photo time with log records (拉动滑块校正时间偏差).
5. **Save / 保存**: Click **Write All Files** to apply changes (点击“写入全部文件”保存)。

## 4. Settings & Logs / 设置与日志
- **Portable Mode / 便携模式**: Save settings in the current folder instead of AppData (将配置保存在程序当前文件夹，而不是系统目录).
- **Log Level / 日志级别**: Set to `DEBUG` if you find bugs (如果遇到报错，把日志级别设为 `DEBUG` 查看详细日志).
