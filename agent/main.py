"""
quant-agent 主程序入口
"""
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import __app_name__, __version__
from agent.api.health import router as health_router
from agent.core.config import settings
from agent.utils.logger import setup_logger


# 设置日志
logger = setup_logger(
    name=settings.app_name,
    level=settings.log_level,
    log_file=settings.log_file
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    TODO: 未来扩展
    - 初始化数据库连接
    - 加载策略插件
    - 初始化 CUDA 环境
    - 启动任务队列 worker
    """
    logger.info(f"{__app_name__} v{__version__} started")
    logger.info(f"Listening on {settings.host}:{settings.port}")
    logger.info("=" * 50)

    yield

    # 关闭时清理资源
    logger.info(f"{__app_name__} shutting down...")
    logger.info("=" * 50)


# 创建 FastAPI 应用
app = FastAPI(
    title=__app_name__,
    version=__version__,
    description="本地量化执行与回测 Agent",
    lifespan=lifespan
)

# CORS 配置（仅允许本地前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",  # Vite 默认端口
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        # 可以根据实际 Web 前端端口添加更多
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health_router, tags=["health"])


def main():
    """
    主函数：启动 uvicorn 服务器

    可通过环境变量覆盖配置：
    - QUANT_AGENT_HOST
    - QUANT_AGENT_PORT
    - QUANT_AGENT_LOG_LEVEL
    """
    try:
        # 直接传递 app 对象而不是字符串路径
        # 这样在 PyInstaller 打包后也能正常工作
        uvicorn.run(
            app,  # 直接使用 app 对象，而不是 "agent.main:app" 字符串
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
            reload=False,  # 生产环境关闭热重载
        )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
