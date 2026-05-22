# -*- coding: utf-8 -*-
"""
E2.3 — финальная сборка payload для ai_assistant_chat: user message + SFM aggregates only.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from security.services.ai_sfm_aggregate_schema import strip_forbidden_llm_params
from security.services.ai_sfm_context_builder import AISFMContextBuilder

logger = logging.getLogger(__name__)

# Re-export for routers
__all__ = [
    "LLM_CONTEXT_POLICY",
    "HERMES_AGGREGATES_POLICY",
    "build_ai_chat_sfm_payload",
    "attach_sfm_aggregates_to_params",
    "build_hermes_prompt_with_aggregates",
]

ExecuteFn = Callable[[str, Dict[str, Any]], Tuple[bool, Any, Optional[str]]]

LLM_CONTEXT_POLICY = "aggregates_only_v1"
HERMES_AGGREGATES_POLICY = "aggregates_only_v1"


def _resolve_locale(response_language: Optional[str], message: str) -> str:
    if response_language:
        code = response_language.strip().lower()[:2]
        if code in ("ru", "en"):
            return code
    if any("\u0400" <= ch <= "\u045f" or ch in "ёЁ" for ch in (message or "")):
        return "ru"
    return "en"


def _format_aggregates_block(aggregates: Dict[str, Any], locale: str) -> str:
    import json

    header_ru = (
        "Контекст ALADDIN (только агрегаты защиты, без персональных логов). "
        "Любые цифры в ответе бери ТОЛЬКО из блока ниже; не выдумывай метрики."
    )
    header_en = (
        "ALADDIN context (protection aggregates only, no personal logs). "
        "Use ONLY the numbers below; do not invent metrics."
    )
    header = header_ru if locale == "ru" else header_en
    body = json.dumps(aggregates, ensure_ascii=False, indent=0)[:3500]
    label = "Агрегаты" if locale == "ru" else "Aggregates"
    return f"{header}\n\n## {label}\n{body}"


def build_hermes_prompt_with_aggregates(
    *,
    message: str,
    execute_fn: ExecuteFn,
    user_id: Optional[str] = None,
    response_language: Optional[str] = None,
    include_aggregates: bool = True,
) -> Tuple[str, List[str]]:
    """
    R3.1: Hermes получает вопрос + whitelisted sfm_aggregates (без raw logs).
    """
    locale = _resolve_locale(response_language, message)
    if not include_aggregates:
        return message.strip(), []

    bundle = AISFMContextBuilder(execute_fn).build(user_id=user_id)
    if not bundle.aggregates:
        return message.strip(), []

    q_label = "Вопрос" if locale == "ru" else "Question"
    prompt = (
        f"{_format_aggregates_block(bundle.aggregates, locale)}\n\n"
        f"## {q_label}\n{message.strip()}"
    )
    clean, removed = strip_forbidden_llm_params(
        {"message": message, "llm_context_policy": HERMES_AGGREGATES_POLICY, "prompt": prompt}
    )
    if removed:
        logger.warning("Hermes prompt stripped forbidden keys: %s", ",".join(sorted(removed)))
    return str(clean.get("prompt") or message.strip()), list(bundle.sources)


def build_ai_chat_sfm_payload(
    *,
    message: str,
    ui_context: str,
    user_id: Optional[str],
    execute_fn: ExecuteFn,
    timestamp: Optional[datetime] = None,
    stream: bool = False,
    message_id: Optional[str] = None,
    resume_from_index: int = 0,
    response_language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Собирает params для SFM ai_assistant_chat.
    В LLM уходит только redacted message + whitelisted sfm_aggregates (без raw logs).
    """
    bundle = AISFMContextBuilder(execute_fn).build(user_id=user_id)

    payload: Dict[str, Any] = {
        "message": message,
        "context": ui_context,
        "user_id": user_id or "guest",
        "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        "llm_context_policy": LLM_CONTEXT_POLICY,
        "sfm_aggregates": bundle.aggregates,
        "sfm_context_sources": bundle.sources,
    }

    if stream:
        payload["stream"] = True
    if message_id:
        payload["message_id"] = message_id
    if resume_from_index:
        payload["resume_from_index"] = resume_from_index
    if response_language:
        payload["response_language"] = response_language

    clean, removed = strip_forbidden_llm_params(payload)
    if removed:
        logger.warning(
            "AI chat payload stripped forbidden keys: %s",
            ",".join(sorted(removed)),
        )
    return clean


def attach_sfm_aggregates_to_params(
    params: Dict[str, Any],
    execute_fn: ExecuteFn,
) -> Dict[str, Any]:
    """Добавляет/обновляет sfm_aggregates для analyze_threat / report_incident."""
    user_id = params.get("user_id")
    bundle = AISFMContextBuilder(execute_fn).build(
        user_id=str(user_id) if user_id else None
    )
    out = dict(params)
    out["llm_context_policy"] = LLM_CONTEXT_POLICY
    out["sfm_aggregates"] = bundle.aggregates
    out["sfm_context_sources"] = bundle.sources
    clean, removed = strip_forbidden_llm_params(out)
    if removed:
        logger.warning("AI params stripped forbidden keys: %s", ",".join(sorted(removed)))
    return clean
