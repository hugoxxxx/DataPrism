# DataPrism User Guide / 使用手册 📖

## 1. ExifTool Setup / 准备工作
- **Path / 路径**: DataPrism needs ExifTool to work (程序需要 ExifTool 才能读写数据).
- **Settings / 设置**: Go to settings and select your `exiftool.exe` (在设置中指定 `exiftool.exe` 的存放路径).

## 2. Basic Use / 基本用法
1. **Import / 导入**: Click "Add Photos" to select images (点击“添加照片”按钮选择文件).
2. **Edit / 编辑**: Click a photo and change its information on the right (点击照片，在右侧修改信息).
3. **Quick Apply / 一键写入**: Use **All** or **Selected** buttons in the sidebar to batch update basic info (使用侧边栏的“全部”或“选中”按钮批量更新基础信息).
4. **Refresh / 刷新**: Click **Refresh EXIF** to reload data from files (点击“刷新 EXIF”从文件重新读取数据).

## 3. JSON Match / 导入测量日志 (Lightme/Logbook)
1. Import photos first (先点击“添加照片”导入扫描件).
2. Click **📄 Import Metadata** (点击“导入元数据”按钮).
3. Choose your log file (选择你的测量日志文件).
4. **Time Offset / 时间偏移**: Adjust the slider if the photo time doesn't match the log time (如果照片和日志时间对不上，拉动滑块进行校正).
5. Click **Write All Files** to save all data (点击“写入全部文件”一次性保存所有更改).

## 4. Settings & Logs / 设置与日志
- **Portable Mode / 便携模式**: Save settings in the current folder instead of AppData (将配置保存在程序当前文件夹，而不是系统目录).
- **Log Level / 日志级别**: Set to `DEBUG` if you find bugs (如果遇到报错，把日志级别设为 `DEBUG` 查看详细日志).
