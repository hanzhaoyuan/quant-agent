# quant-agent

本地量化执行与回测 Agent - 配合 Web 前端使用的客户端程序

## 项目概述

quant-agent 是一个在本地运行的量化交易执行和回测系统。Web 前端仅负责展示和下发任务，所有计算、回测、优化和执行都在本地完成。

**当前版本**: 0.1.0 (MVP)

**技术栈**: Python 3.10+, FastAPI, uvicorn

## 快速开始

### 1. 依赖安装

```bash
cd quant-agent
pip install -e .
```

或使用开发模式（包含测试工具）：

```bash
pip install -e ".[dev]"
```

### 2. 启动服务

**方式一：使用开发脚本（推荐）**

```bash
python scripts/run_dev.py
```

启用热重载（开发模式）：

```bash
python scripts/run_dev.py --reload
```

**方式二：直接使用 uvicorn**

```bash
uvicorn agent.main:app --host 127.0.0.1 --port 17633
```

**方式三：作为 Python 模块运行**

```bash
python -m agent.main
```

### 3. 验证运行

服务启动后，访问以下地址验证：

**健康检查**:
```bash
curl http://127.0.0.1:17633/health
```

预期返回：
```json
{
  "ok": true,
  "name": "quant-agent",
  "version": "0.1.0"
}
```

**API 文档**:
- Swagger UI: http://127.0.0.1:17633/docs
- ReDoc: http://127.0.0.1:17633/redoc

## API 接口

### GET /health

健康检查接口，用于 Web 端检测 Agent 运行状态。

**响应示例**:
```json
{
  "ok": true,
  "name": "quant-agent",
  "version": "0.1.0"
}
```

### POST /tasks (预留)

任务创建接口，当前返回 501 Not Implemented。

**请求示例**:
```json
{
  "task_type": "backtest",
  "strategy_id": "strategy_001",
  "params": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

## 自定义协议与唤起机制

### Windows 自定义协议注册

为了让 Web 端能够唤起本地 Agent，需要在 Windows 注册表中注册自定义协议 `quant-agent://`。

#### 注册方法

创建一个 `.reg` 文件（例如 `register-protocol.reg`），内容如下：

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\quant-agent]
@="URL:Quant Agent Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\quant-agent\DefaultIcon]
@="C:\\Program Files\\QuantAgent\\quant-agent.exe,1"

[HKEY_CLASSES_ROOT\quant-agent\shell]

[HKEY_CLASSES_ROOT\quant-agent\shell\open]

[HKEY_CLASSES_ROOT\quant-agent\shell\open\command]
@="\"C:\\Program Files\\QuantAgent\\quant-agent.exe\" \"%1\""
```

双击运行该 `.reg` 文件即可完成注册。

**注意**:
- 请将 `C:\\Program Files\\QuantAgent\\quant-agent.exe` 替换为实际的安装路径
- 未来打包安装程序时，会自动执行此注册步骤

#### 唤起流程

1. **Agent 未运行**: Web 端访问 `quant-agent://launch`，系统会启动 Agent 程序
2. **Agent 已运行**: 程序应检测到已有实例，激活现有窗口（单实例模式）
3. **Agent 未安装**: 浏览器会提示"无法打开此协议"，Web 端检测到并引导用户下载安装

#### Web 端检测逻辑建议

```javascript
// 1. 尝试访问 health 接口
fetch('http://127.0.0.1:17633/health')
  .then(res => {
    if (res.ok) {
      // Agent 正在运行
      console.log('Agent is running');
    }
  })
  .catch(() => {
    // 2. Agent 未运行，尝试唤起
    window.location.href = 'quant-agent://launch';

    // 3. 等待 2 秒后再次检测
    setTimeout(() => {
      fetch('http://127.0.0.1:17633/health')
        .then(res => {
          if (res.ok) {
            console.log('Agent launched successfully');
          } else {
            // 可能未安装，提示下载
            alert('请先安装 quant-agent 客户端');
          }
        });
    }, 2000);
  });
```

## 项目结构

```
quant-agent/
├── agent/                    # 主应用代码
│   ├── __init__.py
│   ├── main.py              # 程序入口
│   ├── api/                 # API 接口层
│   │   ├── __init__.py
│   │   └── health.py        # 健康检查与基础接口
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   └── config.py        # 全局配置
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── logger.py        # 日志工具
│
├── installer/               # 安装包相关（见 installer/README.md）
│   └── README.md
│
├── scripts/
│   └── run_dev.py          # 开发启动脚本
│
├── README.md
└── pyproject.toml          # 项目配置
```

## 环境变量配置

可通过环境变量覆盖默认配置（所有变量前缀为 `QUANT_AGENT_`）：

```bash
# 服务地址（默认 127.0.0.1，仅本地访问）
QUANT_AGENT_HOST=127.0.0.1

# 服务端口（默认 17633）
QUANT_AGENT_PORT=17633

# 日志级别（默认 INFO）
QUANT_AGENT_LOG_LEVEL=DEBUG

# 日志文件路径（可选）
QUANT_AGENT_LOG_FILE=/var/log/quant-agent.log
```

## 未来扩展设计

### 1. 回测引擎 (Backtest Engine)

**建议实现方案**:
- 使用 `pandas` + `numpy` 进行数据处理
- 支持向量化回测（vectorized backtesting）
- 插件化策略系统，策略继承 `BaseStrategy` 基类
- 回测结果包含：收益曲线、夏普比率、最大回撤等指标

**目录结构**:
```
agent/
├── backtest/
│   ├── __init__.py
│   ├── engine.py          # 回测引擎核心
│   ├── strategy.py        # 策略基类
│   └── metrics.py         # 性能指标计算
```

### 2. 参数优化 (Parameter Optimization)

**建议实现方案**:
- 使用 `Optuna` 进行超参数优化
- 支持并行优化（多进程/多线程）
- 可选 CUDA 加速（使用 `cupy` 或 `numba`）

**目录结构**:
```
agent/
├── optimizer/
│   ├── __init__.py
│   ├── optuna_optimizer.py
│   └── grid_search.py
```

### 3. CUDA/GPU 加速

**建议实现方案**:
- 使用 `cupy` 替换 `numpy` 进行矩阵运算
- 使用 `numba` 的 CUDA JIT 编译加速计算密集型函数
- 配置项：`QUANT_AGENT_CUDA_DEVICE` 指定 GPU 设备

### 4. 任务队列系统

**建议实现方案**:
- 使用 `Celery` + `Redis` 或 `RQ` 作为任务队列
- 任务状态：`pending`, `running`, `completed`, `failed`, `cancelled`
- WebSocket 推送任务进度更新

**数据库设计**:
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- backtest, optimize, live_trade
    status TEXT NOT NULL,
    params TEXT,  -- JSON
    result TEXT,  -- JSON
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 5. 实盘交易 (Live Trading)

**建议实现方案**:
- 接入主流券商 API（东方财富、富途、老虎等）
- 风控模块：仓位管理、止损止盈、最大回撤限制
- 订单管理：委托、成交、撤单、查询

### 6. 数据源管理

**建议实现方案**:
- 支持多数据源：`akshare`, `tushare`, `yfinance`
- 本地缓存机制（SQLite 或 Parquet 文件）
- 增量更新策略

## 打包成独立安装包（不污染用户环境）

### 为什么需要独立打包？

**传统 Python 应用的问题**:
- 用户需要安装 Python 环境
- 需要手动安装依赖包 (pip install)
- 可能与用户系统中其他 Python 应用产生依赖冲突
- 安装过程复杂，对非技术用户不友好

**独立安装包的优势**:
- ✅ **零依赖**: 用户无需安装 Python 或任何第三方库
- ✅ **环境隔离**: 所有依赖打包在一起，完全不污染用户系统
- ✅ **一键安装**: 双击安装程序即可完成安装
- ✅ **专业体验**: 与传统 Windows 软件一样的安装流程
- ✅ **易于分发**: 单个 .exe 安装包即可分发

### 打包方案概述

我们使用以下工具链实现完全独立的安装包：

1. **PyInstaller**: 将 Python 应用及所有依赖打包成单个可执行文件
2. **Inno Setup**: 制作专业的 Windows 安装程序

**关键特性**:
- 所有 Python 解释器、依赖库都打包进可执行文件
- 用户电脑上不需要安装 Python
- 用户电脑上不需要安装任何 pip 包
- 完全独立运行，不依赖外部环境

### 详细打包步骤

#### 步骤 1: 准备打包环境

```bash
# 安装打包工具
pip install pyinstaller

# 确保项目依赖已安装
cd quant-agent
pip install -e .
```

#### 步骤 2: 使用 PyInstaller 打包

创建打包脚本 `build.py`:

```python
# quant-agent/build.py
"""
打包 quant-agent 为独立可执行文件

运行方式: python build.py
输出: dist/quant-agent.exe (完全独立，不依赖任何外部 Python 环境)
"""
import PyInstaller.__main__
import os
import shutil

# 清理旧的构建文件
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# 打包参数
PyInstaller.__main__.run([
    'agent/main.py',                    # 入口文件

    # 基本设置
    '--name=quant-agent',               # 可执行文件名
    '--onefile',                        # 打包成单个文件
    '--console',                        # 显示控制台（方便看日志）

    # 包含的数据和模块
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.protocols.http.h11_impl',
    '--hidden-import=uvicorn.protocols.websockets',
    '--hidden-import=uvicorn.protocols.websockets.auto',
    '--hidden-import=uvicorn.lifespan',
    '--hidden-import=uvicorn.lifespan.on',

    # 图标（可选，未来添加）
    # '--icon=installer/icon.ico',

    # 清理
    '--clean',
])

print("=" * 60)
print("打包完成!")
print("生成的可执行文件: dist/quant-agent.exe")
print("=" * 60)
print("重要提示:")
print("- 这是一个完全独立的可执行文件")
print("- 不需要用户安装 Python")
print("- 不需要用户安装任何依赖库")
print("- 可以直接在任何 Windows 系统上运行")
print("=" * 60)
```

运行打包：

```bash
python build.py
```

**打包后的文件**:
- `dist/quant-agent.exe` (约 40-60 MB，包含 Python 解释器 + 所有依赖)

**测试独立可执行文件**:
```bash
# 直接运行（不需要 Python 环境）
dist/quant-agent.exe

# 在另一台没有 Python 的电脑上也能运行
```

#### 步骤 3: 制作安装程序 (Inno Setup)

下载并安装 [Inno Setup](https://jrsoftware.org/isdl.php)

创建安装脚本 `installer/setup.iss`:

```iss
; Inno Setup 安装脚本
; 用途: 将 quant-agent.exe 打包成专业的安装程序

[Setup]
; 应用信息
AppName=Quant Agent
AppVersion=0.1.0
AppPublisher=Your Company
AppPublisherURL=https://your-company.com
DefaultDirName={autopf}\QuantAgent
DefaultGroupName=Quant Agent
OutputDir=installer\output
OutputBaseFilename=QuantAgentSetup-0.1.0
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; 安装向导设置
WizardStyle=modern
SetupIconFile=installer\icon.ico
UninstallDisplayIcon={app}\quant-agent.exe

[Files]
; 复制独立的可执行文件到安装目录
Source: "dist\quant-agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单快捷方式
Name: "{group}\Quant Agent"; Filename: "{app}\quant-agent.exe"
Name: "{group}\卸载 Quant Agent"; Filename: "{uninstallexe}"

; 桌面快捷方式（可选）
Name: "{autodesktop}\Quant Agent"; Filename: "{app}\quant-agent.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"

[Registry]
; 注册自定义协议 quant-agent://
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: ""; ValueData: "URL:Quant Agent Protocol"; Flags: uninsdeletekey
Root: HKCR; Subkey: "quant-agent"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCR; Subkey: "quant-agent\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\quant-agent.exe,0"
Root: HKCR; Subkey: "quant-agent\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\quant-agent.exe"" ""%1"""

[Run]
; 安装完成后可选择立即运行
Filename: "{app}\quant-agent.exe"; Description: "立即启动 Quant Agent"; Flags: nowait postinstall skipifsilent

[Code]
// 检查是否已有实例在运行
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
```

使用 Inno Setup 编译：

1. 打开 Inno Setup Compiler
2. 打开 `installer/setup.iss`
3. 点击 "Build" -> "Compile"
4. 生成 `installer/output/QuantAgentSetup-0.1.0.exe`

**最终安装包特性**:
- 大小: 约 45-65 MB（包含所有内容）
- 用户体验: 双击安装，下一步下一步即可
- 自动注册自定义协议 `quant-agent://`
- 创建开始菜单快捷方式
- 可选创建桌面快捷方式
- 完整的卸载功能

### 环境隔离说明

**打包后的应用如何做到环境隔离？**

1. **内嵌 Python 解释器**
   - PyInstaller 将 Python 3.10+ 解释器完整打包进 .exe
   - 用户无需安装 Python

2. **内嵌所有依赖库**
   - FastAPI, uvicorn, pydantic 等所有依赖都打包在内
   - 用户无需运行 `pip install`

3. **独立运行时环境**
   - 可执行文件运行时，从自己的内存空间加载所有模块
   - 完全不访问系统的 Python 环境（即使用户安装了 Python）

4. **不修改系统环境变量**
   - 不修改 PATH
   - 不创建全局 Python 环境
   - 除了注册表中的自定义协议，不修改任何系统配置

5. **卸载完全清理**
   - 卸载时删除所有安装文件
   - 删除注册表中的自定义协议
   - 不留任何残留

### 与用户现有环境的关系

| 场景 | 影响 |
|------|------|
| 用户已安装 Python | 完全独立，互不影响 |
| 用户已安装其他 Python 应用 | 完全独立，互不影响 |
| 用户系统中有不同版本的 FastAPI | 完全独立，互不影响 |
| 多个版本的 quant-agent 同时安装 | 不建议，但技术上可以安装到不同目录 |

### 完整打包工作流

```bash
# 1. 准备环境
cd quant-agent
pip install pyinstaller

# 2. 打包可执行文件
python build.py

# 3. 测试可执行文件
dist/quant-agent.exe

# 4. 使用 Inno Setup 制作安装程序
# (在 Inno Setup Compiler 中打开 installer/setup.iss 并编译)

# 5. 测试安装程序
installer/output/QuantAgentSetup-0.1.0.exe
```

### 分发安装包

**分发渠道**:
1. 公司官网下载页面
2. GitHub Releases
3. 内部文件服务器

**建议**:
- 为安装包添加数字签名（避免 Windows SmartScreen 警告）
- 提供 SHA256 校验和
- 提供详细的安装说明文档

**用户安装步骤**:
1. 下载 `QuantAgentSetup-0.1.0.exe`
2. 双击运行
3. 点击"下一步"完成安装
4. 无需任何额外配置

详细的技术细节和示例代码请参考 [installer/README.md](installer/README.md)

## 安全注意事项

1. **本地访问限制**: 服务仅绑定 `127.0.0.1`，不对外网暴露
2. **CORS 配置**: 仅允许本地前端访问
3. **未来扩展**: 如需远程访问，建议添加 Token 认证或 API Key

## 开发指南

### 添加新 API 接口

1. 在 `agent/api/` 下创建新模块（例如 `tasks.py`）
2. 定义 router 和路由函数
3. 在 `agent/main.py` 中注册 router

```python
# agent/api/tasks.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/tasks")
async def create_task():
    return {"message": "Task created"}

# agent/main.py
from agent.api.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
```

### 运行测试（未来）

```bash
pytest tests/
```

## 许可证

MIT License

## 联系方式

如有问题，请联系开发团队。
