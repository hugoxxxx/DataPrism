# GT23_Workflow 兼容性测试指南

## ✅ 已实施的改进

### 方案 A：DataPrism 写入 GT23 可读字段

**核心改动**：`ImageDescription` 字段优先写入胶卷型号，而不是位置信息。

---

## 📝 写入字段优先级

### 场景 1：有胶卷型号 + 有位置

```python
# 用户输入
film_stock = "Kodak Portra 400"
location = "28°31'30.59\"N, 119°30'30.44\"E"

# DataPrism 写入
Film = "Kodak Portra 400"                    # ✅ DataPrism 标准字段
ImageDescription = "Kodak Portra 400"        # ✅ GT23 自动识别（优先级最高）
UserComment = "Film: Kodak Portra 400 | Location: 28°31'30.59\"N, 119°30'30.44\"E"
GPSLatitude = "28.0 31.0 30.59"
GPSLatitudeRef = "N"
GPSLongitude = "119.0 30.0 30.44"
GPSLongitudeRef = "E"
```

### 场景 2：只有胶卷型号

```python
# 用户输入
film_stock = "Kodak Portra 400"
location = None

# DataPrism 写入
Film = "Kodak Portra 400"
ImageDescription = "Kodak Portra 400"        # ✅ GT23 自动识别
UserComment = "Film: Kodak Portra 400"
```

### 场景 3：只有位置

```python
# 用户输入
film_stock = None
location = "Tokyo, Japan"

# DataPrism 写入
ImageDescription = "Tokyo, Japan"            # ⚠️ 备用方案
UserComment = "Location: Tokyo, Japan"
```

---

## 🧪 测试步骤

### 步骤 1：在 DataPrism 中写入元数据

1. 打开 DataPrism
2. 导入照片（如 `test.jpg`）
3. 导入元数据文件
4. 在元数据编辑器中设置：
   - 胶卷型号：`Kodak Portra 400`
   - 位置：`28°31'30.59"N, 119°30'30.44"E`
5. 点击"写入全部文件"

### 步骤 2：验证 EXIF 数据

使用 ExifTool 验证：

```bash
exiftool -Film -ImageDescription -UserComment -GPSLatitude -GPSLongitude test.jpg
```

**预期输出**：
```
Film                            : Kodak Portra 400
Image Description               : Kodak Portra 400
User Comment                    : Film: Kodak Portra 400 | Location: 28°31'30.59"N, 119°30'30.44"E
GPS Latitude                    : 28 deg 31' 30.59" N
GPS Longitude                   : 119 deg 30' 30.44" E
```

### 步骤 3：在 GT23_Workflow 中测试

1. 将 `test.jpg` 放入 GT23_Workflow 的 `photos_in` 目录
2. 运行 GT23_Workflow
3. 选择"Contact Sheet (135)"
4. 生成索引页

**预期结果**：
- ✅ 自动识别胶卷型号为 "Kodak Portra 400"
- ✅ 显示正确的 EdgeCode "PORTRA 400"
- ✅ 使用正确的颜色（橙色）

---

## 🔍 GT23_Workflow 识别逻辑

GT23 会扫描以下字段（按顺序）：

```python
# GT23 的 metadata.py
d1 = str(tags.get('Image ImageDescription', ''))      # ✅ 会读到 "Kodak Portra 400"
d2 = str(tags.get('EXIF UserComment', ''))            # ✅ 会读到 "Film: Kodak Portra 400 | ..."
d3 = str(tags.get('EXIF ImageDescription', ''))       # 备用

search_pool = f"{d1} {d2} {d3}".upper()
# 结果：search_pool = "KODAK PORTRA 400 FILM: KODAK PORTRA 400 | ..."

# 匹配 films.json 中的特征词
# "PORTRA 400" → 匹配成功 → 返回标准名称 "Kodak Portra 400"
```

---

## 📊 兼容性矩阵

| 场景 | DataPrism 写入 | GT23 识别 | 结果 |
|------|---------------|-----------|------|
| 有胶卷 + 有位置 | `ImageDescription = 胶卷` | ✅ 成功 | ✅ 完美 |
| 只有胶卷 | `ImageDescription = 胶卷` | ✅ 成功 | ✅ 完美 |
| 只有位置 | `ImageDescription = 位置` | ❌ 失败 | ⚠️ 预期（无胶卷） |
| 都没有 | `ImageDescription = 空` | ❌ 失败 | ⚠️ 预期 |

---

## 🎯 常见胶卷型号测试

建议测试以下常见胶卷型号，确保 GT23 能正确识别：

### Kodak 系列
- `Kodak Portra 400`
- `Kodak Portra 160`
- `Kodak Portra 800`
- `Kodak Ektar 100`
- `Kodak Gold 200`
- `Kodak Tri-X 400`

### Fujifilm 系列
- `Fujifilm Pro 400H`
- `Fujifilm Velvia 50`
- `Fujifilm Provia 100F`
- `Fujifilm Superia X-TRA 400`

### Ilford 系列
- `Ilford HP5 Plus 400`
- `Ilford Delta 100`
- `Ilford FP4 Plus 125`

### CineStill 系列
- `CineStill 800T`
- `CineStill 50D`

---

## 🐛 故障排除

### 问题 1：GT23 无法识别胶卷型号

**可能原因**：
- 胶卷名称不在 GT23 的 `films.json` 数据库中
- 名称拼写错误

**解决方案**：
1. 检查 GT23 的 `config/films.json`
2. 使用数据库中的标准名称
3. 或在 GT23 中添加新的胶卷型号

### 问题 2：位置信息丢失

**说明**：
- 位置信息存储在 GPS 字段中，不会丢失
- DataPrism 会优先从 GPS 字段读取位置
- GT23 不处理位置信息，这是正常的

### 问题 3：ImageDescription 显示胶卷而不是位置

**说明**：
- 这是预期行为，为了 GT23 兼容性
- 位置信息存储在 GPS 字段中
- 如果需要查看位置，使用 GPS 字段或 UserComment

---

## 📝 总结

### ✅ 优点

1. **完全兼容 GT23_Workflow**：自动识别功能正常工作
2. **向后兼容**：不影响 DataPrism 现有功能
3. **数据完整**：所有信息都被保留（Film、GPS、UserComment）
4. **无需修改 GT23**：GT23_Workflow 无需任何改动

### ⚠️ 注意事项

1. `ImageDescription` 字段优先显示胶卷型号
2. 位置信息主要存储在 GPS 字段中
3. `UserComment` 包含完整的胶卷和位置信息

### 🎉 推荐工作流

```
DataPrism (写入元数据)
    ↓
照片包含完整 EXIF（Film、GPS、UserComment）
    ↓
GT23_Workflow (生成索引页)
    ↓
完美显示胶卷型号和喷码
```
