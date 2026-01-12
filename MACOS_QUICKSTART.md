# macOS 快速开始

一键完成 macOS 安装包的构建和部署。

---

## 📋 前置条件

### 1. 安装 Xcode Command Line Tools（必须！）

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

# 检查工具
which lipo
# 应输出: /usr/bin/lipo

xcrun --version
# 应输出版本号
```

**如果安装失败**，参考 [MACOS_TROUBLESHOOTING.md](MACOS_TROUBLESHOOTING.md)。

---

### 2. 准备 Python 环境

```bash
cd quant-agent

# 创建 conda 环境（如果还没有）
conda create -n quant-agent-env python=3.10 -y

# 激活环境
conda activate quant-agent-env

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

**重要**：确保终端提示符显示 `(quant-agent-env)`，而不是 `(base)`！

---

## ⚡ 快速部署

### 在 macOS 上运行：

```bash
# 0. 确保在正确的环境（重要！）
conda activate quant-agent-env

# 1. 构建 .app
cd quant-agent
python build_macos.py

# 2. 创建 .dmg 安装包
chmod +x create_dmg.sh
./create_dmg.sh

# 3. 复制到前端
cp installer/output/QuantAgent-0.1.0.dmg ../fastbull-demo/public/downloads/

# 4. 重新构建前端
cd ../fastbull-demo
npm run build

# 5. 部署 dist 目录
# ... 上传到服务器 ...

# 完成！
```

---

## 📦 输出文件

| 文件 | 路径 | 大小 | 说明 |
|------|------|------|------|
| **.app bundle** | `quant-agent/dist/quant-agent.app` | ~25 MB | macOS 应用（含 Python 环境） |
| **.dmg 镜像** | `quant-agent/installer/output/QuantAgent-0.1.0.dmg` | ~15 MB | 压缩的安装镜像 |
| **前端副本** | `fastbull-demo/public/downloads/QuantAgent-0.1.0.dmg` | ~15 MB | 供用户下载 |
| **构建产物** | `fastbull-demo/dist/downloads/QuantAgent-0.1.0.dmg` | ~15 MB | 部署到服务器 |

---

## ✨ 功能特性

### ✅ 完全独立
- 包含 Python 3.x 解释器
- 包含所有依赖（FastAPI、uvicorn 等）
- 用户无需安装任何环境

### ✅ URL 协议支持
- 注册 `quant-agent://` 协议
- 网页可以直接启动应用
- Info.plist 自动配置

### ✅ 用户友好
- .dmg 镜像包含拖拽安装界面
- 拖到"应用程序"即完成安装
- 符合 macOS 安装习惯

---

## 🧪 测试流程

### 本地测试

```bash
cd quant-agent

# 1. 验证架构
file dist/quant-agent.app/Contents/MacOS/quant-agent
# Intel Mac 应输出: Mach-O 64-bit executable x86_64
# Apple Silicon 应输出: Mach-O 64-bit executable arm64

# 2. 查看应用大小
du -sh dist/quant-agent.app

# 3. 双击启动应用（推荐）
# 在 Finder 中双击 dist/quant-agent.app

# 或使用命令行启动
open dist/quant-agent.app

# 4. 等待服务启动
sleep 5

# 5. 验证服务
curl http://127.0.0.1:17633/health
# 应返回: {"ok":true,"name":"quant-agent","version":"0.1.0"}

# 6. 测试 URL 协议
open quant-agent://launch

# 7. 测试 DMG 安装
open installer/output/QuantAgent-0.1.0.dmg
# 拖拽到"应用程序"文件夹

# 8. 从应用程序启动
open /Applications/quant-agent.app
sleep 5
curl http://127.0.0.1:17633/health
```

### 前端集成测试

```bash
# 1. 启动前端开发服务器
cd fastbull-demo
npm run dev

# 2. 访问 http://localhost:5173
# 3. 打开"量化"标签
# 4. 创建或打开一个策略文件
# 5. 点击"回测"按钮
# 6. 验证能正确检测和启动 Agent
```

---

## 📱 平台支持

### macOS 版本要求
- **最低版本**：macOS 10.13 (High Sierra)
- **推荐版本**：macOS 11.0+ (Big Sur)

### 架构支持（自动检测）

**构建脚本会自动检测系统架构**：

#### Intel Mac
```
系统架构: x86_64
检测到 Intel Mac (x86_64)
目标架构: x86_64
```
- ✅ 生成 x86_64 二进制
- ✅ 在 Intel Mac 上原生运行
- ✅ 在 Apple Silicon Mac 上通过 Rosetta 2 运行

#### Apple Silicon Mac
```
系统架构: arm64
检测到 Apple Silicon (M1/M2/M3)
目标架构: arm64
```
- ✅ 生成 arm64 二进制
- ✅ 在 Apple Silicon Mac 上原生运行
- ❌ 无法在 Intel Mac 上运行

**建议**：
- **如果只有 Intel Mac**：构建 x86_64 版本（兼容性更好）
- **如果只有 Apple Silicon**：构建 arm64 版本（性能更好）
- **如果需要通用版本**：使用 `lipo` 合并两种架构（参考 MACOS_TROUBLESHOOTING.md）

### 浏览器支持
- Safari 13+
- Chrome 80+
- Firefox 75+
- Edge 80+

---

## 🔧 自定义配置

### 修改版本号

**quant-agent/build_macos.py**:
```python
'CFBundleShortVersionString': '0.2.0',  # 修改这里
```

**quant-agent/create_dmg.sh**:
```bash
VERSION="0.2.0"  # 修改这里
```

### 修改 Bundle ID

**quant-agent/build_macos.py**:
```python
'CFBundleIdentifier': 'com.yourcompany.quantagent',  # 修改这里
```

### 修改显示名称

**quant-agent/build_macos.py**:
```python
'CFBundleDisplayName': 'Your App Name',  # 修改这里
```

---

## ⚠️ 注意事项

### 1. 必须在正确的 conda 环境中

**症状**：`ModuleNotFoundError: No module named 'PyInstaller'`

**原因**：在 `(base)` 环境而不是 `(quant-agent-env)` 环境中运行

**解决**：
```bash
# 检查当前环境（提示符应显示环境名）
# 错误: (base) steven@...
# 正确: (quant-agent-env) steven@...

# 切换环境
conda activate quant-agent-env

# 验证
which python
pip show pyinstaller
```

---

### 2. 必须安装 Xcode Command Line Tools

**症状**：
```
xcrun: error: invalid active developer path
lipo command failed with error code 1
```

**解决**：
```bash
# 重新安装
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install

# 验证
xcode-select -p
which lipo
xcrun --version
```

详细故障排除见 [MACOS_TROUBLESHOOTING.md](MACOS_TROUBLESHOOTING.md#问题-0缺少-xcode-command-line-tools最常见)

---

### 3. 清理缓存后重新构建

**如果构建失败或出现奇怪错误**：

```bash
cd quant-agent

# 彻底清理
rm -rf build dist *.spec

# 清理 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 重新构建
python build_macos.py
```

---

### 4. macOS Gatekeeper

用户首次打开时可能看到："无法打开，因为来自身份不明的开发者"

**用户解决方法**：
- 右键点击 → "打开" → 再次点击"打开"

**开发者解决方法**：
- 进行代码签名（需要 Apple Developer 账号）
- 见 `MACOS_BUILD_GUIDE.md` 的"代码签名"章节

### 2. 文件大小

- .app 约 25 MB（未压缩）
- .dmg 约 15 MB（压缩后）
- 比 Windows 版本稍大（macOS 的 Python 包更大）

### 3. 跨平台构建

**重要**：macOS 安装包必须在 macOS 上构建
- PyInstaller 生成的可执行文件是平台特定的
- Windows/Linux 上无法构建 .app 或 .dmg

如果你只有 Windows：
- 使用虚拟机（VMware/VirtualBox + macOS）
- 使用云服务（MacStadium、MacinCloud）
- 请有 Mac 的朋友帮忙构建

---

## 🚀 CI/CD 集成（可选）

### GitHub Actions 示例

```yaml
name: Build macOS

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd quant-agent
          pip install -r requirements.txt
          pip install pyinstaller
          brew install create-dmg

      - name: Build .app
        run: |
          cd quant-agent
          python build_macos.py

      - name: Create .dmg
        run: |
          cd quant-agent
          chmod +x create_dmg.sh
          ./create_dmg.sh

      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: QuantAgent-macOS
          path: quant-agent/installer/output/QuantAgent-*.dmg
```

---

## 📚 相关文档

- **详细指南**：[MACOS_BUILD_GUIDE.md](MACOS_BUILD_GUIDE.md)
- **代码签名**：[Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- **PyInstaller**：[macOS Bundles](https://pyinstaller.org/en/stable/usage.html#building-mac-os-x-app-bundles)
- **create-dmg**：[GitHub Repository](https://github.com/create-dmg/create-dmg)

---

## ✅ 检查清单

### 构建前检查

- [ ] 已安装 Xcode Command Line Tools（`xcode-select -p` 正常）
- [ ] 已激活 conda 环境（提示符显示 `(quant-agent-env)`）
- [ ] 已安装 PyInstaller（`pip show pyinstaller` 正常）
- [ ] 在正确的目录（`pwd` 显示 `.../quant-agent`）

### 构建后检查

- [ ] `dist/quant-agent.app` 已生成
- [ ] 架构正确（`file dist/quant-agent.app/Contents/MacOS/quant-agent`）
- [ ] 应用可以启动（双击或 `open dist/quant-agent.app`）
- [ ] 服务正常响应（`curl http://127.0.0.1:17633/health`）

### DMG 和部署检查

- [ ] `create_dmg.sh` 有执行权限（`chmod +x create_dmg.sh`）
- [ ] `installer/output/QuantAgent-0.1.0.dmg` 已生成
- [ ] DMG 已复制到 `fastbull-demo/public/downloads/`
- [ ] 前端已重新构建（`npm run build`）
- [ ] `dist/downloads/QuantAgent-0.1.0.dmg` 存在
- [ ] 已部署到服务器
- [ ] 用户可以成功下载和安装

---

**现在你有了完整的 macOS 支持！** 🍎

Windows、macOS、Linux 三平台齐全！✨
