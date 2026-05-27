# -*- coding: utf-8 -*-
from __future__ import annotations

from ..feature_flags import COMPANION_ENABLED, TRUST_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class CompanionModule(PlatformModule):
    module_id = "companion"

    def enabled(self, ctx: ModuleContext) -> bool:
        return COMPANION_ENABLED

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        characters = ["unicorn"]
        if ctx.age_band in ("teen", "parent", "adult_app"):
            characters.extend(["aladdin", "genie"])
        elif ctx.age_band == "senior":
            characters = ["aladdin"]
        elif ctx.age_band == "child":
            characters = ["unicorn"]
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
