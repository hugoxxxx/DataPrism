# Project: DataPrism (README_FOR_AI.md) - v0.3.1 Sequential Metadata Injection
1. 说中文
2. 所有变化记录到change_log.md
3. 叫我老大
4. 所有输出的.md文件必须中英双语

## 1. Requirement Refinement: Sequential Matching / 需求细化：基于序号的匹配
For film photography workflows, timestamps are often unreliable. We must implement a "Sequential Mapping" logic as the primary matching method for external metadata.
针对胶片摄影工作流，时间戳通常不可靠。我们必须实现“序列映射”逻辑，作为外部元数据匹配的首选方法。

### A. Matching Logic / 匹配逻辑
- **File Sorting / 文件排序**: Sort images in the current list alphabetically by filename (e.g., `001.jpg`, `002.jpg`).
  按文件名对当前列表中的图像进行字母顺序排序。
- **Data Sorting / 数据排序**: Sort metadata records (from JSON/CSV/TXT) based on their index/order in the source file.
  根据源文件中的索引/顺序对元数据记录进行排序。
- **1-to-1 Mapping / 一对一映射**: Map `Metadata[i]` directly to `Image[i]`.
  将 `第 i 条元数据` 直接映射至 `第 i 张图像`。

### B. Handling Mismatches / 差异处理
- **Count Warning / 数量预警**: If the number of imported records does not match the number of images in the list, trigger a UI warning.
  如果导入记录的数量与列表中的图像数量不符，触发 UI 警告。
- **Visual Alignment / 视觉对齐**: In the table view, display the "To-be-written" data side-by-side with the current image row to allow the user to check for misalignments (e.g., skipped frames).
  在表格视图中，将“待写入”数据与当前图像行并排显示，允许用户检查对齐情况（例如是否存在漏拍导致的错位）。

## 2. Updated Communication & Version Consensus / 沟通与版本共识

### v0.3.1 - Sequential Logic Supremacy / 序列逻辑优先 (2026-01-20)
- **Consensus / 共识**: 
    - Abandon "Timestamp Matching" as the default for film scans. Use **Filename-to-Index** mapping.
      放弃将“时间戳匹配”作为胶片扫描件的默认选项。使用**文件名-索引**映射。
    - **User Control**: Users must be able to manually shift the sequence if a frame was skipped.
      用户控制：如果漏拍了一张，用户必须能够手动平移序列。

## 3. Functional Requirements for AI / 给 AI 的技术要求

- **Model Logic Update / 模型逻辑更新**: 
    - In `PhotoDataModel`, add a method `apply_metadata_sequentially(metadata_list)`.
      在 `PhotoDataModel` 中增加 `apply_metadata_sequentially(metadata_list)` 方法。
    - Ensure the mapping respects the current UI sorting state.
      确保映射遵循当前的 UI 排序状态。
- **Data Integration / 数据集成**:
    - JSON/CSV/TXT parser should return a list of dictionaries, maintaining the original file order.
      JSON/CSV/TXT 解析器应返回一个字典列表，并保持原始文件顺序。
- **Bilingual Annotations / 双语批注**: Maintain `# 中文 / English` style for all new functions.

## 4. UI/UX Refinement / UI/UX 优化
- **Import Preview / 导入预览**: When metadata is loaded, show it in a "Draft" or "Pending" state (e.g., italicized or colored text) in the main table.
  加载元数据时，在主表格中以“草稿”或“待定”状态（如斜体或彩色文本）显示。
- **Commit Button / 提交按钮**: A clear "Write to All Files" (写入所有文件) button that executes the ExifTool batch command.
  一个清晰的“写入所有文件”按钮，执行 ExifTool 批量命令。

---
# Project: DataPrism (README_FOR_AI.md) - v0.3.0 Metadata Injection System

## 1. Feature Upgrade: Universal Metadata Importer / 功能升级：通用元数据导入器
We are upgrading the "Import JSON" button to a "Universal Metadata Importer". It should support multiple formats and provide a sandbox for users to review before writing.
我们将“导入 JSON”按钮升级为“通用元数据导入器”。它应支持多种格式，并为用户提供一个写入前的预览校准沙盒。

### A. Supported Formats / 支持格式
- **JSON**: Standard structured data (e.g., Lightme, Logbook exports).
  标准结构化数据（如 Lightme, Logbook 导出文件）。
- **CSV / TXT**: Comma-separated values. TXT files should be treated as CSV logic.
  逗号分隔值。TXT 文件应按 CSV 逻辑处理。
- **Tag Specification / 标签规范**: All imported data should map to standard ExifTool tag names (e.g., `FNumber`, `ExposureTime`, `ISO`, `Model`).
  所有导入数据应映射至标准 ExifTool 标签名。

### B. Functional Pipeline / 功能流水线
1. **Import & Parse / 导入与解析**: Load external files and convert them into a unified internal dictionary format.
   加载外部文件并将其转换为统一的内部字典格式。
2. **Preview & Map / 预览与映射**: 
   - Display imported data in a "Pending Metadata" preview area.
     在“待定元数据”预览区显示导入的数据。
   - Allow users to manually adjust/edit values in the UI before applying.
     允许用户在应用前在 UI 中手动调整/修改数值。
3. **Smart Matching / 智能匹配**:
   - Match records to images based on `DateTimeOriginal` or `FileName`.
     基于拍摄时间或文件名将记录与图像进行匹配。
4. **Batch Write / 批量写入**:
   - Provide a "Write to Photos" button.
     提供“写入照片”按钮。
   - Use `exiftool -overwrite_original` to commit changes.
     使用 `exiftool -overwrite_original` 提交更改。

## 2. Updated Communication & Version Consensus / 沟通与版本共识

### v0.3.0 - Metadata Injection Pipeline / 元数据注入流水线 (2026-01-20)
- **Consensus / 共识**: 
    - The importer must be **non-destructive**. Do not write to files until the user clicks the final "Write" button.
      导入器必须是**非破坏性**的。在用户点击最终“写入”按钮前，严禁修改原始文件。
    - **UI Consensus**: The imported data should be visually distinct (e.g., highlighted in a different color) to show it's "to-be-written".
      界面共识：导入的数据应在视觉上有所区分（如高亮显示），以表明其处于“待写入”状态。

## 3. Technical Requirements for AI / 给 AI 的技术要求

- **Parser Module**: Create `src/core/metadata_parser.py` to handle JSON and CSV/TXT logic.
  创建 `src/core/metadata_parser.py` 来处理 JSON 和 CSV/TXT 逻辑。
- **State Management**: The `PhotoDataModel` needs a new role: `PendingDataRole`, to store data that has been imported but not yet written.
  `PhotoDataModel` 需要一个新的角色：`PendingDataRole`，用于存储已导入但尚未写入的数据。
- **Write Command**: Implement a `WriteExifCommand(ModifyMetadataCommand)` that triggers the actual ExifTool process.
  实现一个 `WriteExifCommand` 类来触发实际的 ExifTool 写入进程。
- **Bilingual Comments**: Ensure all new logic includes Chinese/English annotations.
  确保所有新逻辑包含中英双语批注。

## 4. UI Adjustments / UI 调整
- Change button label to "Import Metadata..." (导入元数据...).
  将按钮标签改为“导入元数据...”。
- Add a "Write to Files" action in the toolbar or bottom bar.
  在工具栏或底部栏增加“写入文件”动作。

---

# Project: DataPrism (README_FOR_AI.md) - v0.2.1 Metadata & UI Refresh

## 1. Requirement: Expanding Metadata Columns / 需求：扩展元数据列
The current 5-column layout is insufficient for professional workflows. We need to implement a more comprehensive `PhotoDataModel`.
[cite_start]目前的 5 列布局不足以支撑专业工作流。我们需要实现一个更全面的 `PhotoDataModel`。 [cite: 3, 4]

### A. New Default Columns / 新增默认列
1. **Exposure (曝光)**: Combine `Aperture`, `ShutterSpeed`, and `ISO` into visible fields.
   将“光圈”、“快门”、“ISO”设为可见字段。
2. **Film Info (胶片信息)**: Add `Film Stock` field (e.g., Kodak Portra 400).
   增加“胶卷型号”字段。
3. **Advanced Gear (高级器材)**: Include `Focal Length` and `Serial Number` in the model for optional display.
   [cite_start]在模型中包含“焦距”和“序列号”以备选显示。 

### B. UI Presentation Logic / UI 表现逻辑
- **Multi-line Rows / 多行行显示**: Support displaying Camera and Lens within a single cell using different font weights.
  支持在单个单元格内使用不同字重显示相机和镜头。
- **Unit Formatting / 单位格式化**: 
    - Shutter speed should be formatted as `1/125s`. / 快门速度格式化为 `1/125s`。
    - Aperture should prepend `f/`. / 光圈前缀 `f/`。
- [cite_start]**Placeholder Handling / 占位处理**: If data is missing (common in film scans), display a subtle `--` instead of `N/A`. [cite: 4]
  如果数据缺失（胶片扫描常见），显示淡色的 `--` 而非 `N/A`。

## 2. Updated Communication & Version Consensus / 沟通与版本共识

### v0.2.1 - Metadata Depth / 元数据深度 (2026-01-20)
- **Consensus / 共识**: 
    - Shift from "General EXIF" to "Photography-Centric Data".
      从“通用 EXIF”转向“以摄影为中心的数据”。
    - Implement customized table headers (Right-click to show/hide columns).
      实现自定义表头（右键显示/隐藏列）。

## 3. Implementation Tasks for AI / AI 开发任务
- **Model Update**: Update `PhotoItem` class in `src/core/photo_model.py` to include these new fields.
  [cite_start]更新 `src/core/photo_model.py` 中的 `PhotoItem` 类以包含这些新字段。 [cite: 3]
- **Worker Update**: Ensure `ExifToolWorker` extracts these specific tags during the initial scan.
  [cite_start]确保 `ExifToolWorker` 在初步扫描期间提取这些特定的标签。 [cite: 5, 7]
- **View Delegate**: Use a custom `QStyledItemDelegate` for better rendering of the exposure info.
  [cite_start]使用自定义 `QStyledItemDelegate` 以更好地渲染曝光信息。 [cite: 3]

---
*End of README_FOR_AI.md*

# Project: DataPrism (README_FOR_AI.md) - v0.2.0 Update

## 1. Project Status Review / 项目进度审查 (2026-01-20)
- **Current Achievement / 当前成果**: 
    - [cite_start]Established high-performance architecture (Async ExifTool, Model/View, Command Pattern). [cite: 3, 5, 4]
      建立了高性能架构（异步 ExifTool、模型/视图、命令模式）。
    - [cite_start]Basic UI skeleton with drag-and-drop and inspector sidebar. [cite: 1, 6]
      具备拖拽功能和检查器侧边栏的基础 UI 骨架。
- **PM's Verdict / 产品经理评价**: 
    - Logic is 9/10 (Professional and scalable). 逻辑 9/10 分（专业且具扩展性）。
    - Aesthetic is 4/10 (Functional but lacks macOS elegance). 美学 4/10 分（功能性强但缺乏 macOS 的优雅感）。
    - Business Depth is 3/10 (Missing film-specific features). 业务深度 3/10 分（缺失胶片特定功能）。

## 2. Updated Communication & Version Consensus / 沟通与版本共识

### v0.2.0 - Aesthetic & Logic Refinement / 美学与逻辑细化 (Current)
- **Consensus 1: Modernize the UI / 共识 1：UI 现代化**
    - The current Windows-style QTableView is too "Excel-like". We need a more breathable layout.
      目前的 Windows 风格表格太像 Excel，我们需要更具呼吸感的布局。
    - Action: Optimize row height, use borderless design, and implement "Glassmorphism" where possible.
      行动：优化行高，使用无边框设计，并在可能的地方实现“毛玻璃”效果。
- **Consensus 2: Logic Injection / 共识 2：逻辑注入**
    - Integration of Lightme/Logbook JSON is now the priority.
      Lightme/Logbook JSON 的集成现在是优先级最高的事项。

## 3. Critical UI/UX Adjustments / 关键 UI/UX 调整要求

### A. The "Glassmorphism" Sidebar / “毛玻璃”侧边栏
- **Requirement / 要求**: Sidebar (Filters & Presets) should look more integrated. Use consistent icons (SF Pro style) and rounded buttons.
  侧边栏（过滤器与预设）应更具整体感。使用统一的图标（SF Pro 风格）和圆角按钮。
- **Inspector Layout / 检查器布局**: 
    - [cite_start]Thumbnail is great[cite: 9], but metadata display needs hierarchy.
      缩略图很好，但元数据展示需要层级感。
    - **Digital Back Font / 背后字体**: Use dot-matrix/LCD style fonts for key parameters (Aperture, Shutter) to evoke an analog feel.
      关键参数（光圈、快门）使用点阵/LCD 风格字体，唤起模拟感。

### B. Table View Optimization / 表格视图优化
- [cite_start]**Status Indicators / 状态指示**: Use subtle colored dots (e.g., green for "written", blue for "pending") instead of just text "loaded". [cite: 6]
  使用微小的彩色圆点（如绿色代表“已写入”，蓝色代表“待处理”）代替纯文本“loaded”。
- **Interactivity / 交互**: Double-clicking a row should focus the right panel's editor.
  双击行应使焦点跳转至右侧面板的编辑器。

## 4. Feature Logic: The "Film-Digital Bridge" / 功能逻辑：“胶片-数字桥梁”

### JSON Auto-Matcher / JSON 自动匹配器
- **The Core Problem / 核心问题**: Digital scans often don't match JSON log timestamps perfectly.
  数字扫描件往往无法与 JSON 记录的时间戳完美匹配。
- **Implementation Requirement / 实现要求**: 
    1. **Time Offset Slider / 时间偏移滑块**: Allow user to shift all JSON records ±N minutes to align with file creation dates.
       允许用户偏移所有 JSON 记录 ±N 分钟，以对齐文件创建日期。
    2. **Sequential Force-Match / 顺序强制匹配**: If timestamps fail, allow matching based on the sorting sequence of files and logs.
       如果时间戳匹配失败，允许基于文件和记录的排序顺序进行匹配。

## 5. Technical Next Steps / 技术下一步
1. **Refine UI Theme / 优化 UI 主题**: Implement a custom QSS (Qt Style Sheet) to achieve a modern macOS dark/light mode.
   实现自定义 QSS，以达到现代 macOS 的深色/浅色模式效果。
2. **Develop JSON Import Engine / 开发 JSON 导入引擎**: Create a parser for Lightme `.json` exports.
   为 Lightme 的 `.json` 导出文件创建解析器。

---
*End of README_FOR_AI.md*

# Project: DataPrism (README_FOR_AI.md)

## 1. Project Vision & Goals / 项目愿景与目标
DataPrism is a lightweight, high-aesthetic, and high-performance ExifTool GUI station. It is designed for hardcore photographers, film enthusiasts, and developers who need precise control over image metadata.
DataPrism 是一款轻量、美学领先、高性能的 ExifTool GUI 工作站。专为硬核摄影师、胶片爱好者和开发者设计，提供对图像元数据的精确控制。

- **Objective / 目标**: Replace clunky or command-line-only workflows with a refined macOS-style interface.
  以精致的 macOS 风格界面取代笨重或纯命令行的工作流。
- **Key Feature / 核心功能**: Professional metadata reading (MakerNotes), batch editing, and deep integration with film logging apps (Lightme/Logbook).
  专业的元数据读取（制造商注释）、批量编辑，以及与胶片记录应用（Lightme/Logbook）的深度集成。

## 2. Technical Requirements / 技术要求
- **Language / 语言**: Python 3.10+
- **UI Framework / UI 框架**: PySide6 (Primary choice / 首选)
- **Style / 风格**: Mimic macOS modern design (Rounded corners, clean typography, minimalist layout).
  模仿 macOS 现代设计语言（圆角、清爽的排版、极简布局）。
- **Comment Policy / 批注策略**: All code annotations MUST be bilingual (Chinese and English).
  所有代码批注必须使用中英双语。

## 3. Communication & Version Consensus / 沟通与版本共识
This section tracks the evolution of requirements to ensure the AI Assistant understands the "Why" behind changes.
本部分追踪需求演变，确保 AI 助手理解变更背后的深层原因。

### v0.1.0 - Foundation / 基础定义 (2026-01-20)
- **Status / 状态**: Conceptualization & Architecture Definition. / 概念化与架构定义。
- **Key Consensus / 核心共识**:
    1. **UI Type / 界面类型**: Single-window Dashboard (not a floating widget). / 单窗口仪表盘（而非悬浮挂件）。
    2. **Target User / 目标用户**: Hardcore film photographers (Hasselblad/Medium Format users). / 硬核胶片摄影师（哈苏/中画幅用户）。
    3. **Core Interaction / 核心交互**: Support drag-and-drop, JSON injection (Lightme/Logbook), and manual overwrite. / 支持拖拽、JSON 注入（Lightme/Logbook）和手动覆盖。
    4. **Backend / 后端**: Must use `exiftool` as the reliable engine. / 必须使用 `exiftool` 作为可靠引擎。
- **Requirement Change / 需求变更**: Shifted from a generic EXIF viewer to a specialized "Metadata Workstation" for film-to-digital workflows.
  从通用的 EXIF 查看器转向专门针对“胶片数字化”流程的元数据工作站。

## 4. Product Functional Architecture / 产品功能架构

### A. UI/UX Design (macOS Aesthetics) / UI/UX 设计 (macOS 美学)
- **Sidebar / 侧边栏**: Quick filters (Camera, Lens, Film Stock) and Presets.
  快速过滤器（相机、镜头、胶卷型号）和预设。
- **Main View / 主视图**: Grid or list view of imported photos with status indicators (e.g., "Metadata Modified").
  导入照片的网络或列表视图，带有状态指示（如“元数据已修改”）。
- **Inspector / 检查器 (右侧面板)**: Detailed metadata editor. Supports MakerNotes (Shutter count, focus distance).
  详细的元数据编辑器。支持制造商注释（快门次数、对焦距离等）。

### B. Specialized Features / 特色功能
- **JSON Mapping Logic / JSON 匹配逻辑**: 
    - Function to parse Lightme/Logbook JSON files. / 解析 Lightme/Logbook JSON 文件的功能。
    - Intelligent matching based on timestamp tolerance and file sequence. / 基于时间戳容差和文件顺序的智能匹配。
- **Preset System / 预设系统**: 
    - Ability to save "Equipment Profiles" (e.g., "Hasselblad 503CX + CF 80/2.8"). / 保存“设备配置文件”的能力。
    - One-click application to multiple files. / 一键应用至多个文件。

## 5. Implementation Roadmap / 开发路线图
1. **Phase 1**: Project scaffolding and basic PySide6 window setup (macOS style).
   项目脚手架搭建及基础 PySide6 窗口设置（macOS 风格）。
2. **Phase 2**: Asynchronous ExifTool wrapper implementation.
   异步 ExifTool 封装实现。
3. **Phase 3**: JSON parsing and matching algorithm.
   JSON 解析与匹配算法。

## 6. Historical Context / 历史背景
- User is a medium format enthusiast (Hasselblad). User previously developed `ContactSheetPro` and automated border scripts.
  用户是中画幅爱好者（哈苏）。此前曾开发 `ContactSheetPro` 和自动边框脚本。
- Preference for dot-matrix/retro fonts in specific UI areas.
  倾向在特定 UI 区域使用点阵/复古字体。

---
*End of README_FOR_AI.md*