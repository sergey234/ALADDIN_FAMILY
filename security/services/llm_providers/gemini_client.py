# -*- coding: utf-8 -*-
"""
Optional Gemini (Google AI Studio) fallback when Hermes / OpenRouter fail.

Same contract as openrouter_direct_client.chat_once:
  (ok, text, err) — never logs API key or full user message.

Disabled by default: FEATURE_GEMINI_FALLBACK=0
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Tuple

_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
_API_BASE = os.getenv(
    "GEMINI_API_BASE",
    "https://generativelanguage.googleapis.com/v1beta",
).rstrip("/")
_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT_SEC", "45"))
_MAX_OUT = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1024"))

_ALADDIN_SYSTEM = (
    "Ты AI-помощник ALADDIN — кибербезопасность семьи, приложение iOS, "
    "родительский контроль, тарифы, VPN в приложении (не Telegram-магазин). "
    "Отвечай кратко, по делу. "
    "Если в сообщении есть «Answer only in English» — отвечай только по-английски. "
    "Если есть «Отвечай только по-русски» — только по-русски. "
    "Иначе отвечай на языке вопроса. "
    "Не выдумывай цены. Если не знаешь — скажи честно."
)


def _api_key() -> str:
    return (
        os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("GOOGLE_AI_API_KEY", "").strip()
        or os.getenv("GOOGLE_API_KEY", "").strip()
    )


def gemini_fallback_enabled() -> bool:
    return os.getenv("FEATURE_GEMINI_FALLBACK", "0").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def available() -> bool:
    return gemini_fallback_enabled() and bool(_api_key())


def chat_once(
    message: str,
    *,
    system: Optional[str] = None,
    ui_context: str = "general",
) -> Tuple[bool, str, Optional[str]]:
    """Returns (success, response_text, error). Never logs full message."""
    if not gemini_fallback_enabled():
        return False, "", "gemini fallback disabled"
    key = _api_key()
    if not key:
        return False, "", "no GEMINI_API_KEY"

    user_text = (message or "").replace("\x00", "")[:3500]
    if not user_text.strip():
        return False, "", "empty message"

    sys_text = (system or _ALADDIN_SYSTEM).strip()
    if ui_context == "companion":
        sys_text += (
            " Ты дружелюбный собеседник для ребёнка в семейном приложении; "
            "без шуток при грусти и кризисе."
        )

    model = _DEFAULT_MODEL or "gemini-flash-latest"
    url = (
        f"{_API_BASE}/models/{urllib.parse.quote(model, safe='.-_')}:generateContent"
        f"?key={urllib.parse.quote(key)}"
    )
    body = {
        "systemInstruction": {"parts": [{"text": sys_text}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": _MAX_OUT,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")[:500]
        return False, "", f"gemini http {exc.code}: {err_body}"
    except Exception as exc:
        return False, "", str(exc)[:300]

    if raw.get("error"):
        return False, "", str(raw.get("error"))[:300]

    cands = raw.get("candidates") or []
    if not cands:
        return False, "", "empty candidates"
    parts = ((cands[0].get("content") or {}).get("parts")) or []
    texts = []
    for p in parts:
        t = (p or {}).get("text")
        if t:
            texts.append(str(t))
    text = "\n".join(texts).strip()
    if not text:
        return False, "", "empty content"
    return True, text, None
