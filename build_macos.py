#!/usr/bin/env python3
"""
打包 quant-agent 为 macOS .app bundle

运行方式: python build_macos.py
输出: dist/QuantAgent.app (完全独立的 macOS 应用)

环境隔离说明:
- 打包后的 .app 包含完整的 Python 解释器
- 所有依赖库（FastAPI, uvicorn, pydantic 等）都内嵌在应用中
- 用户无需安装 Python 或任何依赖包
- 完全不会污染用户系统环境
"""
import PyInstaller.__main__
import os
import shutil
import sys
import plistlib
from pathlib import Path


def create_info_plist(app_path):
    """创建 macOS Info.plist 文件"""
    print("[额外步骤] 创建 Info.plist（用于 URL 协议注册）...")

    plist_data = {
        'CFBundleDevelopmentRegion': 'en',
        'CFBundleExecutable': 'quant-agent',
        'CFBundleIdentifier': 'com.fastbull.quantagent',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleName': 'Quant Agent',
        'CFBundleDisplayName': 'Quant Agent',
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '1',
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
        'NSAppleScriptEnabled': False,
        'NSPrincipalClass': 'NSApplication',

        # 注册 quant-agent:// URL 协议
        'CFBundleURLTypes': [
            {
                'CFBundleURLName': 'Quant Agent Protocol',
                'CFBundleURLSchemes': ['quant-agent'],
                'CFBundleTypeRole': 'Viewer'
            }
        ],

        # 后台运行设置（可选）
        'LSUIElement': False,  # True = 不显示在 Dock，False = 正常应用

        # 允许网络访问
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        }
    }

    # 写入 Info.plist
    plist_path = Path(app_path) / 'Contents' / 'Info.plist'
    with open(plist_path, 'wb') as f:
        plistlib.dump(plist_data, f)

    print(f"  ✓ Info.plist 已创建: {plist_path}")


def main():
    print("=" * 70)
    print("Quant Agent - macOS 打包工具")
    print("=" * 70)
    print()

    # 检查操作系统
    if sys.platform != "darwin":
        print("⚠️  警告: 此脚本应在 macOS 上运行")
        print("   当前系统:", sys.platform)
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            print("已取消")
            sys.exit(0)
        print()

    # 清理旧的构建文件
    print("[1/5] 清理旧的构建文件...")
    for directory in ['build', 'dist']:
        if os.path.exists(directory):
            print(f"  - 删除 {directory}/")
            shutil.rmtree(directory)

    print()
    print("[2/5] 准备打包...")

    # 打包参数
    print("[3/5] 开始打包...")
    PyInstaller.__main__.run([
        'agent/main.py',  # 入口文件

        # 基本设置
        '--name=quant-agent',  # 可执行文件名
        '--windowed',  # macOS GUI 应用（不显示终端窗口，但仍然可以在后台运行）
        # 如果需要看日志，改为 '--console'

        # 包含整个 agent 包及其子模块
        '--hidden-import=agent',
        '--hidden-import=agent.main',
        '--hidden-import=agent.api',
        '--hidden-import=agent.api.health',
        '--hidden-import=agent.core',
        '--hidden-import=agent.core.config',
        '--hidden-import=agent.utils',
        '--hidden-import=agent.utils.logger',

        # 包含 uvicorn 的隐藏导入
        '--hidden-import=uvicorn',
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.http.h11_impl',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.protocols.websockets.wsproto',
        '--hidden-import=uvicorn.protocols.websockets.wsproto_impl',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',

        # 包含 FastAPI 和 Pydantic 的隐藏导入
        '--hidden-import=fastapi',
        '--hidden-import=pydantic',
        '--hidden-import=pydantic_settings',
        '--hidden-import=starlette',
        '--hidden-import=starlette.responses',
        '--hidden-import=starlette.routing',

        # 收集所有 uvicorn 相关文件
        '--collect-all=uvicorn',

        # macOS 特定设置
        '--osx-bundle-identifier=com.fastbull.quantagent',

        # 图标（可选，需要 .icns 格式）
        # '--icon=installer/icon.icns',

        # 清理临时文件
        '--clean',

        # 不显示确认对话框
        '--noconfirm',

        # 指定输出目录
        '--distpath', 'dist',
    ])

    print()
    print("[4/5] 配置 .app bundle...")

    # 检查生成的 .app
    app_path = os.path.join('dist', 'quant-agent.app')
    if os.path.exists(app_path):
        # 创建自定义 Info.plist（支持 URL 协议）
        create_info_plist(app_path)

        # 获取文件大小
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(app_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        size_mb = total_size / (1024 * 1024)

        print()
        print("[5/5] 打包完成！")
        print()
        print("=" * 70)
        print("打包结果")
        print("=" * 70)
        print(f"生成的应用: {app_path}")
        print(f"应用大小: {size_mb:.1f} MB")
        print()
        print("=" * 70)
        print("重要提示 - 环境隔离说明")
        print("=" * 70)
        print("✅ 这是一个完全独立的 macOS 应用")
        print("✅ 用户无需安装 Python")
        print("✅ 用户无需安装任何依赖库 (pip install)")
        print("✅ 完全不会污染用户系统环境")
        print("✅ 可以在 macOS 10.13+ 上运行")
        print("✅ 已注册 quant-agent:// URL 协议")
        print()
        print("=" * 70)
        print("下一步")
        print("=" * 70)
        print("1. 测试应用:")
        print(f"   open {app_path}")
        print()
        print("2. 测试 URL 协议:")
        print("   open quant-agent://launch")
        print()
        print("3. 创建 .dmg 安装镜像:")
        print("   ./create_dmg.sh")
        print()
        print("4. （可选）代码签名:")
        print("   codesign --force --deep --sign - dist/quant-agent.app")
        print()
        print("5. 分发给用户")
        print("=" * 70)
    else:
        print("错误: 打包失败，未找到生成的应用")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("=" * 70)
        print(f"错误: {e}")
        print("=" * 70)
        print()
        print("提示: 请确保已安装 PyInstaller")
        print("  pip install pyinstaller")
        import traceback
        traceback.print_exc()
        sys.exit(1)
