#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Architecture Design Document for DataPrism / DataPrism 架构设计文档
"""

"""
# DataPrism High-Efficiency Architecture / DataPrism 高效架构设计

## 1. Async/Multi-threading Pattern / 异步与多线程模式

### Problem / 问题
- ExifTool operations are time-consuming (large files, slow storage) / ExifTool 读写操作耗时。
- Running it on the main thread freezes the UI / 如果在主线程执行，UI 会冻结。

### Solution: QThread + Signal/Slot / 解决方案
```
User clicks "Import" 
    ↓
Main thread (UI) → ExifToolWorker in separate thread
    ↓
Worker.progress → Main thread (update progress bar)
    ↓
UI responsive throughout / 全程响应
```

### Files / 实现文件
- `src/core/exif_worker.py` - Async ExifTool wrapper (异步 ExifTool 包装器)。

---

## 2. Model/View Architecture / 列表与数据架构

### Problem / 问题
- High memory usage and slow UI when handling thousands of photos / 处理海量照片时内存和显示性能堪忧。

### Solution: Qt Model / 解决方案
- Separate Data (Model) from Display (View) / 数据与显示分离。
- Use `QAbstractTableModel` for efficient storage / 使用高效的数据容器。

### Files / 实现文件
- `src/core/photo_model.py` - PhotoDataModel.

---

## 3. Caching & Lazy Loading / 缓存与延迟加载

### Problem / 问题
- Reading 1000 EXIF records at once is slow / 一次性读取 1000 条 EXIF 很慢。

### Solution: Lazy Loading / 解决方案
- Only load EXIF data when a row becomes visible / 只有当行进入视野时才触发读取。
- Results are cached to avoid redundant reads / 结果缓存，避免重复操作。

---

## 4. Command Pattern / 命令模式与撤销重做

### Problem / 问题
- Users expect consistent Undo/Redo capability / 用户需要撤销与重做编辑。

### Solution: Command Pattern / 解决方案
- Each edit is encapsulated as a Command object / 每一个操作都是一个独立的 Command 对象。
- `CommandHistory` maintains a stack of actions / 统一管理撤销/重做栈。

### Files / 实现文件
- `src/core/command_history.py`.

---

## 7. Performance Summary / 性能优化总结

| Strategy / 策略 | Issue / 问题 | Solution / 方案 | Result / 收益 |
| :--- | :--- | :--- | :--- |
| Async / 异步 | UI Freeze / 冻结 | QThread | Responsive UI / 响应式 |
| Model/View | RAM Crash / 内存溢出 | Qt Model | 1000+ Photos / 千张无压力 |
| Caching / 缓存 | Repeat IO / 重复读取 | Lazy Load / 延迟加载 | Instant Start / 极速启动 |
| Argfile (v1.1) | Startup Lag / 启动延迟 | Batching / 饱和写入 | 10x Speed / 10倍提速 |

---

## 10. Performance Roadmap / 性能优化提速路线图

### Current State (v1.0) - "Stability First" / 当前 1.0 版本：稳健优先
- **Pattern**: Asynchronous per-file command execution (异步单文件命令模式)。
- **Trade-off**: High process startup overhead on Windows (Windows 上进程启动开销大)。

### Future Optimization (v1.1+) - "Extreme Batching" / v1.1+：极速饱和模式

#### Phase A: Argfile Mode (The "Pro" Way) / 第一步：饱和指令集
- **Concept**: Instead of calling `exiftool` N times, generate a single `.args` file (将所有任务写入一个参数文件，仅启动一次 ExifTool)。
- **Target**: Reduce 36-frame roll processing time from 16s down to 1.5s (36 张照片处理耗时从 16s 降至 1.5s)。

#### Phase B: Process Persistence (`-stay_open`) / 第二步：进程常驻
- **Concept**: Use persistent Pipes for communication (通过管道保持 ExifTool 进程常驻内存)。

#### Phase C: Concurrent Sharding / 第三步：多核并发
- **Concept**: Spawn multiple instances based on CPU cores (根据 CPU 核心数进行分片并行处理)。

---

*This document serves as the technical mandate for DataPrism performance evolution.*
"""
