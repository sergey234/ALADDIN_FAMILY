"""Support URL loop detection + refund table for Lava."""

from __future__ import annotations

from types import SimpleNamespace

from bot.services.marketing import refund_policy_blurb_html, refund_policy_table_html
from bot.support_links import (
    external_human_support_url,
    support_prefill_url,
    support_url_is_shop_bot_loop,
)


def _s(**kwargs):
    base = dict(support_url="", support_username="", refund_policy_url="https://aimonkeystars.ru/v1/legal/refund")
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_shop_bot_support_url_is_loop() -> None:
    assert support_url_is_shop_bot_loop(_s(support_url="https://t.me/AiMonkeyStars_bot")) is True
    assert support_url_is_shop_bot_loop(_s(support_url="https://t.me/AiMonkeyStars_bot?start=1")) is True
    assert support_url_is_shop_bot_loop(_s(support_username="AiMonkeyStars_bot")) is True
    assert support_url_is_shop_bot_loop(_s()) is True


def test_external_human_support_url() -> None:
    assert external_human_support_url(_s(support_url="https://t.me/AiMonkeyStars_bot")) is None
    assert external_human_support_url(_s(support_url="https://t.me/SomeHumanSupport")) == "https://t.me/SomeHumanSupport"
    assert support_prefill_url(_s(support_url="https://t.me/AiMonkeyStars_bot"), "hi") is None
    assert "text=" in (support_prefill_url(_s(support_url="https://t.me/SomeHumanSupport"), "hi") or "")


def test_refund_table_has_lava_timelines() -> None:
    html = refund_policy_table_html(_s())
    assert "5 минут" in html
    assert "3 календарных" in html
    assert "14 календарных" in html
    assert "10 рабочих" in html
    assert "14 рабочих" in html
    assert "выдан" in html.lower()
    blurb = refund_policy_blurb_html(_s())
    assert "5 мин" in blurb or "5 минут" in blurb
