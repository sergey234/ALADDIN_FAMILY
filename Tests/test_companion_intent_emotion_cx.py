# -*- coding: utf-8 -*-
"""P1-27, P1-28, P1-30 + GATE-CX auto (D01–D03 classification/emotion)."""

from __future__ import annotations

import unittest

# GATE-CX D01–D03 fixtures (FINAL_PLAN § GATE-DIALOG)
D01_CHILD_JOKE = "Расскажи смешную историю про единорога!"
D02_TEEN_LONELY = "Мне 14, в классе никто не разговаривает, одиноко"
D03_SENIOR_BORED = "Мне 68, дома одна, скучно, некому поговорить"


class CompanionIntentRouterTests(unittest.TestCase):
    def test_d01_playful_humor_domain(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent(D01_CHILD_JOKE, "child")
        self.assertEqual(r.mood, "playful")
        self.assertEqual(r.intent_id, "companion_humor")
        self.assertIn(r.domain, ("news_fun", "games", "hobbies", "general"))

    def test_d02_teen_loneliness_not_safety(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent(D02_TEEN_LONELY, "teen")
        self.assertEqual(r.domain, "loneliness")
        self.assertIn(r.mood, ("lonely", "sad", "comfort_needed"))
        self.assertNotEqual(r.domain, "safety")
        self.assertEqual(r.intent_id, "companion_loneliness")

    def test_d03_senior_lonely_daily(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent(D03_SENIOR_BORED, "senior")
        self.assertEqual(r.domain, "loneliness")
        self.assertIn(r.mood, ("lonely", "nostalgic", "comfort_needed"))

    def test_feel_lonely_not_wellness_domain(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent("я чувствую себя одиноким", "child")
        self.assertEqual(r.domain, "loneliness")
        self.assertEqual(r.mood, "lonely")

    def test_safety_domain_on_phishing(self):
        from security.services.ai_platform.companion_intent_router import classify_companion_intent

        r = classify_companion_intent("В письме фишинговая ссылка, что делать?", "parent")
        self.assertEqual(r.domain, "safety")
        self.assertEqual(r.intent_id, "companion_safety")


class CompanionEmotionTests(unittest.TestCase):
    def test_d01_emotion_playful(self):
        from security.services.ai_platform.companion_emotions import emotion_for_mood

        self.assertEqual(emotion_for_mood(D01_CHILD_JOKE), "playful")

    def test_d02_emotion_comfort(self):
        from security.services.ai_platform.companion_emotions import emotion_for_mood

        self.assertIn(emotion_for_mood(D02_TEEN_LONELY), ("comfort", "sad"))

    def test_d03_emotion_nostalgic_or_comfort(self):
        from security.services.ai_platform.companion_emotions import emotion_for_mood

        self.assertIn(emotion_for_mood(D03_SENIOR_BORED), ("comfort", "nostalgic", "sad"))

    def test_d10_style_phrases(self):
        from security.services.ai_platform.companion_emotions import emotion_for_mood

        self.assertEqual(emotion_for_mood("Ура, у меня получилось пятёрка!"), "happy")
        self.assertEqual(emotion_for_mood("Мне грустно сегодня"), "sad")
        self.assertEqual(emotion_for_mood("Расскажи анекдот!"), "playful")
        self.assertEqual(emotion_for_mood("Фишинг в письме"), "alert")


class CompanionAgePersonaTests(unittest.TestCase):
    def test_four_age_band_addons(self):
        from security.services.ai_platform.companion_persona import (
            age_band_persona_addon,
            companion_system_base,
        )

        for band in ("child", "teen", "parent", "senior"):
            addon = age_band_persona_addon(band)
            self.assertGreater(len(addon), 20)
            base = companion_system_base("unicorn", band)
            self.assertIn(addon, base)

    def test_teen_not_child_wording(self):
        from security.services.ai_platform.companion_persona import companion_system_base

        teen = companion_system_base("unicorn", "teen").lower()
        senior = companion_system_base("aladdin", "senior").lower()
        self.assertIn("морализ", teen)
        self.assertIn("60+", senior)


if __name__ == "__main__":
    unittest.main()
