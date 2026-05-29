# -*- coding: utf-8 -*-
import os

from security.services.hermes_key_rotator import (
    load_api_keys,
    rotate_to_next_key,
    should_rotate_on_error,
)


def test_should_rotate_on_429_401_403():
    assert should_rotate_on_error("HTTP 429 rate limit")
    assert should_rotate_on_error("Error code: 403 - requires a subscription")
    assert should_rotate_on_error("invalid api key http 401")
    assert not should_rotate_on_error("connection timeout")


def test_rotate_cycles_keys(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_OPENROUTER_API_KEYS", "key-a,key-b,key-c")
    monkeypatch.setenv("HERMES_KEY_ROTATOR_STATE", str(tmp_path / "idx"))
    assert load_api_keys() == ["key-a", "key-b", "key-c"]
    from security.services import hermes_key_rotator as mod

    monkeypatch.setattr(mod, "_write_index", lambda p, i: p.write_text(str(i)))
    monkeypatch.setattr(mod, "_read_index", lambda p, n: int(p.read_text()) if p.is_file() else 0)
    tmp_path.joinpath("idx").write_text("0")
    rotated, key = rotate_to_next_key("http 429")
    assert rotated is True
    assert key == "key-b"
