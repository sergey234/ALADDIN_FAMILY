# -*- coding: utf-8 -*-
"""hero-x-41…43 topic policy, OOS, wellness guard."""

from security.services.ai_platform.companion_intent_router import (
    COMPANION_DOMAINS,
    classify_companion_intent,
)
from security.services.ai_platform.companion_topic_policy import (
    apply_wellness_topic_guard,
    check_out_of_scope,
    classify_topic_domain,
)


class TestCompanionTopicPolicy:
    def test_expanded_domains_in_ssot(self):
        for d in (
            "philosophy",
            "money_worries",
            "sleep",
            "pets",
            "parenting_stress",
        ):
            assert d in COMPANION_DOMAINS

    def test_money_worries_domain(self):
        r = classify_companion_intent("не хватает денег на кредит", "parent", "aladdin")
        assert r.domain == "money_worries"
        assert r.domain_confidence >= 0.55

    def test_pets_domain(self):
        r = classify_companion_intent("моя собака заболела", "teen", "unicorn")
        assert r.domain == "pets"

    def test_oos_medical_hint(self):
        hint = check_out_of_scope("поставь мне диагноз депрессии", locale="ru")
        assert "врач" in hint.lower() or "диагноз" in hint.lower()

    def test_oos_explicit_hint(self):
        hint = check_out_of_scope("расскажи про секс 18+", locale="ru")
        assert "18" in hint

    def test_low_confidence_graceful_hint(self):
        topic = classify_topic_domain("ну эээ", fallback_domain="general", locale="ru")
        assert topic.low_confidence_hint
        assert "robotic" in topic.low_confidence_hint.lower()

    def test_wellness_guard_clamps_domain(self):
        base = classify_companion_intent("не хватает денег", "parent", "aladdin")
        assert base.domain == "money_worries"
        guarded = apply_wellness_topic_guard(base, "cognitive")
        assert guarded.domain == "wellness"
        assert "cognitive" in guarded.response_hint
        assert guarded.intent_id == "companion_wellness_session"

    def test_wellness_mood_not_overridden_by_career(self):
        r = classify_companion_intent("мне грустно на работе", "parent", "aladdin")
        assert r.domain == "wellness"
