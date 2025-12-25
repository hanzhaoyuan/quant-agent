"""
打包 quant-agent 为独立可执行文件

运行方式: python build.py
输出: dist/quant-agent.exe (完全独立，不依赖任何外部 Python 环境)

环境隔离说明:
- 打包后的 .exe 包含完整的 Python 解释器
- 所有依赖库（FastAPI, uvicorn, pydantic 等）都内嵌在可执行文件中
- 用户无需安装 Python 或任何依赖包
- 完全不会污染用户系统环境
"""
import PyInstaller.__main__
import os
import shutil
import sys


def main():
    print("=" * 70)
    print("Quant Agent - PyInstaller 打包工具")
    print("=" * 70)
    print()

    # 清理旧的构建文件
    print("[1/4] 清理旧的构建文件...")
    for directory in ['build', 'dist']:
        if os.path.exists(directory):
            print(f"  - 删除 {directory}/")
            shutil.rmtree(directory)

    print()
    print("[2/4] 准备打包...")
    print("  - 入口文件: agent/main.py")
    print("  - 打包模式: 单文件 (--onefile)")
    print("  - 控制台: 启用 (方便查看日志)")
    print()

    # 打包参数
    print("[3/4] 开始打包...")
    PyInstaller.__main__.run([
        'agent/main.py',                    # 入口文件

        # 基本设置
        '--name=quant-agent',               # 可执行文件名
        '--onefile',                        # 打包成单个文件（所有依赖都在里面）
        '--console',                        # 显示控制台（方便看日志）

        # 包含 uvicorn 的隐藏导入
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.http.h11_impl',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',

        # 图标（可选，未来添加）
        # '--icon=installer/icon.ico',

        # 清理临时文件
        '--clean',

        # 不显示确认对话框
        '--noconfirm',
    ])

    print()
    print("[4/4] 打包完成！")
    print()
    print("=" * 70)
    print("打包结果")
    print("=" * 70)

    exe_path = os.path.join('dist', 'quant-agent.exe')
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"生成的可执行文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        print()
        print("=" * 70)
        print("重要提示 - 环境隔离说明")
        print("=" * 70)
        print("✅ 这是一个完全独立的可执行文件")
        print("✅ 用户无需安装 Python")
        print("✅ 用户无需安装任何依赖库 (pip install)")
        print("✅ 完全不会污染用户系统环境")
        print("✅ 可以在任何 Windows 系统上运行")
        print()
        print("=" * 70)
        print("下一步")
        print("=" * 70)
        print("1. 测试可执行文件:")
        print(f"   {exe_path}")
        print()
        print("2. 制作安装程序:")
        print("   - 使用 Inno Setup 打开 installer/setup.iss")
        print("   - 编译生成 QuantAgentSetup.exe")
        print()
        print("3. 分发安装包给用户")
        print("=" * 70)
    else:
        print("错误: 打包失败，未找到生成的可执行文件")
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
        sys.exit(1)
