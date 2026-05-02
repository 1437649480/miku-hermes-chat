# Miku Hermes Chat - 初音未来虚拟角色情感聊天系统

[![Hermes Agent](https://img.shields.io/badge/Powered%20by-Hermes%20Agent-blue)](https://github.com/NousResearch/hermes-agent)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen)]()
[![API Cost](https://img.shields.io/badge/API%20Cost-%C2%A50-brightgreen)]()

基于 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 框架构建的**初音未来（Hatsune Miku）虚拟角色情感聊天系统**。通过开源 Free API 反代技术实现零 API 费用的多模态 AI 女友体验，支持微信端实时对话、图片理解、长期记忆、上下文压缩及表情包生成。

## ✨ 核心特性

| 功能 | 状态 | 说明 |
|------|------|------|
| 💬 角色扮演聊天 | ✅ 完成 | 基于 miku.skill 的初音未来女友人格 |
| 🖼️ 图片识别 | ✅ 完成 | 发送图片自动描述，支持多模态理解 |
| 🧠 长期记忆 | ✅ 完成 | 会话永不自动重置，跨天记忆 |
| 📦 上下文压缩 | ✅ 完成 | 自动压缩超长对话历史 |
| 📝 标题自动生成 | ✅ 完成 | 会话自动命名 |
| 🌐 网页内容提取 | ✅ 完成 | URL 发送即解析 |
| 🎨 表情包/图片生成 | 🔧 测试中 | CF Workers AI + Pollinations.ai 双后端 |
| 🔄 Token 自动刷新 | ✅ 完成 | Windows 任务计划程序定时刷新 |
| ⚡ 24×7 保活 | ✅ 完成 | 关屏不关机，持续在线 |

## 🏗️ 架构概览

```
┌──────────────────────────────────────────────────────────────┐
│                      微信客户端 (iLink Bot)                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│              Hermes Gateway (WSL2, 8765)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │  miku.skill  │  │ Image Gen    │  │  Session Manager  │   │
│  │  (角色引擎)   │  │ (CF Plugin)  │  │  (永久记忆)        │   │
│  └─────────────┘  └──────────────┘  └───────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                 ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│ deepseek-free-api│ │ kimi-free-api │ │CF/Pollinations│
│ (Port 8000)     │ │ (Port 8002)  │ │ (Image Gen)  │
│ 主对话模型        │ │ 辅助模型群     │ │ 图片生成       │
└─────────────────┘ └──────────────┘ └──────────────┘
```

## 🚀 快速开始

### 前置条件
- Windows 10/11 + WSL2 (Ubuntu 24.04)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) 已安装
- Python 3.12+, Node.js 18+

### 1. 部署免费 API 反代
```bash
# deepseek-free-api (主对话)
git clone https://github.com/LLM-Red-Team/deepseek-free-api.git
cd deepseek-free-api && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# kimi-free-api (辅助模型 - 需 token)
git clone https://github.com/HuangJHong/kimi-free-api.git
cd kimi-free-api && npm install && npm start  # Port 8002
```

### 2. 安装 Miku Skill
```bash
cp -r miku.skill/ $HERMES_HOME/skills/miku/
```

### 3. 配置 Hermes
```bash
cp config-example/config.yaml.example $HERMES_HOME/config.yaml
# 编辑 config.yaml: 填入 Kimi token 和 DeepSeek API key
```

### 4. 安装生图插件
```bash
cp -r plugins/image_gen/cf/ $HERMES_HOME/../plugins/image_gen/cf/
```

### 5. 启动服务
```bash
bash scripts/start-all-services.sh
```

## 📁 项目结构

```
miku-hermes-chat/
├── README.md                       # 本文件
├── miku.skill/                     # 初音未来角色定义
│   └── SKILL.md                    #    人格、对话规则、示例
├── config-example/                 # 配置模板（已脱敏）
│   └── config.yaml.example
├── plugins/                        # 自定义 Hermes 插件
│   └── image_gen/cf/               #    免费生图插件
│       ├── plugin.yaml
│       └── __init__.py
├── scripts/                        # 运维脚本
│   ├── start-all-services.sh       #   全服务启动 (WSL2)
│   ├── restart-gateway.sh          #   网关重启
│   ├── 启动Miku网关.bat            #   一键重启 (Windows)
│   ├── keep-awake.py               #   系统保活
│   ├── 睡眠保活模式.bat            #   保活启动
│   ├── refresh-kimi-token.py       #   Kimi Token 自动刷新
│   ├── refresh-kimi-token.ps1      #   Windows 任务计划
│   └── refresh-kimi-token.bat      #   刷新批处理
└── docs/                           # 文档
    ├── free-api-guide.md           #   免费 API 部署详解
    └── architecture.md             #   系统架构说明
```

## 🔑 免费 API 说明

本项目完全基于**免费 API 反代**技术，实现零 API 费用：

| 服务 | 上游 | 端口 | 说明 |
|------|------|------|------|
| deepseek-free-api | DeepSeek 网页版 | 8000 | 主对话，OpenAI 兼容 |
| kimi-free-api | Kimi 网页版 | 8002 | 辅助模型群 |
| CF Workers AI | Cloudflare | (云端) | Flux 生图，免费 15 张/天 |
| Pollinations.ai | Pollinations | (云端) | Flux 生图，匿名有限速 |

详细部署指南见 [docs/free-api-guide.md](docs/free-api-guide.md)。

## 🎭 Role Character

本项目使用了初音未来（Hatsune Miku）作为虚拟角色原型：
- **官方设定**: Crypton Future Media
- **形象设计**: KEI
- **音源提供**: 藤田咲
- **代表作品**: 甩葱歌、Tell Your World、世界第一的公主殿下

角色 Skill 文件基于官方设定与同人文化创作，用于虚拟女友角色扮演体验。

## 📄 License

Apache 2.0 - 详见 [LICENSE](LICENSE)

## 🙏 致谢

- [Nous Research](https://github.com/NousResearch) - Hermes Agent 框架
- [LLM-Red-Team](https://github.com/LLM-Red-Team) - deepseek-free-api
- [HuangJHong](https://github.com/HuangJHong) - kimi-free-api (Vision 修复)
- [lzA6](https://github.com/lzA6) - arting-2api 参考
- Crypton Future Media - 初音未来角色版权
