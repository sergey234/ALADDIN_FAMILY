# -*- coding: utf-8 -*-
"""Capability gate for hybrid companion STT (server fallback after on-device / Siri)."""

from __future__ import annotations

from ..companion_stt import active_provider_name, server_stt_configured
from ..feature_flags import COMPANION_SERVER_STT_ENABLED, VOICE_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class CompanionServerSTTModule(PlatformModule):
    module_id = "companion_server_stt"

    def enabled(self, ctx: ModuleContext) -> bool:
        if not VOICE_ENABLED or not COMPANION_SERVER_STT_ENABLED:
            return False
        return server_stt_configured()

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        provider = active_provider_name() if on else "none"
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={
                "server_stt_fallback": on,
                "provider": provider,
                "audio_retention_seconds": 0,
            },
            limits={},
        )
