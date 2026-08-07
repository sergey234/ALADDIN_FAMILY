from __future__ import annotations

from bot.config import Settings
from bot.util_html import esc


def effective_usdt_rub_rate(settings: Settings) -> float:
    """₽ за 1 USDT для отображения; при USDT_RUB_RATE=0 берётся USD_RUB_RATE."""
    if settings.usdt_rub_rate > 0:
        return float(settings.usdt_rub_rate)
    return float(settings.usd_rub_rate)


def fx_payment_hints_html(settings: Settings, *, rub_final: float, usd_base: float) -> str:
    """
    Подсказки к сумме к оплате:
    - ₽ - основной расчёт в боте (уже в rub_final).
    - USDT - ориентир по курсу магазина; сумма в реальном счёте задаётся провайдером (любая сеть USDT в счёте).
    """
    lines: list[str] = []
    rub = float(rub_final)
    usd_nom = float(usd_base)
    rub_rate = float(settings.usd_rub_rate)
    if rub_rate <= 0:
        return ""

    usdt_r = effective_usdt_rub_rate(settings)
    if usdt_r > 0:
        usdt_amt = round(rub / usdt_r, 4)
        lines.append(
            f"<b>USDT</b> - ориентир: <b>{esc(f'{usdt_amt}')}</b> USDT "
            f"(<code>{esc(f'{usdt_r}')}</code> ₽ за 1 USDT)."
        )

    if not lines:
        return ""
    header = (
        "<i><b>Цена в ₽</b> - основа заказа. Ниже - ориентир в USDT; <b>сумма USDT</b> в готовом счёте в Telegram "
        "может чуть отличаться: её фиксирует платёжный сервис при выставлении счёта.</i>"
    )
    out = [header]
    if usd_nom > 0:
        out.insert(
            0,
            f"<i>Номинал позиции в каталоге (USD, не пересчитывается курсом): ~{esc(f'{usd_nom:.2f}')} USD.</i>",
        )
    return "\n\n" + "\n".join(out + lines)
