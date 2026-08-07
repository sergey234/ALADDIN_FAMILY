"""Лестница VPN-цен: год выгоднее помесячной оплаты."""

from __future__ import annotations

from pathlib import Path

import pytest

from bot.config import Settings
from bot.services.catalog import load_products
from bot.services.pricing import list_price_rub
from bot.services.vpn_tariffs import (
    VPN_BASELINE_MONTH_RUB,
    list_vpn_products,
    vpn_tariff_button_label,
    vpn_tariff_savings_rub,
)


def test_vpn_price_ladder_year_is_best_deal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USD_RUB_RATE", "90")
    monkeypatch.setenv("BOT_TOKEN", "1:x")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "x" * 32)
    s = Settings()
    by_id = {p.id: p for p in load_products(Path("bot/products.yaml"))}

    assert by_id["vpn_30d"].price_rub == 200.0
    assert VPN_BASELINE_MONTH_RUB == 200.0

    ladder = [
        (30, 200.0),
        (90, 500.0),
        (180, 900.0),
        (365, 1700.0),
    ]
    per_month: list[float] = []
    for days, rub in ladder:
        pid = {30: "vpn_30d", 90: "vpn_90d", 180: "vpn_180d", 365: "vpn_365d"}[days]
        assert by_id[pid].price_rub == rub
        assert list_price_rub(by_id[pid], s) == rub
        months = days / 30.0
        per_month.append(rub / months)

    # Строго падающая цена за месяц: год дешевле 6 мес. дешевле 3 мес. дешевле 1 мес.
    assert per_month == sorted(per_month, reverse=True)
    assert per_month[-1] < per_month[0]

    year_save = vpn_tariff_savings_rub(days=365, rub_total=1700.0)
    six_save = vpn_tariff_savings_rub(days=180, rub_total=900.0)
    # 365/30 × 200 − 1700 ≈ 733 ₽; 6×200 − 900 = 300 ₽
    assert year_save == pytest.approx(200.0 * (365 / 30.0) - 1700.0, abs=0.01)
    assert six_save == 300.0
    assert year_save > six_save

    label = vpn_tariff_button_label(by_id["vpn_365d"], s)
    assert "1700" in label
    assert "👑" in label
    assert "лучшая цена" not in label.lower()
    assert "экономия" not in label.lower()

    visible = list_vpn_products(list(by_id.values()))
    days_vis = [int(p.vpn_subscription_days or 0) for p in visible]
    assert 7 not in days_vis
    assert 270 not in days_vis
    assert 30 in days_vis
    assert 365 in days_vis
