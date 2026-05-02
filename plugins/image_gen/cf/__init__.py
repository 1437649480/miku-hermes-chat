"""Free image generation backend via Cloudflare Workers AI + Pollinations.ai fallback.

Primary: Cloudflare Workers AI (Flux) — requires free CF account.
Fallback: Pollinations.ai direct URL — rate-limited but needs no account.

Environment variables:
    CLOUDFLARE_ACCOUNT_ID  — Cloudflare account ID (hex string)
    CLOUDFLARE_API_TOKEN   — Cloudflare API token with Workers AI permission
"""

from __future__ import annotations

import base64
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO,
    ImageGenProvider,
    error_response,
    resolve_aspect_ratio,
    success_response,
)

logger = logging.getLogger(__name__)

CF_API = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"

_MODELS: Dict[str, Dict[str, Any]] = {
    "flux-schnell": {
        "display": "FLUX.1 Schnell (CF)",
        "speed": "~8s",
        "strengths": "Fast, free via Cloudflare Workers AI",
        "backend": "cf",
    },
    "pollinations": {
        "display": "Pollinations.ai (Free)",
        "speed": "~10s",
        "strengths": "No account needed, rate-limited",
        "backend": "pollinations",
    },
}

DEFAULT_MODEL = "flux-schnell"

_SIZES_CF = {
    "landscape": (1024, 576),
    "square": (1024, 1024),
    "portrait": (576, 1024),
}


def _images_cache_dir() -> Path:
    try:
        from hermes_constants import get_hermes_home

        path = get_hermes_home() / "cache" / "images"
    except Exception:
        path = Path(os.path.expanduser("~/.hermes/cache/images"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_image_bytes(data: bytes, prefix: str = "image") -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short = uuid.uuid4().hex[:8]
    path = _images_cache_dir() / f"{prefix}_{ts}_{short}.png"
    path.write_bytes(data)
    return path


def _load_config() -> Dict[str, Any]:
    try:
        from hermes_cli.config import load_config

        cfg = load_config()
        section = cfg.get("image_gen") if isinstance(cfg, dict) else None
        return section if isinstance(section, dict) else {}
    except Exception:
        return {}


def _resolve_model() -> Tuple[str, Dict[str, Any]]:
    cfg = _load_config()
    candidate = cfg.get("model")
    if isinstance(candidate, str) and candidate in _MODELS:
        return candidate, _MODELS[candidate]
    return DEFAULT_MODEL, _MODELS[DEFAULT_MODEL]


def _generate_cf(prompt: str, width: int, height: int) -> bytes:
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not account_id or not api_token:
        raise ValueError(
            "CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN must be set. "
            "Get them from https://dash.cloudflare.com/ (free account)."
        )

    url = CF_API.format(account_id=account_id)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt}

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text[:500]
        raise RuntimeError(f"CF Workers AI error (HTTP {resp.status_code}): {detail}")

    return resp.content


def _generate_pollinations(prompt: str, width: int, height: int) -> bytes:
    encoded = requests.utils.quote(prompt, safe="")
    url = POLLINATIONS_URL.format(prompt=encoded)
    params = {"width": width, "height": height, "seed": int(time.time()) % 100000, "nofeed": "true"}
    resp = requests.get(url, params=params, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"Pollinations.ai error (HTTP {resp.status_code}): {resp.text[:300]}")
    return resp.content


class CFFreeImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "cf"

    @property
    def display_name(self) -> str:
        return "CF Free (Cloudflare + Pollinations)"

    def is_available(self) -> bool:
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": mid,
                "display": meta["display"],
                "speed": meta["speed"],
                "strengths": meta["strengths"],
                "price": "free",
            }
            for mid, meta in _MODELS.items()
        ]

    def default_model(self) -> Optional[str]:
        return DEFAULT_MODEL

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "CF Free (Cloudflare Workers AI)",
            "badge": "free",
            "tag": "Free Flux images via Cloudflare Workers AI + Pollinations.ai fallback",
            "env_vars": [
                {
                    "key": "CLOUDFLARE_ACCOUNT_ID",
                    "prompt": "Cloudflare Account ID (from dash.cloudflare.com)",
                    "url": "https://dash.cloudflare.com/",
                },
                {
                    "key": "CLOUDFLARE_API_TOKEN",
                    "prompt": "Cloudflare API Token (with Workers AI permission)",
                    "url": "https://dash.cloudflare.com/profile/api-tokens",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        prompt = (prompt or "").strip()
        aspect = resolve_aspect_ratio(aspect_ratio)

        if not prompt:
            return error_response(
                error="Prompt is required",
                error_type="invalid_argument",
                provider="cf",
                aspect_ratio=aspect,
            )

        model_id, meta = _resolve_model()
        backend = meta.get("backend", "cf")
        width, height = _SIZES_CF.get(aspect, (1024, 1024))

        errors = []

        if backend == "cf":
            try:
                image_bytes = _generate_cf(prompt, width, height)
            except Exception as e:
                errors.append(f"CF: {e}")
                logger.warning("CF Workers AI failed: %s, trying Pollinations fallback", e)
                try:
                    image_bytes = _generate_pollinations(prompt, width, height)
                except Exception as e2:
                    errors.append(f"Pollinations: {e2}")
                    return error_response(
                        error="; ".join(errors),
                        error_type="all_backends_failed",
                        provider="cf",
                        model=model_id,
                        prompt=prompt,
                        aspect_ratio=aspect,
                    )
        else:
            try:
                image_bytes = _generate_pollinations(prompt, width, height)
            except Exception as e:
                errors.append(f"Pollinations: {e}")
                try:
                    image_bytes = _generate_cf(prompt, width, height)
                except Exception as e2:
                    errors.append(f"CF: {e2}")
                    return error_response(
                        error="; ".join(errors),
                        error_type="all_backends_failed",
                        provider="cf",
                        model=model_id,
                        prompt=prompt,
                        aspect_ratio=aspect,
                    )

        try:
            saved_path = _save_image_bytes(image_bytes, prefix=f"cf_{model_id}")
        except Exception as exc:
            return error_response(
                error=f"Could not save image: {exc}",
                error_type="io_error",
                provider="cf",
                model=model_id,
                prompt=prompt,
                aspect_ratio=aspect,
            )

        return success_response(
            image=str(saved_path),
            model=model_id,
            prompt=prompt,
            aspect_ratio=aspect,
            provider="cf",
            extra={"width": width, "height": height, "backend": backend},
        )


def register(ctx) -> None:
    ctx.register_image_gen_provider(CFFreeImageGenProvider())
