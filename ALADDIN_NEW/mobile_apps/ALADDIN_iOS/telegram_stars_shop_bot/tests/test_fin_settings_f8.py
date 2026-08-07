"""F8: fin_settings overrides + Premium 1м TBD display."""

from __future__ import annotations

from types import SimpleNamespace

import aiosqlite
import pytest

from bot.config import Settings
from bot.services import fin_settings_repo as fsr
from bot.services import admin_ux
from bot.services.admin_stats_repo import DashboardAgg


def _ns(**kw):
    base = dict(
        fee_lava_card_percent=6.0,
        fee_sbp_percent=3.4,
        fee_crypto_bot_percent=3.0,
        fee_xrocket_percent=1.5,
        fragment_star_usdt=0.015,
        fragment_premium_3m_usdt=11.99,
        fragment_premium_6m_usdt=15.99,
        fragment_premium_12m_usdt=28.99,
        fragment_premium_1m_usdt=0.0,
        vpn_rent_monthly_rub=0.0,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _settings(**kw) -> Settings:
    """Real Settings via model_construct (ignore .env)."""
    base = dict(
        bot_token="9:test",
        usd_rub_rate=90.0,
        fee_lava_card_percent=6.0,
        fee_sbp_percent=3.4,
        fee_crypto_bot_percent=3.0,
        fee_xrocket_percent=1.5,
        fragment_star_usdt=0.015,
        fragment_premium_3m_usdt=11.99,
        fragment_premium_6m_usdt=15.99,
        fragment_premium_12m_usdt=28.99,
        fragment_premium_1m_usdt=0.0,
        vpn_rent_monthly_rub=0.0,
    )
    base.update(kw)
    return Settings.model_construct(**base)


def test_normalize_and_1m_unset():
    assert fsr.normalize_fin_key("fee_sbp") == "fee_sbp"
    assert fsr.normalize_fin_key("1m") == "fragment_1m"
    assert fsr.normalize_fin_key("nope") is None
    assert fsr.premium_1m_cogs_unset(_ns()) is True
    assert fsr.premium_1m_cogs_unset(_ns(fragment_premium_1m_usdt=4.99)) is False


def test_apply_overrides_copy():
    s = _settings()
    s2 = fsr.apply_overrides(s, {"fee_sbp": 2.5, "fragment_1m": 4.99})
    assert s.fee_sbp_percent == 3.4
    assert s2.fee_sbp_percent == 2.5
    assert s2.fragment_premium_1m_usdt == 4.99


def test_finance_hub_shows_1m_tbd():
    agg = DashboardAgg(
        revenue_rub=100.0,
        orders_count=1,
        net_profit_rub=10.0,
        stars_units_sold=0,
        stars_revenue_rub=0.0,
        premium_units_sold=0,
        premium_revenue_rub=0.0,
    )
    text = admin_ux.format_finance_hub(
        period_label_s="7 дней",
        agg=agg,
        fragment_1m=0.0,
        override_keys={"fee_sbp"},
    )
    assert "не задано (TBD)" in text
    assert "admin_fin_set" in text
    assert "✎" in text


@pytest.mark.asyncio
async def test_fin_settings_roundtrip():
    async with aiosqlite.connect(":memory:") as conn:
        await fsr.ensure_fin_settings_table(conn)
        await fsr.set_value(conn, "fragment_1m", 4.99, updated_by=1)
        allv = await fsr.get_all(conn)
        assert allv["fragment_1m"] == pytest.approx(4.99)
        s = await fsr.settings_with_overrides(conn, _settings())
        assert s.fragment_premium_1m_usdt == pytest.approx(4.99)
        await fsr.clear_key(conn, "1m")
        assert "fragment_1m" not in await fsr.get_all(conn)
