# -*- coding: utf-8 -*-
from __future__ import annotations

from ..feature_flags import VOICE_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class VoiceRealtimeModule(PlatformModule):
    module_id = "voice_realtime"

    def enabled(self, ctx: ModuleContext) -> bool:
        if not VOICE_ENABLED:
            return False
        # Family kids: voice on; can tighten per age_band later
        return True

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={
                "mic_button": on,
                "realtime_websocket": on,
                "ephemeral_token_required": on,
            },
            limits={},
        )
