# Mac 平台快速入门

## 🚀 快速开始（3步完成）

### 1. 准备环境（仅首次）

```bash
# 安装 PyInstaller
pip install pyinstaller

# 可选：安装 create-dmg 以生成更专业的DMG
brew install create-dmg
```

### 2. 构建应用

```bash
# 在 Mac 上运行
cd quant-agent
python build_mac.py
```

构建完成后会生成：
- `dist/QuantAgent.app` - Mac 应用
- `QuantAgent-0.1.0.dmg` - 安装包

### 3. 测试

```bash
# 方式1：直接运行应用测试
open dist/QuantAgent.app

# 方式2：安装后测试URL Scheme
open QuantAgent-0.1.0.dmg
# 拖拽到 Applications 文件夹
open "quant-agent://launch"

# 方式3：测试HTTP服务
curl http://127.0.0.1:17633/health
```

## 📋 核心文件说明

| 文件 | 用途 |
|------|------|
| `quant-agent-mac.spec` | PyInstaller Mac 配置 |
| `build_mac.py` | 自动构建脚本 |
| `MAC_SUPPORT_GUIDE.md` | 详细技术文档 |

## ⚙️ 关键配置

### URL Scheme 配置
在 `quant-agent-mac.spec` 中：

```python
'CFBundleURLTypes': [
    {
        'CFBundleURLName': 'Quant Agent Protocol',
        'CFBundleURLSchemes': ['quant-agent'],  # 自定义协议
    }
]
```

### 平台检测
前端自动检测操作系统并提供对应下载链接：

```typescript
// 在 QuantAgentService.ts 中已实现
quantAgentService.getDownloadUrl()  // 自动返回Mac的.dmg链接
quantAgentService.getPlatformName() // 返回 "macOS"
```

## 🐛 常见问题

### Q: URL Scheme 不工作？

```bash
# 重建 Launch Services 数据库
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user

# 重新安装应用
rm -rf /Applications/QuantAgent.app
cp -R dist/QuantAgent.app /Applications/
```

### Q: 应用被macOS阻止？

```bash
# 移除隔离属性
xattr -d com.apple.quarantine /Applications/QuantAgent.app

# 或在系统偏好设置中允许
# 系统偏好设置 > 安全性与隐私 > 通用 > 仍要打开
```

### Q: 如何查看日志？

```bash
# 查看应用输出
tail -f /tmp/quant-agent.log

# 查看系统日志
log stream --predicate 'process == "QuantAgent"' --level debug
```

## ✅ 完整工作流程

```
用户访问Web前端
    ↓
点击"回测"按钮
    ↓
前端检测Agent状态 (HTTP GET /health)
    ↓
如果未运行 → 调用 window.location.href = "quant-agent://launch"
    ↓
macOS 根据 Info.plist 找到 QuantAgent.app
    ↓
启动应用，监听 127.0.0.1:17633
    ↓
前端重新检测，确认Agent已就绪
    ↓
发送回测任务 (HTTP POST /tasks)
```

## 🎯 下一步

1. **开发阶段**：
   - 使用 `python scripts/run_dev.py --reload` 快速开发
   - 直接运行 `dist/QuantAgent.app` 测试

2. **发布阶段**（需要Apple开发者账号）：
   ```bash
   # 代码签名
   codesign --deep --force --verify --verbose \
     --sign "Developer ID Application: Your Name" \
     dist/QuantAgent.app

   # 创建签名的DMG
   codesign --force --verify --verbose \
     --sign "Developer ID Application: Your Name" \
     QuantAgent-0.1.0.dmg

   # 公证
   xcrun notarytool submit QuantAgent-0.1.0.dmg \
     --apple-id "your@email.com" \
     --password "app-specific-password" \
     --team-id "TEAM_ID" \
     --wait
   ```

3. **用户安装**：
   - 下载 `.dmg` 文件
   - 双击打开
   - 拖拽到 Applications 文件夹
   - 完成！

## 📚 更多信息

详细技术文档请参考：[MAC_SUPPORT_GUIDE.md](./MAC_SUPPORT_GUIDE.md)
