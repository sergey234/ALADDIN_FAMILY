# -*- coding: utf-8 -*-
from __future__ import annotations

from ..companion_characters import STANDARD_COMPANION_CHARACTERS
from ..feature_flags import COMPANION_ENABLED, TRUST_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class CompanionModule(PlatformModule):
    module_id = "companion"

    def enabled(self, ctx: ModuleContext) -> bool:
        return COMPANION_ENABLED

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        characters = list(STANDARD_COMPANION_CHARACTERS)
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={
                "hub_visible": on,
                "characters": characters,
                "trust_bar": TRUST_ENABLED and on,
            },
            limits={},
        )
