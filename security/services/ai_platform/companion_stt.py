# -*- coding: utf-8 -*-
"""
Hybrid companion STT — server fallback only.

Privacy contract:
- Audio bytes processed in RAM; never written to disk for retention.
- Logs: duration, language, provider, confidence — never raw audio.
"""

from __future__ import annotations

import io
import json
import logging
import os
import struct
import uuid
from typing import Any, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = int(os.getenv("COMPANION_STT_MAX_BYTES", str(512 * 1024)))
MAX_DURATION_SEC = float(os.getenv("COMPANION_STT_MAX_AUDIO_SEC", "15"))


def server_stt_configured() -> bool:
    key = _openai_api_key()
    return bool(key)


def _openai_api_key() -> str:
    for name in ("COMPANION_STT_OPENAI_API_KEY", "OPENAI_API_KEY"):
        val = (os.getenv(name) or "").strip()
        if val:
            return val
    return ""


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
    # Rough fallback for compressed m4a/caf (~32 kbps speech)
    return min(MAX_DURATION_SEC, len(audio_bytes) / 4000.0)


def transcribe_audio_bytes(
    audio_bytes: bytes,
    *,
    content_type: str = "audio/wav",
    language: str = "ru",
) -> Dict[str, Any]:
    """
    Transcribe in-memory audio. Raises ValueError with reason code on failure.
    """
    if not audio_bytes:
        raise ValueError("empty_audio")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise ValueError("audio_too_large")
    duration = _estimate_duration_sec(audio_bytes, content_type)
    if duration > MAX_DURATION_SEC + 0.5:
        raise ValueError("audio_too_long")

    api_key = _openai_api_key()
    if not api_key:
        raise ValueError("server_stt_unconfigured")

    text, confidence = _transcribe_openai_whisper(
        audio_bytes,
        content_type=content_type,
        language=language[:8],
        api_key=api_key,
    )
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("empty_transcript")

    logger.info(
        "companion_stt_ok provider=%s language=%s duration_sec=%s confidence=%s text_len=%s",
        "openai_whisper",
        language,
        round(duration, 2),
        round(confidence, 3),
        len(cleaned),
    )
    return {
        "text": cleaned,
        "confidence": confidence,
        "provider": "openai_whisper",
        "language": language,
        "duration_sec": round(duration, 2),
    }


def _transcribe_openai_whisper(
    audio_bytes: bytes,
    *,
    content_type: str,
    language: str,
    api_key: str,
) -> Tuple[str, float]:
    boundary = f"----AladdinSTT{uuid.uuid4().hex}"
    filename = "speech.wav" if "wav" in content_type else "speech.m4a"
    mime = content_type if content_type else "application/octet-stream"

    parts: list[bytes] = []
    for field, value in (
        ("model", "whisper-1"),
        ("language", language.split("-")[0] if language else "ru"),
        ("response_format", "verbose_json"),
    ):
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{field}"\r\n\r\n'.encode())
        parts.append(f"{value}\r\n".encode())
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    )
    parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
    parts.append(audio_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urlopen(req, timeout=45) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        logger.warning(
            "companion_stt_openai_http_error status=%s detail=%s",
            exc.code,
            detail,
        )
        raise ValueError("server_stt_provider_error") from exc
    except URLError as exc:
        logger.warning("companion_stt_openai_network_error error=%s", exc)
        raise ValueError("server_stt_network_error") from exc

    text = str(payload.get("text") or "").strip()
    confidence = 0.85
    segments = payload.get("segments")
    if isinstance(segments, list) and segments:
        scores = [
            float(s.get("avg_logprob", 0))
            for s in segments
            if isinstance(s, dict) and s.get("avg_logprob") is not None
        ]
        if scores:
            # Map logprob [-2..0] → rough 0..1
            avg = sum(scores) / len(scores)
            confidence = max(0.0, min(1.0, 1.0 + avg / 2.5))
    return text, confidence
