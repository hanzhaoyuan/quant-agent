# Quant Agent

本地量化执行与回测 Agent - 配合 Web 前端使用的客户端程序

**当前版本**: 0.1.0 (MVP)
**技术栈**: Python 3.10+, FastAPI, uvicorn

---

## 📋 目录

- [项目概述](#项目概述)
- [快速开始](#快速开始)
  - [开发模式](#开发模式)
  - [生产模式（打包）](#生产模式打包)
- [API 接口](#api-接口)
- [自定义协议唤起](#自定义协议唤起)
- [项目结构](#项目结构)
- [环境变量配置](#环境变量配置)
- [打包与分发](#打包与分发)
- [开发指南](#开发指南)
- [故障排除](#故障排除)

---

## 项目概述

quant-agent 是一个在用户本地运行的量化交易执行和回测系统。

**核心理念**：
- Web 前端仅负责展示和下发任务
- 所有计算、回测、优化在用户本地完成
- 数据不上传，隐私安全有保障

**主要功能**（规划中）：
- ✅ 健康检查接口（已实现）
- ⏳ 策略回测
- ⏳ 参数优化
- ⏳ 实盘交易执行
- ⏳ GPU 加速计算

---

## 快速开始

### 开发模式

#### 1. 准备环境

```bash
# 创建并激活 Conda 环境（可选但推荐）
conda create --name quant-agent-env python=3.10
conda activate quant-agent-env

# 安装依赖
cd quant-agent
pip install -e .

# 或安装开发版本（包含测试工具）
pip install -e ".[dev]"
```

#### 2. 启动开发服务器

```bash
# 方式一：使用开发脚本（推荐）
python scripts/run_dev.py

# 方式二：启用热重载（开发时修改代码自动重启）
python scripts/run_dev.py --reload

# 方式三：使用 uvicorn
uvicorn agent.main:app --host 127.0.0.1 --port 17633

# 方式四：作为模块运行
python -m agent.main
```

#### 3. 验证运行

服务启动后，访问：
- **健康检查**: http://127.0.0.1:17633/health
- **API 文档**: http://127.0.0.1:17633/docs
- **ReDoc**: http://127.0.0.1:17633/redoc

命令行测试：
```bash
curl http://127.0.0.1:17633/health
# 预期返回: {"ok":true,"name":"quant-agent","version":"0.1.0"}
```

---

### 生产模式（打包）

#### 为什么需要打包？

**用户友好的分发方式**：
- ✅ 用户无需安装 Python
- ✅ 用户无需安装依赖包
- ✅ 一键安装，专业体验
- ✅ 完全独立，不污染系统环境

#### 打包步骤

**1. 安装打包工具**
```bash
pip install pyinstaller
```

**2. 打包成独立可执行文件**
```bash
python build.py
```

生成文件：`dist/quant-agent.exe`（约 40-60 MB，包含 Python 解释器和所有依赖）

**3. 制作安装程序（可选）**

a. 下载并安装 [Inno Setup](https://jrsoftware.org/isdl.php)

b. 打包安装程序：
```bash
# 使用脚本（如果有）
python build_installer.py

# 或手动编译
# 1. 打开 Inno Setup Compiler
# 2. 打开 installer/setup.iss
# 3. 点击 "Build" -> "Compile"
```

生成文件：`installer/output/QuantAgentSetup-0.1.0.exe`

详细打包说明请参考：[installer/README.md](installer/README.md) 和 [installer/PACKAGING.md](installer/PACKAGING.md)

---

## API 接口

### GET /health

健康检查接口，用于 Web 端检测 Agent 运行状态。

**响应示例**：
```json
{
  "ok": true,
  "name": "quant-agent",
  "version": "0.1.0"
}
```

### POST /tasks（预留）

任务创建接口，当前返回 501 Not Implemented。

**请求示例**：
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

**响应示例**：
```json
{
  "task_id": "TODO",
  "status": "not_implemented",
  "message": "Task API is under development. Coming soon!"
}
```

---

## 自定义协议唤起

### 工作原理

Web 前端可以通过 `quant-agent://launch` 协议唤起本地 Agent。

**唤起流程**：
1. **Agent 未运行**: 系统启动 Agent 程序
2. **Agent 已运行**: 激活现有窗口（单实例模式）
3. **Agent 未安装**: 浏览器提示无法打开，前端引导用户下载

### Web 端检测示例

```javascript
// 1. 检测 Agent 是否运行
fetch('http://127.0.0.1:17633/health')
  .then(res => {
    if (res.ok) {
      console.log('Agent is running');
    }
  })
  .catch(() => {
    // 2. 未运行，尝试唤起
    window.location.href = 'quant-agent://launch';

    // 3. 等待后再次检测
    setTimeout(() => {
      fetch('http://127.0.0.1:17633/health')
        .then(res => {
          if (res.ok) {
            console.log('Agent launched successfully');
          } else {
            alert('请先安装 Quant Agent 客户端');
          }
        });
    }, 3000);
  });
```

### Windows 协议注册

安装包会自动注册自定义协议，无需手动配置。

如需手动注册，创建 `register-protocol.reg` 文件：
```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\quant-agent]
@="URL:Quant Agent Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\quant-agent\DefaultIcon]
@="C:\\Program Files\\QuantAgent\\quant-agent.exe,1"

[HKEY_CLASSES_ROOT\quant-agent\shell\open\command]
@="\"C:\\Program Files\\QuantAgent\\quant-agent.exe\" \"%1\""
```

双击运行即可注册。

---

## 项目结构

```
quant-agent/
├── agent/                    # 主应用代码
│   ├── __init__.py
│   ├── main.py              # 程序入口
│   ├── api/                 # API 接口层
│   │   ├── __init__.py
│   │   └── health.py        # 健康检查接口
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   └── config.py        # 全局配置
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── logger.py        # 日志工具
│
├── installer/               # 安装包相关
│   ├── README.md           # 打包详细说明
│   ├── PACKAGING.md        # 打包技术细节
│   └── setup.iss           # Inno Setup 脚本
│
├── scripts/
│   └── run_dev.py          # 开发启动脚本
│
├── build.py                # PyInstaller 打包脚本
├── build_installer.py      # 安装程序打包脚本
├── pyproject.toml          # 项目配置
├── README.md               # 本文档
└── CORS_FIX.md            # CORS 问题修复说明
```

---

## 环境变量配置

所有环境变量前缀为 `QUANT_AGENT_`：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `QUANT_AGENT_HOST` | 服务绑定地址 | `127.0.0.1` |
| `QUANT_AGENT_PORT` | 服务端口 | `17633` |
| `QUANT_AGENT_LOG_LEVEL` | 日志级别 | `INFO` |
| `QUANT_AGENT_LOG_FILE` | 日志文件路径（可选） | 无 |

**示例**：
```bash
# Linux/macOS
export QUANT_AGENT_PORT=18000
export QUANT_AGENT_LOG_LEVEL=DEBUG

# Windows CMD
set QUANT_AGENT_PORT=18000
set QUANT_AGENT_LOG_LEVEL=DEBUG

# Windows PowerShell
$env:QUANT_AGENT_PORT=18000
$env:QUANT_AGENT_LOG_LEVEL="DEBUG"
```

---

## 打包与分发

### 完整打包流程

```bash
# 1. 准备环境
cd quant-agent
pip install pyinstaller

# 2. 打包可执行文件
python build.py
# 输出: dist/quant-agent.exe

# 3. 测试可执行文件
dist/quant-agent.exe

# 4. 制作安装程序（使用 Inno Setup）
python build_installer.py
# 输出: installer/output/QuantAgentSetup-0.1.0.exe

# 5. 测试安装程序
installer/output/QuantAgentSetup-0.1.0.exe
```

### 分发建议

**安装包特性**：
- 大小: 约 45-65 MB
- 自动注册 `quant-agent://` 协议
- 创建开始菜单快捷方式
- 可选桌面快捷方式
- 完整卸载功能

**分发渠道**：
1. 公司官网下载页面
2. GitHub Releases
3. 内部文件服务器

**最佳实践**：
- 为安装包添加数字签名（避免 SmartScreen 警告）
- 提供 SHA256 校验和
- 提供安装说明文档

---

## 开发指南

### 添加新 API 接口

**1. 创建新路由模块**

`agent/api/tasks.py`:
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TaskRequest(BaseModel):
    task_type: str
    params: dict

@router.post("/tasks")
async def create_task(task: TaskRequest):
    return {"task_id": "12345", "status": "created"}
```

**2. 注册路由**

`agent/main.py`:
```python
from agent.api.tasks import router as tasks_router

app.include_router(tasks_router, tags=["tasks"])
```

### 代码规范

- 使用 type hints
- 遵循 PEP 8 代码风格
- 添加 docstrings
- 编写单元测试（未来）

### 运行测试（未来）

```bash
pytest tests/
```

---

## 故障排除

### 常见问题

#### 1. 端口被占用

**错误**：`[Errno 10048] error while attempting to bind on address ('127.0.0.1', 17633)`

**解决**：
```bash
# 查找占用端口的进程
netstat -ano | findstr :17633

# 终止进程
taskkill /PID <进程ID> /F

# 或更换端口
python scripts/run_dev.py --port 18000
```

#### 2. CORS 错误（云端访问本地 Agent）

**错误**：`Access to fetch at 'http://127.0.0.1:17633/health' has been blocked by CORS policy`

**解决**：已在 v0.1.0 中修复，CORS 现在允许所有来源访问。详见：[CORS_FIX.md](CORS_FIX.md)

#### 3. 打包后无法运行

**错误**：`Failed to execute script`

**解决**：
- 检查是否安装了所有依赖：`pip install -e .`
- 查看 `build.py` 中的 `--hidden-import` 是否包含所有模块
- 在控制台模式下运行查看详细错误

#### 4. 自定义协议无法唤起

**问题**：点击 `quant-agent://launch` 没有反应

**解决**：
- 检查注册表是否正确注册（运行安装程序会自动注册）
- 手动注册协议（见[自定义协议唤起](#自定义协议唤起)）
- 检查可执行文件路径是否正确

---

## 未来扩展

### 计划功能

- [ ] 回测引擎（基于 pandas + numpy）
- [ ] 参数优化（使用 Optuna）
- [ ] GPU 加速（CUDA/cupy）
- [ ] 任务队列系统（Celery + Redis）
- [ ] 实盘交易接口（券商 API 对接）
- [ ] 数据源管理（akshare, tushare, yfinance）

详细设计请参考项目 Issue 和 Wiki。

---

## 安全说明

- **本地访问限制**: 服务仅绑定 `127.0.0.1`，不对外网暴露
- **CORS 配置**: 允许所有来源访问（安全，因为只能从本地浏览器连接）
- **未来扩展**: 如需远程访问，建议添加 Token 认证

---

## 许可证

MIT License

---

## 联系与支持

如有问题或建议，请：
- 提交 Issue
- 联系开发团队
- 查看项目 Wiki

---

**享受量化交易吧！** 📈
