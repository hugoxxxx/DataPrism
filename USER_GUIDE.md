# DataPrism User Guide / 使用手册 📖

## 1. ExifTool Setup / 准备工作
- **Path / 路径**: DataPrism needs ExifTool to work (程序需要 ExifTool 才能读写数据).
- **Settings / 设置**: Go to settings and select your `exiftool.exe` (在设置中指定 `exiftool.exe` 的存放路径).

## 2. Basic Use / 基本用法
1. **Import / 导入**: Click "Add Photos" to select images (点击“添加照片”按钮选择文件).
2. **Edit / 编辑**: Click a photo and change its information on the right (点击照片，在右侧修改信息).
3. **Refresh / 刷新**: Click **Refresh EXIF** to reload data from files (点击“刷新 EXIF”从文件重新读取数据).

## 3. Quick Write / 一键写入 (Batch Update)
For quickly batch-setting equipment or film info (用于快速批量设置器材或胶卷信息):
1. **Fill Info / 填写信息**: Use the left sidebar to enter Camera, Lens, or Film details (在左侧边栏填写相机、镜头或胶卷)。
2. **History & Auto-fill / 历史与自动填充**: 
   - Previously used names will appear in the dropdown (历史输入过的型号会自动出现在下拉列表)。
   - **Smart Matching / 品牌联动**: When you select a **Model**, the **Make** (Brand) will be automatically filled based on your history (当您选择“型号”时，程序会自动根据历史记录填充对应的“品牌”，无需重复输入)。
   - **Clean History / 清理历史**: Right-click an item in the dropdown to remove it (在下拉列表中点击鼠标右键可删除该记录)。
3. **Apply / 应用**:
   - **All / 全部**: Click **All** to apply to every photo in the list (点击“全部”应用到列表中所有照片)。
   - **Selected / 选中**: Click **Selected** to only update highlighted photos (点击“选中”仅更新选中的行)。

## 4. JSON/CSV/TXT Import / 导入元数据
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
