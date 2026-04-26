from __future__ import annotations

from dataclasses import dataclass

from bot.config import Settings
from bot.services.fx_display import fx_payment_hints_html
from bot.util_html import esc


@dataclass(frozen=True)
class FiatInstruction:
    title: str
    body_html: str


def fiat_placeholder_html(settings: Settings, *, order_id: int, rub: float) -> FiatInstruction:
    _ = settings
    body = (
        f"Заказ <code>{esc(order_id)}</code> на сумму <b>{esc(f'{rub:.2f}')} ₽</b>.\n\n"
        "Для автоматической оплаты настройте <b>LAVA Business</b> в .env "
        "(<code>LAVA_SHOP_ID</code>, <code>LAVA_SECRET_KEY</code>, <code>LAVA_HOOK_URL</code> на Partner API) — "
        "тогда здесь появится кнопка на страницу оплаты LAVA (СБП, карты и др. по тарифам проекта).\n\n"
        "Альтернатива без LAVA: ваш бэкенд после факта оплаты вызывает "
        "<code>POST /v1/payments/provider-webhook</code> (см. документацию Partner API); "
        "пока можно отметить заказ вручную в админке бота."
    )
    return FiatInstruction(title="Оплата ₽ (LAVA или вручную)", body_html=body)


def crypto_payment_block_html(
    settings: Settings,
    *,
    order_id: int,
    rub: float,
    usd_for_fx: float = 0.0,
) -> str:
    memo = f"ORDER{order_id}"
    usd_fx = float(usd_for_fx) if usd_for_fx > 0 else 0.0
    fx = fx_payment_hints_html(settings, rub_final=rub, usd_base=usd_fx) if usd_fx > 0 else ""
    parts: list[str] = [
        f"<b>Криптооплата</b> — заказ <code>{esc(order_id)}</code>",
        f"Сумма к оплате: <b>{esc(f'{rub:.2f}')} ₽</b> (основной расчёт в ₽; в крипте принимаем <b>USDT в сети TRC20</b>).",
        "",
        "<b>Важно:</b> в комментарии / memo к переводу укажите:",
        f"<code>{esc(memo)}</code>",
        "Без этого платёж сложно сопоставить с заказом.",
        "",
    ]
    if settings.crypto_usdt_trc20:
        parts.append(f"USDT (TRC20):\n<code>{esc(settings.crypto_usdt_trc20)}</code>\n")
    else:
        parts.append("USDT (TRC20): <i>не задан в .env</i>\n")
    if settings.crypto_show_ton_manual and settings.crypto_ton:
        parts.append(f"TON (только если согласовано с поддержкой):\n<code>{esc(settings.crypto_ton)}</code>\n")
    parts.append(
        "Это <b>ручной</b> перевод (без счёта Crypto Pay / xRocket): вебхук не приходит — "
        "оператор сверит платёж по memo и отметит оплату. При необходимости напишите в поддержку с номером заказа."
    )
    body = "\n".join(parts)
    return body + fx
