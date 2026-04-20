from __future__ import annotations

from dataclasses import dataclass

from bot.config import Settings
from bot.util_html import esc


@dataclass(frozen=True)
class FiatInstruction:
    title: str
    body_html: str


def fiat_placeholder_html(settings: Settings, *, order_id: int, rub: float) -> FiatInstruction:
    _ = settings
    body = (
        f"Заказ <code>{esc(order_id)}</code> на сумму <b>{esc(f'{rub:.2f}')} ₽</b>.\n\n"
        "Подключите YooKassa / Lava / Robokassa и подставьте сюда ссылку на оплату.\n"
        "После оплаты ваш оркестратор может вызвать Partner API "
        "<code>POST /v1/payments/provider-webhook</code> (см. <code>RUNBOOK</code> раздел 9); "
        "пока админ может отметить заказ вручную."
    )
    return FiatInstruction(title="Оплата СБП / картой", body_html=body)


def crypto_payment_block_html(settings: Settings, *, order_id: int, rub: float) -> str:
    memo = f"ORDER{order_id}"
    parts: list[str] = [
        f"<b>Криптооплата</b> — заказ <code>{esc(order_id)}</code>",
        f"Сумма к оплате: <b>{esc(f'{rub:.2f}')} ₽</b> (пересчитайте в USDT/TON по курсу вашего кошелька).",
        "",
        "<b>Важно:</b> в комментарии / memo к переводу укажите:",
        f"<code>{esc(memo)}</code>",
        "Без этого платёж сложно сопоставить с заказом.",
        "",
    ]
    if settings.crypto_usdt_trc20:
        parts.append(f"USDT TRC20:\n<code>{esc(settings.crypto_usdt_trc20)}</code>\n")
    else:
        parts.append("USDT TRC20: <i>не задан в .env</i>\n")
    if settings.crypto_ton:
        parts.append(f"TON:\n<code>{esc(settings.crypto_ton)}</code>\n")
    else:
        parts.append("TON: <i>не задан в .env</i>\n")
    parts.append("После отправки средств статус обновит администратор после сверки.")
    return "\n".join(parts)
