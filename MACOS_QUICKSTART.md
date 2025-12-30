# macOS 快速开始

一键完成 macOS 安装包的构建和部署。

---

## ⚡ 5 分钟快速部署

### 在 macOS 上运行：

```bash
# 1. 构建 .app 和 .dmg
cd quant-agent
python build_macos.py
chmod +x create_dmg.sh
./create_dmg.sh

# 2. 复制到前端
cp installer/output/QuantAgent-0.1.0.dmg ../fastbull-demo/public/downloads/

# 3. 重新构建前端
cd ../fastbull-demo
npm run build

# 4. 部署 dist 目录
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
# 1. 打开 .app
open dist/quant-agent.app

# 2. 验证服务
curl http://127.0.0.1:17633/health

# 3. 测试 URL 协议
open quant-agent://launch

# 4. 测试 DMG
open installer/output/QuantAgent-0.1.0.dmg
# 拖拽到"应用程序"
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
- **架构**：x86_64 (Intel) 和 arm64 (Apple Silicon) 通用

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

### 1. macOS Gatekeeper

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

在部署前确保：

- [ ] 在 macOS 上运行 `python build_macos.py`
- [ ] `dist/quant-agent.app` 已生成
- [ ] 本地测试 .app 可以启动
- [ ] 运行 `./create_dmg.sh`
- [ ] `installer/output/QuantAgent-0.1.0.dmg` 已生成
- [ ] DMG 已复制到 `fastbull-demo/public/downloads/`
- [ ] 前端已重新构建
- [ ] `dist/downloads/QuantAgent-0.1.0.dmg` 存在
- [ ] 已部署到服务器
- [ ] 用户可以成功下载和安装

---

**现在你有了完整的 macOS 支持！** 🍎

Windows、macOS、Linux 三平台齐全！✨
