# Windows 安装包构建指南

## 📦 概述

为了让用户能够从云端部署的网站启动本地 Quant Agent，我们需要创建一个 Windows 安装程序。这个安装程序会：

1. ✅ 安装 `quant-agent.exe` 到 `C:\Program Files\Quant Agent\`
2. ✅ **注册 `quant-agent://` URL 协议**（关键功能）
3. ✅ 创建开始菜单快捷方式
4. ✅ 可选：添加桌面快捷方式
5. ✅ 可选：设置开机自动启动

## 🔧 准备工作

### 1. 下载并安装 Inno Setup

Inno Setup 是一个免费的 Windows 安装程序制作工具。

**下载地址**: https://jrsoftware.org/isdl.php

**安装步骤**:
1. 下载 `innosetup-6.x.x.exe`（选择最新稳定版）
2. 双击运行安装程序
3. 默认安装即可（会安装到 `C:\Program Files (x86)\Inno Setup 6\`）
4. 安装完成后，Inno Setup 编译器 `iscc.exe` 会被添加到系统路径

### 2. 确认已构建 quant-agent.exe

```bash
cd D:\code\quant-project\quant-agent
python build.py
```

这会在 `dist\installer\` 目录生成 `quant-agent.exe`（约 93.7 MB）

## 🚀 构建安装程序

### 方法一：使用 Inno Setup GUI（推荐初次使用）

1. 打开 Inno Setup Compiler（从开始菜单启动）
2. 点击菜单 `File` → `Open`
3. 选择 `D:\code\quant-project\quant-agent\quant-agent.iss`
4. 点击菜单 `Build` → `Compile`（或按 F9）
5. 等待编译完成（约 10-30 秒）
6. 安装程序会生成在 `dist\installer\QuantAgentSetup-0.1.0.exe`

### 方法二：使用命令行

```bash
cd D:\code\quant-project\quant-agent

# 使用 Inno Setup 编译器
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" quant-agent.iss
```

或者运行我提供的批处理脚本：

```bash
python build_installer.py
```

## 📋 生成的文件

构建成功后，你会得到：

```
dist\installer\
├── quant-agent.exe                    # 主程序（93.7 MB）
└── QuantAgentSetup-0.1.0.exe          # 安装程序（约 95 MB）
```

## 🧪 测试安装程序

### 1. 安装测试

```bash
# 双击运行安装程序
dist\installer\QuantAgentSetup-0.1.0.exe
```

安装过程：
- 选择安装目录（默认 `C:\Program Files\Quant Agent\`）
- 选择是否创建桌面图标
- 选择是否开机自动启动
- 点击"安装"

### 2. 验证 URL 协议注册

打开 Windows Registry Editor 验证：

```
HKEY_CLASSES_ROOT\quant-agent
├── (默认) = "URL:Quant Agent Protocol"
├── URL Protocol = ""
└── shell\open\command
    └── (默认) = "C:\Program Files\Quant Agent\quant-agent.exe" "%1"
```

或者直接测试：

**方法 A - 在浏览器地址栏输入**:
```
quant-agent://launch
```
应该会弹出 Windows 安全对话框，询问是否允许启动应用。

**方法 B - 在命令行测试**:
```cmd
start quant-agent://launch
```

**方法 C - 从你的网站测试**:
1. 打开浏览器访问你的云端网站
2. 打开浏览器控制台（F12）
3. 在 Console 中输入：
   ```javascript
   window.location.href = "quant-agent://launch"
   ```
4. 应该会弹出对话框询问是否启动 Quant Agent

### 3. 验证 HTTP 服务

安装并启动 Quant Agent 后：

```bash
# 访问健康检查接口
curl http://127.0.0.1:17633/health

# 期望返回：
# {"ok":true,"name":"quant-agent","version":"0.1.0"}
```

或在浏览器访问: http://127.0.0.1:17633/health

## 🌐 部署到网站

### 1. 上传安装程序

将生成的 `QuantAgentSetup-0.1.0.exe` 上传到你的网站服务器，例如：

```
https://your-domain.com/downloads/QuantAgentSetup-0.1.0.exe
```

### 2. 更新前端下载链接

在 `fastbull-demo/src/services/QuantAgentService.ts` 中更新：

```typescript
getDownloadUrl(): string {
  const platform = this.detectPlatform();

  const downloadUrls = {
    'windows': 'https://your-domain.com/downloads/QuantAgentSetup-0.1.0.exe',  // 更新这里
    'mac': 'https://your-domain.com/downloads/QuantAgent-0.1.0.dmg',
    'linux': 'https://your-domain.com/downloads/quant-agent-0.1.0-linux.tar.gz'
  };

  return downloadUrls[platform];
}
```

### 3. 用户使用流程

当用户首次访问你的云端网站时：

```
用户访问网站
    ↓
点击"回测"按钮
    ↓
前端检测 Agent 状态（访问 http://127.0.0.1:17633/health）
    ↓
如果未安装 → 显示"下载安装 Quant Agent"对话框
    ↓
用户点击"立即下载" → 下载 QuantAgentSetup-0.1.0.exe
    ↓
用户运行安装程序 → 安装并启动 Agent
    ↓
用户刷新网页 → 点击"回测"
    ↓
前端检测到 Agent 正在运行 → 发送回测任务
    ↓
或者 Agent 未运行但已安装 → window.location.href = "quant-agent://launch"
    ↓
Windows 自动启动 Quant Agent
    ↓
前端重新检测 → Agent 已就绪 → 发送回测任务 ✓
```

## 🛠️ 自定义配置

### 修改安装目录

编辑 `quant-agent.iss`:

```ini
; 默认安装到 Program Files
DefaultDirName={autopf}\{#MyAppName}

; 或者安装到用户目录（不需要管理员权限，但无法注册全局URL协议）
DefaultDirName={userpf}\{#MyAppName}
```

### 修改公司信息

```ini
#define MyAppPublisher "YourCompany"
#define MyAppURL "https://your-domain.com"
```

### 添加图标

如果你有 `.ico` 图标文件：

1. 将图标文件命名为 `icon.ico` 并放在项目根目录
2. 在 `quant-agent.iss` 中取消注释：

```ini
SetupIconFile=icon.ico
```

## ❓ 常见问题

### Q1: 安装时提示"需要管理员权限"

**原因**: 注册 URL 协议需要修改 `HKEY_CLASSES_ROOT`，需要管理员权限。

**解决**: 右键点击安装程序 → "以管理员身份运行"

### Q2: 安装后 URL 协议不工作

**诊断步骤**:

1. 检查注册表：
   ```cmd
   reg query HKEY_CLASSES_ROOT\quant-agent /s
   ```

2. 如果不存在，手动重新安装

3. 重建浏览器缓存（Chrome）：
   - 在地址栏输入 `chrome://restart`

4. 重启电脑（最后的手段）

### Q3: 防火墙阻止 Agent

安装程序不会自动配置防火墙。如果遇到阻止：

```cmd
# 添加防火墙规则（以管理员身份运行）
netsh advfirewall firewall add rule name="Quant Agent" dir=in action=allow program="C:\Program Files\Quant Agent\quant-agent.exe" enable=yes
```

### Q4: 如何卸载

**方法 1**: 从开始菜单
- 开始菜单 → Quant Agent → Uninstall Quant Agent

**方法 2**: 从控制面板
- 控制面板 → 程序和功能 → Quant Agent → 卸载

**方法 3**: 从设置
- Windows 设置 → 应用 → 应用和功能 → Quant Agent → 卸载

卸载时会自动：
- 删除所有已安装文件
- 删除注册表项（URL 协议）
- 删除开始菜单快捷方式

## 📝 下一步

1. **测试完整流程**:
   - 在一台干净的 Windows 机器上安装
   - 访问云端网站
   - 点击回测按钮
   - 验证能否正常启动 Agent

2. **准备发布**:
   - 代码签名（可选，需要证书）
   - 创建用户文档
   - 准备技术支持

3. **持续集成**:
   - 将构建过程集成到 CI/CD
   - 自动化版本号管理
   - 自动上传到服务器

## 🔐 代码签名（可选，推荐）

未签名的安装程序会被 Windows SmartScreen 警告。如果你有代码签名证书：

```bash
# 使用 SignTool 签名
"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe" sign /f your-certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\installer\QuantAgentSetup-0.1.0.exe
```

证书获取：
- 从 DigiCert、Sectigo 等 CA 购买（约 $100-500/年）
- 或申请免费的 Let's Encrypt 代码签名证书（限制较多）

---

**完成以上步骤后，你的用户就可以从云端网站一键启动本地 Quant Agent 了！** 🎉
