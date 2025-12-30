# macOS 打包指南

本指南说明如何为 macOS 构建 Quant Agent 应用和安装镜像。

---

## 📋 前置要求

### 必需
- **macOS** 系统（推荐 macOS 10.13+）
- **Python 3.9+**
- **PyInstaller**：`pip install pyinstaller`

### 可选（用于创建更美观的 DMG）
- **create-dmg**：`brew install create-dmg`

---

## 🚀 快速开始

### 方法 1：一键构建（推荐）

```bash
cd quant-agent

# 1. 构建 .app bundle
python build_macos.py

# 2. 创建 .dmg 安装镜像
chmod +x create_dmg.sh
./create_dmg.sh

# 完成！
# 输出: installer/output/QuantAgent-0.1.0.dmg
```

### 方法 2：分步构建

#### 步骤 1：构建 .app bundle

```bash
python build_macos.py
```

**输出**：
- `dist/quant-agent.app` - 完整的 macOS 应用
- 大小：约 20-30 MB
- 包含：Python 解释器 + 所有依赖

#### 步骤 2：测试 .app

```bash
# 启动应用
open dist/quant-agent.app

# 检查是否运行
curl http://127.0.0.1:17633/health

# 测试 URL 协议
open quant-agent://launch
```

#### 步骤 3：创建 .dmg 镜像

```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

**输出**：
- `installer/output/QuantAgent-0.1.0.dmg`
- 大小：约 15-25 MB（压缩后）
- 用户友好的拖拽安装界面

---

## 📦 文件结构

构建完成后的文件结构：

```
quant-agent/
├── build_macos.py          # macOS 打包脚本
├── create_dmg.sh           # DMG 创建脚本
├── dist/
│   └── quant-agent.app/   # macOS 应用 bundle
│       ├── Contents/
│       │   ├── Info.plist      # 应用配置（含 URL 协议）
│       │   ├── MacOS/
│       │   │   └── quant-agent # 可执行文件
│       │   └── Resources/
│       │       └── ...         # 依赖库
└── installer/
    └── output/
        └── QuantAgent-0.1.0.dmg  # 安装镜像
```

---

## 🔧 配置说明

### Info.plist 配置

`build_macos.py` 自动创建 `Info.plist`，包含以下关键配置：

```xml
<!-- URL 协议注册 -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>Quant Agent Protocol</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>quant-agent</string>
        </array>
    </dict>
</array>

<!-- Bundle 标识符 -->
<key>CFBundleIdentifier</key>
<string>com.fastbull.quantagent</string>

<!-- 版本信息 -->
<key>CFBundleShortVersionString</key>
<string>0.1.0</string>
```

---

## 🎨 自定义 DMG 外观（可选）

如果安装了 `create-dmg`，可以自定义 DMG 外观：

### 1. 创建背景图片

```bash
# 创建 600x400 的背景图
installer/dmg_background.png
```

### 2. 修改 create_dmg.sh

取消注释背景相关的行：

```bash
# 创建自定义背景
mkdir -p "$TEMP_DMG/.background"
cp installer/dmg_background.png "$TEMP_DMG/.background/"
```

---

## 🔐 代码签名和公证（可选）

### 为什么需要签名？

- ✅ 用户打开时不会显示"未识别的开发者"警告
- ✅ 可以通过网络分发
- ✅ 提升用户信任度

### 前置要求

- **Apple Developer 账号**（99 美元/年）
- **Developer ID Application 证书**

### 签名步骤

```bash
# 1. 查看可用的证书
security find-identity -v -p codesigning

# 2. 签名 .app
codesign --force --deep --sign "Developer ID Application: Your Name (TEAM_ID)" \
    dist/quant-agent.app

# 3. 验证签名
codesign --verify --deep --strict --verbose=2 dist/quant-agent.app

# 4. 检查签名信息
codesign -dv --verbose=4 dist/quant-agent.app
```

### 公证步骤

```bash
# 1. 创建 DMG（已签名的 .app）
./create_dmg.sh

# 2. 提交公证
xcrun notarytool submit installer/output/QuantAgent-0.1.0.dmg \
    --apple-id "your@email.com" \
    --password "app-specific-password" \
    --team-id "TEAM_ID" \
    --wait

# 3. 装订公证票据
xcrun stapler staple installer/output/QuantAgent-0.1.0.dmg

# 4. 验证
spctl -a -t open --context context:primary-signature -v installer/output/QuantAgent-0.1.0.dmg
```

---

## 📥 部署流程

### 1. 准备文件

```bash
# 确保 DMG 已构建
ls -lh installer/output/QuantAgent-0.1.0.dmg
```

### 2. 复制到前端项目

```bash
# 从 quant-agent 目录
cp installer/output/QuantAgent-0.1.0.dmg ../fastbull-demo/public/downloads/

# 验证
cd ../fastbull-demo
ls -lh public/downloads/QuantAgent-0.1.0.dmg
```

### 3. 更新前端下载链接

编辑 `fastbull-demo/src/services/QuantAgentService.ts`：

```typescript
const downloadUrls = {
  'windows': '/downloads/QuantAgentSetup-0.1.0.exe',
  'mac': '/downloads/QuantAgent-0.1.0.dmg',  // ← 添加这行
  'linux': '/downloads/quant-agent-0.1.0-linux.tar.gz'
};
```

### 4. 重新构建前端

```bash
cd fastbull-demo
npm run build

# 验证 DMG 已打包到 dist
ls -lh dist/downloads/QuantAgent-0.1.0.dmg
```

### 5. 部署

```bash
# 上传整个 dist 目录到服务器
# 用户即可从网站下载：
# http://your-domain.com/downloads/QuantAgent-0.1.0.dmg
```

---

## 🧪 测试流程

### 本地测试

```bash
# 1. 打开 DMG
open installer/output/QuantAgent-0.1.0.dmg

# 2. 拖拽到"应用程序"文件夹

# 3. 从启动台或命令行启动
open /Applications/quant-agent.app

# 4. 验证服务运行
curl http://127.0.0.1:17633/health
# 应返回: {"status":"ok"}

# 5. 测试 URL 协议
open quant-agent://launch
# 应启动应用（如果未运行）
```

### 用户安装测试

```bash
# 1. 模拟用户下载
curl -O http://your-domain.com/downloads/QuantAgent-0.1.0.dmg

# 2. 打开 DMG
open QuantAgent-0.1.0.dmg

# 3. 按照界面提示安装

# 4. 测试网页启动
# 在浏览器中访问你的网站，点击"回测"按钮
# 应能正确检测和启动 Agent
```

---

## ⚠️ 常见问题

### 问题 1：打包失败

**错误**：`ModuleNotFoundError: No module named 'PyInstaller'`

**解决**：
```bash
pip install pyinstaller
```

### 问题 2："无法打开应用，因为它来自身份不明的开发者"

**解决方法 1**（临时）：
```bash
# 右键点击应用 → 选择"打开" → 点击"打开"
```

**解决方法 2**（永久）：
```bash
# 移除隔离标志
xattr -dr com.apple.quarantine /Applications/quant-agent.app
```

**解决方法 3**（最佳）：
- 进行代码签名和公证（见上文）

### 问题 3：URL 协议不工作

**检查步骤**：

```bash
# 1. 验证 Info.plist
cat dist/quant-agent.app/Contents/Info.plist | grep -A 5 CFBundleURLTypes

# 2. 重新注册协议
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -R -f -all local,system,user /Applications/quant-agent.app

# 3. 测试
open quant-agent://launch
```

### 问题 4：DMG 创建失败

**错误**：`command not found: create-dmg`

**解决**：
```bash
# 安装 create-dmg
brew install create-dmg

# 或使用 hdiutil（macOS 自带）
# create_dmg.sh 会自动回退到 hdiutil
```

### 问题 5：在 Windows/Linux 上打包

**问题**：PyInstaller 打包的应用只能在相同操作系统上运行

**解决**：
- 在 macOS 上运行 `build_macos.py`
- 在 Windows 上运行 `build.py`
- 在 Linux 上运行对应的 Linux 打包脚本（待创建）

---

## 🔄 版本更新流程

### 更新到 0.2.0

1. **修改版本号**：

```python
# build_macos.py
VERSION = "0.2.0"

# create_dmg.sh
VERSION="0.2.0"
```

2. **重新构建**：

```bash
python build_macos.py
./create_dmg.sh
```

3. **更新前端**：

```typescript
// QuantAgentService.ts
'mac': '/downloads/QuantAgent-0.2.0.dmg'
```

4. **部署新版本**

---

## 📚 相关文档

- [macOS Code Signing](https://developer.apple.com/support/code-signing/)
- [Notarizing macOS Software](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [PyInstaller macOS](https://pyinstaller.org/en/stable/usage.html#building-mac-os-x-app-bundles)
- [create-dmg](https://github.com/create-dmg/create-dmg)

---

## 📝 检查清单

- [ ] macOS 系统环境已准备
- [ ] Python 和 PyInstaller 已安装
- [ ] 运行 `python build_macos.py` 成功
- [ ] `dist/quant-agent.app` 已生成
- [ ] 本地测试 .app 可以启动
- [ ] 运行 `./create_dmg.sh` 成功
- [ ] `installer/output/QuantAgent-0.1.0.dmg` 已生成
- [ ] DMG 已复制到前端 `public/downloads/`
- [ ] 前端 `QuantAgentService.ts` 已更新下载链接
- [ ] 前端已重新构建 (`npm run build`)
- [ ] `dist/downloads/QuantAgent-0.1.0.dmg` 存在
- [ ] dist 目录已部署到服务器
- [ ] 用户可以成功下载和安装

---

**完成！现在你有了一个专业的 macOS 安装包！** 🍎
