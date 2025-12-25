@echo off
echo ========================================
echo Quant Agent - Debug Mode
echo ========================================
echo.

cd /d "%~dp0"
dist\quant-agent.exe

echo.
echo ========================================
echo Press any key to exit...
echo ========================================
pause > nul
