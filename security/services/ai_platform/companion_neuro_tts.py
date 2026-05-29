# -*- coding: utf-8 -*-
"""ElevenLabs Flash TTS for Premium companion (server-side, cached)."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import urllib.error
import urllib.request
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple

from .modules.companion_neuro_tts import is_premium_subscription

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5").strip()
ELEVENLABS_BASE = os.getenv("ELEVENLABS_API_BASE", "https://api.elevenlabs.io/v1").rstrip("/")

# VOICE-PREM-04: три разных voice id (🦄🧞🧑) — все обязательны до пилота 03
_HERO_IDS = ("unicorn", "genie", "aladdin")
_DEFAULT_VOICE_BY_CHARACTER: Dict[str, str] = {
    "genie": os.getenv("ELEVENLABS_VOICE_GENIE", "").strip(),
    "unicorn": os.getenv("ELEVENLABS_VOICE_UNICORN", "").strip(),
    "aladdin": os.getenv("ELEVENLABS_VOICE_ALADDIN", "").strip(),
}

_CACHE: "OrderedDict[str, bytes]" = OrderedDict()
_CACHE_MAX = int(os.getenv("COMPANION_TTS_CACHE_MAX", "30"))


def all_hero_voice_ids_configured() -> bool:
    """VOICE-PREM-04: каждый герой — свой ElevenLabs voice id."""
    return all(_DEFAULT_VOICE_BY_CHARACTER.get(h) for h in _HERO_IDS)


def neuro_tts_configured() -> bool:
    return bool(ELEVENLABS_API_KEY) and all_hero_voice_ids_configured()


def voice_id_for_character(character_id: str) -> Optional[str]:
    cid = (character_id or "unicorn").strip().lower()
    return _DEFAULT_VOICE_BY_CHARACTER.get(cid) or None


def _cache_key(character_id: str, text: str, lang: str) -> str:
    digest = hashlib.sha256(f"{character_id}|{lang}|{text}".encode("utf-8")).hexdigest()
    return digest


def _cache_get(key: str) -> Optional[bytes]:
    data = _CACHE.get(key)
    if data is not None:
        _CACHE.move_to_end(key)
    return data


def _cache_put(key: str, audio: bytes) -> None:
    _CACHE[key] = audio
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)


def estimate_speech_seconds(text: str) -> int:
    """Грубая оценка для voice meter (~14 символов/сек RU)."""
    n = len((text or "").strip())
    return max(1, min(120, (n + 13) // 14))


def synthesize_neuro_tts(
    *,
    text: str,
    character_id: str,
    lang: str = "ru",
) -> Tuple[bytes, bool, str]:
    """
    Returns (audio_bytes, cached, content_type).
    Raises ValueError with machine-readable reason on failure.
    """
    trimmed = (text or "").strip()
    if not trimmed:
        raise ValueError("empty_text")
    if len(trimmed) > 2000:
        raise ValueError("text_too_long")

    if not neuro_tts_configured():
        raise ValueError("neuro_tts_unconfigured")

    voice_id = voice_id_for_character(character_id)
    if not voice_id:
        raise ValueError("voice_id_missing")

    key = _cache_key(character_id, trimmed, lang)
    hit = _cache_get(key)
    if hit is not None:
        return hit, True, "audio/mpeg"

    url = f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}"
    payload = {
        "text": trimmed,
        "model_id": ELEVENLABS_MODEL,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            audio = resp.read()
            content_type = resp.headers.get("Content-Type") or "audio/mpeg"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        logger.warning("ElevenLabs HTTP %s: %s", exc.code, body)
        raise ValueError(f"elevenlabs_http_{exc.code}") from exc
    except urllib.error.URLError as exc:
        logger.warning("ElevenLabs network error: %s", exc)
        raise ValueError("elevenlabs_network") from exc

    if not audio:
        raise ValueError("empty_audio")

    _cache_put(key, audio)
    return audio, False, content_type.split(";")[0].strip() or "audio/mpeg"


def build_tts_response_payload(
    audio: bytes,
    *,
    cached: bool,
    content_type: str,
    duration_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    return {
        "audio_base64": base64.b64encode(audio).decode("ascii"),
        "content_type": content_type,
        "provider": "elevenlabs",
        "cached": cached,
        "duration_seconds": duration_seconds,
    }


def assert_premium_tts_allowed(subscription_level: str) -> None:
    if not is_premium_subscription(subscription_level):
        raise ValueError("neuro_tts_requires_premium")
