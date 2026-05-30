# -*- coding: utf-8 -*-
"""OpenAI Whisper — backup STT via optional EU HTTPS/SOCKS proxy."""

from __future__ import annotations

import json
import uuid
from typing import Tuple

from .openai_http import openai_api_key, post_openai_multipart


def configured() -> bool:
    return bool(openai_api_key())


def provider_id() -> str:
    return "openai_whisper"


def transcribe(
    audio_bytes: bytes,
    *,
    content_type: str = "audio/wav",
    language: str = "ru",
) -> Tuple[str, float]:
    api_key = openai_api_key()
    if not api_key:
        raise ValueError("server_stt_unconfigured")

    boundary = f"----AladdinSTT{uuid.uuid4().hex}"
    filename = "speech.wav" if "wav" in (content_type or "").lower() else "speech.m4a"
    mime = content_type if content_type else "application/octet-stream"
    lang = (language or "ru").split("-")[0]

    parts: list[bytes] = []
    for field, value in (
        ("model", "whisper-1"),
        ("language", lang),
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    raw = post_openai_multipart(body, headers, timeout=45)
    payload = json.loads(raw.decode("utf-8"))
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
            avg = sum(scores) / len(scores)
            confidence = max(0.0, min(1.0, 1.0 + avg / 2.5))
    return text, confidence
