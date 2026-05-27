# -*- coding: utf-8 -*-
"""Сборка capabilities из JWT пользователя."""

from __future__ import annotations

from typing import Any, Dict

from .config import AppId, ContentPolicy, DEFAULT_POLICY_BY_APP
from .modules.base import ModuleContext
from .modules.registry import build_capabilities


def module_context_from_user(user: dict) -> ModuleContext:
    payload = user.get("payload") or {}
    app_id = payload.get("app_id", AppId.ALADDIN_FAMILY.value)
    age_band = payload.get("age_band", "parent")
    if app_id == AppId.ALADDIN_FAMILY.value and age_band == "adult_app":
        age_band = "parent"
    policy = payload.get("content_policy")
    if not policy:
        try:
            policy = DEFAULT_POLICY_BY_APP[AppId(app_id)].value
        except ValueError:
            policy = ContentPolicy.FAMILY_PG13.value
    return ModuleContext(
        user_id=user.get("user_id") or "anonymous",
        app_id=app_id,
        age_band=age_band,
        age_verified=bool(payload.get("age_verified", False)),
        content_policy=policy,
        subscription_level=user.get("subscription_level", "free"),
        character_id=payload.get("default_character_id"),
    )


def get_platform_capabilities(user: dict) -> Dict[str, Any]:
    ctx = module_context_from_user(user)
    caps = build_capabilities(ctx)
    limits = user.get("limits") or {}
    caps["subscription_level"] = user.get("subscription_level", "free")
    caps["limits"] = {
        "max_ai_messages": limits.get("max_ai_messages"),
        "voice_minutes_month": limits.get("voice_minutes_month"),
    }
    return caps
