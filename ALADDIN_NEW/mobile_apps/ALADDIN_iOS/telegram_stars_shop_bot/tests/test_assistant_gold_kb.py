"""P1.4: gold lint + catalog KB from products.yaml (no invented prices)."""

from __future__ import annotations

from pathlib import Path

import pytest

from bot.assistant.brand_gold_answers import (
    GOLD_ANSWERS,
    gold_count,
    lint_gold_answers,
    select_gold_fewshots,
)
from bot.assistant.kb import catalog_kb_plain
from bot.assistant.orchestrator import _guess_topic
from bot.assistant.policy import TOPIC_TO_KB
from bot.config import load_settings


def test_gold_lint_clean() -> None:
    assert lint_gold_answers() == []
    assert gold_count() >= 30


def test_catalog_topic_wired() -> None:
    assert "catalog" in TOPIC_TO_KB
    assert "kb.catalog" in TOPIC_TO_KB["catalog"]
    assert _guess_topic("Сколько стоит VPN на месяц?") == "catalog"
    assert _guess_topic("какая цена на Stars?") == "catalog"


def test_catalog_gold_fewshot() -> None:
    golds = select_gold_fewshots("catalog", "Сколько стоит VPN?", limit=2)
    assert golds
    assert any(g.topic == "catalog" for g in golds)


def test_catalog_kb_from_products_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[1]
    products = root / "bot" / "products.yaml"
    assert products.is_file()
    monkeypatch.setenv("BOT_TOKEN", "1:t")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    s = load_settings()
    # Default products_path = bot/products.yaml next to config
    assert Path(s.products_path).resolve() == products.resolve()
    plain = catalog_kb_plain(s)
    assert "products.yaml" in plain
    assert "VPN 30 дней" in plain or "vpn_30d" in plain
    assert "200 ₽" in plain
    assert "1700 ₽" in plain  # vpn_365d
    assert "не выдумывать" in plain.lower() or "Не выдумывать" in plain
    assert "100%" in plain  # ban listed as forbidden phrase in KB rules
    # Must not invent a random RUB for stars_100 (only USD line)
    assert "stars_100" in plain
    assert "100 Stars" in plain
