# -*- coding: utf-8 -*-
"""Реестр модулей: регистрация, capabilities, хуки."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import ModuleContext, PlatformModule
from .chat_core import ChatCoreModule
from .companion import CompanionModule
from .voice_realtime import VoiceRealtimeModule
from .web_search import WebSearchModule

# Порядок = порядок в capabilities JSON
_BUILTIN_MODULES: List[PlatformModule] = [
    ChatCoreModule(),
    VoiceRealtimeModule(),
    CompanionModule(),
    WebSearchModule(),
]

_registry: List[PlatformModule] = list(_BUILTIN_MODULES)


def register_module(module: PlatformModule) -> None:
    """Добавить модуль (Phase B+). Дубликаты по module_id заменяются."""
    global _registry
    _registry = [m for m in _registry if m.module_id != module.module_id]
    _registry.append(module)


def get_modules() -> List[PlatformModule]:
    return list(_registry)


def build_capabilities(ctx: ModuleContext) -> Dict[str, Any]:
    """Ответ для GET /api/ai/platform/capabilities и /companion/capabilities."""
    features: Dict[str, Any] = {}
    for mod in _registry:
        frag = mod.capability_fragment(ctx)
        features[frag.id] = {
            "enabled": frag.enabled,
            "ui": frag.ui,
            "limits": frag.limits,
        }
    return {
        "app_id": ctx.app_id,
        "age_band": ctx.age_band,
        "content_policy": ctx.content_policy,
        "features": features,
        "characters": features.get("companion", {}).get("ui", {}).get("characters", []),
    }


async def run_before_chat_hooks(ctx: ModuleContext, message: str) -> Optional[str]:
    for mod in _registry:
        if not mod.enabled(ctx):
            continue
        block = await mod.before_chat(ctx, message)
        if block:
            return block
    return None
