"""Экран документов AiMonkeyVPN перед оплатой / trial (одно подтверждение навсегда)."""

from __future__ import annotations

from typing import Literal

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services import users_repo
from bot.services.catalog import Product
from bot.services.vpn_tariffs import append_vpn_tariff_buy_rows, vpn_tariffs_card_html
from bot.services.vpn_screen_nav import (
    VPN_HAPP_INSTALL_VIDEO_BTN,
    VPN_MANAGE_BTN,
    VPN_NAV_MAIN,
    VPN_TRIAL_ACTIVATE,
    append_happ_install_video_row,
)
from bot.services.vpn_connect_copy import vpn_tariffs_cta_label, vpn_trial_offer_html
from bot.services.vpn_trial_copy import vpn_trial_button_text, vpn_trial_period_title
from bot.util_html import esc

VPN_LEGAL_GATE_CALLBACK = "vpn:legal:gate"
VPN_LEGAL_CONTINUE_CALLBACK = "vpn:legal:continue"
# Legacy callbacks — старые сообщения в чате с галочками.
VPN_LEGAL_ACK_PRIVACY_CALLBACK = "vpn:legal:ack:privacy"
VPN_LEGAL_ACK_TERMS_CALLBACK = "vpn:legal:ack:terms"

VPN_LEGAL_CONTINUE_BTN = "✅ Продолжить"


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
    privacy_ok: bool = False,
    terms_ok: bool = False,
    flow: Literal["purchase", "trial"] = "purchase",
) -> str:
    """Текст экрана согласия (без галочек). products/privacy_ok/terms_ok — для совместимости."""
    _ = products, privacy_ok, terms_ok
    pu, tu = vpn_privacy_and_terms_urls(settings)
    links = []
    if pu:
        links.append(f'<a href="{esc(pu)}">Политика конфиденциальности</a>')
    if tu:
        links.append(f'<a href="{esc(tu)}">Пользовательское соглашение</a>')
    links_block = "\n".join(f"• {x}" for x in links) if links else (
        "• Политика конфиденциальности\n• Пользовательское соглашение"
    )
    aup_line = ""
    base = vpn_docs_base(settings)
    if base:
        aup_line = (
            f'\n<i>Также: <a href="{esc(base)}/vpn-aup">правила использования (AUP)</a>.</i>'
        )
    continue_hint = (
        f"Нажмите «{esc(VPN_LEGAL_CONTINUE_BTN)}» — это подтверждение, что вы "
        "ознакомились с документами. Дальше откроется выбор тарифа (или пробный период)."
    )
    if flow == "trial":
        header = f"{vpn_trial_offer_html(settings)}\n\n"
        docs_title = f"Документы перед {esc(vpn_trial_period_title(settings).lower())}"
    else:
        header = f"<b>{esc(vpn_tariffs_cta_label(active=False))} — {esc(VPN_PRODUCT_NAME)}</b>\n\n"
        docs_title = "Документы перед выбором тарифа"
    return (
        f"{header}"
        f"<b>📋 {docs_title}</b>\n"
        f"{links_block}"
        f"{aup_line}\n\n"
        f"<i>{continue_hint}</i>"
    )


def vpn_legal_gate_kb(
    settings: Settings,
    products: list[Product],
    *,
    privacy_ok: bool = False,
    terms_ok: bool = False,
    flow: Literal["purchase", "trial"] = "purchase",
) -> InlineKeyboardMarkup:
    """Только ссылки на документы + «Продолжить» (галочек нет)."""
    _ = products, privacy_ok, terms_ok, flow
    pu, tu = vpn_privacy_and_terms_urls(settings)
    b = InlineKeyboardBuilder()
    if pu:
        b.row(InlineKeyboardButton(text="📄 Политика конфиденциальности", url=pu))
    if tu:
        b.row(InlineKeyboardButton(text="📄 Пользовательское соглашение", url=tu))
    b.row(InlineKeyboardButton(text=VPN_LEGAL_CONTINUE_BTN, callback_data=VPN_LEGAL_CONTINUE_CALLBACK))
    b.row(InlineKeyboardButton(text=VPN_MANAGE_BTN, callback_data=VPN_NAV_MAIN))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:vpn"))
    return b.as_markup()


def vpn_purchase_html(settings: Settings, products: list[Product]) -> str:
    return (
        f"<b>{esc(vpn_tariffs_cta_label(active=False))} — {esc(VPN_PRODUCT_NAME)}</b>\n\n"
        f"{vpn_tariffs_card_html(settings, products)}\n\n"
        f"<b>📲 Нет Happ на iPhone?</b> Кнопка «{esc(VPN_HAPP_INSTALL_VIDEO_BTN)}» — "
        "видео и шаги смены региона App Store."
    )


def vpn_purchase_kb(settings: Settings, products: list[Product]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    append_happ_install_video_row(b)
    append_vpn_tariff_buy_rows(b, products, settings)
    b.row(InlineKeyboardButton(text=VPN_MANAGE_BTN, callback_data=VPN_NAV_MAIN))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:vpn"))
    return b.as_markup()


def vpn_trial_ready_html(settings: Settings) -> str:
    return (
        f"<b>🎁 {esc(vpn_trial_period_title(settings))} — {esc(VPN_PRODUCT_NAME)}</b>\n\n"
        f"{vpn_trial_offer_html(settings)}\n\n"
        f"<i>Документы приняты. Нажмите «{esc(vpn_trial_button_text(settings))}» ниже.</i>"
    )


def vpn_trial_ready_kb(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    append_happ_install_video_row(b)
    b.row(
        InlineKeyboardButton(
            text=vpn_trial_button_text(settings),
            callback_data=VPN_TRIAL_ACTIVATE,
        )
    )
    b.row(InlineKeyboardButton(text=VPN_MANAGE_BTN, callback_data=VPN_NAV_MAIN))
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
    *,
    flow: Literal["purchase", "trial"] = "purchase",
) -> None:
    _ = conn, user_id
    text = vpn_legal_gate_html(settings, products, flow=flow)
    kb = vpn_legal_gate_kb(settings, products, flow=flow)
    await _edit_or_answer(message, text, kb)


async def present_vpn_purchase_screen(
    message: Message,
    settings: Settings,
    products: list[Product],
) -> None:
    await _edit_or_answer(message, vpn_purchase_html(settings, products), vpn_purchase_kb(settings, products))


async def present_vpn_trial_ready_screen(message: Message, settings: Settings) -> None:
    await _edit_or_answer(message, vpn_trial_ready_html(settings), vpn_trial_ready_kb(settings))


async def present_vpn_checkout_or_legal(
    message: Message,
    settings: Settings,
    conn,
    user_id: int,
    products: list[Product],
    *,
    flow: Literal["purchase", "trial"] = "purchase",
) -> None:
    """Гибрид: без accept — документы + «Продолжить»; с accept — сразу оплата/trial."""
    if await users_repo.has_vpn_legal_accepted(conn, user_id):
        if flow == "trial":
            await present_vpn_trial_ready_screen(message, settings)
        else:
            await present_vpn_purchase_screen(message, settings, products)
        return
    await present_vpn_legal_gate(message, settings, conn, user_id, products, flow=flow)


async def ensure_vpn_legal_accepted(
    *,
    conn,
    user_id: int,
    settings: Settings,
    message: Message,
    products: list[Product],
) -> bool:
    """True — можно идти дальше; False — показан экран документов."""
    if await users_repo.has_vpn_legal_accepted(conn, user_id):
        return True
    await present_vpn_legal_gate(message, settings, conn, user_id, products, flow="purchase")
    return False
