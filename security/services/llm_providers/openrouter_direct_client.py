# -*- coding: utf-8 -*-
"""
Short-prompt OpenRouter fallback when Hermes CLI exceeds free-tier prompt limits (402).

Does NOT use `hermes chat` — only /v1/chat/completions with compact system text.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional, Tuple

_DEFAULT_MODEL = os.getenv("OPENROUTER_DIRECT_MODEL", "deepseek/deepseek-v4-flash")
_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1").rstrip("/")
_TIMEOUT = int(os.getenv("OPENROUTER_DIRECT_TIMEOUT_SEC", "45"))
_MAX_OUT = int(os.getenv("OPENROUTER_DIRECT_MAX_TOKENS", "1024"))

_ALADDIN_SYSTEM = (
    "Ты AI-помощник ALADDIN — кибербезопасность семьи, приложение iOS, "
    "родительский контроль, тарифы, VPN в приложении (не Telegram-магазин). "
    "Отвечай кратко, по делу, на русском если вопрос на русском. "
    "Не выдумывай цены. Если не знаешь — скажи честно."
)


def _api_key() -> str:
    return (
        os.getenv("OPENROUTER_API_KEY", "").strip()
        or os.getenv("HERMES_OPENROUTER_API_KEY", "").strip()
    )


def direct_fallback_enabled() -> bool:
    return os.getenv("FEATURE_OPENROUTER_DIRECT_FALLBACK", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def chat_once(
    message: str,
    *,
    system: Optional[str] = None,
    ui_context: str = "general",
) -> Tuple[bool, str, Optional[str]]:
    """Returns (success, response_text, error). Never logs full message."""
    if not direct_fallback_enabled():
        return False, "", "openrouter direct fallback disabled"
    key = _api_key()
    if not key:
        return False, "", "no OPENROUTER_API_KEY"

    user_text = (message or "").replace("\x00", "")[:3500]
    if not user_text.strip():
        return False, "", "empty message"

    sys_text = (system or _ALADDIN_SYSTEM).strip()
    if ui_context == "companion":
        sys_text += " Ты дружелюбный собеседник для ребёнка в семейном приложении; без шуток при грусти и кризисе."

    body = {
        "model": _DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": sys_text},
            {"role": "user", "content": user_text},
        ],
        "max_tokens": _MAX_OUT,
        "temperature": 0.4,
    }
    req = urllib.request.Request(
        f"{_API_BASE}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aladdin-ai.ru",
            "X-Title": "ALADDIN",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")[:500]
        return False, "", f"openrouter http {exc.code}: {err_body}"
    except Exception as exc:
        return False, "", str(exc)[:300]

    err = raw.get("error")
    if err:
        return False, "", str(err)[:300]

    choices = raw.get("choices") or []
    if not choices:
        return False, "", "empty choices"
    text = (
        (choices[0].get("message") or {}).get("content") or ""
    ).strip()
    if not text:
        return False, "", "empty content"
    return True, text, None
