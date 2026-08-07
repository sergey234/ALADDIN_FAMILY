"""QR подписки /sub/ для Happ."""

from __future__ import annotations

import logging

from aiogram.types import BufferedInputFile, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.vpn_screen_nav import HAPP_PLUS_BTN, VPN_HAPP_INSTALL_VIDEO, VPN_NAV_MAIN, kb_back_main
from bot.services.vpn_user_links import COPY_SUB_LINK_BTN, subscription_copy_button
from bot.services.wg_qr_util import pay_url_qr_png_bytes as text_qr_png_bytes

_log = logging.getLogger(__name__)


def xray_import_reply_kb(*, sub_url: str, vless_line: str = "") -> InlineKeyboardBuilder:
    _ = vless_line
    b = InlineKeyboardBuilder()
    sub = (sub_url or "").strip()
    if sub:
        copy_btn = subscription_copy_button(sub)
        if copy_btn:
            b.row(copy_btn)
    b.row(InlineKeyboardButton(text=HAPP_PLUS_BTN, callback_data=VPN_HAPP_INSTALL_VIDEO))
    b.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    return b


async def send_xray_import_pack(
    message: Message,
    *,
    sub_url: str,
    vless_mobile_rf: str = "",
) -> None:
    """QR подписки — Happ."""
    sub = (sub_url or "").strip()
    if not sub:
        return

    kb = xray_import_reply_kb(sub_url=sub, vless_line=vless_mobile_rf).as_markup()

    try:
        png = text_qr_png_bytes(sub)
        await message.answer_photo(
            BufferedInputFile(png, filename="aimonkey-vpn-sub-qr.png"),
            caption=(
                "<b>📷 QR-код для подключения</b>\n"
                "Happ → «+» → Добавить подписку → скан QR.\n"
                f"Или «{COPY_SUB_LINK_BTN}» → вставить URL в Happ."
            ),
            reply_markup=kb,
        )
    except Exception:
        _log.exception("send_xray_import_pack failed chat_id=%s", message.chat.id)
        await message.answer(
            f"Не удалось отправить QR. Нажмите «{COPY_SUB_LINK_BTN}» в личном кабинете "
            f"или «{HAPP_PLUS_BTN}» для инструкции.",
            reply_markup=kb_back_main(),
        )
