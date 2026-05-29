# -*- coding: utf-8 -*-
"""Premium neuro-TTS (ElevenLabs Flash) — premium + trial (testing via FEATURE_NEURO_TTS_TRIAL)."""

from __future__ import annotations

from ..feature_flags import NEURO_TTS_ENABLED, NEURO_TTS_TRIAL_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


def is_neuro_tts_subscription(subscription_level: str) -> bool:
    level = (subscription_level or "free").strip().lower()
    if level == "premium":
        return True
    if level == "trial" and NEURO_TTS_TRIAL_ENABLED:
        return True
    return False


# Back-compat alias (router + synthesize guards)
is_premium_subscription = is_neuro_tts_subscription


class CompanionNeuroTTSModule(PlatformModule):
    module_id = "companion_neuro_tts"

    def enabled(self, ctx: ModuleContext) -> bool:
        if not NEURO_TTS_ENABLED:
            return False
        return is_neuro_tts_subscription(ctx.subscription_level)

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        eligible = is_neuro_tts_subscription(ctx.subscription_level)
        neuro_on = NEURO_TTS_ENABLED and eligible
        required_tiers = "premium,trial" if NEURO_TTS_TRIAL_ENABLED else "premium"
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
                "requires_subscription": required_tiers,
            },
        )
