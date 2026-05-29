# -*- coding: utf-8 -*-
from __future__ import annotations

from ..feature_flags import IMAGE_GEN_ENABLED, VIDEO_GEN_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class MediaGenModule(PlatformModule):
    module_id = "media_gen"

    def enabled(self, ctx: ModuleContext) -> bool:
        return IMAGE_GEN_ENABLED or VIDEO_GEN_ENABLED

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        return CapabilityFragment(
            id=self.module_id,
            enabled=self.enabled(ctx),
            ui={
                "image_gen": IMAGE_GEN_ENABLED,
                "video_gen": VIDEO_GEN_ENABLED and ctx.age_band != "child",
            },
            limits={},
        )
