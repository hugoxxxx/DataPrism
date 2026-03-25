# DataPrism Change Log / 变更日志

## [1.2.0] 2026-03-15 - Zero-Dependency & Portability / 零依赖与便携性强化
- **ExifTool Bundling / 集成 ExifTool 引擎**:
    - **Engine Integration / 引擎内置**: Bundled `exiftool.exe` and its libraries directly into `src/resources/bin` (直接将 ExifTool 引擎及类库整合至 bin 目录，彻底消除外部依赖).
    - **Zero-Config / 零配置使用**: Application now auto-detects and prioritizes the internal bundled ExifTool, achieving "batteries-included" portability (程序自动优先调用内置引擎，实现真正意义上的“开箱即用”与便携性).
- **Repository Maintenance / 仓库维护与清理**:
    - **Binary Tracking / 二进制追踪**: Configured `.gitignore` to force-include essential binaries while maintaining exclusion for local media (优化 Git 忽略规则，在保持媒体文件隔离的同时确保核心引擎被正确追踪).
    - **Log Isolation / 日志隔离**: Untracked `dataprism.log` to keep the repository clean from local runtime noise (将运行日志移出版本控制，确保仓库整洁).
- **Core Logic Refinement / 核心逻辑优化**:
    - **Smart Path Resolution / 智能路径溯源**: Enhanced `ExifToolWorker` path resolution logic to seamlessly transition between development and packaged (PyInstaller) environments (重构路径解析逻辑，完美兼容开发环境与打包后的单文件环境).


## [1.1.0] 2026-01-31 - The "Prism" Update / 棱镜更新
- **Critical Stability / 核心稳定性**:
    - **Crash Fixes / 崩溃修复**: Fixed application freeze on bulk import (thread optimization) and editor crash on reordering (修复了批量导入卡死和编辑器排序报错的问题).
- **Brand Identity / 品牌视觉**:
    - **Visual Overhaul / 视觉重塑**: Removed white border from app icon for a cleaner, frameless look (移除应用图标白框，实现无边框透明设计).
    - **Icon Stability / 图标稳定性**: Fixed resource loading paths to ensure icon appears correctly in all dialogs (修复资源路径，确图标在所有窗口稳定加载).
- **Core Stability / 核心稳定性**:
    - **ExifTool Robustness / ExifTool 鲁棒性**: Refactored `batch_write_exif` with `-common_args` to ensure flags like `-overwrite_original` persist across all batch tasks (使用 `-common_args` 重构批量写入，彻底解决多文件处理时的配置失效拥堵).
    - **Parser Priority / 解析优先级**: Fixed `MetadataParser` logic to prioritize `Model` over `Make`, ensuring correct camera model detection (修复解析器优先级，防止将厂商名误认为型号).
- **High-Performance Parallel Batching / 高性能并发批量处理**:
    - **Multi-core Parallelism / 多核并发技術**: Achieved 21.4x speedup (6s for 100 photos) using Multi-core Sharding and Argfile patterns (通过多核分片与 Argfile 技术实现 21.4 倍性能提升).
    - **Turbo TIFF Previews / 极速 TIFF 预览**: Switched to `QImageReader` to handle 500MB+ TIFFs without OOM (升级预览加载引擎，支持亿级像素 TIFF 秒开).
    - **Deep JSON Probe / 深度 JSON 探测**: Recursive mapping for complex metadata structures (支持深度递归解析复杂 JSON 元数据).

## [1.0.0] 2026-01-28 - Official Release / 正式版发布
- **Exe Packaging / 打包封装**: Packaged as a single `.exe` file using PyInstaller (使用 PyInstaller 封装为单文件 exe)。
- **Size Optimization / 体积优化**: Reduced file size by excluding unused modules (通过排除无用模块减小了文件体积)。
- **Plain Bilingual Docs / 双语手册**: Updated README and User Guide with plain EN/CN mixed text (更新了中英混写的双语版 README 和使用手册)。
- **File Isolation / 环境隔离**: Hidden debug scripts and test media from GitHub (在 GitHub 仓库中屏蔽了调试脚本和测试资源)。
- **UI & Logistics / 界面与逻辑**: Finished settings layout and log control (完善了设置界面布局和日志管理功能)。

## [2026-01-28] Log Management & Sync / 日志管理与同步
- **Git Sync / 代码同步**: Synced local code with latest GitHub commits (从 GitHub 同步了最新的代码)。
- **Log Rotation / 自动日志管理**: Added automatic log rotation to prevent large files (增加了日志自动切分功能，防止文件过大)。
- **Log Settings / 日志设置**: Added UI controls for log size and level (在设置界面增加了日志大小和级别的控制)。
    - **完善国际化**: 补全了所有新增设置项的中英双语翻译。
- **稳定性修复 (Bug Fix)**:
    - 修复了 `settings_dialog.py` 中因导包缺失导致的 `NameError: QDialog is not defined` 启动错误。

## [2026-01-27] 智能生产力：记忆与便携 (Smart Productivity)
- **智能历史与自动填充 (Smart History & Auto-fill)**:
    - **全能记忆库**: 引入了独立的 `history.json` 存储引擎，自动记录您使用过的所有相机、镜头和胶卷型号。
    - **智能自动联想**: “一键写入”面板全面升级为可编辑组合框 (`QComboBox`)。当您选择已保存的型号时，对应的品牌（Make）会自动秒填，大幅减少重复录入工作。
    - **即时学习**: 新输入的器材组合会在应用成功后自动存入记忆库，越用越顺手。
    - **右键管理**: 在下拉框中点击右键，即可快速删除不需要的历史条目，保持列表整洁。
- **便携模式 (Portable Mode)**:
    - **灵活存储架构**: 在设置中心新增了“便携模式”开关，支持在“系统级漫游 (AppData)”与“本地级便携 (Portable)”之间一键切换。
    - **无痕单文件体验**: 默认模式下所有配置均存储在系统目录，保证 EXE 所在文件夹的极致整洁。
    - **数据无缝迁移**: 切换模式时，系统会自动将所有配置和历史记录搬运到新位置，确保数据零丢失。

## [2026-01-27] 架构稳定性与工业级 UI 交互深调
- **终极稳定性修复 (Architectural Stability)**:
    - **彻底解决信号槽死锁**: 通过拆分 `read_finished` 与 `write_finished` 信号，从根源切断了“无限读写循环”导致的界面死锁问题。
    - **跨线程安全增强**: 修复了 `QObject::setParent` 警告，确保所有驱动 UI 更新的信号均通过 `Qt.QueuedConnection` 在主线程安全执行。
- **元数据写入流程重构 (Workflow Decoupling)**:
    - **“即点即写”交互**: `MetadataEditorDialog` 现支持确认后立即关闭，任务静默移交至主窗口常驻 `ExifToolWorker` 执行，配合“执行状态”栏实时进度输出，操作连贯性显著提升。
    - **零干扰刷新**: 写入完成后主界面数据静默后台刷新，移除了多余的弹窗确认流程。
- **工业级 UI 细节打磨 (Interface Refinement)**:
    - **后背数据屏 (LCD) 优化**: 英文模式下自动精简标签为 **Ap** (Aperture) 和 **Sh** (Shutter)；三个 LCD 参数面板强制 **1:1:1 等宽**，视觉结构更加稳固、平衡。
    - **自适应表格大瘦身**: 
        - 移除了冗余的“状态 (Status)”列，将注意力锁定在核心元数据。
        - **全交互式列宽**: 所有表格列现在支持手动自由拉拽。
        - **智能初始宽度保护**: 为“文件名”和“胶卷型号”设置了 160px 初始宽度，有效防止超长字符串（如 KODAK Gold 200）在导入时被截断。
    - **状态栏截断修复**: 优化了元数据编辑器底部的 `warning_label` 布局优先级，并精简了多语言翻译，确保在各种窗口尺寸下警告文本均 100% 完整显示。
- **侧边栏布局微调**: 将“设置中心”齿轮与“语言切换”按钮移至侧边栏最下方，对齐专业图片处理软件（如 Phocus）的视觉工业标准。

## [2026-01-27] 设置中心与工业生产力增强
- **哈苏风格设置中心 (Settings Center)**:
    - **原生设置入口**: 在侧边栏顶部新增齿轮图标按钮 (`⚙`)，点击即可唤起全新的集成设置面板。
    - **UI 鲁棒性精修**: 为复选框注入了高对比度 CSS 样式，解决了组件在暗色背景下的辨识度问题。
    - **全系统本地化与说明**: 补全了所有设置项的中英双语翻译，并为每项功能增加了直观的辅助说明文案。
    - **快捷路径浏览**: 为 ExifTool 路径选项增加了文件夹浏览入口。
    - **多维度配置支持**: 实现了对 ExifTool 路径、超时设置、并行工作线程数以及自动保存逻辑的交互式管理。
- **工业级元数据写回策略**:
    - **文件覆写模式 (Overwrite Strategy)**: 支持在直接覆写原图与保留 `.original` 备份之间自主切换。
    - **修改日期保持 (Preserve Date)**: 引入了 EXIF 写入时的 `-P` 参数支持，确保文件的“修改时间”在元数据更新后依然纹丝不动，符合专业工作流习惯。
- **智能路径记忆 (Path Memory)**:
    - 应用程序现在会自动记忆上次“添加照片”或“导入元数据”时的文件夹路径，大幅提升重复性操作的效率。

## [2026-01-27] 环境就绪与 UI 进阶优化
- **环境配置**: 成功搭建 `venv` 虚拟环境，并解决由于本地代理导致的 SSL/pip 安装问题。
- **控制台高度优化**: 将底部的“进程状态” (Process Status) 控制台高度从 120 像素增加至 180 像素，提升日志可读性。
- **预览图像增强**: 
    - **影院级呼吸边距 (Cinema Padding)**: 为预览黑盒注入了 10px 的垂直呼吸间距，彻底消除照片顶格感，视觉体验更为从容、高级。
    - **极简主义控制件**: 旋转按钮精华至 48x34px，在维持功能性的同时大幅缩减视觉占位，提升界面精致度。
    - **Ultra-Bold 符号标记**: 图标加粗至极限 900 字重，在精简按钮中依然具备极强的视觉爆发力。
    - **UI 布局稳定性增强**: 锁定 Inspector 面板宽度为 **300px**，彻底解决了窗口缩放时右侧面板宽度抖动的问题。
    - **像素级居中方案**: 强制固定像素对齐，确保任何旋转状态下都达成了完美的“物理居中”。
- **表格视觉精修**: 
    - **像素级对齐 (Pixel-Perfect Sync)**: 解决了由于 `Delegate` 使用点号单位 (Point Size) 而样式表使用像素单位 (Pixel Size) 导致的字号不一问题。**全系统统一采用 11px (Pixels)**，确保表头与内容视觉高度绝对一致。
    - **彻底移除硬编码**: 剥离了 `main_window.py` 和 `borderless_delegate.py` 中散落的所有 `setFont` 和硬编码字号设置。
- **数码后背显示屏 (LCD) 终极修复**: 
    - 优化了样式加载逻辑，通过 `exposure_card` 顶层容器统领所有 LCD 标签样式，彻底解决了因重构导致的颜色失效问题。
    - **视觉微调 (Studio Refinement)**: 实现了 LCD 面板内文字的**全居中对齐**，并将数值字重调优至 **Bold (700)**，哈苏橙数值更显醒目、纯粹。

## [2026-01-26] 工业级元数据深度扩展
### 🔍 焦距系统升级 (Dual-Focal Engine)
- **双焦距表项支持**: 
    - 主界面表格新增“焦距 (Focal)”与“等效 (F35mm)”列，提供直观的镜头参数对比。
    - 元数据编辑器 (Metadata Studio) 增加等效焦距专门输入框，支持自动识别 CSV 中的 `FocalLengthIn35mmFormat` 标签。
    - 检查器 (Inspector) 面板同步展示原生/等效焦距，对齐哈苏专业工作流。
- **日期写入逻辑修复**: 彻底修复了日期 (DateTimeOriginal) 无法写入的问题，增加了日期自动补全与标准化逻辑（YYYY:MM:DD）。
- **元数据专业化呈现**: 
    - **光圈显示优化**: 全面移除 `f/` 前缀（如 `f/2.8` -> `2.8`），对齐现代专业图片管理器的极简风格。
    - **快门格式重构**: 引入专业快门后缀逻辑，1秒及以上显示 `S` 后缀（如 `1.0S`），分数值保持原样且不带余项。
- **Studio 侧边栏 2.3 功能增强**:
    - **批量写入灵活性**: “一键写入”面板新增“全部”与“选中”按钮，支持针对全部或特定选定照片进行精准的元数据批量修改。文字已精简以适配狭窄侧边栏。
    - **逻辑重塑**: 将“导入元数据”置为最高优先级，其下衔接“一键写入”区。
    - **标题栏绝对固定**: 修正了无照片时的提示位布局，提示语现在紧贴表头下方显示，确保标题栏位置不随导入状态跳动。
    - **一键写入 (Quick Write)**: 集成相机品牌/型号、镜头品牌/型号、焦距、**等效35mm焦距**及胶卷输入。
    - **国际化全覆盖**: 补齐了主表格表头（C-Make, C-Model 等）及侧边栏所有新增字段的中文翻译，修复了语言切换时的显示死角。
    - **操作直观化**: 将“浏览文件”全线更名为“添加照片”，并将提示语移动到表头下方以固定标题栏位置；增加照片列表右键“移除”功能，管理更灵活。
    - **专业元数据规范**: 统一焦距显示格式，全线移除无效小数点（如 `1000.0` 修正为 `1000 mm`），并支持无单位快捷输入。
    - **稳定性增强**: 修复了语言切换时因属性缺失导致的崩溃（`content_title` 等）；修复了检查器 LCD 面板的类型匹配错误，增强了系统的健壮性。

## [2026-01-25] UI/UX 终极美化与 Studio 2.0 重构
### 🏗️ 设计系统与架构升级 (Engineering Refactor)
- **Studio 设计系统 2.0**:
    - **主题外部化**: 配色参数从 Python 移至 `resources/themes/studio_dark.json`，支持零代码主题切换。
    - **哈苏 3 阶按钮体系**: 引入 `Primary` (高亮橙), `Secondary` (描边), `Ghost` (纯文本) 三级逻辑，信息层级更专业。
    - **对比度深度审计**: 大幅调亮“序列偏移”等标签。彻底修复了 `QMessageBox` (Yes/No) 按钮文本无法辨认的“白内障”问题。
- **全能编辑器布局重构**:
    - **双导航联动**: 实现照片与元数据记录列表的双向同步导航。
    - **实时预览**: 编辑器内置实时照片预览与 LCD 式数字背屏数据显示。
    - **智能自适应**: 实现了响应式 4 列架构，权重分配更合理 (2:2:4:3)。

### 🎨 视觉与审美细节
- **无感表格分栏**: 移除重复细线，改用具有“质感”的半透明色块与交替行背景。
- **暮色调色板 (Twilight Palette)**: 采用更深邃的 #101012 背景配合哑光哈苏橙。
- **列表精简化**: 移除多余的帧号备注，仅保留简洁的 `#[序号]` (如 `#01`)。
- **分栏条优化**：将 Splitter 线条优化为 1px 极细风格，仅在悬停时产生交互反馈。

2026-01-24  修正与改进
- 新增：将主界面表格中的“相机”列拆分为独立的“品牌（Make）”与“型号（Model）”两列，优化器材信息展示与编辑精度。
- 优化：更新 JSON/CSV 解析逻辑，支持分别抓取并同步品牌与型号字段（如展示为 "Hasselblad" | "500C/M"）。
- 新增：主界面表格内直接编辑元数据功能。
    - 支持通过双击单元格直接修改相机、镜头、快门、光圈、ISO、胶卷型号、地理位置、日期等字段。
    - 修改操作触发后台自动异步写入 EXIF，修改成功后自动刷新 UI。
    - 编辑过程中集成了元数据校验逻辑，确保格式基本合规。
- 新增：CSV/TXT 智能导入功能，支持字段映射对话框、GPS 方向选择、按行序号匹配照片。
- 修复：元数据编辑器数据同步逻辑。实现 `_save_current_metadata` 方法，确保手动修改的 ISO、胶卷、快门等字段在切换照片、调整偏移或写入前能自动保存到内存任务列表中。
- 修复：解决了手动修改元数据后无法写入的问题。
    - 修正了 `MetadataEditorDialog` 中 `notes` 字段访问函数错误（`toPlainText` 改为 `text`）。
    - 统一了 ExifTool 读取与写入的标签命名规则（移除 `-G` 标志），确保写入后的 ISO 等数据能正确回显在主界面。
    - 放宽了胶卷型号识别的关键词限制，支持显示所有手动输入的描述信息。
    - 自动补齐缺失的元数据条目，确保所有照片都能进行手动录入。
- 鲁棒性：增强了元数据写入的兼容性。
    - 验证失败时自动回退到原始输入值，确保非标准数据也可尝试写入。
    - 自动转换日期格式（`-`、`/` 转 `:`）和焦距（移除 `mm`）。
    - 为 ExifTool 添加 UTF-8 字符集支持，解决 Windows 路径和特殊字符编码问题。
- 优化：移除元数据写入完成后多余的“成功读取 EXIF”提示框，减少操作干扰，使流程更顺滑。
- 修正：元数据写入流程进度与完成确认。
	- 在 [src/ui/metadata_editor_dialog.py](src/ui/metadata_editor_dialog.py) 中：确保写入完成时将进度设置为 100、关闭进度对话框；改为弹出模态确认框（用户点击“确定”后关闭编辑器）；增加写入线程结束的后备处理以防止对话框残留。
- 修正：在 [src/core/exif_worker.py](src/core/exif_worker.py) 中修复批量写入的缩进错误并增加超时与日志，确保每个任务实际执行并正确返回结果。
- 改进：调整 [src/ui/main_window.py](src/ui/main_window.py) 的刷新按钮布局和 EXIF 读取/写入进度处理逻辑，增强 UI 反馈。
- 国际化：修复并补充 [src/utils/i18n.py](src/utils/i18n.py) 中的翻译字符串，避免语法错误并添加新提示文本。
- 修复：统一主界面与元数据编辑器的地理位置格式，创建 [src/utils/gps_utils.py](src/utils/gps_utils.py) 集中处理 GPS 解析/格式化逻辑；修复因引号导致的正则解析失败，确保类似 "28deg ... \" N North" 的非标准字符串能被正确格式化为度分秒标准格式；同时增强了 UserComment 中 Location 字段的解析。
- 优化：修改元数据写入完成后的交互逻辑，移除自动关闭编辑器的行为，确保在弹出“写入完成”对话框并等待用户点击确认后，再关闭编辑器窗口，提供更明确的操作反馈。
- 调试：在 [src/core/exif_worker.py](src/core/exif_worker.py) 中增加信号发射的调试输出，用于诊断 result_ready 信号未被接收的问题。
- 修复：在 [src/ui/metadata_editor_dialog.py](src/ui/metadata_editor_dialog.py) 中为所有跨线程信号连接添加 Qt.QueuedConnection，确保信号槽在主 GUI 线程中执行，解决模态对话框导致的线程死锁问题。
- 修复：使用 QTimer.singleShot 延迟弹出完成对话框，避免模态对话框阻塞事件循环导致 finished 信号无法完成的死锁问题。
- 修复：由于 PySide6 的 result_ready 信号无法可靠传递 dict 类型数据，改用在 worker 中存储结果，在 finished 信号处理器中读取的方式，绕过信号系统的限制。
- 修复：完全禁用 result_ready.emit() 调用，因为该调用会阻塞 worker 线程，改为只使用 last_result 实例变量传递数据。
- 修复：移除 finished 信号连接到 quit/deleteLater 的逻辑（会导致死锁），改用 QTimer 每 100ms 轮询线程状态，检测到完成后读取结果并清理资源。
- 修复：完全禁用 finished.emit() 调用（也会阻塞），worker 方法执行完毕后线程自然结束，由 QTimer 检测线程状态变化。

## 2026-01-24 - 鲁棒性改进 / Robustness Improvements

- 新增：统一日志系统 [src/utils/logger.py](src/utils/logger.py)，支持控制台和文件输出，替换所有 print() 调用。
- 新增：全局异常处理器，捕获所有未处理的异常并记录到日志文件，防止程序崩溃。
- 新增：ExifTool 重试机制，最多重试 3 次，使用指数退避策略，提高写入操作的可靠性。
- 新增：资源清理机制，在 MetadataEditorDialog 的 closeEvent 中确保线程和 worker 正确清理，防止内存泄漏。
- 新增：输入验证器 [src/utils/validators.py](src/utils/validators.py)，验证所有元数据字段（光圈、快门、ISO、焦距、日期时间等），防止写入非法数据。
- 新增：配置管理系统 [src/core/config.py](src/core/config.py)，支持 JSON 配置文件持久化，管理 ExifTool 路径、重试次数、UI 设置等。
- 优化：所有调试输出统一使用 logger，支持不同日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）。
- 优化：使用信号触发 worker 方法，避免 started 信号的 lambda 阻塞线程事件循环。
- 优化：清理所有调试用的 print() 语句，全部替换为规范的 logger 调用，提升生产环境可用性。
- 修复：胶卷型号写入后不显示的问题，现在同时写入 Film 字段 and UserComment，并在刷新时显示进度对话框。
- 新增：GT23_Workflow 兼容性，ImageDescription 字段优先写入胶卷型号，确保 GT23 自动识别功能正常工作。
- 修复：GPS 坐标写入格式，现在使用与 1.json 一致的 ExifTool 标准格式（如 "28deg 31' 30.59\" N"）。

说明：以上改动为本地调试与用户交互可感知的修复，已在本地测试写入流程并增加调试输出以方便进一步排查。

DataPrism change log
====================

2026-01-23
- Main window columns (v0.3.1): Added Film Stock and Location columns to photo table; inspector now shows film and location; header sizing updated for the two new columns; location now surfaces GPSLatitude/GPSLongitude when present.
- Metadata write enhancement (v0.3.1): Enhanced _build_exif_dict() in metadata_editor_dialog.py with improved field handling: split camera field into Make and Model tags (supports both "Make Model" and single-word formats), added format conversion for aperture (f/2.8→2.8), ISO (ISO 400→400), and focal length (80mm→80); added multi-date field write (DateTimeOriginal, CreateDate, ModifyDate); changed location storage from invalid GPSInfo tag to ImageDescription; enhanced UserComment to combine film stock, location and notes; added notes field to UserComment with proper chaining.
- GPS write support (v0.3.1): Location text now parsed into GPSLatitude/GPSLatitudeRef/GPSLongitude/GPSLongitudeRef when possible while still writing ImageDescription for human-readable location.
- GPS read combining (v0.3.1): Metadata import now merges GPSLatitude/GPSLongitude (+Ref) fields into a single location string for editor display and writing.
- GPS display cleanup (v0.3.1): GPS lat/lon now formatted without duplicated direction words (N/S/E/W) for cleaner Location display.
- Metadata import fix (v0.3.1): Fixed MetadataParser to support ExifTool EXIF tags (Make, Model, FNumber, ExposureTime, ISO, FocalLength, DateTimeOriginal, etc.) in JSON exports; added automatic numeric format conversion (f-stop for FNumber, fraction for ExposureTime, mm for focal length, etc.); extended field mapping across all 10 metadata attributes to handle both Lightme format and ExifTool format simultaneously.
- Editor dialog debugging (v0.3.1): Added logging to metadata_editor_dialog.py load_photo() method for diagnostic support.
- Additional metadata fields (v0.3.1): Added shot_date and location fields to MetadataEntry dataclass; extended field mapping in _parse_entry() for shot_date (DateTimeOriginal, DateTime, CreateDate, ModifyDate, SubSecDateTimeOriginal) and location (GPSLatitude, GPSLongitude, GPSAltitude, GPSLatitudeRef, GPSLongitudeRef, etc.) with tags; updated MetadataEditorDialog UI with 2 new QLineEdit fields for shot date and location; added translations for "Shot Date:" and "Location:" to i18n.py.
- Write metadata fix (v0.3.1): Fixed on_write_metadata() to correctly map each photo to its corresponding metadata entry with offset consideration; updated _build_exif_dict() to include shot_date and location fields; improved exif_worker.py value validation (check for None and empty string) to ensure all valid metadata is written; added debug logging to track photo-to-metadata mapping during batch write.
- Main window refresh button (v0.3.1): Added "Refresh EXIF" button to main window sidebar for reloading all photos' EXIF data after external modifications; implemented refresh_exif() method that re-reads EXIF asynchronously via queue_exif_read(); button styled with blue gradient matching metadata import button; added translations for "Refresh EXIF" and "No photos to refresh" to i18n.py.
- Cleanup: Removed temporary test scripts, diagnostic documentation files, and all v0.3.1 development draft reports; kept only core implementation and production files.

2026-01-20 (v0.3.1) - Metadata Editor Upgrade
- Universal metadata parser (src/core/metadata_parser.py): created MetadataParser class supporting JSON/CSV/TXT file formats with auto-detection; MetadataEntry dataclass unifies 10 fields (camera, lens, aperture, shutter_speed, iso, film_stock, focal_length, timestamp, frame_number, notes) across all formats.
- JSON parsing (v0.3.1): extended _parse_json() to handle 3 wrapper types (frames, entries, shots); flexible field name mapping with 10+ fallback names per attribute (Camera/camera/Body/body/Model/model etc.); timestamp extraction from ISO 8601 and custom date formats; frame_number inference from entry position or explicit field.
- CSV parsing (v0.3.1): implemented _parse_csv() using DictReader with header-based flexible field mapping; 6+ fallback field names per attribute (e.g., Lens/Lens Model/LensModel/Lens-Model/LensName); handles missing columns gracefully with None defaults.
- TXT parsing (v0.3.1): implemented _parse_txt() with delimiter detection (pipe | or tab); positional field assignment with order: camera, lens, aperture, shutter, iso, film_stock, focal_length, notes; supports variable-length rows.
- New metadata editor dialog (src/ui/metadata_editor_dialog.py): created MetadataEditorDialog as dedicated window for preview/edit/write workflow; 3-section layout with QListWidget for photo navigation, QFormLayout with 8 editable QLineEdit fields, offset spinbox (±20 frames) for sequence adjustment; batch write capability via ExifToolWorker; metadata_written signal triggers main window refresh.
- Offset control (v0.3.1): added QSpinBox in editor dialog for sequence offset adjustment; on_offset_changed() reloads metadata_entries[index + offset] to handle film photography frame skips; range ±20 frames covers typical photoshoot scenarios.
- Count warning (v0.3.1): editor dialog compares metadata record count vs photo count; displays color-coded warning label if mismatch detected; helps users identify incomplete metadata or extra photos.
- Main window integration (v0.3.1): replaced import_json() with import_metadata() supporting all 3 formats; button text changed "Import JSON" → "Import Metadata"; new method opens file dialog (*.json *.csv *.txt), parses via MetadataParser, launches MetadataEditorDialog; new on_metadata_written() callback refreshes EXIF after write.
- Removed old methods (v0.3.1): deleted _apply_json_matches(), _on_batch_write_complete(), _on_batch_write_error() from main_window.py as logic migrated to MetadataEditorDialog.
- Matching strategy update (v0.3.1): changed match_hybrid() default from prefer_timestamp=True to prefer_timestamp=False; sequence-first matching (1:1 in-order) now default for film photography workflows with potential frame skips and multiple dates.
- i18n expansion (v0.3.1): added 20+ new translation strings for metadata editor dialog (Metadata Editor, Edit Metadata, Photos, Camera/Lens/Aperture/Shutter/ISO/Film Stock/Focal Length/Notes labels, Sequence Offset, warning message, Write All Files, Write Metadata, confirmation/success messages) to TranslationManager; full Chinese/English support.
- v0.3.1 complete workflow: Import → Dedicated Editor Window with inline field editing → Sequence offset adjustment → Batch write from dialog → Auto-refresh main window; replaces old preview-only approach with full edit capability in single window.

2026-01-20
- Init log file for PM review.
- UI import: drag-and-drop enabled for image extensions; added Browse files… button that opens a file dialog and reuses drop handler.
- UI list: hooked center view to PhotoDataModel with QTableView; dropped/browsed files are added into the model, placeholder hides when list has data.
- EXIF: MainWindow now wires ExifToolWorker via QThread; new imports trigger queued EXIF reads, results populate PhotoDataModel; worker errors logged; thread stops on window destruction.
- Inspector: right panel now shows selected photo info (file, camera, lens, date, status) with live updates when selection or EXIF results change.
- EXIF decoding: ExifTool worker now decodes stdout/stderr as UTF-8 with errors=replace and guards JSON parse errors to avoid GBK UnicodeDecodeError; timeout bumped to 15s.
- Fonts: removed explicit "System" font to let Qt use default Windows font and silence DirectWrite warnings.
- Inspector thumbnail: added 180x180 preview in inspector; loads QPixmap from file, caches per photo, clears when no selection.
- UI aesthetics (v0.2.0): upgraded table to 52px rows, no grid, macOS colors; status column now shows colored dots (green/blue/red/gray); sidebar buttons have 10px radius with gradients; inspector uses Consolas monospace for data, hierarchical labels, 200px thumbnail with separator; global Big Sur theme (#f5f5f7 background).
- Selection contrast: deepened selection background to #0051d5 with explicit white text for better visibility.
- Metadata expansion (v0.2.1): extended PhotoItem with aperture/shutter/ISO/focal_length/film_stock/serial_number fields; table now 8 columns (File/Camera/Lens/Aperture/Shutter/ISO/Date/Status); formatted display (f/2.8, 1/125s, -- for missing); auto-parse exposure from EXIF; inspector adds Exposure section with bold Consolas font; optimized column widths (fixed for exposure, stretch for file).
- i18n support (v0.2.1): created src/utils/i18n.py translation manager with auto system language detection (Chinese/English); added 中/EN toggle button in sidebar; all UI text (titles/labels/buttons/tooltips/columns) now use tr() function; refresh_ui() method updates entire interface on language switch.
- JSON film log import (v0.3.0): created src/core/json_parser.py with FilmLogParser supporting Lightme/Logbook JSON formats; FilmLogEntry dataclass extracts camera/lens/aperture/shutter/ISO/film_stock/timestamp fields with flexible field name mapping; handles array wrappers (frames/entries/shots) and multiple timestamp formats.
- Photo matching algorithms (v0.3.0): implemented src/core/json_matcher.py with PhotoMatcher class; three strategies: match_by_timestamp (±5min tolerance), match_by_sequence (1:1 order), match_hybrid (timestamp first, fallback to sequence if <50% matched); get_match_statistics returns match rate and counts.
- JSON import UI (v0.3.0): added green gradient "Import JSON" button in sidebar; import_json() method opens file dialog, parses JSON, auto-matches photos, shows preview dialog; integrated with FilmLogParser and PhotoMatcher; checks for imported photos before proceeding.
- Match preview dialog (v0.3.0): created src/ui/match_dialog.py with MatchPreviewDialog showing 6-column table (Photo File/Date → Log Camera/Lens/Date); displays match statistics (matched/total with percentage); time offset adjustment spinbox (±180 minutes) with rematch button; macOS Big Sur styling with rounded corners; confirm/cancel buttons.
- Batch EXIF write (v0.3.0): extended ExifToolWorker.batch_write_exif() for multi-file async writes with progress signals; _apply_json_matches() builds EXIF tasks mapping log entries to Make/Model/LensModel/FNumber/ExposureTime/ISO/FocalLength/DateTimeOriginal/UserComment; QProgressDialog shows write progress; auto-refreshes photo data after completion; error handling with success/failure counts.
- Bug fix (v0.3.0): corrected PhotoMatcher instantiation in main_window.py and match_dialog.py; __init__ only takes time_tolerance_minutes parameter, photos/log_entries passed to match methods; added tuple-to-dict conversion for match results (List[Tuple[PhotoItem, FilmLogEntry]] to Dict[int, int] index mapping) to interface with MatchPreviewDialog.
- Bug fix (v0.3.0): fixed AttributeError in match_dialog.py where PhotoItem.date_taken was accessed but doesn't exist; changed to extract date from exif_data['DateTimeOriginal'] or exif_data['CreateDate']; updated rematch_with_offset to adjust EXIF date strings directly instead of using non-existent date_taken attribute.
- 优化：前台 GPS 显示格式更简洁，去掉秒的小数部分（如 28°31'31"N 而不是 28°31'30.59"N）。
