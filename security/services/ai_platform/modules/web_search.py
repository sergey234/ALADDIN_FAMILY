# -*- coding: utf-8 -*-
from __future__ import annotations

from ..feature_flags import WEB_SEARCH_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class WebSearchModule(PlatformModule):
    module_id = "web_search"

    def enabled(self, ctx: ModuleContext) -> bool:
        return WEB_SEARCH_ENABLED

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={"attach_search_badge": on},
            limits={},
        )
