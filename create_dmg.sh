#!/bin/bash
# 创建 macOS .dmg 安装镜像
# 用途: 将 Quant Agent.app 打包成专业的 .dmg 安装程序
#
# 使用方法:
# 1. 先运行 python build_macos.py 生成 dist/quant-agent.app
# 2. 运行此脚本: ./create_dmg.sh
# 3. 输出: installer/output/QuantAgent-0.1.0.dmg

set -e  # 遇到错误立即退出

echo "======================================================================"
echo "Quant Agent - macOS DMG 镜像创建工具"
echo "======================================================================"
echo

# 配置
APP_NAME="quant-agent"
APP_DISPLAY_NAME="Quant Agent"
VERSION="0.1.0"
APP_PATH="dist/${APP_NAME}.app"
OUTPUT_DIR="installer/output"
DMG_NAME="QuantAgent-${VERSION}.dmg"
DMG_PATH="${OUTPUT_DIR}/${DMG_NAME}"
TEMP_DMG="temp_dmg"

# 检查 .app 是否存在
echo "[1/6] 检查前置条件..."
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误: 未找到 $APP_PATH"
    echo "请先运行: python build_macos.py"
    exit 1
fi
echo "✓ 找到应用: $APP_PATH"

# 获取应用大小
APP_SIZE=$(du -sh "$APP_PATH" | awk '{print $1}')
echo "✓ 应用大小: $APP_SIZE"

echo
echo "[2/6] 准备临时目录..."

# 清理旧文件
rm -rf "$TEMP_DMG"
mkdir -p "$TEMP_DMG"
mkdir -p "$OUTPUT_DIR"

# 复制 .app 到临时目录
echo "[3/6] 复制应用到临时目录..."
cp -R "$APP_PATH" "$TEMP_DMG/"

# 创建"应用程序"文件夹的符号链接（方便用户拖拽安装）
echo "[4/6] 创建安装符号链接..."
ln -s /Applications "$TEMP_DMG/Applications"

# 创建自定义背景（可选）
# mkdir -p "$TEMP_DMG/.background"
# cp installer/dmg_background.png "$TEMP_DMG/.background/"

# 创建 .dmg 镜像
echo "[5/6] 创建 DMG 镜像..."

# 删除旧的 DMG
[ -f "$DMG_PATH" ] && rm "$DMG_PATH"

# 检查是否安装了 create-dmg
if command -v create-dmg &> /dev/null; then
    echo "使用 create-dmg 工具..."

    # 使用 create-dmg（推荐，更美观）
    create-dmg \
        --volname "${APP_DISPLAY_NAME}" \
        --volicon "${APP_PATH}/Contents/Resources/icon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 150 190 \
        --hide-extension "${APP_NAME}.app" \
        --app-drop-link 450 190 \
        --no-internet-enable \
        "$DMG_PATH" \
        "$TEMP_DMG" 2>/dev/null || {
            echo "⚠️  create-dmg 失败，使用 hdiutil 备用方案..."
            USE_HDIUTIL=1
        }
else
    echo "未找到 create-dmg，使用 hdiutil 命令..."
    USE_HDIUTIL=1
fi

# 备用方案：使用 hdiutil（macOS 自带）
if [ "$USE_HDIUTIL" = "1" ]; then
    # 创建临时 dmg
    hdiutil create -volname "${APP_DISPLAY_NAME}" -srcfolder "$TEMP_DMG" -ov -format UDRW temp.dmg

    # 挂载
    DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen temp.dmg | awk '/\/Volumes\// {print $1}')
    VOLUME=$(hdiutil attach -readwrite -noverify -noautoopen temp.dmg | grep '/Volumes/' | sed 's/.*\/Volumes\//\/Volumes\//')

    # 等待挂载完成
    sleep 2

    # 设置图标位置（可选）
    # osascript -e "tell application \"Finder\"" \
    #           -e "  set f to POSIX file (\"$VOLUME\" as string) as alias" \
    #           -e "  tell folder f" \
    #           -e "    open" \
    #           -e "    set current view of container window to icon view" \
    #           -e "    set toolbar visible of container window to false" \
    #           -e "    set statusbar visible of container window to false" \
    #           -e "    set bounds of container window to {200, 120, 800, 520}" \
    #           -e "    set viewOptions to the icon view options of container window" \
    #           -e "    set arrangement of viewOptions to not arranged" \
    #           -e "    set icon size of viewOptions to 100" \
    #           -e "    close" \
    #           -e "  end tell" \
    #           -e "end tell"

    # 卸载
    hdiutil detach "$DEVICE"

    # 转换为压缩的只读镜像
    hdiutil convert temp.dmg -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"

    # 清理临时文件
    rm -f temp.dmg
fi

# 清理临时目录
echo "[6/6] 清理临时文件..."
rm -rf "$TEMP_DMG"

# 完成
echo
echo "======================================================================"
echo "✅ DMG 镜像创建成功！"
echo "======================================================================"
echo
echo "输出文件:"
echo "  $(pwd)/$DMG_PATH"
echo
DMG_SIZE=$(du -sh "$DMG_PATH" | awk '{print $1}')
echo "文件大小: $DMG_SIZE"
echo
echo "======================================================================"
echo "测试步骤"
echo "======================================================================"
echo "1. 打开 DMG:"
echo "   open $DMG_PATH"
echo
echo "2. 拖拽 ${APP_DISPLAY_NAME}.app 到 Applications 文件夹"
echo
echo "3. 从启动台启动应用"
echo
echo "4. 测试 URL 协议:"
echo "   open quant-agent://launch"
echo
echo "======================================================================"
echo "部署步骤"
echo "======================================================================"
echo "1. 上传 DMG 到你的网站服务器"
echo
echo "2. 在前端更新下载链接 (QuantAgentService.ts):"
echo "   'mac': 'https://your-domain.com/downloads/${DMG_NAME}'"
echo
echo "3. 用户下载并安装后，即可从网站启动 Agent"
echo
echo "======================================================================"
echo
echo "可选: 代码签名（需要 Apple Developer 账号）"
echo "  codesign --force --deep --sign \"Developer ID Application: Your Name\" $APP_PATH"
echo "  codesign --verify --deep --strict --verbose=2 $APP_PATH"
echo
echo "可选: 公证（需要 Apple Developer 账号）"
echo "  xcrun notarytool submit $DMG_PATH --keychain-profile \"AC_PASSWORD\" --wait"
echo
echo "======================================================================"
