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