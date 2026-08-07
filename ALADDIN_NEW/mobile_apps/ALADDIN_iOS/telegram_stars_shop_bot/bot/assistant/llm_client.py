"""OpenAI-compatible chat completions client (isolated timeouts, R9/R21)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)

_last_admin_alert_mono: float = 0.0

# Sensible Free/auto defaults for OpenRouter when FALLBACK_MODELS empty.
_DEFAULT_OPENROUTER_FALLBACKS = (
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
)

# Retry next model on these outcomes.
_RETRYABLE_ERRORS = frozenset(
    {
        "http_402",
        "http_429",
        "http_500",
        "http_502",
        "http_503",
        "http_504",
        "empty_choices",
        "empty_content",
        "TimeoutException",
        "ReadTimeout",
        "ConnectTimeout",
        "ConnectError",
    }
)


@dataclass
class LLMResult:
    ok: bool
    text: str
    error: str | None = None
    raw: dict[str, Any] | None = None
    model_used: str | None = None


def llm_configured(settings: Settings) -> bool:
    return bool(
        (settings.assistant_llm_base_url or "").strip()
        and (settings.assistant_llm_api_key or "").strip()
        and (settings.assistant_llm_model or "").strip()
    )


def assistant_llm_model_chain(settings: Settings) -> list[str]:
    """Primary model + fallbacks (deduped, order preserved)."""
    primary = (settings.assistant_llm_model or "").strip()
    raw = (getattr(settings, "assistant_llm_fallback_models", "") or "").strip()
    extras: list[str] = []
    if raw:
        extras = [p.strip() for p in raw.split(",") if p.strip()]
    else:
        base = (settings.assistant_llm_base_url or "").lower()
        if "openrouter.ai" in base:
            extras = list(_DEFAULT_OPENROUTER_FALLBACKS)

    out: list[str] = []
    seen: set[str] = set()
    for m in [primary, *extras]:
        if not m or m in seen:
            continue
        seen.add(m)
        out.append(m)
    return out


def _is_retryable(error: str | None) -> bool:
    if not error:
        return False
    if error in _RETRYABLE_ERRORS:
        return True
    # httpx names / transport noise
    return any(x in error for x in ("Timeout", "Connect", "Network", "RemoteProtocol"))


async def _post_once(
    *,
    client: httpx.AsyncClient,
    url: str,
    headers: dict[str, str],
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
) -> LLMResult:
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    try:
        r = await client.post(url, json=payload, headers=headers)
        if r.status_code >= 400:
            logger.warning(
                "assistant_llm_http model=%s status=%s body=%s",
                model,
                r.status_code,
                (r.text or "")[:300],
            )
            return LLMResult(ok=False, text="", error=f"http_{r.status_code}", model_used=model)
        data = r.json()
        choices = data.get("choices") or []
        if not choices:
            return LLMResult(ok=False, text="", error="empty_choices", raw=data, model_used=model)
        msg = (choices[0].get("message") or {}).get("content") or ""
        text = str(msg).strip()
        if not text:
            return LLMResult(ok=False, text="", error="empty_content", raw=data, model_used=model)
        return LLMResult(ok=True, text=text, raw=data, model_used=model)
    except Exception as e:
        logger.warning("assistant_llm_error model=%s %s: %s", model, type(e).__name__, e)
        return LLMResult(ok=False, text="", error=type(e).__name__, model_used=model)


async def chat_complete(
    settings: Settings,
    messages: list[dict[str, str]],
) -> LLMResult:
    if not llm_configured(settings):
        return LLMResult(ok=False, text="", error="llm_not_configured")

    base = (settings.assistant_llm_base_url or "").rstrip("/")
    url = f"{base}/chat/completions"
    timeout = max(5, int(settings.assistant_llm_timeout_sec or 45))
    max_tokens = max(64, int(settings.assistant_max_out_tokens or 800))
    headers = {
        "Authorization": f"Bearer {settings.assistant_llm_api_key.strip()}",
        "Content-Type": "application/json",
        # Helps OpenRouter attribution / free routing
        "HTTP-Referer": "https://t.me/AiMonkeyStars_bot",
        "X-Title": "AiMonkeyAssistant",
    }
    chain = assistant_llm_model_chain(settings)
    last = LLMResult(ok=False, text="", error="no_models")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            for i, model in enumerate(chain):
                last = await _post_once(
                    client=client,
                    url=url,
                    headers=headers,
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                )
                if last.ok:
                    if i > 0:
                        logger.info(
                            "assistant_llm_failover ok model=%s after=%s",
                            model,
                            chain[i - 1],
                        )
                    return last
                if i + 1 < len(chain) and _is_retryable(last.error):
                    logger.warning(
                        "assistant_llm_failover try_next from=%s err=%s next=%s",
                        model,
                        last.error,
                        chain[i + 1],
                    )
                    continue
                break
    except Exception as e:
        logger.warning("assistant_llm_error %s: %s", type(e).__name__, e)
        return LLMResult(ok=False, text="", error=type(e).__name__)

    return last


def should_alert_admin_llm_down(*, cooldown_sec: float = 900.0) -> bool:
    global _last_admin_alert_mono
    now = time.monotonic()
    if now - _last_admin_alert_mono < cooldown_sec:
        return False
    _last_admin_alert_mono = now
    return True


FALLBACK_USER_HTML = (
    "Сейчас ИИ-помощник временно недоступен. "
    "Нажмите <b>👨‍💼 Человек</b> — поможем в поддержке. "
    "Раздел «Поддержка» в меню тоже работает."
)
