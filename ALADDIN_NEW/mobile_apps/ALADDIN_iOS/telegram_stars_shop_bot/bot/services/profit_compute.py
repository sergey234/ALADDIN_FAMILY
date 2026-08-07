from __future__ import annotations

"""Админ-аналитика прибыли (ТЗ FIN: ADMIN_FINANCE_PROFIT_TZ_RU.md).

VPN: net = sale (fee 0%, Fragment нет).
Stars/Premium: sale − Fragment(USDT) − fee(method) − реф.
Комиссии: lava_card 6% · sbp 3.4% · crypto_bot 3% · xrocket 1.5%.
"""

from typing import Any

# Canonical payment rails for fee lookup / reporting.
RAIL_LAVA_CARD = "lava_card"
RAIL_SBP = "sbp"
RAIL_CRYPTO_BOT = "crypto_bot"
RAIL_XROCKET = "xrocket"
RAIL_UNKNOWN = "unknown"


def payment_gateway_fee_rub(sale_rub: float, fee_percent: float) -> float:
    return round(max(0.0, float(sale_rub)) * max(0.0, float(fee_percent)) / 100.0, 2)


def auto_cogs_rub(usd_base: float, usd_rub_rate: float, usd_fraction: float) -> float:
    """Legacy: доля каталожного USD (до FIN Fragment table)."""
    u = max(0.0, float(usd_base))
    r = max(0.0, float(usd_rub_rate))
    f = max(0.0, min(1.0, float(usd_fraction)))
    return round(u * r * f, 2)


def net_profit_rub(
    *,
    sale_rub: float,
    cogs_rub: float,
    payment_fee_rub: float,
    referral_bonus_rub: float,
    referral_discount_rub: float,
) -> float:
    return round(
        float(sale_rub)
        - float(cogs_rub)
        - float(payment_fee_rub)
        - float(referral_bonus_rub)
        - float(referral_discount_rub),
        2,
    )


def normalize_payment_rail(raw: str | None) -> str:
    t = (raw or "").strip().lower().replace("-", "_").replace(" ", "_")
    if t in ("sbp", "sbp_qr", "sbpqr", "pay_sbp"):
        return RAIL_SBP
    if t in ("lava_card", "card", "bank", "fiat", "lava", "bank_card"):
        return RAIL_LAVA_CARD
    if t in ("crypto_bot", "cryptobot", "crypto_pay", "cryptopay", "crypto", "mix_crypto", "mixcr"):
        return RAIL_CRYPTO_BOT
    if t in ("xrocket", "x_rocket", "rocket"):
        return RAIL_XROCKET
    if t in (RAIL_UNKNOWN, ""):
        return RAIL_UNKNOWN
    return t if t in (RAIL_LAVA_CARD, RAIL_SBP, RAIL_CRYPTO_BOT, RAIL_XROCKET) else RAIL_UNKNOWN


def infer_payment_rail(
    *,
    payment_rail: str | None = None,
    payment_method: str | None = None,
    invoice_last_provider: str | None = None,
    lava_pay_service: str | None = None,
) -> str:
    """Best-effort rail from order fields / webhook."""
    if payment_rail:
        n = normalize_payment_rail(payment_rail)
        if n != RAIL_UNKNOWN:
            return n
    if lava_pay_service:
        n = normalize_payment_rail(lava_pay_service)
        if n != RAIL_UNKNOWN:
            return n
    prov = (invoice_last_provider or "").strip().lower()
    if prov in ("crypto_pay", "cryptobot", "crypto"):
        return RAIL_CRYPTO_BOT
    if prov in ("xrocket",):
        return RAIL_XROCKET
    if prov in ("lava", "ckassa", "cardlink"):
        # card vs sbp only known via pay_service / explicit rail
        pm = (payment_method or "").strip().lower()
        if "sbp" in pm:
            return RAIL_SBP
        return RAIL_LAVA_CARD
    pm = (payment_method or "").strip().lower()
    if pm in ("crypto", "mix_crypto", "mixcr") or "crypto" in pm:
        return RAIL_CRYPTO_BOT
    if "xrocket" in pm or "rocket" in pm:
        return RAIL_XROCKET
    if "sbp" in pm:
        return RAIL_SBP
    if pm in ("fiat", "card", "bank", "lava"):
        return RAIL_LAVA_CARD
    return RAIL_UNKNOWN


def fee_percent_for_rail(settings: Any, rail: str, *, product_kind: str) -> float:
    """VPN → 0%. Else per-rail settings; unknown → lava_card % (conservative)."""
    kind = (product_kind or "").strip().lower()
    if kind == "vpn":
        return 0.0
    r = normalize_payment_rail(rail)
    if r == RAIL_SBP:
        return float(getattr(settings, "fee_sbp_percent", 3.4) or 0)
    if r == RAIL_CRYPTO_BOT:
        return float(getattr(settings, "fee_crypto_bot_percent", 3.0) or 0)
    if r == RAIL_XROCKET:
        return float(getattr(settings, "fee_xrocket_percent", 1.5) or 0)
    # lava_card + unknown
    return float(getattr(settings, "fee_lava_card_percent", 6.0) or 0)


def fragment_cogs_usdt(
    *,
    product_kind: str,
    stars_qty: int | None,
    premium_months: int | None,
    settings: Any,
) -> float:
    """Закуп Fragment в USDT. VPN / unknown → 0."""
    kind = (product_kind or "").strip().lower()
    if kind == "vpn":
        return 0.0
    if kind in ("stars", "gift"):
        qty = int(stars_qty or 0)
        if qty <= 0:
            return 0.0
        per = float(getattr(settings, "fragment_star_usdt", 0.015) or 0.015)
        return round(qty * per, 6)
    if kind == "premium":
        months = int(premium_months or 0)
        if months == 3:
            return float(getattr(settings, "fragment_premium_3m_usdt", 11.99) or 11.99)
        if months == 6:
            return float(getattr(settings, "fragment_premium_6m_usdt", 15.99) or 15.99)
        if months == 12:
            return float(getattr(settings, "fragment_premium_12m_usdt", 28.99) or 28.99)
        if months == 1:
            v = getattr(settings, "fragment_premium_1m_usdt", None)
            if v is not None and float(v) > 0:
                return float(v)
            return 11.99  # канон: 1м = 11.99 USDT (внутренняя закупка)
        return 0.0
    return 0.0


def resolve_cogs_rub_for_order(
    *,
    product_kind: str,
    manual_cogs_rub: float | None,
    usd_base: float,
    usd_rub_rate: float,
    auto_cogs_fraction: float,
    vpn_cogs_rub: float = 0.0,
    stars_qty: int | None = None,
    premium_months: int | None = None,
    settings: Any | None = None,
    cogs_usdt_out: list[float] | None = None,
) -> float:
    """Себестоимость ₽: manual → VPN 0 → Fragment USDT×rate → legacy 85% USD."""
    if manual_cogs_rub is not None:
        if cogs_usdt_out is not None:
            cogs_usdt_out.clear()
            cogs_usdt_out.append(0.0)
        return round(max(0.0, float(manual_cogs_rub)), 2)
    kind = (product_kind or "").strip().lower()
    if kind == "vpn":
        # ТЗ FIN: Fragment нет; аренда не в snapshot (vpn_cogs_rub игнорируем для net).
        if cogs_usdt_out is not None:
            cogs_usdt_out.clear()
            cogs_usdt_out.append(0.0)
        _ = vpn_cogs_rub  # legacy env retained, not applied to VPN net
        return 0.0
    usdt = 0.0
    if settings is not None:
        usdt = fragment_cogs_usdt(
            product_kind=kind,
            stars_qty=stars_qty,
            premium_months=premium_months,
            settings=settings,
        )
    if cogs_usdt_out is not None:
        cogs_usdt_out.clear()
        cogs_usdt_out.append(float(usdt))
    if usdt > 1e-9:
        return round(usdt * max(0.0, float(usd_rub_rate)), 2)
    # Legacy fallback for odd rows without qty/months
    return auto_cogs_rub(usd_base, usd_rub_rate, auto_cogs_fraction)


def admin_profit_breakdown_html(order_row, *, payment_gateway_fee_percent: float | None = None) -> str:
    """Краткая расшифровка прибыли в карточке заказа (админ)."""
    from bot.util_html import esc

    sale = float(order_row["rub_after_discounts"] or 0)
    fee = float(order_row["payment_gateway_fee_rub"] or 0)
    cogs = float(order_row["cogs_rub"] or 0)
    ref_bonus = float(order_row["commission_rub"] or 0)
    ref_disc = float(order_row["referral_discount_rub"] or 0)
    net = float(order_row["net_profit_rub"] or 0)
    kind = (order_row["product_kind"] or "").strip().lower()
    try:
        pct = float(order_row["payment_fee_percent_snapshot"])
    except (KeyError, TypeError, ValueError):
        pct = float(payment_gateway_fee_percent or 0)
    try:
        rail = str(order_row["payment_rail"] or "") or "—"
    except (KeyError, TypeError):
        rail = "—"
    try:
        cogs_u = float(order_row["cogs_usdt"] or 0)
    except (KeyError, TypeError, ValueError):
        cogs_u = 0.0

    parts: list[str] = [f"{esc(f'{sale:.2f}')} ₽"]
    if kind == "vpn":
        parts.append("− 0 ₽ комиссия платёжки (VPN: вся сумма в чистую)")
    else:
        parts.append(
            f"− {esc(f'{fee:.2f}')} ₽ комиссия ({esc(rail)}, {pct:g}%)"
        )
    if ref_bonus > 0.009:
        parts.append(f"− {esc(f'{ref_bonus:.2f}')} ₽ реф. бонус")
    if ref_disc > 0.009:
        parts.append(f"− {esc(f'{ref_disc:.2f}')} ₽ реф. скидка")
    if kind == "vpn":
        parts.append("− 0 ₽ Fragment (нет) · аренда серверов — только оценка Dashboard")
    elif cogs_u > 1e-9:
        parts.append(
            f"− {esc(f'{cogs:.2f}')} ₽ Fragment ({esc(f'{cogs_u:.4g}')} USDT)"
        )
    elif cogs > 0.009:
        parts.append(f"− {esc(f'{cogs:.2f}')} ₽ себестоимость")

    formula = "\n".join(f"• {p}" for p in parts)
    return (
        f"\n\n💰 <b>Чистая прибыль:</b> <b>{esc(f'{net:.2f}')} ₽</b>\n"
        f"{formula}"
    )
