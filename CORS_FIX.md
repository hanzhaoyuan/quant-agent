# 解决云端访问本地 Agent 的 CORS 问题

## 问题原因

从云端域名（如 `http://43.138.248.158`）访问本地 Agent（`http://127.0.0.1:17633`）时，浏览器的 CORS 策略会阻止请求，导致检测失败并弹出"需要本地 Quant Agent 支持"的提示。

## 已修复

已将 `quant-agent/agent/main.py` 中的 CORS 配置修改为允许所有来源访问：

```python
# CORS 配置（允许所有来源访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 如何应用修复

### 方法一：重启开发服务器（推荐用于开发调试）

如果你正在使用开发模式运行 Agent：

1. **停止当前运行的 Agent**（如果正在运行）
   - 在命令行窗口按 `Ctrl+C` 停止

2. **重新启动 Agent**
   ```bash
   cd quant-agent
   python scripts/run_dev.py
   ```

3. **验证 CORS 是否生效**
   - 打开浏览器控制台（F12）
   - 从云端页面（http://43.138.248.158）访问并点击回测
   - 应该不再出现 CORS 错误

### 方法二：重新打包安装包（用于分发给用户）

如果你需要生成新的安装包：

1. **重新打包可执行文件**
   ```bash
   cd quant-agent
   python build.py
   ```
   生成的文件在：`dist/quant-agent.exe`

2. **（可选）制作安装程序**
   如果需要制作完整的安装程序：

   a. 确保已安装 [Inno Setup](https://jrsoftware.org/isdl.php)

   b. 运行打包脚本（如果有）：
   ```bash
   python build_installer.py
   ```

   或手动编译：
   - 打开 Inno Setup Compiler
   - 打开 `installer/setup.iss`
   - 点击 "Build" -> "Compile"
   - 生成的安装包在：`installer/output/QuantAgentSetup-0.1.0.exe`

3. **分发新的安装包**
   - 将新的安装包分发给用户
   - 用户安装后，从云端访问将不再有 CORS 问题

## 验证步骤

1. 确保本地 Agent 正在运行：
   ```bash
   curl http://127.0.0.1:17633/health
   ```

   应该返回：
   ```json
   {"ok": true, "name": "quant-agent", "version": "0.1.0"}
   ```

2. 从云端页面访问：
   - 打开 http://43.138.248.158
   - 点击"量化"标签
   - 打开策略文件
   - 点击"回测"按钮
   - 应该能够正常检测到本地 Agent，不再出现 CORS 错误

## 安全说明

允许所有来源访问本地 Agent 是安全的，因为：
1. Agent 只监听 `127.0.0.1`（本地回环地址），外网无法访问
2. Agent 运行在用户本地机器上，由用户自己控制
3. 即使允许所有来源，也只有本地浏览器能够连接到 `127.0.0.1`

## 下次部署前端时的建议

当你将前端部署到新的域名时，无需修改 Agent 的 CORS 配置，因为现在已经允许所有来源访问。
