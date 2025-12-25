@echo off
echo ========================================
echo 检查 quant-agent:// 协议注册状态
echo ========================================
echo.

echo [1] 检查协议注册...
reg query "HKEY_CLASSES_ROOT\quant-agent" /ve 2>nul
if %errorlevel% equ 0 (
    echo    ✓ 协议已注册
) else (
    echo    ✗ 协议未注册
    goto :end
)

echo.
echo [2] 检查 URL Protocol 标记...
reg query "HKEY_CLASSES_ROOT\quant-agent" /v "URL Protocol" 2>nul
if %errorlevel% equ 0 (
    echo    ✓ URL Protocol 已设置
) else (
    echo    ✗ URL Protocol 未设置
)

echo.
echo [3] 检查命令行配置...
reg query "HKEY_CLASSES_ROOT\quant-agent\shell\open\command" /ve 2>nul
if %errorlevel% equ 0 (
    echo    ✓ 命令行已配置
) else (
    echo    ✗ 命令行未配置
)

echo.
echo [4] 完整注册表信息:
echo ========================================
reg query "HKEY_CLASSES_ROOT\quant-agent" /s 2>nul

:end
echo.
echo ========================================
echo 检查完成
echo ========================================
pause
