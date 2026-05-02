# 系统架构说明

## 核心逻辑流

```
用户输入 (微信)
    │
    ▼
┌──────────────────────────────────────┐
│         Hermes Gateway               │
│                                      │
│  ┌────────────────────────────┐     │
│  │   消息预处理                 │     │
│  │   └ 平台适配 (Weixin)      │     │
│  │   └ 图片提取 (Vision)      │     │
│  │   └ URL 识别 (Web Extract) │     │
│  └────────────┬───────────────┘     │
│               ▼                      │
│  ┌────────────────────────────┐     │
│  │   Skill 引擎                │     │
│  │   └ miku.skill 注入         │     │
│  │   └ 角色人格匹配            │     │
│  │   └ 对话规则应用            │     │
│  └────────────┬───────────────┘     │
│               ▼                      │
│  ┌────────────────────────────┐     │
│  │   上下文管理                 │     │
│  │   └ 会话加载 (永久模式)    │     │
│  │   └ 自动压缩 (Compressor)  │     │
│  │   └ 长期记忆查询           │     │
│  └────────────┬───────────────┘     │
│               ▼                      │
│  ┌────────────────────────────────┐ │
│  │   工具决策 (Function Calling)  │ │
│  │   └ image_generate ─→ CF 插件 │ │
│  │   └ web_search                 │ │
│  │   └ code_execution             │ │
│  │   └ browser                    │ │
│  └────────────┬───────────────────┘ │
│               ▼                      │
│  ┌────────────────────────────┐     │
│  │   主模型调用                │     │
│  │   └ deepseek-free-api:8000 │     │
│  │   └ DeepSeek V3.2         │     │
│  └────────────┬───────────────┘     │
│               ▼                      │
│  ┌────────────────────────────┐     │
│  │   辅助模型调用 (并行)       │     │
│  │   └ 标题生成 (kimi:8002)  │     │
│  │   └ 上下文压缩 (kimi:8002)│     │
│  └────────────┬───────────────┘     │
│               ▼                      │
│  ┌────────────────────────────┐     │
│  │   响应后处理                 │     │
│  │   └ 消息格式化              │     │
│  │   └ 平台过滤 (微信优化)    │     │
│  │   └ 会话持久化             │     │
│  └────────────────────────────┘     │
└──────────────────────────────────────┘
    │
    ▼
用户收到回复 (微信)
```

## 多模型协作架构

### 主模型 (DeepSeek V3.2)
- **负责**: 核心对话生成、工具调用决策、角色扮演
- **通道**: deepseek-free-api (port 8000)
- **推理设置**: reasoning_effort = none (降本)

### 辅助模型群 (Kimi)
- **Vision**: 图片内容识别描述
- **Title Generation**: 自动生成会话标题
- **Compression**: 超长上下文智能压缩
- **Web Extract**: URL 内容提取
- **Session Search**: 历史会话搜索
- **Approval**: 敏感操作确认
- **MCP**: Model Context Protocol 处理
- **Skills Hub**: Skill 推荐与匹配

## 长期记忆机制

```
Hermes 默认: session_reset.mode = "both" (每天早上4点 + 24小时空闲)
本项目修改:  session_reset.mode = "none"  (永不自动重置)
```

- 存储路径: `D:\桌面\opencil\hermes-agent\bit by bit\`
- 存储格式: SQLite + JSON
- 空间预估: 50消息 + 10图片/天 ≈ 2.3MB/天，年约 0.8GB

## Token 自动刷新机制

```
Windows 任务计划程序 (每天 03:00)
    │
    ▼
refresh-kimi-token.ps1
    │
    ▼
WSL: refresh-kimi-token.py
    │
    ├── 读取 config.yaml 中的 JWT token
    ├── 解码 JWT → 计算剩余有效期
    ├── 若 < 30天 → POST /api/auth/token/refresh
    ├── 新 token 写入 config.yaml (所有辅助模型)
    └── 重启 Hermes Gateway
```

## 24×7 保活方案

**方案**: 关屏不关机 (Windows powercfg)

```powershell
powercfg /change standby-timeout-ac 0    # 永不休眠
powercfg /change monitor-timeout-ac 10   # 10分钟关屏
```

**辅助脚本**: `keep-awake.py` 使用 Win32 API `SetThreadExecutionState`
- `ES_CONTINUOUS | ES_SYSTEM_REQUIRED`: 禁止系统睡眠
- 显示器仍可正常关闭（节能）
- 每 30 秒调用一次保持唤醒状态

## 微信平台优化

### 本项目的定制修改
1. **禁止打断消息**: 检查 `event.source.platform.value != 'weixin'` 时发送 busy ack
2. **禁止标题生成警告**: 网关 `run.py` 中失败回调设为 `None`
3. **禁止推理过程**: 配置 `display.show_reasoning: false`
4. **禁止流式输出**: 配置 `display.streaming: false`

修改位置: `hermes-agent/gateway/run.py` 约第 1665、1671、1800 行
