@echo off
REM Quant Agent 便携版启动脚本
REM 无需安装，直接运行

echo ======================================
echo Quant Agent - 便携版
echo ======================================
echo.

REM 检查可执行文件是否存在
if not exist "dist\installer\quant-agent.exe" (
    echo [错误] 未找到 quant-agent.exe
    echo 请先运行 build.py 构建可执行文件
    echo.
    pause
    exit /b 1
)

echo [信息] 正在启动 Quant Agent...
echo [信息] 服务地址: http://127.0.0.1:17633
echo [信息] 按 Ctrl+C 停止服务
echo.

REM 启动 Agent
dist\installer\quant-agent.exe

pause
