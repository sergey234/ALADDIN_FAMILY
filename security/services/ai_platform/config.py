# -*- coding: utf-8 -*-
"""Platform-wide enums and defaults (multi-app)."""

from enum import Enum


class AppId(str, Enum):
    """Client application identifier (JWT claim `app_id`)."""

    ALADDIN_FAMILY = "aladdin_family"
    ALADDIN_ADULT = "aladdin_adult"


class ContentPolicy(str, Enum):
    """Content policy bound to app + age verification."""

    FAMILY_PG13 = "family_pg13"
    ADULT_18 = "adult_18"


class ChatMode(str, Enum):
    """Grok-like response modes."""

    FAST = "fast"
    REASONING = "reasoning"
    THINK = "think"


DEFAULT_POLICY_BY_APP = {
    AppId.ALADDIN_FAMILY: ContentPolicy.FAMILY_PG13,
    AppId.ALADDIN_ADULT: ContentPolicy.ADULT_18,
}
