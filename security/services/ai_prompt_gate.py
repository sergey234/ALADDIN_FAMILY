# -*- coding: utf-8 -*-
"""
E2.2 — подготовка текста для LLM/SFM: redact + запрет сырого PII в промпте.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Set

from security.services.ai_pii_redactor import (
    RedactResult,
    contains_blocked_pii,
    redact,
    redact_dict_fields,
)
from security.services.ai_sfm_aggregate_schema import strip_forbidden_llm_params

logger = logging.getLogger(__name__)

# Поля, которые могут попасть в LLM-промпт через SFM.
_LLM_TEXT_FIELDS: Set[str] = {
    "message",
    "threat",
    "description",
    "context",
    "comment",
    "query_text",
}

_AI_FUNCTION_PREFIX = "ai_assistant_"
_AI_LLM_FUNCTIONS: Set[str] = {
    "ai_assistant_chat",
    "ai_assistant_analyze_threat",
    "ai_assistant_report_incident",
    "get_ai_response",
    "super_ai_support_assistant",
}


class PIIPromptBlockedError(ValueError):
    """Текст не прошёл проверку после redact — сырой PII в промпт запрещён."""


@dataclass(frozen=True)
class PreparedPrompt:
    text: str
    redaction_count: int


def prepare_for_llm_prompt(raw: str, *, field_name: str = "message") -> PreparedPrompt:
    """
    Двойной redact + блокировка, если high-confidence PII всё ещё присутствует.
    """
    trimmed = (raw or "").strip()
    if not trimmed:
        raise PIIPromptBlockedError(f"Empty AI prompt field: {field_name}")

    result: RedactResult = redact(trimmed)
    if contains_blocked_pii(result.text):
        result = redact(result.text)

    if contains_blocked_pii(result.text):
        logger.warning(
            "AI prompt blocked: residual PII after redact field=%s len=%d",
            field_name,
            len(trimmed),
        )
        raise PIIPromptBlockedError(
            "Message contains personal data that cannot be sent to AI. "
            "Please remove emails, phone numbers, or payment details."
        )

    return PreparedPrompt(text=result.text, redaction_count=result.replacement_count)


def prepare_optional_for_llm(raw: Optional[str], *, field_name: str) -> Optional[str]:
    if raw is None:
        return None
    trimmed = raw.strip()
    if not trimmed:
        return None
    return prepare_for_llm_prompt(trimmed, field_name=field_name).text


def redact_feedback_only(raw: Optional[str]) -> Optional[str]:
    """Feedback — redact без жёсткой блокировки (не LLM-промпт)."""
    if raw is None:
        return None
    trimmed = raw.strip()
    if not trimmed:
        return None
    return redact(trimmed).text


def should_redact_sfm_call(function_name: str) -> bool:
    return function_name in _AI_LLM_FUNCTIONS or function_name.startswith(_AI_FUNCTION_PREFIX)


def redact_sfm_params(function_name: str, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Defense-in-depth: redact AI-related params перед HTTP-вызовом SFM :8003.
    Для LLM-полей при residual PII — выбрасывает PIIPromptBlockedError.
    """
    data = dict(params or {})
    if not should_redact_sfm_call(function_name):
        clean, removed = strip_forbidden_llm_params(data)
        if removed:
            logger.warning(
                "SFM params stripped forbidden keys function=%s keys=%s",
                function_name,
                ",".join(sorted(removed)),
            )
        return clean

    data, removed = strip_forbidden_llm_params(data)
    if removed:
        logger.warning(
            "AI SFM params stripped forbidden keys function=%s keys=%s",
            function_name,
            ",".join(sorted(removed)),
        )

    llm_fields = _LLM_TEXT_FIELDS.intersection(data.keys())
    feedback_only = function_name == "ai_assistant_feedback"

    total = 0
    for field in sorted(llm_fields):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        if feedback_only and field in {"comment", "query_text"}:
            data[field] = redact_feedback_only(value)
            continue
        if field == "context" and value.strip() in {
            "general",
            "feedback",
            "resume",
            "protection_status",
            "threat_analysis",
            "recommendations",
            "help",
        }:
            continue
        prepared = prepare_for_llm_prompt(value, field_name=field)
        data[field] = prepared.text
        total += prepared.redaction_count

    # Остальные строковые поля — мягкий redact
    other_fields = set(data.keys()) - llm_fields
    soft, soft_count = redact_dict_fields(
        {k: data[k] for k in other_fields if isinstance(data.get(k), str)},
        other_fields,
    )
    data.update(soft)
    total += soft_count

    if total:
        logger.info(
            "AI SFM params redacted function=%s replacements=%d",
            function_name,
            total,
        )
    return data
