# Installer - 打包与安装

本目录用于存放 Windows 安装包相关的配置和脚本。

## 当前状态

**MVP 阶段**: 暂未实现真实的安装包，本文档提供打包方案说明。

## Windows 安装包方案

### 推荐工具

1. **PyInstaller** (推荐)
   - 将 Python 应用打包成独立可执行文件
   - 支持单文件或单目录模式
   - 自动收集依赖

2. **Inno Setup** (推荐用于安装程序)
   - 免费的 Windows 安装包制作工具
   - 支持注册表操作、快捷方式创建等
   - 可定制安装向导

3. **NSIS**
   - 另一款流行的 Windows 安装包制作工具
   - 脚本化配置

### 打包步骤（未来实施）

#### 1. 使用 PyInstaller 打包可执行文件

创建 `installer/build_exe.py`:

```python
"""
使用 PyInstaller 打包 quant-agent
"""
import PyInstaller.__main__
import os

# 项目根目录
project_root = os.path.dirname(os.path.dirname(__file__))

PyInstaller.__main__.run([
    os.path.join(project_root, 'agent', 'main.py'),
    '--name=quant-agent',
    '--onefile',  # 打包成单文件
    '--windowed',  # 无控制台窗口（如需 GUI）
    '--icon=installer/icon.ico',  # 应用图标
    '--add-data=agent:agent',  # 包含 agent 模块
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.lifespan.on',
])
```

运行打包：
```bash
cd installer
python build_exe.py
```

生成的 `quant-agent.exe` 位于 `dist/` 目录。

#### 2. 创建 Inno Setup 安装脚本

创建 `installer/setup.iss`:

```iss
; Inno Setup 安装脚本

[Setup]
AppName=Quant Agent
AppVersion=0.1.0
DefaultDirName={pf}\QuantAgent
DefaultGroupName=Quant Agent
OutputDir=output
OutputBaseFilename=QuantAgentSetup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\quant-agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
DesktopIcon: "{commondesktop}\Quant Agent"
StartMenuIcon: "{group}\Quant Agent"

[Registry]
; 注册自定义协议 quant-agent://
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: ""; ValueData: "URL:Quant Agent Protocol"; Flags: uninsdeletekey
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCR; Subkey: "quant-agent\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\quant-agent.exe,1"
Root: HKCR; Subkey: "quant-agent\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\quant-agent.exe"" ""%1"""

[Run]
Filename: "{app}\quant-agent.exe"; Description: "Launch Quant Agent"; Flags: nowait postinstall skipifsilent
```

使用 Inno Setup 编译器编译 `setup.iss`，生成 `QuantAgentSetup.exe`。

#### 3. 自定义协议处理

在 `agent/main.py` 中添加协议参数处理：

```python
import sys

def handle_protocol(uri: str):
    """
    处理自定义协议调用

    Example:
        quant-agent://launch
        quant-agent://open-strategy?id=123
    """
    if uri.startswith("quant-agent://"):
        command = uri.replace("quant-agent://", "")

        if command == "launch":
            # 启动服务
            logger.info("Launched via protocol")
        elif command.startswith("open-strategy"):
            # 解析参数并打开策略
            pass

def main():
    # 检查是否通过协议调用
    if len(sys.argv) > 1 and sys.argv[1].startswith("quant-agent://"):
        handle_protocol(sys.argv[1])

    # 启动服务
    uvicorn.run(...)
```

#### 4. 单实例检测（防止重复启动）

使用文件锁或命名互斥量确保只运行一个实例：

```python
import socket
import sys

def is_already_running(port=17633):
    """检测端口是否已被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return False
    except OSError:
        return True

def main():
    if is_already_running():
        logger.info("Agent is already running, activating existing instance...")
        # 可选：发送信号到现有实例，激活窗口
        sys.exit(0)

    # 启动服务
    ...
```

### GUI 托盘图标（可选）

如果需要系统托盘图标，可使用 `pystray`:

```python
import pystray
from PIL import Image
import threading

def create_tray_icon():
    icon = pystray.Icon(
        "quant-agent",
        Image.open("icon.png"),
        menu=pystray.Menu(
            pystray.MenuItem("Open Web", lambda: webbrowser.open("http://127.0.0.1:17633/docs")),
            pystray.MenuItem("Exit", lambda: sys.exit(0))
        )
    )
    icon.run()

def main():
    # 在后台线程启动托盘图标
    threading.Thread(target=create_tray_icon, daemon=True).start()

    # 启动服务
    uvicorn.run(...)
```

## 自动更新方案（未来）

1. **检测更新**: Agent 启动时访问更新服务器检查新版本
2. **下载更新**: 后台下载新版安装包
3. **提示用户**: 弹出通知，引导用户安装更新
4. **静默更新**: 如需静默更新，可使用增量更新方案

## 签名与分发

### 代码签名（推荐）

Windows 应用建议使用数字证书签名，避免 SmartScreen 警告：

```bash
signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com QuantAgentSetup.exe
```

### 分发渠道

- 公司官网下载
- GitHub Releases
- 内部更新服务器

## 测试清单

打包完成后，请测试：

- [ ] 安装程序正常运行
- [ ] 注册表协议注册成功
- [ ] `quant-agent://launch` 能正确唤起程序
- [ ] 单实例检测生效
- [ ] 卸载程序能清理所有文件和注册表项
- [ ] 程序能在全新 Windows 系统上运行（无需额外依赖）

## 目录规划

```
installer/
├── README.md              # 本文档
├── build_exe.py           # PyInstaller 打包脚本（未来）
├── setup.iss              # Inno Setup 配置（未来）
├── icon.ico               # 应用图标（未来）
└── output/                # 输出目录（未来）
    └── QuantAgentSetup.exe
```

## 参考资料

- [PyInstaller 文档](https://pyinstaller.org/)
- [Inno Setup 文档](https://jrsoftware.org/isinfo.php)
- [Windows 自定义协议](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa767914(v=vs.85))
