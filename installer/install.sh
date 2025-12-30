#!/bin/bash
# Quant Agent 安装脚本（macOS）
# 功能：安装应用并配置开机自启动

set -e

APP_NAME="quant-agent.app"
PLIST_NAME="com.fastbull.quantagent.plist"
INSTALL_DIR="/Applications"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "======================================================================"
echo "Quant Agent 安装程序"
echo "======================================================================"
echo

# 检查是否在 DMG 中运行
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/$APP_NAME"
PLIST_PATH="$SCRIPT_DIR/$PLIST_NAME"

# 1. 检查应用是否存在
echo "[1/5] 检查应用文件..."
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误: 未找到 $APP_NAME"
    echo "请确保此脚本在 DMG 挂载目录中运行"
    exit 1
fi
echo "✓ 找到应用: $APP_PATH"

# 2. 停止正在运行的实例
echo
echo "[2/5] 停止旧版本（如果正在运行）..."
if launchctl list | grep -q "com.fastbull.quantagent"; then
    echo "  停止 LaunchAgent..."
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
fi

# 检查进程
if pgrep -x "quant-agent" > /dev/null; then
    echo "  停止运行中的进程..."
    pkill -x "quant-agent" || true
    sleep 2
fi
echo "✓ 已清理旧版本"

# 3. 复制应用到 Applications
echo
echo "[3/5] 安装应用到 $INSTALL_DIR..."

# 删除旧版本
if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
    echo "  删除旧版本..."
    rm -rf "$INSTALL_DIR/$APP_NAME"
fi

# 复制新版本
echo "  复制应用..."
cp -R "$APP_PATH" "$INSTALL_DIR/"
echo "✓ 应用已安装到 $INSTALL_DIR/$APP_NAME"

# 4. 配置开机自启动
echo
echo "[4/5] 配置开机自启动..."

# 确保 LaunchAgents 目录存在
mkdir -p "$LAUNCH_AGENTS_DIR"

# 复制 plist 文件
if [ -f "$PLIST_PATH" ]; then
    cp "$PLIST_PATH" "$LAUNCH_AGENTS_DIR/"
    echo "✓ LaunchAgent 配置已安装"

    # 加载 LaunchAgent
    echo "  启动服务..."
    launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
    echo "✓ 服务已启动"
else
    echo "⚠️  警告: 未找到 LaunchAgent 配置文件"
    echo "   应用已安装，但不会开机自启动"
    echo "   你可以手动启动应用"
fi

# 5. 移除隔离标志（避免 Gatekeeper 警告）
echo
echo "[5/5] 移除安全隔离标志..."
xattr -dr com.apple.quarantine "$INSTALL_DIR/$APP_NAME" 2>/dev/null || true
echo "✓ 已移除隔离标志"

echo
echo "======================================================================"
echo "✅ 安装完成！"
echo "======================================================================"
echo
echo "应用位置:"
echo "  $INSTALL_DIR/$APP_NAME"
echo
echo "自启动配置:"
echo "  $LAUNCH_AGENTS_DIR/$PLIST_NAME"
echo
echo "日志文件:"
echo "  /tmp/com.fastbull.quantagent.out.log"
echo "  /tmp/com.fastbull.quantagent.err.log"
echo
echo "======================================================================"
echo "验证安装"
echo "======================================================================"
echo

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 验证服务是否运行
if launchctl list | grep -q "com.fastbull.quantagent"; then
    echo "✓ LaunchAgent 已加载"
else
    echo "⚠️  LaunchAgent 未加载，尝试手动加载..."
    launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
fi

# 验证 HTTP 服务
echo
echo "检查 HTTP 服务..."
for i in {1..5}; do
    if curl -s http://127.0.0.1:17633/health > /dev/null 2>&1; then
        echo "✓ Agent 正在运行！"
        echo "  访问: http://127.0.0.1:17633/health"
        break
    else
        if [ $i -lt 5 ]; then
            echo "  等待服务启动... ($i/5)"
            sleep 2
        else
            echo "⚠️  服务未响应，可能需要手动启动"
            echo "  运行: open $INSTALL_DIR/$APP_NAME"
        fi
    fi
done

echo
echo "======================================================================"
echo "使用说明"
echo "======================================================================"
echo
echo "1. Agent 已在后台运行，无需手动启动"
echo
echo "2. 测试 URL 协议:"
echo "   open quant-agent://launch"
echo
echo "3. 查看日志:"
echo "   tail -f /tmp/com.fastbull.quantagent.out.log"
echo
echo "4. 停止服务:"
echo "   launchctl unload ~/Library/LaunchAgents/$PLIST_NAME"
echo
echo "5. 启动服务:"
echo "   launchctl load ~/Library/LaunchAgents/$PLIST_NAME"
echo
echo "6. 卸载应用:"
echo "   运行 /Applications/$APP_NAME/Contents/Resources/uninstall.sh"
echo "   或删除 $INSTALL_DIR/$APP_NAME"
echo
echo "======================================================================"
echo
