# -*- coding: utf-8 -*-
from __future__ import annotations

from ..feature_flags import CHAT_CORE_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class ChatCoreModule(PlatformModule):
    module_id = "chat"

    def enabled(self, ctx: ModuleContext) -> bool:
        return CHAT_CORE_ENABLED

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={"text_input": on, "streaming": on},
            limits={},
        )
