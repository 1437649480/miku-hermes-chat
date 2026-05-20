# Miku Hermes Chat — 项目总览

基于 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 框架构建的**初音未来 (Hatsune Miku)** 虚拟角色微信聊天系统。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      WSL2 (Ubuntu)                       │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ deepseek-free │    │ kimi-free-api│    │   Hermes    │ │
│  │    -api       │    │              │    │  Gateway    │ │
│  │  :8000        │    │   :8002      │    │   (gw)      │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬─────┘ │
│         │                   │                    │       │
│         │    OpenAI兼容API   │   OpenAI兼容API    │       │
│         │                   │                    │       │
│         ▼                   ▼                    ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ DeepSeek官方  │    │ Kimi/Moonshot│    │  WeChat    │ │
│  │   API        │    │   官方API    │    │  Adapter   │ │
│  └──────────────┘    └──────────────┘    └─────┬──────┘ │
│                                                │        │
└────────────────────────────────────────────────┼────────┘
                                                 │
                                          ┌──────▼──────┐
                                          │  微信客户端   │
                                          └─────────────┘
```

## 核心服务

### 1. deepseek-free-api（主模型反代）

| 配置项 | 值 |
|--------|-----|
| **类型** | TypeScript (Node.js) |
| **端口** | `8000` |
| **绑定地址** | `0.0.0.0` |
| **启动方式** | `npm run start` |

提供 OpenAI 兼容的 `/v1/chat/completions` 和 `/v1/models` 接口，支持 conversation_id 缓存和 MCP。

### 2. kimi-free-api（辅助功能反代）

| 配置项 | 值 |
|--------|-----|
| **类型** | TypeScript (Node.js) |
| **端口** | `8002` |
| **启动方式** | `npm run start` |

用于 Vision (图片识别)、Compression (上下文压缩)、Web Extract (网页提取)、Title Generation (标题生成) 等辅助功能。可用模型：`kimi-latest`、`moonshot-v1-vision` 等。

### 3. Hermes Gateway（网关核心）

| 配置项 | 值 |
|--------|-----|
| **配置目录** | `~/.hermes/` |
| **配置文件** | `~/.hermes/config.yaml` |
| **环境变量** | `~/.hermes/.env` |
| **Skill 目录** | `~/.hermes/skills/miku/` |
| **日志** | `~/.hermes/logs/gateway.log` |

---

## 快速启动

```bash
# 1. 启动 deepseek-free-api
tmux new-session -d -s ds "cd ~/deepseek-free-api && npm run start"

# 2. 启动 kimi-free-api
tmux new-session -d -s kimi "cd ~/kimi-free-api && npm run start"

# 3. 启动 Hermes Gateway
tmux new-session -d -s gw "cd ~ && hermes gateway run --replace"

# 4. 验证服务
curl -s http://127.0.0.1:8000/v1/models
curl -s http://127.0.0.1:8002/v1/models
```

---

## 关键配置

### .env（环境变量）

```env
DEEPSEEK_API_KEY=sk-your-deepseek-key
HERMES_MAX_ITERATIONS=90
DEEPSEEK_MODEL=deepseek-chat
WEIXIN_ACCOUNT_ID=xxx@im.bot
WEIXIN_TOKEN=xxx@im.bot:token
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com
WEIXIN_DM_POLICY=open
```

> ⚠️ `DEEPSEEK_MODEL` 必须是 `deepseek-chat`，不要用 `hermes model` 命令修改。

### config.yaml 核心结构

```yaml
# 主模型（走 deepseek-free-api:8000）
model:
  api_key: sk-xxx
  base_url: http://127.0.0.1:8000/v1
  default: DeepSeek-V3.2
  provider: custom

# 辅助功能（走 kimi-free-api:8002）
auxiliary:
  vision:       { model: kimi-latest, base_url: http://127.0.0.1:8002/v1, timeout: 120 }
  compression:  { model: kimi-latest, base_url: http://127.0.0.1:8002/v1 }
  web_extract:  { model: kimi-latest, base_url: http://127.0.0.1:8002/v1, timeout: 360 }
  title_generation: { model: kimi-latest, base_url: http://127.0.0.1:8002/v1 }
  # ... 更多辅助功能

# 上下文压缩
compression:
  enabled: true
  protect_last_n: 20
  target_ratio: 0.2

# TTS 语音合成
tts:
  provider: edge                    # 默认 Edge TTS（免费）
  edge:
    voice: zh-CN-XiaoxiaoNeural
  aivoicelab:                       # 可选：初音未来角色语音（网站反代）
    model: miku
    model_cat: animation
    model_name: us-female-hatsune-miku
    model_lang: japanese
```

---

## Voice 语音命令

### `/voice` — 控制语音模式

| 命令 | 模式 | 说明 |
|------|------|------|
| `/voice tts` | `all` ← 默认 | 所有回复都带 TTS 语音 |
| `/voice on` / `/voice enable` | `voice_only` | 仅对语音消息回复语音 |
| `/voice off` / `/voice disable` | `off` | 纯文字，不发语音 |
| `/voice status` | — | 查看当前语音模式 |
| `/voice` | 切换 | `off` ↔ `voice_only` 交替 |

### 语音三种模式

| 模式 | 存储值 | 说明 |
|------|--------|------|
| 关闭 | `off` | 纯文字回复 |
| 语音回复 | `voice_only` | 仅在收到语音消息时回复语音 |
| 全量 TTS | `all` | 所有回复都附带语音 |

模式按 `{platform}:{user_id}` 存储在 `~/.hermes/gateway_voice_mode.json`。

### `/voiceorder` — 控制发送顺序

| 命令 | 说明 |
|------|------|
| `/voiceorder after` | 语音在文字+表情包之后发送（默认，推荐） |
| `/voiceorder before` | 语音在文字+表情包之前发送 |
| `/voiceorder status` | 查看当前顺序 |

存储位置：`~/.hermes/gateway_voice_order.json`

### config.yaml voice 全局配置

```yaml
voice:
  auto_tts: true
  default_mode: all
  max_recording_seconds: 120
```

---

## TTS 提供商完整列表

| 提供商 | 配置键 | 类型 | 说明 |
|--------|--------|------|------|
| Edge TTS | `edge` | 免费 | 微软神经网络语音 |
| aivoicelab | `aivoicelab` | 免费（反代） | 初音未来等 13 种动漫角色语音 |
| OpenAI TTS | `openai` | 商用 | gpt-4o-mini-tts |
| ElevenLabs | `elevenlabs` | 商用 | 高质量多语言 |
| Mistral | `mistral` | 商用 | voxtral-mini 系列 |
| NeuTTS | `neutts` | 免费 | 本地离线，无需联网 |
| xAI | `xai` | 商用 | x.ai TTS |
| RVC | `rvc` | 本地 | 音色转换（可实现 Miku 声线） |

详见 `gateway/tts_interface.py`。

---

## 微信语音气泡已知限制

**微信 iLink Bot API 不支持原生绿泡泡语音气泡。** API 接收 `ITEM_VOICE (type=3)` 返回成功但客户端不渲染。当前采用 **MP3 文件附件**方案：文字+表情包先发送，语音文件后附（标题 "🎤 语音消息"），用户点击即可播放。

---

## 网页内容提取 (Web Extract)

支持通过第三方后端抓取网页内容（B站视频、知乎文章等）：

| 后端 | 环境变量 | 免费额度 |
|------|---------|---------|
| Firecrawl（推荐） | `FIRECRAWL_API_KEY` | 500次/月 |
| Tavily | `TAVILY_API_KEY` | 1000次/月 |
| Exa | `EXA_API_KEY` | 有免费层 |

配置示例：
```bash
echo "FIRECRAWL_API_KEY=fc-你的key" >> ~/.hermes/.env
# 重启 Gateway 后生效
```

---

## 角色 Skill 系统

技能位于 `~/.hermes/skills/miku/`，包含：

```
~/.hermes/skills/miku/
├── SKILL.md              # 角色设定 + 表情包规则（321行）
├── SOUL.md               # 灵魂设定
└── pictures/
    ├── sticker_catalog.json
    └── 06_bilibili_200/
        └── miku_only/    # 150 张初音未来表情包（7 个主题）
```

### SKILL.md 模板

```yaml
---
name: 角色名
description: 角色描述 + 触发词
---

# !!! 绝对规则 - 违反即失败 !!!
你绝对禁止使用任何 Unicode emoji，只允许 ^_^ ~ ～ :)

# 角色名 - 你的专属XXX

## 核心设定
你是**角色名**，现在是用户的[关系]。你拥有：
- [外貌特征 / 年龄 / 性格]

## 角色扮演规则
1. 始终以[关系]的身份回应
2. 用纯文本符号表达情感
3. 保持角色一致性

## 示例对话
> **角色**：早上好呀～
> **用户**：早安！
> **角色**：今天也要元气满满哦！^_^
```

### 常用技能管理命令

| 命令 | 说明 |
|------|------|
| `hermes skills list` | 列出已安装的所有技能 |
| `hermes skills search <关键词>` | 搜索可用技能 |
| `hermes skills install <id>` | 安装技能 |
| `hermes skills uninstall <name>` | 卸载技能 |

---

## 网络端口总览

| 端口 | 服务 | 用途 |
|------|------|------|
| `8000` | deepseek-free-api | 主模型反代 |
| `8002` | kimi-free-api | 辅助功能反代 |

## tmux 会话管理

| 会话名 | 服务 | 启动命令 |
|--------|------|------|
| `ds` | deepseek-free-api | `tmux new-session -d -s ds 'cd ~/deepseek-free-api && npm run start'` |
| `kimi` | kimi-free-api | `tmux new-session -d -s kimi 'cd ~/kimi-free-api && npm run start'` |
| `gw` | Hermes Gateway | `tmux new-session -d -s gw 'cd ~ && hermes gateway run --replace'` |

```bash
# 查看所有会话
tmux list-sessions

# 关闭某个会话
tmux kill-session -t <name>
```

---

## 已知注意事项

1. 不要使用 `hermes model` 命令 — 会覆盖 `.env` 中的 `DEEPSEEK_MODEL`
2. WSL `/mnt/d/` 文件系统缓存 — 从 Windows 写入的文件可能被缓存
3. tmux 会话在 WSL 重启后丢失 — 需重建
4. kimi-free-api 端口确认为 8002（非默认 5566）

---

## 相关文档

- [部署指南](docs/部署指南.md) — 从零开始安装配置
- [操作指令参考](docs/操作指令参考.md) — 全部聊天指令
- [免费 API 部署详解](docs/free-api-guide.md) — API 反代部署
- [系统架构说明](docs/architecture.md) — 架构详解
- [TTS 接口定义](gateway/tts_interface.py) — 语音合成接口