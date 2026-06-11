# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from security.services.llm_providers import openrouter_direct_client as orc


def test_direct_fallback_disabled(monkeypatch):
    monkeypatch.setenv("FEATURE_OPENROUTER_DIRECT_FALLBACK", "0")
    ok, text, err = orc.chat_once("hi")
    assert not ok
    assert err and "disabled" in err


def test_no_api_key(monkeypatch):
    monkeypatch.setenv("FEATURE_OPENROUTER_DIRECT_FALLBACK", "1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("HERMES_OPENROUTER_API_KEY", raising=False)
    ok, text, err = orc.chat_once("hi")
    assert not ok
    assert "OPENROUTER_API_KEY" in (err or "")


def test_chat_once_success(monkeypatch):
    monkeypatch.setenv("FEATURE_OPENROUTER_DIRECT_FALLBACK", "1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    payload = json.dumps(
        {"choices": [{"message": {"content": "  два  "}}]}
    ).encode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = payload
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        ok, text, err = orc.chat_once("1+1?")
    assert ok
    assert text == "два"
    assert err is None


def test_companion_system_suffix(monkeypatch):
    monkeypatch.setenv("FEATURE_OPENROUTER_DIRECT_FALLBACK", "1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    captured = {}

    def fake_urlopen(req, timeout=0):
        body = json.loads(req.data.decode())
        captured["system"] = body["messages"][0]["content"]
        payload = json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode()
        m = MagicMock()
        m.read.return_value = payload
        m.__enter__ = lambda s: s
        m.__exit__ = MagicMock(return_value=False)
        return m

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        orc.chat_once("привет", ui_context="companion")
    assert "ребёнка" in captured.get("system", "")
