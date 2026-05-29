# -*- coding: utf-8 -*-
"""Premium neuro-TTS (ElevenLabs Flash) — только subscription premium."""

from __future__ import annotations

from ..feature_flags import NEURO_TTS_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule

_PREMIUM_LEVELS = frozenset({"premium"})


def is_premium_subscription(subscription_level: str) -> bool:
    return (subscription_level or "free").strip().lower() in _PREMIUM_LEVELS


class CompanionNeuroTTSModule(PlatformModule):
    module_id = "companion_neuro_tts"

    def enabled(self, ctx: ModuleContext) -> bool:
        if not NEURO_TTS_ENABLED:
            return False
        return is_premium_subscription(ctx.subscription_level)

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        premium = is_premium_subscription(ctx.subscription_level)
        neuro_on = NEURO_TTS_ENABLED and premium
        return CapabilityFragment(
            id=self.module_id,
            enabled=neuro_on,
            ui={
                # iOS: neuro_tts_premium=true → POST /companion/tts (ElevenLabs)
                "neuro_tts_premium": neuro_on,
                # Визуал героев одинаковый на всех тарифах (PNG/Rive)
                "hero_visual_tier": "all",
                "tts_local_avspeech": True,
                "auto_speak_toggle": True,
                "tts_provider": "elevenlabs" if neuro_on else "avspeech",
            },
            limits={
                "requires_subscription": "premium",
            },
        )
