from __future__ import annotations

"""Расчёт чистой прибыли по ТЗ (админ-аналитика).

Прибыль = Цена продажи − (Себестоимость + Комиссия платёжки + Реф. бонус + Реф. скидка покупателю)
где цена продажи = сумма, уплаченная клиентом (rub_after_discounts).
"""


def payment_gateway_fee_rub(sale_rub: float, fee_percent: float) -> float:
    return round(max(0.0, float(sale_rub)) * max(0.0, float(fee_percent)) / 100.0, 2)


def auto_cogs_rub(usd_base: float, usd_rub_rate: float, usd_fraction: float) -> float:
    """Оценка себестоимости: доля от номинала в ₽ по каталожному USD (настраивается)."""
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
