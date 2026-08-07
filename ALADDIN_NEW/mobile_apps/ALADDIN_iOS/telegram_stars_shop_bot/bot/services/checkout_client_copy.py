"""Клиентские тексты checkout Stars / Premium / VPN (ТЗ Миши). Без техтерминов."""

from __future__ import annotations

from bot.config import Settings
from bot.util_html import esc

RULE = "━━━━━━━━━━━━━━"

# Запрещены на клиентских экранах (тесты).
FORBIDDEN_CLIENT_TERMS = (
    "База заказа",
    "База:",
    "номинал",
    "курс магазина",
    "Курс USDT",
    "курс USDT",
    "ориентир",
    "фиксируется",
    "фиксирует",
)


def usd_equiv(settings: Settings, rub: float) -> float:
    rate = float(settings.usd_rub_rate or 0.0)
    if rate <= 0:
        return 0.0
    return float(rub) / rate


def price_block_html(settings: Settings, rub: float, *, catalog_usd: float | None = None) -> str:
    """Только ₽ и ≈USD. Курсы/USDT/номинал — не показывать."""
    rub_s = esc(f"{float(rub):.2f}")
    usd = usd_equiv(settings, rub)
    if usd <= 0 and catalog_usd is not None and float(catalog_usd) > 0:
        usd = float(catalog_usd)
    usd_s = esc(f"{usd:.2f}")
    return (
        f"<b>Стоимость</b>\n"
        f"🇷🇺 <b>{rub_s} ₽</b>\n"
        f"🇺🇸 ≈ <b>{usd_s} USD</b>\n"
        f"<i>Цена обновляется автоматически по курсу ЦБ.</i>"
    )


def format_product_heading(emoji: str, title: str) -> str:
    em = (emoji or "").strip()
    tt = esc((title or "").strip())
    if em:
        return f"<b>{em} {tt}</b>"
    return f"<b>{tt}</b>"


def _title(raw: str) -> str:
    """Заголовок уже собран нами (emoji + title); экранируем целиком безопасно по частям не нужно."""
    return f"<b>{raw}</b>" if not raw.startswith("<b>") else raw


def offer_with_recipient_choice_html(
    settings: Settings,
    *,
    title: str,
    rub: float,
    catalog_usd: float,
    kind: str,
) -> str:
    """Экран после выбора товара: цена + вопрос «кому»."""
    ask = "👤 Кому отправить Stars?" if kind == "stars" else "👤 Кому оформить Premium?"
    return (
        f"{_title(title)}\n"
        f"{RULE}\n"
        f"{price_block_html(settings, rub, catalog_usd=catalog_usd)}\n"
        f"{RULE}\n"
        f"<b>{ask}</b>"
    )


def review_html(
    settings: Settings,
    *,
    title: str,
    rub: float,
    catalog_usd: float,
    recipient: str,
    for_self: bool,
    kind: str,
) -> str:
    """Экран проверки перед «Перейти к оплате»."""
    if for_self:
        head = "⭐ Покупка для себя" if kind == "stars" else "⭐ Premium для себя"
    else:
        head = "⭐ Покупка Stars" if kind == "stars" else "⭐ Telegram Premium"
    return (
        f"<b>{head}</b>\n\n"
        f"{_title(title)}\n"
        f"{RULE}\n"
        f"<b>Получатель</b>\n"
        f"<code>{esc(recipient)}</code>\n"
        f"{RULE}\n"
        f"{price_block_html(settings, rub, catalog_usd=catalog_usd)}"
    )


def ask_username_html(*, kind: str) -> str:
    what = "Stars" if kind == "stars" else "Premium"
    return (
        f"<b>Введите @username получателя</b>\n\n"
        f"Кому отправить {what}?\n"
        f"Пример: <code>@nickname</code>"
    )


def payment_methods_intro_html(
    settings: Settings,
    *,
    title: str,
    rub: float,
    catalog_usd: float,
    recipient: str | None = None,
) -> str:
    lines = [
        _title(title),
        RULE,
        price_block_html(settings, rub, catalog_usd=catalog_usd),
    ]
    if recipient:
        lines.extend([RULE, f"<b>Получатель</b>\n<code>{esc(recipient)}</code>"])
    lines.extend([RULE, "<b>Выберите способ оплаты</b>"])
    return "\n".join(lines)


def vpn_offer_html(
    settings: Settings,
    *,
    title: str,
    rub: float,
    catalog_usd: float,
) -> str:
    """VPN перед выбором оплаты: как Stars — ₽ + ≈USD + фраза про ЦБ."""
    return (
        f"{_title(title)}\n"
        f"{RULE}\n"
        f"{price_block_html(settings, rub, catalog_usd=catalog_usd)}\n"
        f"{RULE}\n"
        f"<b>Выберите способ оплаты</b>"
    )


def invoice_brief_html(
    settings: Settings,
    *,
    title: str,
    rub: float,
    catalog_usd: float = 0.0,
    recipient: str = "",
    deadline: str = "",
    balance_applied: float = 0.0,
    pay_crypto: bool = False,
) -> str:
    """Короткий счёт после создания заказа (Stars/Premium)."""
    lines = [
        _title(title),
        RULE,
        price_block_html(settings, rub, catalog_usd=catalog_usd or None),
    ]
    if balance_applied > 0.01:
        lines.append(f"С баланса учтено: <b>{esc(f'{balance_applied:.2f}')} ₽</b>")
    if recipient:
        lines.extend([RULE, f"<b>Получатель</b>\n<code>{esc(recipient)}</code>"])
    if deadline:
        lines.extend([RULE, f"⏰ Оплатите до <b>{esc(deadline)}</b>"])
    if pay_crypto:
        lines.append("\nНиже — оплата <b>USDT</b>.")
    else:
        lines.append("\nНажмите кнопку оплаты ниже.")
    return "\n".join(lines)


def vpn_invoice_brief_html(
    settings: Settings,
    *,
    title: str,
    rub: float,
    catalog_usd: float = 0.0,
    until_disp: str = "",
    deadline: str = "",
    balance_applied: float = 0.0,
    pay_crypto: bool = False,
    legal_html: str = "",
) -> str:
    lines = [
        _title(title),
        RULE,
        price_block_html(settings, rub, catalog_usd=catalog_usd or None),
    ]
    if balance_applied > 0.01:
        lines.append(f"С баланса учтено: <b>{esc(f'{balance_applied:.2f}')} ₽</b>")
    if until_disp:
        lines.extend([RULE, f"Подписка до: <b>{esc(until_disp)}</b>"])
    if deadline:
        lines.append(f"⏰ Оплатите до <b>{esc(deadline)}</b>")
    if pay_crypto:
        lines.append("\nНиже — оплата <b>USDT</b>.")
    else:
        lines.append("\nНажмите кнопку оплаты ниже.")
    if legal_html:
        lines.append(legal_html)
    return "\n".join(lines)


def assert_no_forbidden_client_terms(html: str) -> None:
    low = html.lower()
    for term in FORBIDDEN_CLIENT_TERMS:
        if term.lower() in low:
            raise AssertionError(f"forbidden client term in html: {term!r}")
