"""FIN profit_compute unit tests (no DB)."""

from types import SimpleNamespace

from bot.services import profit_compute as pc


def _settings(**kw):
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
        auto_cogs_usd_fraction=0.85,
        vpn_cogs_rub=100.0,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def test_vpn_fee_zero_and_cogs_zero():
    s = _settings()
    assert pc.fee_percent_for_rail(s, "sbp", product_kind="vpn") == 0.0
    box: list[float] = []
    cogs = pc.resolve_cogs_rub_for_order(
        product_kind="vpn",
        manual_cogs_rub=None,
        usd_base=10,
        usd_rub_rate=90,
        auto_cogs_fraction=0.85,
        vpn_cogs_rub=100,
        settings=s,
        cogs_usdt_out=box,
    )
    assert cogs == 0.0
    assert box[0] == 0.0
    net = pc.net_profit_rub(
        sale_rub=200, cogs_rub=0, payment_fee_rub=0, referral_bonus_rub=0, referral_discount_rub=0
    )
    assert net == 200.0


def test_stars_fragment_and_sbp_fee():
    s = _settings()
    assert pc.fee_percent_for_rail(s, "sbp", product_kind="stars") == 3.4
    usdt = pc.fragment_cogs_usdt(
        product_kind="stars", stars_qty=1000, premium_months=None, settings=s
    )
    assert usdt == 15.0
    box: list[float] = []
    cogs = pc.resolve_cogs_rub_for_order(
        product_kind="stars",
        manual_cogs_rub=None,
        usd_base=16.5,
        usd_rub_rate=100.0,
        auto_cogs_fraction=0.85,
        stars_qty=1000,
        settings=s,
        cogs_usdt_out=box,
    )
    assert box[0] == 15.0
    assert cogs == 1500.0  # 15 * 100
    fee = pc.payment_gateway_fee_rub(1000, 3.4)
    assert fee == 34.0
    net = pc.net_profit_rub(
        sale_rub=1000, cogs_rub=cogs, payment_fee_rub=fee, referral_bonus_rub=0, referral_discount_rub=0
    )
    assert net == 1000 - 1500 - 34  # negative possible if sale < cogs at test rate


def test_premium_table_and_rails():
    s = _settings()
    assert pc.fragment_cogs_usdt(
        product_kind="premium", stars_qty=None, premium_months=1, settings=s
    ) == 11.99
    assert pc.fragment_cogs_usdt(
        product_kind="premium", stars_qty=None, premium_months=3, settings=s
    ) == 11.99
    assert pc.fragment_cogs_usdt(
        product_kind="premium", stars_qty=None, premium_months=6, settings=s
    ) == 15.99
    assert pc.fragment_cogs_usdt(
        product_kind="premium", stars_qty=None, premium_months=12, settings=s
    ) == 28.99
    assert pc.fee_percent_for_rail(s, "lava_card", product_kind="stars") == 6.0
    assert pc.fee_percent_for_rail(s, "crypto_bot", product_kind="stars") == 3.0
    assert pc.fee_percent_for_rail(s, "xrocket", product_kind="stars") == 1.5


def test_infer_rail():
    assert pc.infer_payment_rail(lava_pay_service="sbp") == "sbp"
    assert pc.infer_payment_rail(invoice_last_provider="crypto_pay") == "crypto_bot"
    assert pc.infer_payment_rail(invoice_last_provider="xrocket") == "xrocket"
    assert pc.infer_payment_rail(payment_method="fiat", invoice_last_provider="lava") == "lava_card"


def test_f7_user_handlers_have_no_profit_jargon():
    """User-facing handlers must not leak FIN/admin profit fields."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "bot" / "handlers"
    bad = (
        "net_profit_rub",
        "payment_fee_percent_snapshot",
        "cogs_usdt",
        "fragment_star_usdt",
        "fee_lava_card",
        "admin_profit_breakdown",
    )
    for name in ("shop.py", "hub.py", "vpn.py", "common.py"):
        text = (root / name).read_text(encoding="utf-8")
        for b in bad:
            assert b not in text, f"{name} contains {b}"
