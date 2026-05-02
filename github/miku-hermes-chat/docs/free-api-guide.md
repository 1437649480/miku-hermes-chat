# 免费 API 部署详解

本指南说明如何部署本项目依赖的免费 API 反代服务，实现零 API 费用的 AI 虚拟角色系统。

## 架构概述

```
┌─────────────────────────────────────────────┐
│                Hermes Gateway               │
│                                             │
│  主模型 (对话) ──→ deepseek-free-api :8000  │
│  辅助模型群  ──→ kimi-free-api    :8002   │
│  图片生成    ──→ CF Workers AI + Pollinations│
└─────────────────────────────────────────────┘
```

## 一、deepseek-free-api（主对话模型）

### 部署
```bash
cd ~
git clone https://github.com/LLM-Red-Team/deepseek-free-api.git
cd deepseek-free-api
pip install -r requirements.txt

# 配置 Token
cp .env.example .env
# 编辑 .env，填入 DeepSeek 网页版的用户 Token（多 Token 逗号分隔）

# 启动
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 接口
- **Base URL**: `http://127.0.0.1:8000/v1`
- **Chat 端点**: `POST /v1/chat/completions`
- **模型**: `deepseek-chat`（V4-Flash）、`deepseek-r1`（R1思考）
- **完全兼容** OpenAI Chat Completions API

### Windows 客户端接入
| 设置项 | 值 |
|--------|-----|
| API Base URL | `http://127.0.0.1:8000/v1` |
| API Key | 任意非空字符串 |
| 模型 | `deepseek-chat` |

> WSL2 默认将 localhost 端口自动转发到 Windows。

## 二、kimi-free-api（辅助模型群）

### 部署
```bash
cd ~
git clone https://github.com/HuangJHong/kimi-free-api.git kimi-free-api-new
cd kimi-free-api-new

# 安装依赖（Node.js 18+）
npm install

# 如果遇到 mime 包 CJS/ESM 兼容问题：
npm install mime@3

# 配置 Token
cp .env.example .env
# 编辑 .env，填入 REFRESH_TOKEN（Kimi 网页版的 refresh_token）

# 启动
npm start
```

### 获取 Kimi Refresh Token

1. 访问 https://kimi.moonshot.cn 并登录
2. 随便开启一个对话
3. 按 F12 → Application → Cookies → `kimi.moonshot.cn`
4. 复制 `refresh_token` 的值
5. 粘贴到 `.env` 文件的 `REFRESH_TOKEN` 字段

> Token 有效期约 13 个月，可通过 `/api/auth/token/refresh` 接口刷新。

### Token 自动刷新

本项目的 `scripts/refresh-kimi-token.py` 实现：
1. 解析 JWT Token，计算剩余有效期
2. 若剩余 < 30 天，自动调用刷新接口
3. 更新 Hermes config.yaml 中所有辅助模型的 api_key
4. 重启 Hermes Gateway

Windows 定时配置：
```powershell
# 使用 scripts/refresh-kimi-token.ps1
# 在 Windows 任务计划程序中创建每日定时任务
schtasks /create /tn "Kimi Token Refresh" /tr "powershell -File D:\桌面\opencil\scripts\refresh-kimi-token.ps1" /sc daily /st 03:00
```

## 三、图片生成

### Pollinations.ai（零账户，匿名）
- **端点**: `https://image.pollinations.ai/prompt/{prompt}`
- **无需** API Key
- **限速**: 严重（几次/天）
- **适用**: 偶尔使用

### Cloudflare Workers AI（推荐）
1. 注册免费 Cloudflare 账号: https://dash.cloudflare.com
2. 创建 API Token: https://dash.cloudflare.com/profile/api-tokens
   - 权限: Workers AI → Edit
3. 复制 Account ID
4. 设置环境变量：
```bash
export CLOUDFLARE_ACCOUNT_ID="your_account_id"
export CLOUDFLARE_API_TOKEN="your_api_token"
```
5. 修改 config.yaml:
```yaml
image_gen:
  model: flux-schnell
```
- **免费额度**: 10,000 神经元/天 ≈ 15-20 张图
- **模型**: FLUX.1 Schnell

## 四、备选方案

### arting-2api
```bash
git clone https://github.com/lzA6/arting-2api.git
cd arting-2api && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8090
```
需要 Arting.ai 的 auth token（从浏览器抓取）。

## 五、端口规划

| 端口 | 服务 | 用途 |
|------|------|------|
| 8000 | deepseek-free-api | 主对话 |
| 8001 | (预留) | 备用 |
| 8002 | kimi-free-api | 辅助模型群 |
| 8090 | arting-2api | 备用生图 |
| 8765 | Hermes Gateway | 核心网关 |
