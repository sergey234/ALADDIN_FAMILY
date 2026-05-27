# -*- coding: utf-8 -*-
"""P1-13 voice + P1-07 cosmetics — unit tests (no live LLM / WS)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

if "jwt" not in sys.modules:
    sys.modules["jwt"] = MagicMock()

os.environ.setdefault("JWT_SECRET", "test-secret-companion-voice")
os.environ.setdefault("FEATURE_VOICE_ENABLED", "true")


class CompanionVoiceCosmeticsTests(unittest.TestCase):
    def test_voice_router_has_no_security_stub(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "security",
            "api",
            "routers",
            "ai_voice_ws_router.py",
        )
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("безопасност", src.lower())
        self.assertIn("run_companion_voice_turn", src)
        self.assertIn("transcript", src)

    def test_profile_equipped_cosmetic_persisted(self):
        from security.services.ai_platform import companion_store
        from security.services.ai_platform.companion_store import CompanionStore
        from security.api.routers.ai_companion_router import (
            _load_companion_profile,
            _normalize_profile_payload,
        )

        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "vc.db")
            os.environ["COMPANION_DB_PATH"] = db
            companion_store._store = None  # noqa: SLF001
            store = CompanionStore(db_path=db)
            store.set_profile(
                "user-vc",
                {
                    "personality_preset": "playful",
                    "equipped_cosmetic_id": "horn_glow_soft",
                    "equipped_cosmetic_character_id": "unicorn",
                },
            )
            profile = _load_companion_profile("user-vc")
            self.assertEqual(profile["equipped_cosmetic_id"], "horn_glow_soft")
            normalized = _normalize_profile_payload(profile)
            self.assertEqual(normalized["equipped_cosmetic_character_id"], "unicorn")
            companion_store._store = None  # noqa: SLF001

    def test_cosmetic_unlock_gate(self):
        from security.api.routers import ai_companion_router as mod

        with patch.object(mod, "_trust_score", return_value=25):
            self.assertTrue(mod._cosmetic_unlocked("unicorn", "horn_glow_soft", "u1"))
            self.assertFalse(mod._cosmetic_unlocked("unicorn", "mane_sparkle", "u1"))

    def test_companion_voice_turn_delegates_to_chat(self):
        import asyncio
        from security.services.ai_platform.companion_voice_turn import run_companion_voice_turn

        fake_resp = type(
            "R",
            (),
            {
                "response": "Привет, друг!",
                "emotion": "happy",
                "character_id": "unicorn",
                "companion_domain": "general",
                "companion_mood": "neutral",
                "trust_score": 12,
                "cosmetic_unlocked": None,
            },
        )()

        async def _run():
            with patch(
                "security.api.routers.ai_companion_router.companion_chat",
                new=AsyncMock(return_value=fake_resp),
            ):
                return await run_companion_voice_turn(
                    user={"user_id": "u1", "payload": {}},
                    character_id="unicorn",
                    transcript="привет",
                )

        resp = asyncio.run(_run())
        self.assertEqual(resp.response, "Привет, друг!")


if __name__ == "__main__":
    unittest.main()
