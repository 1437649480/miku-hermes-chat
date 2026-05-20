"""
Miku Hermes Chat — TTS 语音合成接口定义

本文件仅定义 TTS 接口契约，完整实现见 hermes-agent/tools/tts_tool.py 。
任何 TTS 后端只要实现以下接口即可接入消息管道。
"""


# =============================================================================
# 1. 核心工具函数 — text_to_speech_tool
# =============================================================================
def text_to_speech_tool(
    text: str,
    output_path: Optional[str] = None,
) -> str:
    """
    Convert text to speech audio.

    行为:
      - 从 ~/.hermes/config.yaml (tts: 段) 读取 provider/voice 配置
      - 根据 provider 调用对应的生成函数
      - 返回 JSON: {"success": True, "file_path": "...", "media_tag": "MEDIA:..."}

    返回格式:
      {
        "success": True/False,
        "file_path": "/path/to/output.mp3",   # 生成的音频文件路径
        "media_tag": "MEDIA:/path/to/output.mp3",  # 消息管道使用的媒体标签
        "provider": "edge",                    # 使用的 TTS 提供商
        "characters": 42                       # 合成的字符数
      }

    Args:
        text (str): 要合成的文本
        output_path (str, optional): 自定义输出路径，默认 ~/voice-memos/<timestamp>.mp3
    """


# =============================================================================
# 2. TTS Provider 接口 — 添加新语音后端
# =============================================================================
"""
每个 TTS Provider 需要实现一个 _generate_<name>_tts(text, file_path, config) 函数:

    def _generate_xxx_tts(text: str, file_path: str, config: dict) -> None:
        '''
        Args:
            text:      待合成的文本
            file_path: 输出文件路径 (.mp3 或 .ogg)
            config:    tts 配置字典 (从 config.yaml 的 tts: 段加载)

        Raises:
            Exception: 合成失败时抛异常，由上层捕获并返回错误 JSON
        '''

在 tts_config.yaml 中注册:
    tts:
      provider: xxx           # 默认使用的 provider
      xxx:                    # provider 专属配置
        voice: xxx-voice
        api_key: ${XXX_API_KEY}
"""

# =============================================================================
# 3. 已支持的 TTS Provider 一览
# =============================================================================
SUPPORTED_PROVIDERS = {
    # ---- 免费方案（无需 API Key） ----
    "edge": {
        "description": "Microsoft Edge 浏览器内置 TTS，免费使用，中文语音质量好",
        "voice": "zh-CN-XiaoxiaoNeural",
        "dependencies": ["pip install edge-tts"],
        "audio_format": "mp3",
        "note": "当前默认方案"
    },
    "aivoicelab": {
        "description": "AI Voice Lab — 初音未来等虚拟角色语音，通过网站反代获取",
        "voice": "ja-female-hatsune-miku-cover",
        "dependencies": ["aivoicelab_core.py"],
        "audio_format": "mp3",
        "note": "需自行实现反代/调用逻辑，详见 docs/aivoicelab_AI翻唱_反代方法.md"
    },
    "neutts": {
        "description": "本地离线 TTS (NeuTTS)，免费，无需网络",
        "voice": "default",
        "dependencies": ["neutts_cli (需自行编译安装)"],
        "audio_format": "wav",
        "note": "适合离线/无GPU环境"
    },

    # ---- 商用/高质量方案（需 API Key） ----
    "elevenlabs": {
        "description": "最高质量 TTS，支持语音克隆，商业使用",
        "dependencies": ["pip install elevenlabs"],
        "audio_format": "mp3/ogg",
        "env": "ELEVENLABS_API_KEY"
    },
    "openai": {
        "description": "OpenAI TTS (gpt-4o-mini-tts)，支持情感控制",
        "dependencies": ["pip install openai"],
        "audio_format": "mp3/ogg",
        "env": "OPENAI_API_KEY"
    },

    # ---- 本地模型方案（需 GPU / 自行部署） ----
    "rvc": {
        "description": "RVC (Retrieval-based Voice Conversion) — 音色转换，可实现 Miku 音色",
        "voice": "Miku.pth + Miku.index",
        "dependencies": ["RVC 模型文件 (见 music/rvc/)"],
        "audio_format": "wav",
        "note": "流水线: Edge TTS 生成 → RVC 音色转换 → 输出 Miku 声线"
    },
    "kittentts": {
        "description": "KittenTTS — 轻量本地 TTS 模型 (25MB)，可自行训练角色语音",
        "voice": "Jasper",
        "dependencies": ["pip install kittentts"],
        "audio_format": "wav",
        "note": "适合 fine-tune 为 Miku 声线的本地方案"
    },
}

# =============================================================================
# 4. 发送接口 — send_voice (平台无关)
# =============================================================================
"""
def send_voice(chat_id, audio_path, caption=None) -> SendResult:
    '''
    将音频文件发送给指定对话。
    
    各平台 (WeChat/Telegram/Discord) 实现各自的 send_voice 方法。
    WeChat 版本位于 hermes-agent/gateway/platforms/weixin.py:send_voice()
    
    当前 WeChat 以文件附件形式发送 MP3，原生语音绿泡泡需要 .silk 格式。
    详见 docs/MP3转绿泡泡接口文档.txt
    '''

# WeChat 发送流程:
#   send_voice() → _send_file() → CDN 加密上传 → _outbound_media_builder()
#
# MEDIA_VOICE=4  (原生语音气泡，需 .silk 格式)
# MEDIA_FILE=3   (文件附件，当前使用 force_file_attachment=True)
"""

# =============================================================================
# 5. TTS 配置模板
# =============================================================================
TTS_CONFIG_EXAMPLE = """
# ~/.hermes/config.yaml 中的 tts: 段
tts:
  provider: edge                     # 默认 TTS provider
  edge:
    voice: zh-CN-XiaoxiaoNeural     # 微软神经网络中文女声

  # ---- 可选方案 ----
  # aivoicelab:
  #   modelname: ja-female-hatsune-miku-cover
  #   modelcat: animation
  #
  # elevenlabs:
  #   voice_id: pNInz6obpgDQGcFmaJgB
  #   model: eleven_multilingual_v2
  #
  # openai:
  #   model: gpt-4o-mini-tts
  #   voice: nova
  #
  # rvc:
  #   model_path: music/rvc/Miku.pth
  #   index_path: music/rvc/Miku.index
"""