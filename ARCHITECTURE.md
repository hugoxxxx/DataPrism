#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Architecture Design Document for DataPrism
DataPrism 的架构设计文档
"""

"""
# DataPrism 高效架构设计

## 1. 异步/多线程模式（Async Pattern）

### 问题
- ExifTool 读写操作可能耗时（大图片、网络存储）
- 如果在主线程执行，UI 会冻结，用户体验差

### 解决方案：QThread + Signal/Slot
```
User clicks "Import" 
    ↓
Main thread (UI) → ExifToolWorker in separate thread
    ↓
Worker.progress → Main thread (update progress bar)
Worker.result_ready → Main thread (update model)
    ↓
UI responsive throughout
```

### 实现文件
- `src/core/exif_worker.py` - 异步 ExifTool 包装器

### 使用示例
```python
from PySide6.QtCore import QThread
from src.core.exif_worker import ExifToolWorker

worker = ExifToolWorker()
thread = QThread()
worker.moveToThread(thread)

# Connect signals
worker.progress.connect(update_progress_bar)
worker.result_ready.connect(on_exif_loaded)
worker.error_occurred.connect(on_error)

thread.started.connect(lambda: worker.read_exif(file_paths))
worker.finished.connect(thread.quit)

thread.start()
```

---

## 2. Model/View 架构（Qt Model/View Pattern）

### 问题
- 处理数百/数千张照片时，直接创建 UI 控件很低效
- 数据变化时无法高效更新 UI

### 解决方案：Qt Model
- Model（数据层）和 View（显示层）分离
- 使用 QAbstractTableModel 作为数据容器
- View 自动与 Model 保持同步

### 实现文件
- `src/core/photo_model.py` - PhotoDataModel

### 优势
- 自动支持排序、过滤
- 内存高效（只显示可见行）
- 支持虚拟滚动

---

## 3. 缓存与延迟加载（Caching & Lazy Loading）

### 问题
- 加载 1000 张照片的 EXIF 数据会很慢
- 用户可能只查看其中几张

### 解决方案：Lazy Loading
- 初始化时只记录文件路径
- 用户滚动到某行时，才加载该行的 EXIF 数据
- 加载结果缓存，避免重复读取

### 流程
```
User imports 1000 photos
    ↓
PhotoDataModel 记录 1000 个文件路径（快速）
    ↓
User scrolls to row 500
    ↓
Model.data() 被调用 → 发现 exif_data 为 None
    ↓
Trigger async EXIF load for row 500
    ↓
ExifToolWorker 在后台读取 → result_ready signal
    ↓
Model.set_exif_data() 更新缓存
    ↓
View 自动刷新该行
```

### 实现
- `PhotoModel.data()` 中实现延迟加载逻辑
- `ExifToolWorker` 负责后台加载

---

## 4. 命令模式与撤销/重做（Command Pattern & Undo/Redo）

### 问题
- 用户需要撤销/重做编辑
- 批量修改后无法追踪变化

### 解决方案：Command Pattern
- 每个操作（修改元数据）都是一个 Command
- Command 知道如何执行（execute）和撤销（undo）
- CommandHistory 维护两个栈：undo_stack 和 redo_stack

### 流程
```
User 修改 Camera 信息
    ↓
创建 ModifyMetadataCommand(old_data, new_data)
    ↓
CommandHistory.execute(command)
    ↓
command.execute() → Model 更新
command 入栈到 undo_stack
    ↓
User 按 Ctrl+Z
    ↓
CommandHistory.undo()
    ↓
command.undo() → Model 恢复旧数据
command 移出到 redo_stack
```

### 实现文件
- `src/core/command_history.py` - Command 基类和 CommandHistory

### 优势
- 完整的撤销/重做历史
- 易于实现批量操作（组合命令）
- 便于添加"Undo All Changes"等功能

---

## 5. 依赖注入与服务定位（Dependency Injection & Service Locator）

### 问题
- 各模块之间紧耦合
- 难以测试（无法 mock 依赖）
- 全局变量污染命名空间

### 解决方案：AppContext（Service Locator）
- 统一的服务注册和获取点
- 各模块通过 AppContext 获取其他服务
- 降低耦合度，便于测试

### 使用流程
```python
# 初始化时注册服务
AppContext.register("photo_model", PhotoDataModel())
AppContext.register("command_history", CommandHistory())

# 需要时获取服务
photo_model = AppContext.get("photo_model")
history = AppContext.get("command_history")

# 测试时可以注入 mock
AppContext.register("photo_model", MockPhotoModel())
```

### 实现文件
- `src/core/app_context.py` - AppContext 单例

---

## 6. 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    MainWindow (UI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  左侧栏      │  │  中央列表    │  │  右侧检查器  │      │
│  │ (Filters)   │  │ (PhotoView)  │  │ (Inspector)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                 │               │
│         └──────────────────┼─────────────────┘               │
│                            ↓                                 │
│                    ┌────────────────┐                        │
│                    │  AppContext    │ ← 服务定位器          │
│                    │  (Singleton)   │                        │
│                    └────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
         ┌───────────────────┼───────────────────┐
         ↓                   ↓                   ↓
    ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
    │ PhotoModel  │  │ CommandHist. │  │ExifTool Worker│
    │(Data Layer) │  │ (Undo/Redo)  │  │(Async Thread) │
    │             │  │              │  │              │
    │ - Cache     │  │ - Execute    │  │ - Read EXIF  │
    │ - Lazy load │  │ - Undo       │  │ - Write EXIF │
    │             │  │ - Redo       │  │              │
    └─────────────┘  └──────────────┘  └──────────────┘
         ↓                                      ↓
    ┌─────────────┐                   ┌──────────────┐
    │  SQLite DB  │                   │  exiftool    │
    │(Optional)   │                   │  executable  │
    └─────────────┘                   └──────────────┘
```

---

## 7. 性能优化总结

| 优化策略 | 问题 | 方案 | 收益 |
|---------|------|------|------|
| 异步处理 | UI 冻结 | QThread + Worker | 响应式 UI |
| Model/View | 内存溢出 | Qt Model | 1000+ 照片无压力 |
| 缓存 | 重复计算 | 延迟加载 + 缓存 | 快速启动 |
| 批量操作 | 逐个编辑慢 | 命令模式 | 支持批量 |
| 撤销/重做 | 无法追踪变化 | CommandHistory | 完整历史 |
| 松耦合 | 代码僵化 | AppContext | 易于维护和测试 |

---

## 8. 后续开发步骤

1. **Phase 1 - 基础框架** ✓ (已完成)
   - PySide6 窗口
   - 异步 ExifTool 工作线程
   - PhotoDataModel + 缓存

2. **Phase 2 - 功能集成**
   - 拖拽导入（drag & drop）
   - EXIF 编辑器界面
   - 命令模式集成

3. **Phase 3 - 高级功能**
   - JSON 匹配算法（Lightme/Logbook）
   - 预设系统
   - 批量编辑

4. **Phase 4 - 优化**
   - 性能测试
   - 内存优化
   - 可选的数据库后端（SQLite）

---

## 10. Performance Roadmap (提速路线图)

Based on developer discussion and community feedback (e.g., Reddit "Over-scripting" concern), the following performance optimization plan is established for future versions.

### Current State (v1.0) - "Stability First"
- **Pattern**: Asynchronous per-file command execution.
- **Why**: High robustness, simple error handling, and sufficient for small batches (36-72 frames). 
- **Trade-off**: High process startup overhead on Windows (~200ms per file).

### Future Optimization (v1.1+) - "Extreme Batching"

#### Phase A: Argfile Mode (The "Pro" Way)
- **Concept**: Instead of calling `exiftool` N times, generate a temporary `.args` file containing all tasks.
- **Execution**: `exiftool -@ temp.args`.
- **Target**: Reduce 100-file processing time from 30s to <2s.

#### Phase B: Process Persistence (`-stay_open`)
- **Concept**: Keep a single ExifTool instance running in the background via Pipes.
- **Reliability**: Implement a "watchdog" mechanism to restart the process immediately if it crashes on a corrupt file.

#### Phase C: Concurrent Sharding
- **Concept**: Spawning multiple ExifTool instances based on CPU cores (e.g., 4 instances for 400 photos).
- **Target**: Maximize CPU/IO utilization across all hardware threads.

---

*This document serves as the technical mandate for future performance sprints.*
"""
