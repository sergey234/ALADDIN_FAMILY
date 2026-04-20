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
    - ₽ — основной расчёт в боте (уже в rub_final).
    - USDT — по курсу USDT_RUB_RATE (или USD_RUB_RATE), считается как точный пересчёт из ₽.
    - UAH / BYN — ориентир через «сколько UAH/BYN за 1 USD» и курс ₽/USD (без гарантии рыночного курса).
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
            f"<b>USDT</b> (пересчёт из ₽ по курсу из .env): <b>{esc(f'{usdt_amt}')}</b> USDT "
            f"(<code>{esc(f'{usdt_r}')}</code> ₽ за 1 USDT)."
        )

    if settings.display_usd_uah_rate > 0:
        uah = round(rub * (settings.display_usd_uah_rate / rub_rate), 2)
        lines.append(
            f"<i>Ориентир UAH (через USD, приблизительно): ≈ {esc(f'{uah}')} UAH к сумме {esc(f'{rub:.2f}')} ₽.</i>"
        )
    if settings.display_usd_byn_rate > 0:
        byn = round(rub * (settings.display_usd_byn_rate / rub_rate), 2)
        lines.append(
            f"<i>Ориентир BYN (через USD, приблизительно): ≈ {esc(f'{byn}')} BYN к сумме {esc(f'{rub:.2f}')} ₽.</i>"
        )

    if not lines:
        return ""
    header = (
        "<i>Дополнительно к ₽: USDT — по вашему курсу в .env; UAH/BYN — только ориентир для пользователя.</i>"
    )
    out = [header]
    if usd_nom > 0:
        out.insert(0, f"<i>Номинал в прайсе (USD): ~{esc(f'{usd_nom:.2f}')} USD.</i>")
    return "\n\n" + "\n".join(out + lines)
