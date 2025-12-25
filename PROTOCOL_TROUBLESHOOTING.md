# Quant Agent 协议注册问题排查指南

## 问题现象

安装了 Quant Agent，但是 Web 端点击"回测"后仍然提示"需要安装 Quant Agent"。

## 排查步骤

### 步骤 1: 检查协议注册状态

运行检查脚本：
```bash
cd quant-agent
check_protocol.bat
```

**预期输出**:
```
[1] 检查协议注册...
   ✓ 协议已注册

[2] 检查 URL Protocol 标记...
   ✓ URL Protocol 已设置

[3] 检查命令行配置...
   ✓ 命令行已配置
```

**如果看到 "✗ 协议未注册"**，说明安装不成功，请重新安装：
1. 先运行 `python build.py` 生成 exe
2. 使用 Inno Setup 重新编译安装程序
3. 以管理员身份运行安装程序

---

### 步骤 2: 测试协议是否可用

在浏览器中打开测试文件：
```bash
# 方法 1: 直接打开文件
quant-agent/test_protocol.html

# 方法 2: 在浏览器地址栏输入
file:///D:/code/quant-project/quant-agent/test_protocol.html
```

**测试流程**:
1. 点击 "🚀 唤起 Agent"
   - 浏览器可能会弹出确认对话框，点击"打开"
   - 应该能看到 Agent 程序启动

2. 点击 "🏥 检查健康状态"
   - 如果 Agent 正在运行，应该显示成功
   - 如果失败，说明 Agent 没有运行或端口被占用

3. 点击 "🔄 开始完整测试"
   - 这会模拟 Web 前端的完整流程
   - 唤起 → 等待 5 秒 → 检查（最多重试 3 次）

---

### 步骤 3: 检查 Agent 是否能正常启动

#### 3.1 手动启动测试

双击运行：
```
C:\Program Files\QuantAgent\quant-agent.exe
```

或使用调试批处理：
```bash
cd quant-agent
run_debug.bat
```

**预期输出**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
[2025-12-25 20:00:00] [quant-agent] [INFO] quant-agent v0.1.0 started
[2025-12-25 20:00:00] [quant-agent] [INFO] Listening on 127.0.0.1:17633
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:17633 (Press CTRL+C to quit)
```

**如果启动失败**，检查：
- 端口 17633 是否被占用：`netstat -ano | findstr :17633`
- Python 环境是否正确（打包后不应该需要 Python）
- 是否有杀毒软件拦截

#### 3.2 测试健康接口

Agent 启动后，在浏览器访问：
```
http://127.0.0.1:17633/health
```

**预期响应**:
```json
{
  "ok": true,
  "name": "quant-agent",
  "version": "0.1.0"
}
```

---

### 步骤 4: 检查协议注册的命令行

打开注册表编辑器 (`Win+R` → `regedit`)，导航到：
```
HKEY_CLASSES_ROOT\quant-agent\shell\open\command
```

**预期值**（默认项）:
```
"C:\Program Files\QuantAgent\quant-agent.exe" "%1"
```

**常见问题**:
- 路径错误（文件不存在）
- 缺少双引号导致路径解析失败
- `%1` 参数位置不正确

---

### 步骤 5: 检查浏览器控制台日志

打开 Web 前端，按 `F12` 打开开发者工具，切换到 Console 标签：

1. 打开策略文件（如 MAPlus.py）
2. 点击"回测"按钮
3. 查看控制台输出

**正常流程日志**:
```
Quant Agent 正在运行 - 版本: 0.1.0
```

**需要唤起的日志**:
```
Agent 未运行: [错误信息]
尝试通过自定义协议唤起 Agent...
已发送唤起请求，等待 Agent 启动...
第 1/3 次检查 Agent 状态...
第 2/3 次检查 Agent 状态...
✓ Agent 启动成功！
```

**未安装的日志**:
```
Agent 未运行: [错误信息]
尝试通过自定义协议唤起 Agent...
已发送唤起请求，等待 Agent 启动...
第 1/3 次检查 Agent 状态...
第 2/3 次检查 Agent 状态...
第 3/3 次检查 Agent 状态...
✗ Agent 未能启动，可能未安装
```

---

## 常见问题及解决方案

### 问题 1: 协议已注册但唤起无响应

**可能原因**:
- 浏览器安全策略阻止了协议唤起
- Windows 防火墙或杀毒软件拦截

**解决方案**:
1. 检查浏览器是否弹出确认对话框（可能被拦截）
2. 在浏览器设置中允许协议唤起
3. 添加 Agent 到杀毒软件白名单

### 问题 2: Agent 启动缓慢

**可能原因**:
- 首次启动需要解压内嵌的 Python 环境
- 杀毒软件实时扫描拖慢启动

**解决方案**:
1. 已经将等待时间增加到 3 秒 + 最多 3 次重试（共约 9 秒）
2. 如果仍然不够，可以调整 `QuantAgentService.ts` 中的参数：
   ```typescript
   private readonly INITIAL_WAIT = 5000; // 改为 5 秒
   private readonly MAX_RETRIES = 5; // 改为 5 次重试
   ```

### 问题 3: 端口被占用

**检查方法**:
```bash
netstat -ano | findstr :17633
```

**如果端口被占用**:
1. 找到占用进程的 PID（最后一列数字）
2. 结束进程：`taskkill /F /PID [进程ID]`
3. 或者修改 Agent 配置使用其他端口（需要同时修改前端配置）

### 问题 4: 权限问题

**现象**: Agent 无法在 `Program Files` 目录创建日志文件

**解决方案**:
1. 以管理员身份运行 Agent
2. 或者在安装时选择用户目录：
   ```iss
   DefaultDirName={userpf}\QuantAgent
   ```

---

## 重新安装步骤

如果以上排查都失败，建议完全重新安装：

### 1. 卸载现有版本

```
控制面板 → 程序和功能 → Quant Agent → 卸载
```

或运行：
```
C:\Program Files\QuantAgent\unins000.exe
```

### 2. 清理注册表（可选）

手动删除（或使用 CCleaner 等工具）：
```
HKEY_CLASSES_ROOT\quant-agent
```

### 3. 重新构建和安装

```bash
# 1. 重新打包
cd quant-agent
python build.py

# 2. 检查生成的文件
dir dist\quant-agent.exe

# 3. 使用 Inno Setup 编译安装程序
# 打开 installer/setup.iss
# Build → Compile

# 4. 运行安装程序（以管理员身份）
installer\output\QuantAgentSetup-0.1.0.exe
```

### 4. 验证安装

安装完成后：
1. 运行 `check_protocol.bat` 检查协议注册
2. 打开 `test_protocol.html` 测试协议功能
3. 在 Web 前端测试回测功能

---

## 技术细节

### 协议注册原理

Windows 自定义协议通过注册表实现：

```
HKCR\quant-agent
├── (Default) = "URL:Quant Agent Protocol"
├── URL Protocol = ""
├── DefaultIcon
│   └── (Default) = "C:\...\quant-agent.exe,0"
└── shell
    └── open
        └── command
            └── (Default) = "C:\...\quant-agent.exe" "%1"
```

当浏览器访问 `quant-agent://launch` 时：
1. Windows 查找注册表 `HKCR\quant-agent`
2. 读取 `shell\open\command` 的值
3. 执行命令：`"C:\...\quant-agent.exe" "quant-agent://launch"`

### Web 端检测流程

```
1. 尝试访问 /health (3秒超时)
   ├─ 成功 → Agent 正在运行 ✓
   └─ 失败 ↓

2. 调用 quant-agent://launch
   └─ 等待 3 秒 ↓

3. 重试检测（最多 3 次，间隔 2 秒）
   ├─ 成功 → Agent 已启动 ✓
   └─ 失败 → Agent 未安装 ✗
```

总等待时间：3秒（初始）+ 3次×2秒（重试）= 最多 9 秒

---

## 开发调试

### 修改等待时间

编辑 `src/services/QuantAgentService.ts`:
```typescript
private readonly INITIAL_WAIT = 3000;  // 初始等待（毫秒）
private readonly RETRY_DELAY = 2000;   // 重试间隔（毫秒）
private readonly MAX_RETRIES = 3;      // 最大重试次数
```

### 查看详细日志

在浏览器控制台启用详细日志：
```javascript
localStorage.setItem('debug', 'quant-agent:*');
```

### 手动测试协议

在浏览器控制台：
```javascript
window.location.href = 'quant-agent://launch';
```

---

## 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. `check_protocol.bat` 的完整输出
2. `test_protocol.html` 的测试结果截图
3. Agent 手动启动的日志
4. 浏览器控制台的完整日志
5. Windows 版本和浏览器版本

---

**最后更新**: 2025-12-25
