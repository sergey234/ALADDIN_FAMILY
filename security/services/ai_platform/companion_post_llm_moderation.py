# -*- coding: utf-8 -*-
"""P1-22 — Post-LLM moderation for companion replies (policy + blocklist)."""

from __future__ import annotations

import re
from typing import Optional, Tuple

from .policy_engine import evaluate_request_policy

_POST_MODERATION_FALLBACK = (
    "Я рядом и хочу, чтобы тебе было спокойно. "
    "Давай поговорим о чём-то дружелюбном — а про защиту в ALADDIN помогу, если спросишь."
)

_OUTPUT_BLOCKLIST = (
    re.compile(r"ignore (all )?(previous|prior) instructions", re.I),
    re.compile(r"system prompt", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"как (сделать|изготовить|сварить) (бомбу|оружие|взрывчат)", re.I),
    re.compile(r"убей (его|её|их|себя)", re.I),
)


def moderate_companion_assistant_text(
    text: str,
    *,
    app_id: str,
    age_band: str,
    age_verified: bool = False,
    jwt_policy: Optional[str] = None,
) -> Tuple[str, bool, str]:
    """
    Returns (safe_text, blocked, reason).
    """
    raw = (text or "").strip()
    if not raw:
        return raw, False, ""

    for pattern in _OUTPUT_BLOCKLIST:
        if pattern.search(raw):
            return _POST_MODERATION_FALLBACK, True, "blocklist"

    decision = evaluate_request_policy(
        app_id=app_id,
        message=raw,
        age_verified=age_verified,
        jwt_policy=jwt_policy,
        client_requests_nsfw=False,
        age_band=age_band,
    )
    if not decision.allowed:
        return _POST_MODERATION_FALLBACK, True, decision.blocked_reason or "policy"

    return raw, False, ""
