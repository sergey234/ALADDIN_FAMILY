# -*- coding: utf-8 -*-
"""Capability module tests for companion server STT."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from security.services.ai_platform.modules.base import ModuleContext
from security.services.ai_platform.modules.companion_server_stt import CompanionServerSTTModule


class TestCompanionServerSTTModule(unittest.TestCase):
    def _ctx(self) -> ModuleContext:
        return ModuleContext(
            user_id="1",
            app_id="aladdin_family",
            age_band="parent",
            age_verified=False,
            content_policy="family_pg13",
            subscription_level="premium",
        )

    def test_disabled_when_feature_flag_off(self):
        ctx = self._ctx()
        with patch(
            "security.services.ai_platform.modules.companion_server_stt.COMPANION_SERVER_STT_ENABLED",
            False,
        ):
            mod = CompanionServerSTTModule()
            self.assertFalse(mod.enabled(ctx))
            frag = mod.capability_fragment(ctx)
            self.assertFalse(frag.enabled)
            self.assertFalse(frag.ui.get("server_stt_fallback"))

    def test_enabled_when_configured(self):
        ctx = self._ctx()
        with patch(
            "security.services.ai_platform.modules.companion_server_stt.COMPANION_SERVER_STT_ENABLED",
            True,
        ), patch(
            "security.services.ai_platform.modules.companion_server_stt.server_stt_configured",
            return_value=True,
        ), patch(
            "security.services.ai_platform.modules.companion_server_stt.active_provider_name",
            return_value="yandex_speechkit",
        ):
            mod = CompanionServerSTTModule()
            self.assertTrue(mod.enabled(ctx))
            frag = mod.capability_fragment(ctx)
            self.assertTrue(frag.ui.get("server_stt_fallback"))
            self.assertEqual(frag.ui.get("provider"), "yandex_speechkit")


if __name__ == "__main__":
    unittest.main()
