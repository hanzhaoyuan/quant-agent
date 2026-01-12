# macOS 打包问题修复

## ✅ 已修复：Apple Silicon (M1/M2) 架构问题

### 问题描述

在 Apple Silicon Mac 上运行 `build_macos.py` 时出现错误：

```
SystemError: lipo command (['lipo', '-thin', 'x86_64', ...]) failed with error code 1!
```

### 原因

PyInstaller 默认尝试创建 x86_64 二进制，但在 ARM64 Mac 上会失败。

### 解决方案

`build_macos.py` 现在会**自动检测系统架构**并使用正确的目标架构：

- **Apple Silicon** (M1/M2/M3): 使用 `arm64`
- **Intel Mac**: 使用 `x86_64`

---

## 🚀 使用方法

### 在 Apple Silicon Mac 上

```bash
cd quant-agent
python build_macos.py
```

**输出**：
```
系统架构: arm64
检测到 Apple Silicon (M1/M2/M3)
目标架构: arm64
...
✅ 支持 Apple Silicon (M1/M2/M3) Mac
```

### 在 Intel Mac 上

```bash
cd quant-agent
python build_macos.py
```

**输出**：
```
系统架构: x86_64
检测到 Intel Mac (x86_64)
目标架构: x86_64
...
✅ 支持 Intel (x86_64) Mac
```

---

## 📦 构建通用二进制（Universal Binary）

如果你想创建同时支持 Intel 和 Apple Silicon 的通用二进制：

### 方法 1：使用 lipo 合并（推荐）

```bash
# 1. 在 Intel Mac 上构建 x86_64 版本
python build_macos.py
mv dist/quant-agent.app dist/quant-agent-x86_64.app

# 2. 在 Apple Silicon Mac 上构建 arm64 版本
python build_macos.py
mv dist/quant-agent.app dist/quant-agent-arm64.app

# 3. 使用 lipo 合并二进制
mkdir -p dist/quant-agent.app/Contents/MacOS
lipo -create \
  dist/quant-agent-x86_64.app/Contents/MacOS/quant-agent \
  dist/quant-agent-arm64.app/Contents/MacOS/quant-agent \
  -output dist/quant-agent.app/Contents/MacOS/quant-agent

# 4. 复制其他文件（使用任一版本）
cp -R dist/quant-agent-arm64.app/Contents/Resources dist/quant-agent.app/Contents/
cp dist/quant-agent-arm64.app/Contents/Info.plist dist/quant-agent.app/Contents/

# 5. 验证
file dist/quant-agent.app/Contents/MacOS/quant-agent
# 应显示: Mach-O universal binary with 2 architectures
```

### 方法 2：修改脚本使用 universal2

编辑 `build_macos.py`，在第 161 行修改：

```python
# 目标架构（关键！）
'--target-architecture', 'universal2',  # 通用二进制
```

**注意**：这需要在 Apple Silicon Mac 上运行，并且可能需要安装 Rosetta 2。

---

## ⚠️ 其他常见问题

### 问题 0：缺少 Xcode Command Line Tools（最常见！）

**症状**：
```
xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools)
missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
```

或者：
```
SystemError: lipo command (['lipo', '-thin', 'x86_64', ...]) failed with error code 1!
```

**原因**：macOS 缺少 Apple 开发工具，`lipo` 命令是 Command Line Tools 的一部分。

**解决方法**：

```bash
# 安装 Command Line Tools
xcode-select --install
```

会弹出安装对话框，点击"安装"并等待完成（约 5-10 分钟）。

**验证安装**：
```bash
# 检查路径
xcode-select -p
# 应输出: /Library/Developer/CommandLineTools

# 检查 lipo 命令
which lipo
# 应输出: /usr/bin/lipo

# 测试 lipo
lipo -info /bin/ls
# 应输出: Architectures in the fat file: /bin/ls are: x86_64 arm64e
```

安装完成后重新运行：
```bash
python build_macos.py
```

---

### 问题 1：ModuleNotFoundError: No module named 'PyInstaller'

**症状**：
```
ModuleNotFoundError: No module named 'PyInstaller'
```

**原因**：
1. **在错误的 conda 环境中运行**（`(base)` 而不是 `(quant-agent-env)`）⚠️ 最常见
2. 或者没有安装 PyInstaller

**解决方法**：

#### 情况 1：环境错误（最常见！）

检查终端提示符：
```bash
# ❌ 错误示例（在 base 环境）
(base) steven@StevendeMacBook-Pro quant-agent %

# ✅ 正确示例（在 quant-agent-env 环境）
(quant-agent-env) steven@StevendeMacBook-Pro quant-agent %
```

**解决**：
```bash
# 切换到正确的环境
conda activate quant-agent-env

# 验证环境
which python
# 应输出: /opt/miniconda3/envs/quant-agent-env/bin/python

# 验证 PyInstaller 已安装
pip show pyinstaller
```

#### 情况 2：未安装 PyInstaller

```bash
# 在正确的环境中安装
conda activate quant-agent-env
pip install pyinstaller
```

---

### 问题 2：打包后应用无法启动

**检查日志**：
```bash
# 查看系统日志
log stream --predicate 'process == "quant-agent"' --level debug
```

**或使用 Console.app**（应用程序 → 实用工具 → 控制台）

### 问题 3：应用启动但端口未监听

**调试模式构建**：

修改 `build_macos.py` 第 117 行：
```python
'--console',  # 显示终端窗口，可以看到日志
```

然后重新构建：
```bash
python build_macos.py
open dist/quant-agent.app
```

### 问题 4：应用体积太大

**原因**：包含了完整的 Python 环境和所有依赖

**解决**：
1. 使用虚拟环境减少依赖
2. 排除不必要的模块

编辑 `build_macos.py`，添加：
```python
'--exclude-module=matplotlib',
'--exclude-module=numpy',
# ... 其他不需要的模块
```

---

## 📋 架构兼容性

| Mac 类型 | 架构 | 可以运行 arm64 | 可以运行 x86_64 |
|---------|------|---------------|----------------|
| **Apple Silicon** (M1/M2/M3) | arm64 | ✅ 原生 | ✅ Rosetta 2 |
| **Intel** | x86_64 | ❌ 不支持 | ✅ 原生 |

### 建议

- **大多数情况**：只构建目标用户的架构即可
- **通用应用**：使用 lipo 合并两种架构
- **文件大小优先**：只提供单一架构（用户群体明确时）

---

## 🧪 验证构建

### 检查架构

```bash
# 查看应用包含的架构
file dist/quant-agent.app/Contents/MacOS/quant-agent

# 单架构输出示例：
# Mach-O 64-bit executable arm64

# 通用二进制输出示例：
# Mach-O universal binary with 2 architectures: [x86_64:Mach-O 64-bit executable x86_64] [arm64]
```

### 测试运行

```bash
# 启动应用
open dist/quant-agent.app

# 等待几秒

# 验证服务
curl http://127.0.0.1:17633/health

# 应返回：
# {"ok":true,"name":"quant-agent","version":"0.1.0"}
```

### 测试 URL 协议

```bash
# 测试 URL 协议
open quant-agent://launch
```

---

## 🔄 清理和重试

如果遇到问题，尝试完全清理后重新构建：

```bash
cd quant-agent

# 1. 删除所有构建产物
rm -rf build dist *.spec

# 2. 清理 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 3. 重新安装 PyInstaller（可选）
pip uninstall pyinstaller -y
pip install pyinstaller

# 4. 重新构建
python build_macos.py
```

---

## 📞 仍然有问题？

如果上述方法都无法解决，请提供以下信息：

1. **系统信息**：
   ```bash
   sw_vers
   uname -m
   python --version
   pip show pyinstaller
   ```

2. **完整错误日志**：
   ```bash
   python build_macos.py 2>&1 | tee build.log
   ```

3. **Python 环境**：
   ```bash
   pip list
   ```

---

**问题已修复！现在可以在 Apple Silicon 和 Intel Mac 上正常构建了！** 🎉
