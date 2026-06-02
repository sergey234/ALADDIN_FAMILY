# -*- coding: utf-8 -*-
"""Referral map for L2 escalation (p1-21)."""

from __future__ import annotations

from typing import Any, Dict

from security.services.ai_platform.wellness_i18n_loader import get_referral_payload_from_i18n


def get_referral_payload(*, locale: str = "ru", level: str = "L2") -> Dict[str, Any]:
    return get_referral_payload_from_i18n(locale=locale, level=level)
