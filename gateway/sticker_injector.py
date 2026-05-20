import os
import re
import random
import time
import logging
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

PICTURES_BASE = Path.home() / ".hermes" / "skills" / "miku" / "pictures"

EMOTION_RULES = [
    {
        "name": "开心",
        "keywords": ["哈哈", "好棒", "太好了", "耶", "厉害", "恭喜", "nice", "赞",
                      "开心", "高兴", "快乐", "成功", "赢了", "太棒了", "好耶"],
        "stickers": [
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_nice.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_哈哈哈哈.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_打call.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_赞.png",
            "06_bilibili_200/miku_only/329-未来有你5周年/未来有你_好耶.png",
            "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_开心撒花.png",
            "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_棒棒哒.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_干杯.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_太棒了.png",
            "01_miratsu/cv5897018_真棒.png",
        ],
    },
    {
        "name": "撒娇",
        "keywords": ["想你", "陪我", "人家", "抱抱", "贴贴", "亲亲", "喜欢你",
                      "不理我", "嘛", "期待", "喜欢"],
        "stickers": [
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_抱抱.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_贴贴.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_拜托拜托.png",
            "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_啾咪.png",
            "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_爱你.png",
            "06_bilibili_200/miku_only/714-初音未来圣诞快乐/初音未来圣诞快乐_发射爱心.png",
            "01_miratsu/miratsu_喜欢你.png",
        ],
    },
    {
        "name": "安慰",
        "keywords": ["加油", "别难过", "陪你", "辛苦了", "没关系", "会好的",
                      "心疼", "累了", "休息", "抱抱"],
        "stickers": [
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_相信你.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_打气.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_摸头.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_加油.png",
            "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_暖暖的.png",
        ],
    },
    {
        "name": "傲娇",
        "keywords": ["切", "才没有", "谁要", "哼", "嫌弃", "无语", "啊这",
                      "酸了", "才不是", "笨蛋", "讨厌"],
        "stickers": [
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_嫌弃.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_无语.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_啊这.png",
            "06_bilibili_200/miku_only/329-未来有你5周年/未来有你_酸了.png",
            "06_bilibili_200/miku_only/329-未来有你5周年/未来有你_生闷气.png",
            "01_miratsu/miku不是坏孩子.png",
            "01_miratsu/miratsu_啊这.jpg",
        ],
    },
    {
        "name": "难过",
        "keywords": ["呜呜", "哭了", "委屈", "心疼", "难过", "伤心", "叹气",
                      "不开心", "烦", "郁闷", "寂寞"],
        "stickers": [
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_哭了.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_委屈.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_自闭.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_叹气.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_泪目.png",
            "06_bilibili_200/miku_only/329-未来有你5周年/未来有你_委屈.png",
        ],
    },
    {
        "name": "惊讶",
        "keywords": ["诶", "什么", "真的吗", "不会吧", "居然", "OMG", "天哪",
                      "哇", "吓", "没想到", "吃惊"],
        "stickers": [
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_吃惊.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_问号.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_忽然出现.png",
            "06_bilibili_200/miku_only/329-未来有你5周年/未来有你_真的么.png",
            "06_bilibili_200/miku_only/714-初音未来圣诞快乐/初音未来圣诞快乐_OMG.png",
        ],
    },
    {
        "name": "日常",
        "keywords": ["早安", "晚安", "再见", "困了", "饿了", "吃饭", "睡觉",
                      "工作", "学习", "天气", "在吗"],
        "stickers": [
            "06_bilibili_200/miku_only/162-雪未来/雪未来_早安.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_干饭.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_睡了.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_困了.png",
            "06_bilibili_200/miku_only/162-雪未来/雪未来_赖床.png",
            "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_困困_乏了.png",
            "01_miratsu/晚安.jpg",
            "01_miratsu/吧唧吧唧吃东西.png",
            "01_miratsu/我来了或者偷看.png",
        ],
    },
]

CONTEXT_RULES = {
    "食物": ["吃", "饭", "餐", "饿", "零食", "奶茶", "蛋糕", "火锅"],
    "睡觉": ["睡觉", "睡了", "困", "晚安", "休息", "躺"],
    "喜欢": ["喜欢你", "爱你", "表白", "在一起", "想你"],
    "天气冷": ["冷", "雪", "冬天", "降温"],
    "节日": ["圣诞", "新年", "春节", "生日", "中秋"],
}

CONTEXT_STICKERS = {
    "食物": [
        "01_miratsu/吧唧吧唧吃东西.png",
        "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_干饭.png",
        "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_端碗.png",
    ],
    "睡觉": [
        "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_睡了.png",
        "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_困了.png",
        "01_miratsu/晚安.jpg",
    ],
    "喜欢": [
        "01_miratsu/miratsu_喜欢你.png",
        "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_爱你.png",
        "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_表白.png",
    ],
    "天气冷": [
        "06_bilibili_200/miku_only/714-初音未来圣诞快乐/初音未来圣诞快乐_好冷.png",
        "06_bilibili_200/miku_only/162-雪未来/雪未来_下雪了.png",
    ],
    "节日": [
        "06_bilibili_200/miku_only/714-初音未来圣诞快乐/初音未来圣诞快乐_圣诞快乐.png",
        "06_bilibili_200/miku_only/4525-初音未来三连快乐表情包/初音未来三连快乐表情包_新年快乐.png",
    ],
}

TIME_STICKERS = {
    "morning": [
        "06_bilibili_200/miku_only/162-雪未来/雪未来_早安.png",
    ],
    "noon": [
        "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_干饭.png",
        "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_端碗.png",
    ],
    "afternoon": [
        "06_bilibili_200/miku_only/162-雪未来/雪未来_喝奶茶.png",
        "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_赏樱.png",
    ],
    "evening": [
        "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_睡了.png",
        "06_bilibili_200/miku_only/162-雪未来/雪未来_赖床.png",
    ],
    "night": [
        "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_困了.png",
        "06_bilibili_200/miku_only/1330-樱花未来/樱花未来_困困_乏了.png",
        "01_miratsu/晚安.jpg",
    ],
}


class StickerInjector:
    def __init__(self):
        self._history: dict[str, list[float]] = {}
        self._MIN_INTERVAL = 2

    def _get_time_period(self) -> str:
        hour = datetime.now().hour
        if 6 <= hour < 11:
            return "morning"
        elif 11 <= hour < 14:
            return "noon"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _can_send(self, chat_id: str) -> bool:
        history = self._history.get(chat_id, [])
        now = time.time()
        recent = [t for t in history if now - t < 300]
        self._history[chat_id] = recent

        if len(recent) >= 1 and (now - recent[-1]) < 30:
            return False
        if len(recent) >= 2 and (now - recent[-1]) < 60:
            return False
        return True

    def _record_send(self, chat_id: str):
        self._history.setdefault(chat_id, []).append(time.time())

    def _check_user_sticker_request(self, user_msg: str) -> bool:
        triggers = ["发个表情", "发表情", "表情包", "来个表情", "给个表情",
                     "发张图", "来张图", "斗图", "发图"]
        return any(t in user_msg for t in triggers)

    def _detect_emotion(self, response_text: str, user_msg: str) -> Optional[dict]:
        combined = response_text + " " + user_msg
        best = None
        best_count = 0

        for rule in EMOTION_RULES:
            count = sum(1 for kw in rule["keywords"] if kw in combined)
            if count > best_count:
                best_count = count
                best = rule

        if best and best_count >= 1:
            return best

        for ctx_name, ctx_kws in CONTEXT_RULES.items():
            if any(kw in combined for kw in ctx_kws):
                return {
                    "name": ctx_name,
                    "keywords": ctx_kws,
                    "stickers": CONTEXT_STICKERS.get(ctx_name, []),
                }

        return None

    def _select_sticker(self, rule: dict, response_text: str, user_msg: str) -> Optional[str]:
        combined = response_text + " " + user_msg

        for ctx_name, ctx_kws in CONTEXT_RULES.items():
            if any(kw in combined for kw in ctx_kws) and ctx_name in CONTEXT_STICKERS:
                candidates = CONTEXT_STICKERS[ctx_name]
                if candidates:
                    return random.choice(candidates)

        time_period = self._get_time_period()
        if rule["name"] == "日常":
            time_candidates = TIME_STICKERS.get(time_period, [])
            if time_candidates and random.random() < 0.6:
                return random.choice(time_candidates)

        stickers = rule.get("stickers", [])
        if not stickers:
            return None
        return random.choice(stickers)

    def inject_sticker(
        self,
        response: str,
        user_message: str,
        chat_id: str,
        already_has_media: bool = False,
    ) -> str:
        if already_has_media and "MEDIA:" in response:
            return response

        force = self._check_user_sticker_request(user_message)
        if not force and not self._can_send(chat_id):
            logger.debug("[StickerInjector] Rate limited for chat %s", chat_id)
            return response

        if not force:
            rule = self._detect_emotion(response, user_message)
            if not rule:
                logger.debug("[StickerInjector] No emotion detected")
                return response
        else:
            rule = {"name": "日常", "keywords": [], "stickers": EMOTION_RULES[-1]["stickers"]}

        sticker_rel = self._select_sticker(rule, response, user_message)
        if not sticker_rel:
            return response

        sticker_path = PICTURES_BASE / sticker_rel
        if not sticker_path.exists():
            logger.warning("[StickerInjector] Sticker file not found: %s", sticker_path)
            fallback = self._get_fallback_sticker()
            if fallback:
                sticker_path = fallback
            else:
                return response

        self._record_send(chat_id)
        media_tag = f"MEDIA:{sticker_path}"
        logger.info(
            "[StickerInjector] Injecting sticker (category=%s): %s",
            rule["name"],
            sticker_rel,
        )
        return response.rstrip() + "\n" + media_tag

    def _get_fallback_sticker(self) -> Optional[Path]:
        fallbacks = [
            "06_bilibili_200/miku_only/162-雪未来/雪未来_嘿嘿.png",
            "06_bilibili_200/miku_only/115-初音未来13周年/初音未来_喜欢.png",
        ]
        for fb in fallbacks:
            p = PICTURES_BASE / fb
            if p.exists():
                return p
        return None


_injector: Optional[StickerInjector] = None


def get_sticker_injector() -> StickerInjector:
    global _injector
    if _injector is None:
        _injector = StickerInjector()
    return _injector
