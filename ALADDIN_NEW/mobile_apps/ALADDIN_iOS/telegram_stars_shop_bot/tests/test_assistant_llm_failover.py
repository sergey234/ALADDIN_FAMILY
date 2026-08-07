"""LLM model chain / failover helpers."""

from __future__ import annotations

from types import SimpleNamespace

from bot.assistant.llm_client import assistant_llm_model_chain, _is_retryable


def test_openrouter_default_free_chain() -> None:
    s = SimpleNamespace(
        assistant_llm_model="deepseek/deepseek-chat",
        assistant_llm_fallback_models="",
        assistant_llm_base_url="https://openrouter.ai/api/v1",
    )
    chain = assistant_llm_model_chain(s)  # type: ignore[arg-type]
    assert chain[0] == "deepseek/deepseek-chat"
    assert "openrouter/free" in chain
    assert any(m.endswith(":free") for m in chain)


def test_explicit_fallback_overrides_defaults() -> None:
    s = SimpleNamespace(
        assistant_llm_model="openrouter/free",
        assistant_llm_fallback_models="a:free,b:free,openrouter/free",
        assistant_llm_base_url="https://openrouter.ai/api/v1",
    )
    chain = assistant_llm_model_chain(s)  # type: ignore[arg-type]
    assert chain == ["openrouter/free", "a:free", "b:free"]


def test_retryable_codes() -> None:
    assert _is_retryable("http_402")
    assert _is_retryable("http_429")
    assert not _is_retryable("http_401")
    assert not _is_retryable("llm_not_configured")
