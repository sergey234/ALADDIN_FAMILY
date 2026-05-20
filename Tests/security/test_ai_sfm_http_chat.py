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
