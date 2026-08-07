"""Карточный пульт «Мои устройства» в боте + ссылка на полную панель get."""

from __future__ import annotations

import html
from datetime import datetime
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.vpn_screen_nav import VPN_NAV_MAIN
from bot.services.vpn_user_links import copy_text_button

VPN_DEVICES = "vpn:devices"
VPN_DEVICES_ADD = "vpn:devices:add"
VPN_DEVICES_NAV_PREFIX = "vpn:devices:nav:"
VPN_DEVICES_QR_PREFIX = "vpn:devices:qr:"
VPN_DEVICES_REN_PREFIX = "vpn:devices:ren:"
VPN_DEVICES_REVOKE_PREFIX = "vpn:devices:rev:"
VPN_DEVICES_REVOKE_YES_PREFIX = "vpn:devices:revyes:"
VPN_DEVICES_OPEN_PANEL = "vpn:devices:panel"

_STATUS_LABEL = {
    "online": "🟢 в сети сейчас",
    "offline": "🟡 был в сети",
    "awaiting": "⚪️ ожидает подключения",
}

_KIND_ICON = {
    "iphone": "📱",
    "android": "📱",
    "tablet": "📲",
    "laptop": "💻",
    "desktop": "🖥️",
    "unknown": "📟",
}

_MONTHS_RU = (
    "",
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


def _esc(s: str) -> str:
    return html.escape(s or "", quote=False)


def devices_progress_bar(used: int, maximum: int) -> str:
    maximum = max(1, int(maximum))
    used = max(0, min(int(used), maximum))
    free_ratio = (maximum - used) / maximum
    if used >= maximum:
        color = "🔴"
    elif (maximum - used) == 1:
        color = "🟡"
    elif free_ratio > 0.20:
        color = "🟢"
    else:
        color = "🟡"
    filled = round(8 * used / maximum)
    bar = "█" * filled + "░" * (8 - filled)
    return f"{bar}  {color}"


def normalize_device_index(payload: dict[str, Any], index: int) -> int:
    devices = list(payload.get("devices") or [])
    n = len(devices)
    if n <= 0:
        return 0
    return int(index) % n


def index_of_device(payload: dict[str, Any], device_id: int) -> int:
    for i, d in enumerate(list(payload.get("devices") or [])):
        if int(d.get("id") or 0) == int(device_id):
            return i
    return 0


def format_connected_ru(iso: str | None) -> str:
    raw = (iso or "").strip()
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return ""
    month = _MONTHS_RU[dt.month] if 1 <= dt.month <= 12 else ""
    if not month:
        return ""
    return f"Подключен {dt.day} {month} {dt.year}"


def device_card_html(payload: dict[str, Any], index: int = 0) -> str:
    used = int(payload.get("used") or 0)
    maximum = int(payload.get("max") or 1)
    devices = list(payload.get("devices") or [])
    lines = [
        "<b>🏠 Мои устройства</b>",
        "",
        f"Занято <b>{used} из {maximum}</b>",
        devices_progress_bar(used, maximum),
        "",
    ]
    if not devices:
        lines.append(
            "<i>Устройства ещё нет. Подписка включает одно устройство — подключите его ниже.</i>"
        )
        lines.extend(
            [
                "",
                "<i>Несколько устройств — в планах.</i>",
            ]
        )
        return "\n".join(lines)

    idx = normalize_device_index(payload, index)
    d = devices[idx]
    kind = str(d.get("device_kind") or "unknown")
    icon = _KIND_ICON.get(kind, "📟")
    name = _esc(str(d.get("display_name") or "Устройство"))
    st = _STATUS_LABEL.get(str(d.get("status") or "awaiting"), "⚪️")
    connected = format_connected_ru(d.get("first_connected_at"))
    lines.extend(
        [
            f"{icon} <b>{name}</b>",
            st,
            connected if connected else "Ещё не подключалось",
            f"Устройство <b>{idx + 1} из {len(devices)}</b>",
            "",
            "<i>Можно бесплатно заменить. Несколько устройств — в планах.</i>",
        ]
    )
    return "\n".join(lines)


def devices_screen_html(payload: dict[str, Any]) -> str:
    """Совместимость: одна карточка с индексом 0."""
    return device_card_html(payload, 0)


def device_card_keyboard(
    payload: dict[str, Any],
    index: int = 0,
    *,
    panel_url: str = "",
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    devices = list(payload.get("devices") or [])
    used = int(payload.get("used") or 0)
    maximum = int(payload.get("max") or 1)
    can_add = bool(payload.get("can_add"))
    n = len(devices)

    if n > 1:
        idx = normalize_device_index(payload, index)
        prev_i = (idx - 1) % n
        next_i = (idx + 1) % n
        b.row(
            InlineKeyboardButton(text="‹", callback_data=f"{VPN_DEVICES_NAV_PREFIX}{prev_i}"),
            InlineKeyboardButton(text="›", callback_data=f"{VPN_DEVICES_NAV_PREFIX}{next_i}"),
        )

    if n > 0:
        idx = normalize_device_index(payload, index)
        d = devices[idx]
        did = int(d.get("id") or 0)
        url = str(d.get("subscription_url") or "").strip()
        if url:
            from bot.services.vpn_devices_platform_hub import happ_open_callback_button

            open_btn = happ_open_callback_button(did) if did > 0 else None
            if open_btn:
                b.row(open_btn)
            copy_btn = copy_text_button(label="🔗 Скопировать ссылку Happ", text=url)
            if copy_btn:
                b.row(copy_btn)
        if did > 0:
            b.row(
                InlineKeyboardButton(
                    text="📷 Показать QR",
                    callback_data=f"{VPN_DEVICES_QR_PREFIX}{did}",
                )
            )
            b.row(
                InlineKeyboardButton(
                    text="✏️ Переименовать",
                    callback_data=f"{VPN_DEVICES_REN_PREFIX}{did}",
                )
            )
            from bot.services.vpn_devices_platform_hub import replace_device_button_label

            name = str(d.get("display_name") or "Устройство")
            b.row(
                InlineKeyboardButton(
                    text=replace_device_button_label(name),
                    callback_data=f"{VPN_DEVICES_REVOKE_PREFIX}{did}",
                )
            )

    if can_add and used < maximum:
        # After revoke (0 of 1) — reconnect a replacement device.
        b.row(
            InlineKeyboardButton(
                text="➕ Подключить устройство",
                callback_data=VPN_DEVICES_ADD,
            )
        )
    # When already 1/1 — replace via «Заменить» (revoke) then add.

    if panel_url:
        b.row(
            InlineKeyboardButton(
                text="🌐 Полная панель в браузере",
                url=panel_url,
            )
        )
    b.row(InlineKeyboardButton(text="⬅️ К VPN", callback_data=VPN_NAV_MAIN))
    return b.as_markup()


def devices_keyboard(payload: dict[str, Any], *, panel_url: str = "") -> InlineKeyboardMarkup:
    """Совместимость: карточка с индексом 0."""
    return device_card_keyboard(payload, 0, panel_url=panel_url)


def devices_panel_url(origin: str) -> str:
    base = (origin or "https://aimonkeystars.ru").rstrip("/")
    return f"{base}/devices"


def devices_revoke_confirm_kb(device_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text="Да, заменить",
            callback_data=f"{VPN_DEVICES_REVOKE_YES_PREFIX}{int(device_id)}",
        )
    )
    b.row(InlineKeyboardButton(text="Отмена", callback_data=VPN_DEVICES))
    return b.as_markup()


def devices_revoke_confirm_html(*, display_name: str = "") -> str:
    name = _esc((display_name or "").strip())
    who = f"«{name}»" if name else "это устройство"
    return (
        "<b>Заменить устройство?</b>\n\n"
        f"Отвяжем {who}: старая ссылка станет недействительной.\n"
        "После этого можно подключить новое устройство (снова 1 из 1)."
    )
