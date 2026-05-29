# -*- coding: utf-8 -*-
from __future__ import annotations

from ..feature_flags import WORKSPACES_ENABLED
from .base import CapabilityFragment, ModuleContext, PlatformModule


class WorkspacesModule(PlatformModule):
    module_id = "workspaces"

    def enabled(self, ctx: ModuleContext) -> bool:
        return WORKSPACES_ENABLED

    def capability_fragment(self, ctx: ModuleContext) -> CapabilityFragment:
        on = self.enabled(ctx)
        return CapabilityFragment(
            id=self.module_id,
            enabled=on,
            ui={"folders_visible": on},
            limits={"max_workspaces": 20 if on else 0},
        )
