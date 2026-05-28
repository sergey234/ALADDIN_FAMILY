"""Экран принятия политики и соглашения AiMonkeyVPN (две галочки) перед тарифами и оплатой."""

from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services import users_repo
from bot.services.catalog import Product
from bot.services.vpn_tariffs import append_vpn_tariff_buy_rows, vpn_tariffs_card_html
from bot.util_html import esc

VPN_LEGAL_GATE_CALLBACK = "vpn:legal:gate"
VPN_LEGAL_CONTINUE_CALLBACK = "vpn:legal:continue"
VPN_LEGAL_ACK_PRIVACY_CALLBACK = "vpn:legal:ack:privacy"
VPN_LEGAL_ACK_TERMS_CALLBACK = "vpn:legal:ack:terms"


def vpn_docs_base(settings: Settings) -> str:
    return (settings.vpn_docs_public_base or "").strip().rstrip("/")


def vpn_privacy_and_terms_urls(settings: Settings) -> tuple[str, str]:
    base = vpn_docs_base(settings)
    if base:
        return f"{base}/vpn-data", f"{base}/vpn-terms"
    pu = (settings.privacy_policy_url or "").strip()
    tu = (settings.terms_of_service_url or "").strip()
    return pu, tu


def vpn_legal_gate_html(
    settings: Settings,
    products: list[Product],
    *,
    privacy_ok: bool,
    terms_ok: bool,
) -> str:
    pu, tu = vpn_privacy_and_terms_urls(settings)
    links = []
    if pu:
        links.append(f'<a href="{esc(pu)}">Политика конфиденциальности</a>')
    if tu:
        links.append(f'<a href="{esc(tu)}">Пользовательское соглашение</a>')
    links_block = "\n".join(f"• {x}" for x in links) if links else (
        "• Политика конфиденциальности\n• Пользовательское соглашение"
    )
    status = (
        f"\n<b>Статус:</b> политика — {'✅' if privacy_ok else '☐'}; "
        f"соглашение — {'✅' if terms_ok else '☐'}."
    )
    if privacy_ok and terms_ok:
        status += "\n<i>Можно выбрать тариф или открыть пульт VPN.</i>"
    else:
        status += "\n<i>Сначала отметьте обе галочки ниже.</i>"
    aup_line = ""
    base = vpn_docs_base(settings)
    if base:
        aup_line = (
            f'\n<i>Также: <a href="{esc(base)}/vpn-aup">правила использования (AUP)</a>.</i>'
        )
    tariffs_card = vpn_tariffs_card_html(settings, products)
    return (
        f"<b>🟢 Оплата — {esc(VPN_PRODUCT_NAME)}</b>\n\n"
        f"{tariffs_card}\n\n"
        f"<b>📋 Документы перед оплатой</b>\n"
        f"{links_block}"
        f"{status}"
        f"{aup_line}"
    )


def vpn_legal_gate_kb(
    settings: Settings,
    products: list[Product],
    *,
    privacy_ok: bool,
    terms_ok: bool,
) -> InlineKeyboardMarkup:
    pu, tu = vpn_privacy_and_terms_urls(settings)
    b = InlineKeyboardBuilder()
    append_vpn_tariff_buy_rows(b, products, settings)
    p_mark = "✅" if privacy_ok else "☐"
    t_mark = "✅" if terms_ok else "☐"
    if pu:
        b.row(
            InlineKeyboardButton(text="📄 Политика", url=pu),
            InlineKeyboardButton(
                text=f"{p_mark} Ознакомлен",
                callback_data=VPN_LEGAL_ACK_PRIVACY_CALLBACK,
            ),
        )
    else:
        b.row(
            InlineKeyboardButton(
                text=f"{p_mark} Ознакомлен с политикой",
                callback_data=VPN_LEGAL_ACK_PRIVACY_CALLBACK,
            )
        )
    if tu:
        b.row(
            InlineKeyboardButton(text="📄 Соглашение", url=tu),
            InlineKeyboardButton(
                text=f"{t_mark} Ознакомлен",
                callback_data=VPN_LEGAL_ACK_TERMS_CALLBACK,
            ),
        )
    else:
        b.row(
            InlineKeyboardButton(
                text=f"{t_mark} Ознакомлен с соглашением",
                callback_data=VPN_LEGAL_ACK_TERMS_CALLBACK,
            )
        )
    b.row(
        InlineKeyboardButton(
            text="➡️ Продолжить в пульт VPN",
            callback_data=VPN_LEGAL_CONTINUE_CALLBACK,
        )
    )
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:vpn"))
    return b.as_markup()


async def _edit_or_answer(message: Message, text: str, reply_markup: InlineKeyboardMarkup | None) -> None:
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        err = str(exc).lower()
        if "message is not modified" in err:
            return
        await message.answer(text, reply_markup=reply_markup)


async def present_vpn_legal_gate(
    message: Message,
    settings: Settings,
    conn,
    user_id: int,
    products: list[Product],
) -> None:
    privacy_ok, terms_ok = await users_repo.vpn_legal_ack_flags(conn, user_id)
    text = vpn_legal_gate_html(
        settings, products, privacy_ok=privacy_ok, terms_ok=terms_ok
    )
    kb = vpn_legal_gate_kb(
        settings, products, privacy_ok=privacy_ok, terms_ok=terms_ok
    )
    await _edit_or_answer(message, text, kb)


async def ensure_vpn_legal_accepted(
    *,
    conn,
    user_id: int,
    settings: Settings,
    message: Message,
    products: list[Product],
) -> bool:
    """True — можно идти дальше; False — показан экран галочек."""
    if await users_repo.has_vpn_legal_accepted(conn, user_id):
        return True
    await present_vpn_legal_gate(message, settings, conn, user_id, products)
    return False
