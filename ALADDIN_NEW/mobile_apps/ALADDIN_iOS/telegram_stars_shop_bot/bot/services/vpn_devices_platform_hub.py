"""Гибрид «Все устройства»: витрина платформ (A) / пульт слота (B) отдельно.

Гость → iPhone | Android | iPad + короткие шаги.
Оплативший → «Мои устройства» (см. vpn_devices_ux), не этот модуль.
"""

from __future__ import annotations

import html

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.vpn_happ_constants import (
    HAPP_ANDROID_APP_NAME,
    HAPP_ANDROID_PLAY_URL,
    HAPP_APP_NAME,
    HAPP_IOS_APP_STORE_GLOBAL_URL,
)
from bot.services.vpn_connect_copy import vpn_tariffs_cta_label
from bot.services.vpn_legal_gate import VPN_LEGAL_GATE_CALLBACK
from bot.services.vpn_screen_nav import (
    VPN_HUB_BACK_BTN,
    VPN_NAV_MARKETING,
    append_happ_install_video_row,
)
from bot.services.vpn_trial_service import append_vpn_trial_row

# Re-export for callers that check active VPN on device cards
async def _platform_cta_active(settings, user_id: int) -> bool:
    from bot.services import vpn_admin_support_repo
    from bot.services.vpn_subscription_dates import parse_paid_until_utc
    from datetime import datetime, timezone

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return False
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, user_id)
    if not row or (row.get("status") or "").strip() != "vpn_active":
        return False
    end = parse_paid_until_utc((row.get("paid_until") or "").strip())
    if end is None:
        return False
    return end > datetime.now(timezone.utc)

VPN_Y_DEV = "vpn:y:dev"
VPN_Y_DEV_IPHONE = "vpn:y:dev:iphone"
VPN_Y_DEV_ANDROID = "vpn:y:dev:android"
VPN_Y_DEV_IPAD = "vpn:y:dev:ipad"
VPN_DEVICES_OPEN_HAPP_PREFIX = "vpn:devices:openhapp:"

_HAPP_OPEN_BTN = "📲 Открыть в Happ"
_REPLACE_BTN_PREFIX = "♻️ Заменить:"

DEVICE_LIMIT_FOOTER_HTML = (
    "<i>Сейчас — одно устройство. Можно бесплатно заменить.\n"
    "Несколько устройств — в планах.</i>"
)


def _esc(s: str) -> str:
    return html.escape(s or "", quote=False)


def happ_add_deeplink(subscription_url: str) -> str:
    """One-tap импорт: happ://add/ + plain https URL (без base64)."""
    url = (subscription_url or "").strip()
    if not url:
        return ""
    return f"happ://add/{url}"


def happ_open_callback_button(device_id: int) -> InlineKeyboardButton | None:
    """Кнопка-callback: Telegram не принимает happ:// в url= кнопок."""
    did = int(device_id or 0)
    if did <= 0:
        return None
    return InlineKeyboardButton(
        text=_HAPP_OPEN_BTN,
        callback_data=f"{VPN_DEVICES_OPEN_HAPP_PREFIX}{did}",
    )


def happ_open_message_html(subscription_url: str) -> str:
    sub = (subscription_url or "").strip()
    deeplink = happ_add_deeplink(sub)
    if not deeplink:
        return "Ссылка Happ пока недоступна."
    safe_sub = _esc(sub)
    # Текст-ссылка: клиент может открыть happ://; плюс обычный https для копирования.
    return (
        "<b>📲 Открыть в Happ</b>\n\n"
        f'<a href="{_esc(deeplink)}">Нажмите, чтобы открыть Happ</a>\n\n'
        f"Или скопируйте ссылку подписки:\n<code>{safe_sub}</code>"
    )


# Совместимость со старыми импортами/тестами: url-кнопка больше не используется в UI.
def happ_open_url_button(subscription_url: str) -> InlineKeyboardButton | None:
    _ = subscription_url
    return None


def devices_hub_html() -> str:
    """Корень витрины A — без /sub/ и без управления слотом."""
    return (
        "<b>📱 Мои устройства</b>\n\n"
        "Выберите, на чём будете подключать VPN — "
        "короткая инструкция под вашу платформу.\n\n"
        f"{DEVICE_LIMIT_FOOTER_HTML}"
    )


def devices_hub_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📱 iPhone", callback_data=VPN_Y_DEV_IPHONE),
        InlineKeyboardButton(text="🤖 Android", callback_data=VPN_Y_DEV_ANDROID),
    )
    b.row(InlineKeyboardButton(text="📲 iPad", callback_data=VPN_Y_DEV_IPAD))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=VPN_NAV_MARKETING))
    return b.as_markup()


def platform_iphone_html() -> str:
    name = _esc(HAPP_APP_NAME)
    return (
        "<b>📱 iPhone</b>\n\n"
        f"<b>1.</b> Установите <b>{name}</b> из App Store "
        "(если нет в РФ-каталоге — видео ниже).\n"
        f"<b>2.</b> В Happ: Настройки → <b>HWID</b> → включить "
        "<i>до</i> добавления подписки.\n"
        "<b>3.</b> Оплатите VPN в боте → получите ссылку → "
        "Happ → «+» → Добавить подписку.\n\n"
        f"{DEVICE_LIMIT_FOOTER_HTML}"
    )


def platform_android_html() -> str:
    name = _esc(HAPP_ANDROID_APP_NAME)
    return (
        f"<b>🤖 Android</b>\n\n"
        f"<b>1.</b> Google Play → установите <b>{name}</b> (Flyfrog LLC).\n"
        f"<b>2.</b> В Happ: Настройки → <b>HWID</b> → включить "
        "<i>до</i> добавления подписки.\n"
        "<b>3.</b> Оплатите VPN в боте → получите ссылку → "
        "Happ → «+» → Добавить подписку.\n\n"
        f"<i>Не ставьте «Happ VPN» с платной подпиской внутри — ключ только из бота.</i>\n\n"
        f"{DEVICE_LIMIT_FOOTER_HTML}"
    )


def platform_ipad_html() -> str:
    name = _esc(HAPP_APP_NAME)
    return (
        "<b>📲 iPad</b>\n\n"
        f"Тот же клиент, что на iPhone — <b>{name}</b>, "
        "но это <b>отдельное</b> устройство.\n\n"
        f"<b>1.</b> Установите <b>{name}</b> на iPad из App Store.\n"
        f"<b>2.</b> HWID → включить до импорта подписки.\n"
        "<b>3.</b> После оплаты добавьте подписку в Happ на планшете.\n\n"
        f"{DEVICE_LIMIT_FOOTER_HTML}"
    )


def platform_card_html(slug: str) -> str:
    key = (slug or "").strip().lower()
    if key == "iphone":
        return platform_iphone_html()
    if key == "android":
        return platform_android_html()
    if key == "ipad":
        return platform_ipad_html()
    return devices_hub_html()


async def platform_card_kb(
    slug: str,
    settings,
    conn,
    user_id: int,
) -> InlineKeyboardMarkup:
    """Платформа: магазин (+видео iPhone/iPad) + оплата/trial + назад к hub."""
    key = (slug or "").strip().lower()
    b = InlineKeyboardBuilder()
    if key in ("iphone", "ipad"):
        b.row(
            InlineKeyboardButton(
                text="📲 Открыть Happ в App Store",
                url=HAPP_IOS_APP_STORE_GLOBAL_URL,
            )
        )
        append_happ_install_video_row(b)
    elif key == "android":
        b.row(
            InlineKeyboardButton(
                text="📲 Открыть в Google Play",
                url=HAPP_ANDROID_PLAY_URL,
            )
        )
    b.row(
        InlineKeyboardButton(
            text=vpn_tariffs_cta_label(active=await _platform_cta_active(settings, user_id)),
            callback_data=VPN_LEGAL_GATE_CALLBACK,
        ),
    )
    await append_vpn_trial_row(b, settings, conn, user_id)
    b.row(InlineKeyboardButton(text="⬅️ К устройствам", callback_data=VPN_Y_DEV))
    b.row(InlineKeyboardButton(text=VPN_HUB_BACK_BTN, callback_data="nav:hub"))
    return b.as_markup()


def replace_device_button_label(display_name: str) -> str:
    name = (display_name or "устройство").strip() or "устройство"
    label = f"{_REPLACE_BTN_PREFIX} {name}"
    return label[:64]
