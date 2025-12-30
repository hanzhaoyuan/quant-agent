#!/usr/bin/env python3
"""
Windows 安装程序构建脚本
使用 Inno Setup 创建安装程序
"""

import os
import sys
import subprocess
from pathlib import Path

def find_inno_setup():
    """查找 Inno Setup 编译器"""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\iscc.exe",
        r"C:\Program Files\Inno Setup 6\iscc.exe",
        r"C:\Program Files (x86)\Inno Setup 5\iscc.exe",
        r"C:\Program Files\Inno Setup 5\iscc.exe",
    ]

    for path in possible_paths:
        if Path(path).exists():
            return path

    return None

def check_prerequisites():
    """检查前置条件"""
    print("\n=== 检查前置条件 ===")

    # 1. 检查是否在 Windows 上
    if sys.platform != "win32":
        print("[X] 此脚本仅在 Windows 上运行")
        return False

    # 2. 检查 Inno Setup
    iscc_path = find_inno_setup()
    if not iscc_path:
        print("[X] 未找到 Inno Setup")
        print("\n请先安装 Inno Setup:")
        print("  1. 访问: https://jrsoftware.org/isdl.php")
        print("  2. 下载并安装最新版本")
        print("  3. 重新运行此脚本")
        return False

    print(f"[OK] 找到 Inno Setup: {iscc_path}")

    # 3. 检查 .iss 脚本文件
    iss_file = Path("quant-agent.iss")
    if not iss_file.exists():
        print(f"[X] 找不到 {iss_file}")
        return False

    print(f"[OK] 找到配置文件: {iss_file}")

    # 4. 检查 quant-agent.exe
    exe_file = Path("dist/installer/quant-agent.exe")
    if not exe_file.exists():
        print(f"[X] 找不到 {exe_file}")
        print("\n请先构建可执行文件:")
        print("  python build.py")
        return False

    print(f"[OK] 找到可执行文件: {exe_file}")
    print(f"  大小: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")

    return iscc_path

def build_installer(iscc_path):
    """构建安装程序"""
    print("\n=== 构建安装程序 ===")

    iss_file = "quant-agent.iss"

    print(f"编译脚本: {iss_file}")
    print(f"使用编译器: {iscc_path}")
    print()

    # 运行 Inno Setup 编译器
    cmd = [iscc_path, iss_file]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='gbk',  # Inno Setup 使用 GBK 编码
            errors='ignore'
        )

        # 打印输出
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print(f"\n[X] 构建失败（退出码: {result.returncode}）")
            return False

        # 检查输出文件
        output_file = Path("installer/output/QuantAgentSetup-0.1.0.exe")
        if not output_file.exists():
            print("\n[X] 未找到输出文件")
            return False

        print(f"\n[OK] 安装程序构建成功！")
        print(f"  文件: {output_file}")
        print(f"  大小: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

        return output_file

    except Exception as e:
        print(f"\n[X] 构建过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_instructions(output_file):
    """打印使用说明"""
    print("\n" + "=" * 70)
    print("[OK] 构建完成！")
    print("=" * 70)

    print(f"\n[*] 输出文件:")
    print(f"  {output_file.absolute()}")

    print(f"\n[*] 测试步骤:")
    print(f"  1. 双击运行安装程序:")
    print(f"     {output_file}")
    print(f"  2. 完成安装后，测试 URL 协议:")
    print(f"     在浏览器地址栏输入: quant-agent://launch")
    print(f"  3. 或从命令行测试:")
    print(f"     start quant-agent://launch")
    print(f"  4. 验证 HTTP 服务:")
    print(f"     curl http://127.0.0.1:17633/health")

    print(f"\n[*] 部署步骤:")
    print(f"  1. 上传安装程序到你的网站服务器")
    print(f"  2. 在前端更新下载链接 (QuantAgentService.ts):")
    print(f"     'windows': 'https://your-domain.com/downloads/QuantAgentSetup-0.1.0.exe'")
    print(f"  3. 用户下载并安装后，即可从网站启动 Agent")

    print(f"\n[*] 详细文档:")
    print(f"  查看 WINDOWS_INSTALLER_GUIDE.md 了解更多信息")

    print("\n" + "=" * 70)

def main():
    """主函数"""
    try:
        print("=" * 70)
        print("Quant Agent - Windows 安装程序构建工具")
        print("=" * 70)

        # 检查前置条件
        iscc_path = check_prerequisites()
        if not iscc_path:
            sys.exit(1)

        # 构建安装程序
        output_file = build_installer(iscc_path)
        if not output_file:
            sys.exit(1)

        # 打印使用说明
        print_instructions(output_file)

    except KeyboardInterrupt:
        print("\n\n[!] 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] 发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
