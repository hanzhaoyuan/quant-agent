"""
健康检查与基础接口
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional

from agent.core.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应"""
    ok: bool
    name: str
    version: str


class TaskRequest(BaseModel):
    """任务请求结构（预留）"""
    task_type: str  # backtest, optimize, live_trade 等
    strategy_id: Optional[str] = None
    params: Optional[dict] = None


class TaskResponse(BaseModel):
    """任务响应结构（预留）"""
    task_id: str
    status: str
    message: str


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    健康检查接口

    Returns:
        HealthResponse: 包含服务状态、名称和版本信息
    """
    return HealthResponse(
        ok=True,
        name=settings.app_name,
        version=settings.app_version
    )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_task(task: TaskRequest):
    """
    创建任务接口（预留）

    TODO: 未来实现完整的任务创建逻辑
    - 任务类型：回测 (backtest)、优化 (optimize)、实盘 (live_trade)
    - 任务队列管理（异步执行）
    - 任务状态跟踪 (pending, running, completed, failed)
    - 结果存储与查询

    建议实现方案：
    1. 使用 Celery 或 RQ 作为任务队列
    2. 任务状态存储在 SQLite/PostgreSQL
    3. WebSocket 推送任务进度更新
    4. 支持任务取消、暂停、恢复

    Args:
        task: 任务请求参数

    Returns:
        TaskResponse: 任务创建响应（当前返回 501 Not Implemented）
    """
    return TaskResponse(
        task_id="TODO",
        status="not_implemented",
        message="Task API is under development. Coming soon!"
    )
