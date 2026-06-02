# -*- coding: utf-8 -*-
"""p3-10 canary + p3-11 postgres helpers."""

from __future__ import annotations

import os


def test_canary_bucket_stable():
    from security.services.ai_platform.wellness_canary import (
        wellness_canary_bucket,
        user_in_wellness_canary,
    )

    assert wellness_canary_bucket("42") == wellness_canary_bucket("42")
    assert user_in_wellness_canary("901701") is True  # bypass


def test_canary_percent_env(monkeypatch):
    from security.services.ai_platform import wellness_canary as wc

    monkeypatch.setenv("WELLNESS_CANARY_PERCENT", "0")
    assert wc.user_in_wellness_canary("999888777") is False
    monkeypatch.setenv("WELLNESS_CANARY_PERCENT", "100")
    assert wc.user_in_wellness_canary("999888777") is True


def test_sleep_stories_url_rewrite(monkeypatch):
    from security.services.ai_platform.wellness_sleep_stories import list_sleep_stories

    stories = list_sleep_stories(locale="ru")
    assert len(stories) >= 5
    for s in stories:
        assert "aladdin-ai.ru/static/wellness/sleep" in s["audio_url"]
        assert "cdn.aladdin-ai.ru" not in s["audio_url"]


def test_postgres_ping_sqlite_default(monkeypatch):
    from security.services.ai_platform.wellness_store_postgres import WellnessPostgresStore

    monkeypatch.delenv("WELLNESS_PG_DSN", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    ping = WellnessPostgresStore().ping()
    assert ping["backend"] == "sqlite"
    assert ping["configured"] is False


def test_parent_playbook_llm_flag_off():
    from security.services.ai_platform.wellness_parent_playbook import build_parent_playbook

    payload = build_parent_playbook(locale="ru", topic="school", use_llm=True)
    assert payload["phrases"]
    assert payload["llm_used"] is False
