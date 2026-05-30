# -*- coding: utf-8 -*-
"""
Hybrid companion STT — server fallback only.

Privacy contract:
- Audio bytes processed in RAM; never written to disk for retention.
- Logs: duration, language, provider, confidence — never raw audio.
"""

from __future__ import annotations

import logging
import os
import struct
from typing import Any, Dict

from .stt_providers.openai_http import (
    OPENAI_TRANSCRIPTIONS_URL,
    http_error_reason,
    openai_api_key,
    openai_https_proxy,
    post_openai_multipart,
    post_via_proxy,
)
from .stt_providers.router import (
    active_provider_name,
    server_stt_configured as _router_configured,
    transcribe_with_fallback,
)

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = int(os.getenv("COMPANION_STT_MAX_BYTES", str(512 * 1024)))
MAX_DURATION_SEC = float(os.getenv("COMPANION_STT_MAX_AUDIO_SEC", "15"))

# Back-compat for tests / imports
_openai_api_key = openai_api_key
_openai_https_proxy = openai_https_proxy
_http_error_reason = http_error_reason
_post_openai_multipart = post_openai_multipart
_post_via_proxy = post_via_proxy


def server_stt_configured() -> bool:
    return _router_configured()


def _estimate_duration_sec(audio_bytes: bytes, content_type: str) -> float:
    ct = (content_type or "").lower()
    if "wav" in ct and len(audio_bytes) > 44:
        try:
            _chunk, _channels, sample_rate, _byte_rate, _block, bits = struct.unpack(
                "<4sIHHIIHH", audio_bytes[:36]
            )
            data_size = len(audio_bytes) - 44
            if sample_rate > 0 and bits > 0:
                return data_size / (sample_rate * (bits // 8))
        except struct.error:
            pass
    return min(MAX_DURATION_SEC, len(audio_bytes) / 4000.0)


def transcribe_audio_bytes(
    audio_bytes: bytes,
    *,
    content_type: str = "audio/wav",
    language: str = "ru",
) -> Dict[str, Any]:
    """Transcribe in-memory audio. Raises ValueError with reason code on failure."""
    if not audio_bytes:
        raise ValueError("empty_audio")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise ValueError("audio_too_large")
    duration = _estimate_duration_sec(audio_bytes, content_type)
    if duration > MAX_DURATION_SEC + 0.5:
        raise ValueError("audio_too_long")

    if not server_stt_configured():
        raise ValueError("server_stt_unconfigured")

    result = transcribe_with_fallback(
        audio_bytes,
        content_type=content_type,
        language=language[:8],
    )
    cleaned = str(result.get("text") or "").strip()
    if not cleaned:
        raise ValueError("empty_transcript")

    provider = str(result.get("provider") or active_provider_name())
    confidence = float(result.get("confidence") or 0.0)
    logger.info(
        "companion_stt_ok provider=%s language=%s duration_sec=%s confidence=%s text_len=%s",
        provider,
        language,
        round(duration, 2),
        round(confidence, 3),
        len(cleaned),
    )
    return {
        "text": cleaned,
        "confidence": confidence,
        "provider": provider,
        "language": language,
        "duration_sec": round(duration, 2),
    }


__all__ = [
    "OPENAI_TRANSCRIPTIONS_URL",
    "active_provider_name",
    "server_stt_configured",
    "transcribe_audio_bytes",
]
