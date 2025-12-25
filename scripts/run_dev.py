"""
开发环境启动脚本

用法：
    python scripts/run_dev.py

或带参数：
    python scripts/run_dev.py --reload
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn


def main():
    """启动开发服务器"""
    import argparse

    parser = argparse.ArgumentParser(description="启动 quant-agent 开发服务器")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载（开发模式）"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=17633,
        help="端口号（默认 17633）"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="日志级别"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Starting quant-agent Development Server")
    print("=" * 60)
    print(f"Host: 127.0.0.1")
    print(f"Port: {args.port}")
    print(f"Reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"Log Level: {args.log_level.upper()}")
    print("=" * 60)
    print(f"Health Check: http://127.0.0.1:{args.port}/health")
    print(f"API Docs: http://127.0.0.1:{args.port}/docs")
    print("=" * 60)

    uvicorn.run(
        "agent.main:app",
        host="127.0.0.1",
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
