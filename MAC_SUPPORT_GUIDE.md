# Mac 平台支持指南

本指南说明如何在 Mac 上实现类似 Windows 的自定义协议唤起功能，让 Web 前端可以通过 `quant-agent://launch` 启动本地应用。

## 一、技术方案对比

### Windows 实现方式
- 使用 PyInstaller 打包成 `.exe`
- 使用 Inno Setup 创建安装程序
- 通过注册表注册 URL Protocol
- 安装包：`.exe` 安装程序

### Mac 实现方式
- 使用 PyInstaller 打包成 `.app` bundle
- 在 `Info.plist` 中注册 URL Scheme
- 创建 `.dmg` 或 `.pkg` 安装包
- 支持拖拽安装

## 二、实现步骤

### 步骤 1：修改 PyInstaller 配置

创建 Mac 专用的 spec 文件 `quant-agent-mac.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'agent', 'agent.main', 'agent.api', 'agent.api.health',
    'agent.core', 'agent.core.config', 'agent.utils', 'agent.utils.logger',
    'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl', 'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto', 'uvicorn.protocols.websockets.wsproto',
    'uvicorn.protocols.websockets.wsproto_impl', 'uvicorn.lifespan',
    'uvicorn.lifespan.on', 'fastapi', 'pydantic', 'pydantic_settings',
    'starlette', 'starlette.responses', 'starlette.routing'
]

tmp_ret = collect_all('uvicorn')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['agent/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='quant-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Mac上通常设为False，隐藏终端窗口
    disable_windowed_traceback=False,
    argv_emulation=False,  # Mac上设为False
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='quant-agent',
)

app = BUNDLE(
    coll,
    name='QuantAgent.app',
    icon=None,  # 可选：添加应用图标 'icon.icns'
    bundle_identifier='com.yourcompany.quantagent',
    info_plist={
        'CFBundleName': 'Quant Agent',
        'CFBundleDisplayName': 'Quant Agent',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',  # 设为False以显示在Dock
        'LSUIElement': 'False',  # 设为False以显示菜单栏
        # 注册 URL Scheme（关键！）
        'CFBundleURLTypes': [
            {
                'CFBundleURLName': 'Quant Agent Protocol',
                'CFBundleURLSchemes': ['quant-agent'],
            }
        ],
    },
)
```

### 步骤 2：处理 URL Scheme 事件

修改 `agent/main.py`，添加 Mac URL 处理：

```python
import sys
import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# ... 你的现有代码 ...

def start_server():
    """启动 FastAPI 服务器"""
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=17633,
        log_level="info"
    )

if __name__ == "__main__":
    # 检查是否是通过 URL Scheme 启动
    if len(sys.argv) > 1:
        url_arg = sys.argv[1]
        print(f"通过 URL Scheme 启动: {url_arg}")
        # 可以解析 URL 参数进行特殊处理
        # 例如: quant-agent://launch?action=backtest

    # 启动服务
    start_server()
```

### 步骤 3：构建 Mac 应用

在 Mac 上执行以下命令：

```bash
# 1. 安装 PyInstaller（如果未安装）
pip install pyinstaller

# 2. 构建应用
pyinstaller quant-agent-mac.spec

# 3. 应用会生成在 dist/QuantAgent.app
```

### 步骤 4：创建 DMG 安装包（推荐）

**方式一：使用 create-dmg（推荐）**

```bash
# 1. 安装 create-dmg
brew install create-dmg

# 2. 创建 DMG
create-dmg \
  --volname "Quant Agent" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "QuantAgent.app" 200 190 \
  --hide-extension "QuantAgent.app" \
  --app-drop-link 600 185 \
  "QuantAgent-0.1.0.dmg" \
  "dist/QuantAgent.app"
```

**方式二：手动创建 DMG**

```bash
# 1. 创建临时 DMG
hdiutil create -size 100m -fs HFS+ -volname "Quant Agent" temp.dmg

# 2. 挂载 DMG
hdiutil attach temp.dmg

# 3. 复制应用到 DMG
cp -R dist/QuantAgent.app "/Volumes/Quant Agent/"
ln -s /Applications "/Volumes/Quant Agent/Applications"

# 4. 卸载并转换为压缩格式
hdiutil detach "/Volumes/Quant Agent"
hdiutil convert temp.dmg -format UDZO -o QuantAgent-0.1.0.dmg
rm temp.dmg
```

### 步骤 5：测试 URL Scheme

安装应用后，在终端测试：

```bash
# 测试 URL Scheme 是否注册成功
open "quant-agent://launch"

# 或在浏览器地址栏输入
quant-agent://launch
```

## 三、跨平台构建脚本

创建 `build_mac.py` 自动化构建：

```python
#!/usr/bin/env python3
"""
Mac 平台构建脚本
自动化构建 .app 和 .dmg
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """执行命令并打印输出"""
    print(f"\n[执行] {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"命令执行失败: {cmd}")

    return result

def build_app():
    """构建 .app 应用"""
    print("\n=== 步骤 1: 构建 .app 应用 ===")

    # 清理旧的构建
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")

    # 运行 PyInstaller
    run_command("pyinstaller quant-agent-mac.spec")

    app_path = Path("dist/QuantAgent.app")
    if not app_path.exists():
        raise RuntimeError("应用构建失败")

    print(f"✓ 应用已生成: {app_path}")
    return app_path

def create_dmg(app_path):
    """创建 DMG 安装包"""
    print("\n=== 步骤 2: 创建 DMG 安装包 ===")

    dmg_name = "QuantAgent-0.1.0.dmg"

    # 检查是否安装了 create-dmg
    try:
        run_command("which create-dmg")
        has_create_dmg = True
    except:
        has_create_dmg = False
        print("⚠ 未安装 create-dmg，使用手动方式")

    if has_create_dmg:
        # 使用 create-dmg
        cmd = f"""
        create-dmg \
          --volname "Quant Agent" \
          --window-pos 200 120 \
          --window-size 800 400 \
          --icon-size 100 \
          --icon "QuantAgent.app" 200 190 \
          --hide-extension "QuantAgent.app" \
          --app-drop-link 600 185 \
          "{dmg_name}" \
          "{app_path}"
        """
        run_command(cmd)
    else:
        # 手动创建 DMG
        temp_dmg = "temp.dmg"

        # 创建临时 DMG
        run_command(f'hdiutil create -size 200m -fs HFS+ -volname "Quant Agent" {temp_dmg}')

        # 挂载
        run_command(f'hdiutil attach {temp_dmg}')

        # 复制应用
        run_command(f'cp -R {app_path} "/Volumes/Quant Agent/"')
        run_command('ln -s /Applications "/Volumes/Quant Agent/Applications"')

        # 卸载并转换
        run_command('hdiutil detach "/Volumes/Quant Agent"')
        run_command(f'hdiutil convert {temp_dmg} -format UDZO -o {dmg_name}')
        os.remove(temp_dmg)

    dmg_path = Path(dmg_name)
    if not dmg_path.exists():
        raise RuntimeError("DMG 创建失败")

    print(f"✓ DMG 已生成: {dmg_path}")
    print(f"  大小: {dmg_path.stat().st_size / 1024 / 1024:.1f} MB")
    return dmg_path

def main():
    """主函数"""
    try:
        print("=" * 60)
        print("Quant Agent - Mac 平台构建脚本")
        print("=" * 60)

        # 构建应用
        app_path = build_app()

        # 创建 DMG
        dmg_path = create_dmg(app_path)

        print("\n" + "=" * 60)
        print("✓ 构建完成！")
        print("=" * 60)
        print(f"\n应用文件: {app_path}")
        print(f"安装包:   {dmg_path}")
        print("\n测试方法:")
        print("  1. 双击安装 .dmg 文件")
        print("  2. 将 QuantAgent.app 拖到 Applications 文件夹")
        print("  3. 在终端运行: open 'quant-agent://launch'")
        print("  4. 或在浏览器访问: http://127.0.0.1:17633/health")

    except Exception as e:
        print(f"\n❌ 构建失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 四、自动启动和后台运行（可选）

### 方式一：使用 LaunchAgent（推荐）

创建 `~/Library/LaunchAgents/com.yourcompany.quantagent.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourcompany.quantagent</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Applications/QuantAgent.app/Contents/MacOS/quant-agent</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/quant-agent.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/quant-agent.error.log</string>
</dict>
</plist>
```

加载服务：

```bash
launchctl load ~/Library/LaunchAgents/com.yourcompany.quantagent.plist
```

### 方式二：登录时启动

在应用中添加到"系统偏好设置 > 用户与群组 > 登录项"。

## 五、代码签名和公证（发布必需）

```bash
# 1. 代码签名
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/QuantAgent.app

# 2. 创建签名的 DMG
codesign --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  QuantAgent-0.1.0.dmg

# 3. 公证（需要 Apple Developer 账号）
xcrun notarytool submit QuantAgent-0.1.0.dmg \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# 4. 装订公证票据
xcrun stapler staple QuantAgent-0.1.0.dmg
```

## 六、常见问题

### Q1: URL Scheme 不工作？

**解决方法：**
```bash
# 1. 重建 Launch Services 数据库
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user

# 2. 重新安装应用
rm -rf /Applications/QuantAgent.app
cp -R dist/QuantAgent.app /Applications/

# 3. 测试
open "quant-agent://launch"
```

### Q2: 应用无法启动？

检查日志：
```bash
# 查看系统日志
log stream --predicate 'process == "QuantAgent"' --level debug

# 查看应用日志
tail -f /tmp/quant-agent.log
```

### Q3: 权限问题？

```bash
# 授予可执行权限
chmod +x /Applications/QuantAgent.app/Contents/MacOS/quant-agent

# 移除隔离属性
xattr -d com.apple.quarantine /Applications/QuantAgent.app
```

## 七、完整的跨平台支持

### 修改下载链接逻辑

在 `QuantAgentService.ts` 中：

```typescript
getDownloadUrl(): string {
  // 检测操作系统
  const platform = this.detectPlatform();

  const downloadUrls = {
    'windows': 'https://your-company.com/downloads/QuantAgentSetup-0.1.0.exe',
    'mac': 'https://your-company.com/downloads/QuantAgent-0.1.0.dmg',
    'linux': 'https://your-company.com/downloads/quant-agent-0.1.0-linux.tar.gz'
  };

  return downloadUrls[platform] || downloadUrls['windows'];
}

private detectPlatform(): 'windows' | 'mac' | 'linux' {
  const userAgent = window.navigator.userAgent.toLowerCase();

  if (userAgent.includes('mac')) {
    return 'mac';
  } else if (userAgent.includes('linux')) {
    return 'linux';
  }
  return 'windows';
}
```

## 八、总结

Mac 平台实现与 Windows 类似，主要区别：

| 方面 | Windows | Mac |
|------|---------|-----|
| 打包格式 | `.exe` | `.app` bundle |
| 安装包 | Inno Setup (`.exe`) | DMG/PKG (`.dmg`) |
| URL 注册 | 注册表 | `Info.plist` |
| 自启动 | 注册表/任务计划 | LaunchAgent |
| 代码签名 | Authenticode | Apple 代码签名 |

**核心要点：**
1. ✅ URL Scheme 在 Mac 上完全支持
2. ✅ 通过 `Info.plist` 配置 `CFBundleURLTypes`
3. ✅ 使用 PyInstaller 的 BUNDLE 模式
4. ✅ DMG 提供专业的安装体验
5. ✅ 发布需要代码签名和公证

按照本指南操作，可以实现与 Windows 平台完全相同的用户体验！
