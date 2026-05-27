# -*- coding: utf-8 -*-
"""
Content policy engine — shared by ALADDIN Family and Adult companion apps.

NSFW / explicit content is allowed only for aladdin_adult + age_verified.
ALADDIN Family app must never enable NSFW even if client sends flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .config import AppId, ContentPolicy, DEFAULT_POLICY_BY_APP

# Patterns for hard block in family app (and optional soft block in adult)
_FAMILY_HARD_BLOCK_FRAGMENTS = (
    "nsfw",
    "nude",
    "sexual",
    "эрот",
    "секс",
    "интим",
    "раздев",
    "porn",
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    blocked_reason: Optional[str]
    content_policy: ContentPolicy
    nsfw_allowed: bool
    recording_allowed: bool
    max_intimacy_level: int  # 0=none, 5=Grok Ani-like (adult only)


def resolve_content_policy(
    app_id: str,
    *,
    jwt_policy: Optional[str] = None,
    age_verified: bool = False,
) -> ContentPolicy:
    try:
        app = AppId(app_id)
    except ValueError:
        app = AppId.ALADDIN_FAMILY
    policy = DEFAULT_POLICY_BY_APP[app]
    if jwt_policy:
        try:
            policy = ContentPolicy(jwt_policy)
        except ValueError:
            pass
    if app == AppId.ALADDIN_ADULT and policy == ContentPolicy.ADULT_18 and not age_verified:
        return ContentPolicy.FAMILY_PG13
    return policy


def evaluate_request_policy(
    *,
    app_id: str,
    message: str,
    age_verified: bool = False,
    jwt_policy: Optional[str] = None,
    client_requests_nsfw: bool = False,
    age_band: Optional[str] = None,
) -> PolicyDecision:
    policy = resolve_content_policy(app_id, jwt_policy=jwt_policy, age_verified=age_verified)

    try:
        app = AppId(app_id)
    except ValueError:
        app = AppId.ALADDIN_FAMILY

    nsfw_allowed = (
        app == AppId.ALADDIN_ADULT
        and policy == ContentPolicy.ADULT_18
        and age_verified
        and client_requests_nsfw
    )
    recording_allowed = False  # product decision: no in-app conversation recording

    lower = (message or "").lower()
    band = age_band or "parent"
    if app == AppId.ALADDIN_FAMILY:
        if any(fragment in lower for fragment in _FAMILY_HARD_BLOCK_FRAGMENTS):
            return PolicyDecision(
                allowed=False,
                blocked_reason="family_content_policy",
                content_policy=policy,
                nsfw_allowed=False,
                recording_allowed=False,
                max_intimacy_level=2,
            )
        if band == "child" and any(
            w in lower for w in ("встретимся", "встреча", "адрес", "телефон", "где живёшь", "сколько лет")
        ):
            return PolicyDecision(
                allowed=False,
                blocked_reason="child_pii_or_meetup",
                content_policy=policy,
                nsfw_allowed=False,
                recording_allowed=False,
                max_intimacy_level=1,
            )
        return PolicyDecision(
            allowed=True,
            blocked_reason=None,
            content_policy=policy,
            nsfw_allowed=False,
            recording_allowed=recording_allowed,
            max_intimacy_level=1 if band == "child" else 2,
        )

    # Adult app: allow broader topics; explicit NSFW only when nsfw_allowed
    if not nsfw_allowed and any(fragment in lower for fragment in _FAMILY_HARD_BLOCK_FRAGMENTS):
        # Without NSFW toggle, still block explicit requests (configurable later)
        return PolicyDecision(
            allowed=False,
            blocked_reason="adult_nsfw_disabled",
            content_policy=policy,
            nsfw_allowed=False,
            recording_allowed=recording_allowed,
            max_intimacy_level=3,
        )

    return PolicyDecision(
        allowed=True,
        blocked_reason=None,
        content_policy=policy,
        nsfw_allowed=nsfw_allowed,
        recording_allowed=recording_allowed,
        max_intimacy_level=5 if nsfw_allowed else 3,
    )
