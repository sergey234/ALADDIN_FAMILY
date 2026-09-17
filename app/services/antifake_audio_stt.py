"""afhub-p2-01 — STT for audio/call → same text scam pipeline (RU+EN).

Prefer client/preset transcript; else companion server STT (ru then en).
Never invent speech — soft-fail with None when STT unavailable.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def _content_type_from_name(file_name: str) -> str:
    lowered = (file_name or "").lower()
    if lowered.endswith(".wav"):
        return "audio/wav"
    if lowered.endswith(".mp3"):
        return "audio/mpeg"
    if lowered.endswith(".m4a"):
        return "audio/mp4"
    if lowered.endswith(".aac"):
        return "audio/aac"
    return "audio/wav"


def try_transcript(
    file_bytes: bytes,
    *,
    file_name: str = "upload",
    extra: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[str], str]:
    """Return (text, lang_tag). lang_tag: ru|en|preset|unknown.

    Preset keys (extra): stt_transcript, transcript, text.
    """
    extra = extra or {}
    for key in ("stt_transcript", "transcript", "text"):
        preset = str(extra.get(key) or "").strip()
        if preset:
            lang = str(extra.get("stt_lang") or extra.get("lang") or "preset").lower()
            if lang.startswith("en"):
                return preset, "en"
            if lang.startswith("ru"):
                return preset, "ru"
            return preset, "preset"

    if not file_bytes:
        return None, "unknown"

    preferred = str(extra.get("stt_lang") or extra.get("lang") or "ru").lower()
    order = ["en", "ru"] if preferred.startswith("en") else ["ru", "en"]

    try:
        from security.services.ai_platform.companion_stt import (
            server_stt_configured,
            transcribe_audio_bytes,
        )
    except Exception:
        return None, "unknown"

    if not server_stt_configured():
        return None, "unknown"

    ctype = _content_type_from_name(file_name)
    for lang in order:
        try:
            result = transcribe_audio_bytes(
                file_bytes,
                content_type=ctype,
                language=lang,
            )
            text = str(result.get("text") or "").strip()
            if text:
                return text, lang
        except Exception:
            continue
    return None, "unknown"


def try_ru_transcript(
    file_bytes: bytes,
    *,
    file_name: str = "upload",
    extra: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Backward-compatible wrapper."""
    text, _lang = try_transcript(file_bytes, file_name=file_name, extra=extra)
    return text
