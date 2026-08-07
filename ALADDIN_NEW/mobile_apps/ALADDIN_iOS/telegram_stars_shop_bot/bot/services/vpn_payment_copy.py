"""Тексты оплаты VPN: СБП/QR, карта (не путать с QR подключения Happ)."""

from __future__ import annotations

from bot.config import Settings
from bot.services.lava_api import lava_checkout_configured
from bot.util_html import esc

# Подписи кнопок (лимит Telegram ~64 символа)
VPN_SBP_INVOICE_BTN = "🍐 СБП · QR в банке"
VPN_CARD_INVOICE_BTN = "💳 Карта"

_VPN_PAY_RULE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


def order_invoice_fiat_methods_hint_html(
    settings: Settings, *, payment_method: str, product_kind: str | None = None
) -> str:
    """Подсказка на экране счёта: СБП / карта / крипта."""
    from bot.services.crypto_pay_api import crypto_pay_invoice_api_ready
    from bot.services.xrocket_pay_api import xrocket_invoice_api_ready

    pm = (payment_method or "").strip().lower()
    kind = (product_kind or "").strip().lower()
    has_lava = lava_checkout_configured(settings)
    has_crypto = crypto_pay_invoice_api_ready(settings) or xrocket_invoice_api_ready(settings)

    lines: list[str] = []
    if has_lava and pm not in ("crypto", "mix_crypto", "mixcr"):
        lines.append(
            f"• <b>{esc(VPN_SBP_INVOICE_BTN)}</b> или <b>💳 Карта</b> — "
            "<b>откроется страница оплаты</b> сразу. На ней QR НСПК (СБП) и оплата картой."
        )
    if has_crypto and (pm in ("crypto", "mix_crypto", "mixcr") or pm in ("fiat", "mix_fiat", "mixfi")):
        lines.append("• <b>₿ USDT / крипта</b> — счёт в Crypto Pay или xRocket.")
    if not lines:
        return "Выберите способ оплаты ниже."
    if kind == "vpn":
        lines.append(
            "\n<i>📷 QR НСПК — только оплата. Ключ VPN — ссылка <code>/sub/…</code> в Happ после оплаты.</i>"
        )
    return "\n".join(lines)


def vpn_invoice_fiat_methods_hint_html(settings: Settings, *, payment_method: str) -> str:
    """Подсказка на экране счёта VPN (совместимость)."""
    return order_invoice_fiat_methods_hint_html(
        settings, payment_method=payment_method, product_kind="vpn"
    )


def vpn_invoice_sbp_checkout_html(*, order_id: int, rub_due: float, qr_in_chat: bool) -> str:
    """Экран после выбора СБП: пошагово, без путаницы с VPN-QR."""
    rub_s = esc(f"{float(rub_due):.2f}")
    oid_s = esc(str(order_id))
    qr_note = (
        "<i>Ниже придёт <b>картинка QR</b> — откроет страницу оплаты; "
        "на ней будет QR СБП для банка.</i>\n"
        if qr_in_chat
        else "<i>QR появится на открывшейся странице LAVA — не ищите его в меню VPN.</i>\n"
    )
    steps = (
        "1️⃣ Нажмите <b>«📱 Открыть СБП (QR)»</b> ниже.\n"
        "2️⃣ На странице найдите <b>QR для СБП</b> (или кнопку «Оплатить по СБП»).\n"
        "3️⃣ Отсканируйте QR в <b>приложении банка</b> на телефоне.\n"
        "4️⃣ Проверьте сумму <b>"
        f"{rub_s} ₽</b> и подтвердите платёж.\n"
        "5️⃣ Вернитесь в бот — статус «Оплачен» обычно за 1–3 мин."
    )
    return (
        f"<b>{esc(VPN_SBP_INVOICE_BTN)}</b>\n"
        f"Заказ <code>{oid_s}</code> · <b>{rub_s} ₽</b>\n\n"
        f"{_VPN_PAY_RULE}\n"
        f"<blockquote><b>Как оплатить за 30 секунд</b>\n{steps}</blockquote>\n"
        f"{_VPN_PAY_RULE}\n\n"
        f"{qr_note}"
        "<i>Карту и второй QR СБП не нажимайте — достаточно одной оплаты.</i>"
    )


def vpn_invoice_card_checkout_html(*, order_id: int, rub_due: float) -> str:
    rub_s = esc(f"{float(rub_due):.2f}")
    oid_s = esc(str(order_id))
    return (
        f"<b>{esc(VPN_CARD_INVOICE_BTN)}</b>\n"
        f"Заказ <code>{oid_s}</code> · <b>{rub_s} ₽</b>\n\n"
        "Нажмите <b>«💳 Оплатить картой»</b> ниже.\n"
        "На странице введите данные карты. Сумма должна совпадать с заказом.\n\n"
        "<i>Если нужен QR — выберите «СБП · QR в банке» на предыдущем экране.</i>"
    )


def vpn_invoice_pay_url_button_label(*, channel: str) -> str:
    ch = (channel or "").strip().lower()
    if ch == "sbp":
        return "📱 Открыть СБП (QR)"
    if ch == "card":
        return "💳 Оплатить картой"
    return "➡️ Перейти к оплате"
