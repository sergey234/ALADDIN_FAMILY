# -*- coding: utf-8 -*-
"""Premium neuro-TTS capability + synthesis helpers."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from security.services.ai_platform.modules.base import ModuleContext
from security.services.ai_platform.modules.companion_neuro_tts import (
    CompanionNeuroTTSModule,
    is_premium_subscription,
)
from security.services.ai_platform.companion_neuro_tts import (
    all_hero_voice_ids_configured,
    assert_premium_tts_allowed,
    build_tts_response_payload,
    estimate_speech_seconds,
    synthesize_neuro_tts,
    voice_id_for_character,
    _cache_put,
    _cache_get,
    _cache_key,
)


class TestPremiumSubscription(unittest.TestCase):
    def test_premium_only(self):
        self.assertTrue(is_premium_subscription("premium"))
        self.assertFalse(is_premium_subscription("free"))
        self.assertFalse(is_premium_subscription("trial"))

    def test_assert_premium_raises_for_free(self):
        with self.assertRaises(ValueError):
            assert_premium_tts_allowed("free")


class TestCompanionNeuroTTSModule(unittest.TestCase):
    def _ctx(self, level: str) -> ModuleContext:
        return ModuleContext(
            user_id="u1",
            app_id="aladdin_family",
            age_band="parent",
            age_verified=False,
            content_policy="family_pg13",
            subscription_level=level,
        )

    @patch("security.services.ai_platform.modules.companion_neuro_tts.NEURO_TTS_ENABLED", True)
    def test_capability_premium_on(self):
        mod = CompanionNeuroTTSModule()
        frag = mod.capability_fragment(self._ctx("premium"))
        self.assertTrue(frag.ui["neuro_tts_premium"])
        self.assertEqual(frag.ui["hero_visual_tier"], "all")
        self.assertEqual(frag.ui["tts_provider"], "elevenlabs")

    @patch("security.services.ai_platform.modules.companion_neuro_tts.NEURO_TTS_ENABLED", True)
    def test_capability_free_off(self):
        mod = CompanionNeuroTTSModule()
        frag = mod.capability_fragment(self._ctx("free"))
        self.assertFalse(frag.ui["neuro_tts_premium"])
        self.assertEqual(frag.ui["tts_provider"], "avspeech")
        self.assertTrue(frag.ui["tts_local_avspeech"])

    @patch("security.services.ai_platform.modules.companion_neuro_tts.NEURO_TTS_ENABLED", False)
    def test_flag_off(self):
        mod = CompanionNeuroTTSModule()
        self.assertFalse(mod.enabled(self._ctx("premium")))


class TestCompanionNeuroTTSCache(unittest.TestCase):
    def test_cache_roundtrip(self):
        key = _cache_key("genie", "Привет!", "ru")
        _cache_put(key, b"mp3bytes")
        self.assertEqual(_cache_get(key), b"mp3bytes")

    def test_estimate_seconds(self):
        self.assertGreaterEqual(estimate_speech_seconds("x" * 28), 2)

    def test_build_payload_base64(self):
        payload = build_tts_response_payload(b"\x01\x02", cached=True, content_type="audio/mpeg")
        self.assertTrue(payload["audio_base64"])
        self.assertTrue(payload["cached"])


class TestThreeHeroVoices(unittest.TestCase):
    @patch.dict(
        "security.services.ai_platform.companion_neuro_tts._DEFAULT_VOICE_BY_CHARACTER",
        {"unicorn": "u1", "genie": "g1", "aladdin": "a1"},
        clear=False,
    )
    def test_distinct_voice_per_hero(self):
        self.assertTrue(all_hero_voice_ids_configured())
        self.assertEqual(voice_id_for_character("unicorn"), "u1")
        self.assertEqual(voice_id_for_character("genie"), "g1")
        self.assertEqual(voice_id_for_character("aladdin"), "a1")
        self.assertIsNone(voice_id_for_character("unknown"))

    @patch.dict(
        "security.services.ai_platform.companion_neuro_tts._DEFAULT_VOICE_BY_CHARACTER",
        {"unicorn": "u1", "genie": "", "aladdin": "a1"},
        clear=False,
    )
    def test_no_genie_fallback_for_unicorn(self):
        self.assertFalse(all_hero_voice_ids_configured())
        self.assertEqual(voice_id_for_character("unicorn"), "u1")
        self.assertIsNone(voice_id_for_character("genie"))


class TestSynthesizeGuards(unittest.TestCase):
    def test_unconfigured_raises(self):
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}, clear=False):
            with patch(
                "security.services.ai_platform.companion_neuro_tts.ELEVENLABS_API_KEY",
                "",
            ):
                with patch(
                    "security.services.ai_platform.companion_neuro_tts._DEFAULT_VOICE_BY_CHARACTER",
                    {"genie": "", "unicorn": "", "aladdin": ""},
                ):
                    with self.assertRaises(ValueError):
                        synthesize_neuro_tts(text="hi", character_id="genie")


if __name__ == "__main__":
    unittest.main()
