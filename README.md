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

## 打包与分发

详见 [installer/README.md](installer/README.md)

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
