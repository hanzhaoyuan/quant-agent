"""
全局配置文件
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "quant-agent"
    app_version: str = "0.1.0"

    # 服务配置
    host: str = "127.0.0.1"  # 仅本地访问
    port: int = 17633

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None  # 如需文件日志，设置路径

    # TODO: 未来扩展配置项
    # - 回测引擎配置 (backtest_engine)
    # - 优化器配置 (optimizer)
    # - CUDA/GPU 配置 (cuda_device)
    # - 数据源配置 (data_sources)
    # - 策略插件路径 (strategy_plugins)
    # - 任务队列配置 (task_queue)

    class Config:
        env_prefix = "QUANT_AGENT_"  # 环境变量前缀
        case_sensitive = False


# 全局配置实例
settings = Settings()
