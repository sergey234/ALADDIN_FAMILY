# -*- coding: utf-8 -*-
"""Prod-safe SFM HTTP chat responses (no 1074 stub)."""
from security.services.ai_sfm_http_chat import build_ai_assistant_chat_result
from security.services.ai_response_helpers import is_probable_mock_response


def test_meta_learn_question_no_forbidden_phrase():
    result = build_ai_assistant_chat_result({
        "message": "Ты учишься?",
        "context": "general",
        "sfm_aggregates": {"protection_status": "ACTIVE", "healthy_components": 4, "total_components": 4},
        "sfm_context_sources": ["get_components_health"],
    })
    text = result["response"]
    assert "1074" not in text
    assert "реальный ai" not in text.lower()
    assert "не «учусь»" in text.lower() or "не обуча" in text.lower()
    assert not is_probable_mock_response(text)


def test_simple_math_offline():
    result = build_ai_assistant_chat_result({
        "message": "1+1 сколько будет?",
        "context": "general",
        "sfm_aggregates": {"protection_status": "ACTIVE"},
        "sfm_context_sources": ["get_analytics_overview"],
    })
    assert "2" in result["response"]
    assert "ALADDIN" in result["response"]


def test_threats_use_aggregates():
    result = build_ai_assistant_chat_result({
        "message": "сколько угроз заблокировано",
        "context": "general",
        "sfm_aggregates": {"threats_blocked": 12, "protection_status": "ACTIVE"},
        "sfm_context_sources": ["get_analytics_overview"],
    })
    assert "12" in result["response"]
    assert result.get("grounded") is True


def test_companion_context_no_threats_template_on_casual_question():
    result = build_ai_assistant_chat_result({
        "message": "как дела у тебя",
        "context": "companion",
        "sfm_aggregates": {"threats_blocked": 47, "protection_status": "ACTIVE"},
        "sfm_context_sources": [],
    })
    text = result["response"]
    assert "47" not in text
    assert "заблокировала" not in text.lower()


def test_companion_user_turn_extraction_strips_system_prefix():
    """Mirror of ai_assistant_router._companion_user_turn_for_sfm (no FastAPI import)."""
    text = (
        "[ALADDIN Family Companion — Единорог]\n"
        "Суперсила ALADDIN (~30%, по запросу): угрозы и VPN.\n"
        "\n[Companion routing: domain=friendship; mood=happy.]\n"
        "как дела?"
    )
    marker = "\n[Companion routing:"
    tail = text.rsplit(marker, 1)[-1]
    user_turn = tail.split("]", 1)[-1].strip()
    assert user_turn == "как дела?"
