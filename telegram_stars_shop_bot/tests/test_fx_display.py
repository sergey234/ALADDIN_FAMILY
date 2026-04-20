from __future__ import annotations

from bot.config import Settings
from bot.services.fx_display import effective_usdt_rub_rate, fx_payment_hints_html


def test_effective_usdt_falls_back_to_usd_rate(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "0")
    s = Settings()
    assert effective_usdt_rub_rate(s) == 100.0


def test_effective_usdt_explicit(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "99")
    s = Settings()
    assert effective_usdt_rub_rate(s) == 99.0


def test_fx_hints_usdt_only(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("USDT_RUB_RATE", "100")
    s = Settings()
    html = fx_payment_hints_html(s, rub_final=1000.0, usd_base=10.0)
    assert "USDT" in html
    assert "10" in html or "10.0" in html


def test_fx_hints_uah_when_set(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:test")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("DISPLAY_USD_UAH_RATE", "42")
    s = Settings()
    html = fx_payment_hints_html(s, rub_final=1000.0, usd_base=10.0)
    assert "UAH" in html
    # 1000 * 42/100 = 420
    assert "420" in html
