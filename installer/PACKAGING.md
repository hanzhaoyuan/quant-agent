# 打包快速参考

## 文件说明

- `build.py` - PyInstaller 打包脚本（生成独立 .exe）
- `installer/setup.iss` - Inno Setup 安装程序配置

## 打包流程

### 步骤 1: 生成独立可执行文件

```bash
# 安装打包工具
pip install pyinstaller

# 运行打包脚本
python build.py
```

**输出**: `dist/quant-agent.exe` (约 40-60 MB)

**特性**:
- 包含完整 Python 解释器
- 包含所有依赖库（FastAPI, uvicorn, pydantic 等）
- 用户无需安装 Python
- 完全不污染用户环境

### 步骤 2: 制作安装程序

1. 下载 [Inno Setup](https://jrsoftware.org/isdl.php) 并安装
2. 打开 Inno Setup Compiler
3. 打开 `installer/setup.iss`
4. 点击 Build -> Compile

**输出**: `installer/output/QuantAgentSetup-0.1.0.exe` (约 45-65 MB)

**特性**:
- 专业的安装向导
- 自动注册 `quant-agent://` 协议
- 创建快捷方式
- 完整的卸载功能

## 测试

### 测试独立可执行文件

```bash
dist\quant-agent.exe
```

访问 http://127.0.0.1:17633/health 验证

### 测试安装程序

1. 双击 `installer/output/QuantAgentSetup-0.1.0.exe`
2. 按照向导完成安装
3. 从开始菜单或桌面启动 Quant Agent
4. 访问 http://127.0.0.1:17633/health 验证

## 环境隔离验证

在没有安装 Python 的电脑上测试：
- ✅ 可执行文件能正常运行
- ✅ 不需要安装任何依赖
- ✅ 不会创建 Python 环境
- ✅ 不会修改系统环境变量（除了注册自定义协议）

## 常见问题

**Q: 打包后的文件为什么这么大？**
A: 因为包含了完整的 Python 解释器（约 20-30 MB）和所有依赖库。这是实现环境隔离的代价，但用户体验更好。

**Q: 用户卸载后会留下残留吗？**
A: 不会。Inno Setup 会完全删除安装目录和注册表项。

**Q: 可以在 Python 2.x 系统上运行吗？**
A: 可以！打包后的 .exe 完全独立，不依赖系统的 Python 环境。

**Q: 如何减小文件大小？**
A: 可以使用 UPX 压缩，或排除不必要的依赖。但不建议过度优化，稳定性更重要。

## 分发建议

1. 为安装包添加数字签名（避免 SmartScreen 警告）
2. 提供 SHA256 校验和
3. 在官网提供下载链接
4. 编写用户安装指南

## 详细文档

- 完整说明: [README.md](../README.md)
- 技术细节: [installer/README.md](README.md)
