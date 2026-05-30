# -*- coding: utf-8 -*-
"""Yandex Cloud SpeechKit STT — primary server fallback for RU VPS."""

from __future__ import annotations

import json
import logging
import os
from typing import Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

YANDEX_STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


def _api_key() -> str:
    for name in ("YANDEX_SPEECHKIT_API_KEY", "YANDEX_CLOUD_API_KEY"):
        val = (os.getenv(name) or "").strip()
        if val:
            return val
    return ""


def _folder_id() -> str:
    return (os.getenv("YANDEX_SPEECHKIT_FOLDER_ID") or os.getenv("YANDEX_FOLDER_ID") or "").strip()


def configured() -> bool:
    return bool(_api_key())


def provider_id() -> str:
    return "yandex_speechkit"


def _pcm_from_wav(audio_bytes: bytes, content_type: str) -> bytes:
    ct = (content_type or "").lower()
    if "wav" in ct and len(audio_bytes) > 44:
        return audio_bytes[44:]
    return audio_bytes


def transcribe(
    audio_bytes: bytes,
    *,
    content_type: str = "audio/wav",
    language: str = "ru",
) -> Tuple[str, float]:
    api_key = _api_key()
    if not api_key:
        raise ValueError("server_stt_unconfigured")

    lang = (language or "ru").replace("_", "-")
    if not lang.lower().startswith("ru"):
        lang = "ru-RU"
    elif len(lang) == 2:
        lang = f"{lang}-{lang.upper()}"

    pcm = _pcm_from_wav(audio_bytes, content_type)
    if not pcm:
        raise ValueError("empty_audio")

    params = {
        "lang": lang if "-" in lang else "ru-RU",
        "format": "lpcm",
        "sampleRateHz": "16000",
    }
    folder = _folder_id()
    if folder:
        params["folderId"] = folder

    url = f"{YANDEX_STT_URL}?{urlencode(params)}"
    req = Request(
        url,
        data=pcm,
        method="POST",
        headers={
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "audio/x-pcm",
        },
    )
    try:
        with urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", errors="replace").strip()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        logger.warning(
            "companion_stt_yandex_http_error status=%s detail=%s",
            exc.code,
            detail,
        )
        if exc.code in (403, 451):
            raise ValueError("server_stt_geo_blocked") from exc
        raise ValueError("server_stt_provider_error") from exc
    except URLError as exc:
        logger.warning("companion_stt_yandex_network_error error=%s", exc)
        raise ValueError("server_stt_network_error") from exc

    text = raw
    if raw.startswith("{"):
        try:
            payload = json.loads(raw)
            text = str(payload.get("result") or payload.get("text") or "").strip()
        except json.JSONDecodeError:
            text = raw.strip()
    if not text:
        raise ValueError("empty_transcript")
    return text, 0.88
