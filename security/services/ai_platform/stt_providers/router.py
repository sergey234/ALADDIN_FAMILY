# -*- coding: utf-8 -*-
"""Route companion STT to Yandex (primary) with OpenAI EU backup."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from . import openai_whisper, yandex_speechkit

logger = logging.getLogger(__name__)


def _provider_env() -> str:
    return (os.getenv("COMPANION_STT_PROVIDER") or "auto").strip().lower()


def _fallback_provider_env() -> str:
    return (os.getenv("COMPANION_STT_FALLBACK_PROVIDER") or "openai_whisper").strip().lower()


def _module_for(name: str):
    if name in ("yandex", "yandex_speechkit", "speechkit"):
        return yandex_speechkit
    if name in ("openai", "openai_whisper", "whisper"):
        return openai_whisper
    return None


def server_stt_configured() -> bool:
    mode = _provider_env()
    if mode == "auto":
        return yandex_speechkit.configured() or openai_whisper.configured()
    mod = _module_for(mode)
    return bool(mod and mod.configured())


def active_provider_name() -> str:
    mode = _provider_env()
    if mode == "auto":
        if yandex_speechkit.configured():
            return yandex_speechkit.provider_id()
        if openai_whisper.configured():
            return openai_whisper.provider_id()
        return "none"
    mod = _module_for(mode)
    return mod.provider_id() if mod and mod.configured() else "none"


def _ordered_providers() -> list:
    mode = _provider_env()
    if mode == "auto":
        chain = []
        if yandex_speechkit.configured():
            chain.append(yandex_speechkit)
        fallback = _module_for(_fallback_provider_env())
        if fallback and fallback.configured() and fallback not in chain:
            chain.append(fallback)
        if openai_whisper.configured() and openai_whisper not in chain:
            chain.append(openai_whisper)
        return chain
    mod = _module_for(mode)
    return [mod] if mod and mod.configured() else []


def transcribe_with_fallback(
    audio_bytes: bytes,
    *,
    content_type: str = "audio/wav",
    language: str = "ru",
) -> Dict[str, Any]:
    providers = _ordered_providers()
    if not providers:
        raise ValueError("server_stt_unconfigured")

    last_error: ValueError | None = None
    for idx, mod in enumerate(providers):
        try:
            text, confidence = mod.transcribe(
                audio_bytes,
                content_type=content_type,
                language=language,
            )
            cleaned = (text or "").strip()
            if not cleaned:
                raise ValueError("empty_transcript")
            provider = mod.provider_id()
            logger.info(
                "companion_stt_ok provider=%s language=%s text_len=%s chain_index=%s",
                provider,
                language,
                len(cleaned),
                idx,
            )
            return {
                "text": cleaned,
                "confidence": confidence,
                "provider": provider,
                "language": language,
            }
        except ValueError as exc:
            last_error = exc
            if str(exc) == "empty_transcript":
                raise exc
            logger.warning(
                "companion_stt_provider_failed provider=%s reason=%s",
                mod.provider_id(),
                exc,
            )
            continue

    if last_error is not None:
        raise last_error
    raise ValueError("server_stt_unconfigured")
