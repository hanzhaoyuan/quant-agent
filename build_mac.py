#!/usr/bin/env python3
"""
Mac 平台构建脚本
自动化构建 .app 和 .dmg

使用方法：
    python build_mac.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

VERSION = "0.1.0"
APP_NAME = "QuantAgent"

def run_command(cmd, cwd=None, check=True):
    """执行命令并打印输出"""
    print(f"\n[执行] {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if check and result.returncode != 0:
        raise RuntimeError(f"命令执行失败: {cmd}")

    return result

def check_macos():
    """检查是否在 macOS 上运行"""
    if sys.platform != "darwin":
        print("❌ 此脚本仅在 macOS 上运行")
        print(f"   当前平台: {sys.platform}")
        sys.exit(1)

def clean_build():
    """清理旧的构建文件"""
    print("\n=== 清理旧的构建文件 ===")
    dirs_to_clean = ["build", "dist"]

    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"删除: {dir_path}")
            shutil.rmtree(dir_path)

def build_app():
    """构建 .app 应用"""
    print("\n=== 步骤 1: 构建 .app 应用 ===")

    # 检查 spec 文件是否存在
    spec_file = "quant-agent-mac.spec"
    if not Path(spec_file).exists():
        raise RuntimeError(f"找不到 {spec_file} 文件")

    # 运行 PyInstaller
    run_command(f"pyinstaller {spec_file}")

    app_path = Path(f"dist/{APP_NAME}.app")
    if not app_path.exists():
        raise RuntimeError("应用构建失败")

    print(f"✓ 应用已生成: {app_path}")

    # 显示应用大小
    size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
    print(f"  应用大小: {size / 1024 / 1024:.1f} MB")

    return app_path

def create_dmg_with_create_dmg(app_path):
    """使用 create-dmg 工具创建 DMG"""
    print("\n使用 create-dmg 工具...")

    dmg_name = f"{APP_NAME}-{VERSION}.dmg"

    # 删除旧的 DMG
    if Path(dmg_name).exists():
        os.remove(dmg_name)

    cmd = f"""
    create-dmg \\
      --volname "{APP_NAME}" \\
      --window-pos 200 120 \\
      --window-size 800 400 \\
      --icon-size 100 \\
      --icon "{APP_NAME}.app" 200 190 \\
      --hide-extension "{APP_NAME}.app" \\
      --app-drop-link 600 185 \\
      "{dmg_name}" \\
      "{app_path}"
    """

    run_command(cmd)
    return Path(dmg_name)

def create_dmg_manual(app_path):
    """手动创建 DMG（不依赖 create-dmg）"""
    print("\n手动创建 DMG...")

    dmg_name = f"{APP_NAME}-{VERSION}.dmg"
    temp_dmg = "temp.dmg"
    volume_name = APP_NAME

    # 删除旧文件
    for f in [dmg_name, temp_dmg]:
        if Path(f).exists():
            os.remove(f)

    # 1. 创建临时 DMG
    print("创建临时 DMG...")
    run_command(f'hdiutil create -size 200m -fs HFS+ -volname "{volume_name}" {temp_dmg}')

    # 2. 挂载
    print("挂载 DMG...")
    run_command(f'hdiutil attach {temp_dmg}')

    # 3. 复制应用
    print("复制应用...")
    run_command(f'cp -R "{app_path}" "/Volumes/{volume_name}/"')

    # 4. 创建 Applications 链接
    print("创建 Applications 链接...")
    run_command(f'ln -s /Applications "/Volumes/{volume_name}/Applications"')

    # 5. 卸载
    print("卸载 DMG...")
    run_command(f'hdiutil detach "/Volumes/{volume_name}"')

    # 6. 转换为压缩格式
    print("压缩 DMG...")
    run_command(f'hdiutil convert {temp_dmg} -format UDZO -o {dmg_name}')

    # 7. 清理
    os.remove(temp_dmg)

    return Path(dmg_name)

def create_dmg(app_path):
    """创建 DMG 安装包"""
    print("\n=== 步骤 2: 创建 DMG 安装包 ===")

    # 检查是否安装了 create-dmg
    result = run_command("which create-dmg", check=False)
    has_create_dmg = result.returncode == 0

    if has_create_dmg:
        print("✓ 检测到 create-dmg 工具")
        try:
            dmg_path = create_dmg_with_create_dmg(app_path)
        except:
            print("⚠ create-dmg 失败，使用手动方式")
            dmg_path = create_dmg_manual(app_path)
    else:
        print("⚠ 未安装 create-dmg，使用手动方式")
        print("  提示: 可以通过 'brew install create-dmg' 安装以获得更好的DMG")
        dmg_path = create_dmg_manual(app_path)

    if not dmg_path.exists():
        raise RuntimeError("DMG 创建失败")

    print(f"✓ DMG 已生成: {dmg_path}")
    print(f"  大小: {dmg_path.stat().st_size / 1024 / 1024:.1f} MB")

    return dmg_path

def test_instructions(app_path, dmg_path):
    """打印测试说明"""
    print("\n" + "=" * 70)
    print("✓ 构建完成！")
    print("=" * 70)

    print(f"\n📦 输出文件:")
    print(f"  应用:     {app_path}")
    print(f"  安装包:   {dmg_path}")

    print(f"\n🧪 测试步骤:")
    print(f"  1. 双击打开 {dmg_path}")
    print(f"  2. 将 {APP_NAME}.app 拖到 Applications 文件夹")
    print(f"  3. 从 Applications 启动 {APP_NAME}")
    print(f"  4. 测试 URL Scheme:")
    print(f"     在终端运行: open 'quant-agent://launch'")
    print(f"  5. 测试 HTTP 服务:")
    print(f"     在浏览器访问: http://127.0.0.1:17633/health")

    print(f"\n🔧 故障排查:")
    print(f"  - 如果 URL Scheme 不工作，运行:")
    print(f"    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user")
    print(f"  - 查看应用日志:")
    print(f"    tail -f /tmp/quant-agent.log")
    print(f"  - 移除隔离属性:")
    print(f"    xattr -d com.apple.quarantine /Applications/{APP_NAME}.app")

    print("\n" + "=" * 70)

def main():
    """主函数"""
    try:
        print("=" * 70)
        print(f"{APP_NAME} - Mac 平台构建脚本")
        print(f"版本: {VERSION}")
        print("=" * 70)

        # 检查平台
        check_macos()

        # 清理旧文件
        clean_build()

        # 构建应用
        app_path = build_app()

        # 创建 DMG
        dmg_path = create_dmg(app_path)

        # 打印测试说明
        test_instructions(app_path, dmg_path)

    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
