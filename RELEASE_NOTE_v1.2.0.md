# DataPrism v1.2.0 Release Note / 发布说明

## 🚀 The "Portability" Update / 极致便携版

DataPrism v1.2.0 focuses on delivering a true "zero-dependency" experience. You can now run the tool immediately on any Windows machine without worrying about external dependencies.

v1.2.0 版本专注于打造真正的“零依赖”体验。现在，您可以在任何 Windows 设备上立即运行该工具，无需再为外部依赖项担忧。

---

### 🌟 Key Highlights / 核心亮点

#### 📦 Zero-Dependency ExifTool / 内置 ExifTool 引擎
- **Chinese**: 我们已将强大的 ExifTool 引擎直接整合进 DataPrism 内部。这意味着您不再需要手动安装 ExifTool 或在设置中手动配置路径。
- **English**: We've bundled the powerful ExifTool engine directly into DataPrism. No more manual installation or path configuration required.

#### 🎮 Batteries-Included Portability / 开箱即用的便携性
- **Chinese**: 增强了智能路径溯源逻辑。无论您是从源码运行还是直接分发打包好的 EXE，程序都能自动精准识别并调用内置引擎，真正实现“随拷随用”。
- **English**: Enhanced smart path resolution logic. Whether running from source or distributing the packaged EXE, the app automatically detects and utilizes the internal engine.

#### 🧹 Cleaner Repository & Workflows / 仓库与工作流优化
- **Chinese**: 优化了 Git 追踪规则，确保核心二进制文件被正确版本化，同时隔离了运行时产生的本地日志，保持工作区整洁。
- **English**: Refined Git tracking rules to ensure core binaries are versioned correctly while isolating runtime logs to maintain a clean workspace.

#### 💎 Versioned Deliverables / 规范化交付
- **Chinese**: 现在生成的安装包文件名将自动携带版本号（如 `DataPrism_v1.2.0.exe`），方便版本管理。
- **English**: Generated executables now automatically include the version number in the filename for better version control.

---

### 🛠️ Technical Details / 技术细节
- **Internal Version**: 1.2.0
- **Base Engine**: ExifTool 13.x (Bundled)
- **Compatibility**: Windows 10/11 (64-bit)

### 📥 Download / 下载
Check the `dist/` folder for the latest **`DataPrism_v1.2.0.exe`**.

请查看 `dist/` 目录获取最新的 **`DataPrism_v1.2.0.exe`**。
