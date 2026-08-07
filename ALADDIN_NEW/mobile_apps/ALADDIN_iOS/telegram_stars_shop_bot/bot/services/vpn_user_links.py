"""Персональные ссылки VPN: подписка Xray (/sub/) и реферал для друга + Copy Text кнопки."""

from __future__ import annotations

import base64
import logging
from urllib.parse import quote

import httpx
from aiogram import Bot
from aiogram.types import CopyTextButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services import vpn_admin_support_repo

_log = logging.getLogger(__name__)

# Короткие подписи: каждая кнопка — отдельная строка (Telegram обрезает две в ряд).
XRAY_SUBSCRIPTION_BTN = "📡 Открыть ссылку"  # legacy callback vpn:sub:link; не в новых KB
COPY_SUB_LINK_BTN = "🔗 Скопировать ссылку VPN"  # CopyText — одна кнопка на всю ширину
VPN_QR_CONNECT_BTN = "📷 QR-код подключения VPN"
MIRROR_SUBSCRIPTION_BTN = "📋 Зеркало (.com)"  # отключено на проде
XRAY_BRIDGE_BTN = "📋 Xray мост"  # vless://… «Мобильный мост» — primary 4G
XRAY_WIFI_BTN = "📋 Xray Wi‑Fi"  # vless://… «Домашний Wi-Fi»
HITWAVE_BRIDGE_BTN = XRAY_BRIDGE_BTN
HITWAVE_WIFI_BTN = XRAY_WIFI_BTN
FRIEND_INVITE_BTN = "👥 Пригласить друга"  # ref_… в бот, не ключ VPN
REFERRAL_COPY_BTN = "👥 Скопировать приглашение"
REFERRAL_SHARE_BTN = "📤 Поделиться в Telegram"
# text= для t.me/share/url; сама реф-ссылка уже в параметре url= (дублировать в тексте не нужно).
REFERRAL_SHARE_TEXT = (
    "Присоединяйся к Ai Monkey Stars — VPN, Stars и Premium в одном боте."
)
VLESS_MOBILE_RF_BTN = "📋 4G-профиль"  # vless mobile-xhttp (если мост не нужен)
VLESS_MOBILE_XHTTP_BTN = VLESS_MOBILE_RF_BTN
HAPP_SUBSCRIPTION_BTN = XRAY_SUBSCRIPTION_BTN
LEGACY_BACKUP_BTN = XRAY_SUBSCRIPTION_BTN
_COPY_TEXT_MAX = 256  # лимит Telegram CopyTextButton


def _clip_copy_text(text: str) -> str:
    t = (text or "").strip()
    if len(t) <= _COPY_TEXT_MAX:
        return t
    return t[:_COPY_TEXT_MAX]


def fits_copy_text_limit(text: str) -> bool:
    return 0 < len((text or "").strip()) <= _COPY_TEXT_MAX


def copy_text_button(*, label: str, text: str) -> InlineKeyboardButton | None:
    clipped = _clip_copy_text(text)
    if not clipped or not fits_copy_text_limit(clipped):
        return None
    return InlineKeyboardButton(
        text=label,
        copy_text=CopyTextButton(text=clipped),
    )


def subscription_copy_button(subscription_url: str) -> InlineKeyboardButton | None:
    """CopyText для /sub/… — короткая подпись, полный URL, одна кнопка в ряд."""
    return copy_text_button(label=COPY_SUB_LINK_BTN, text=subscription_url)


def referral_share_telegram_url(ref_url: str, *, share_text: str = "") -> str:
    """t.me/share/url — выбор чата и отправка ссылки отдельным сообщением."""
    ref = (ref_url or "").strip()
    base = f"https://t.me/share/url?url={quote(ref, safe='')}"
    text = (share_text or "").strip()
    if text:
        return f"{base}&text={quote(text, safe='')}"
    return base


def referral_copy_button(ref_url: str) -> InlineKeyboardButton | None:
    return copy_text_button(label=REFERRAL_COPY_BTN, text=ref_url)


def referral_share_button(
    ref_url: str,
    *,
    share_text: str | None = None,
) -> InlineKeyboardButton | None:
    ref = (ref_url or "").strip()
    if not ref:
        return None
    text = REFERRAL_SHARE_TEXT if share_text is None else share_text
    return InlineKeyboardButton(
        text=REFERRAL_SHARE_BTN,
        url=referral_share_telegram_url(ref, share_text=text),
    )


def append_referral_action_rows(b: InlineKeyboardBuilder, ref_url: str) -> None:
    """CopyText + Share URL для ref_… — профиль, «Пригласить друга», VPN."""
    copy_btn = referral_copy_button(ref_url)
    if copy_btn:
        b.row(copy_btn)
    share_btn = referral_share_button(ref_url)
    if share_btn:
        b.row(share_btn)


def parse_subscription_vless_lines(raw_body: str) -> list[str]:
    """Разбор тела GET /sub/: plain vless:// или base64 от некоторых панелей."""
    text = (raw_body or "").strip()
    if not text:
        return []
    if "vless://" not in text:
        try:
            text = base64.b64decode(text, validate=False).decode("utf-8")
        except Exception:
            return []
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("vless://")]


def pick_vless_profile_line(lines: list[str], profile_name: str = "mobile-xhttp") -> str:
    aliases = (profile_name,)
    if profile_name in ("mobile-xhttp", "mobile-rf", "Мобильный интернет"):
        aliases = ("mobile-xhttp", "mobile-rf", "Мобильный интернет")
    elif profile_name in ("wifi-direct", "default", "Домашний Wi-Fi"):
        aliases = ("wifi-direct", "default", "Домашний Wi-Fi")
    for name in aliases:
        marker = f"#{name}"
        for ln in lines:
            if ln.endswith(marker) or marker in ln:
                return ln
    return lines[0] if lines else ""


def _subscription_fetch_url(subscription_url: str) -> str:
    url = (subscription_url or "").strip()
    if not url:
        return ""
    if "plain=1" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}plain=1"
    return url


async def _fetch_vless_profile_line(subscription_url: str, profile_name: str) -> str:
    url = _subscription_fetch_url(subscription_url)
    if not url:
        return ""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url)
            r.raise_for_status()
            lines = parse_subscription_vless_lines(r.text)
            return pick_vless_profile_line(lines, profile_name)
    except Exception:
        _log.debug("fetch vless profile=%s failed url=%s", profile_name, url[:48], exc_info=True)
        return ""


async def fetch_vless_mobile_rf_line(subscription_url: str) -> str:
    return await _fetch_vless_profile_line(subscription_url, "Мобильный интернет")


async def fetch_vless_bridge_line(subscription_url: str) -> str:
    return await _fetch_vless_profile_line(subscription_url, "Мобильный мост")


async def fetch_vless_wifi_line(subscription_url: str) -> str:
    return await _fetch_vless_profile_line(subscription_url, "Домашний Wi-Fi")


def _append_copy_row(b: InlineKeyboardBuilder, *buttons: InlineKeyboardButton | None) -> None:
    row = [btn for btn in buttons if btn is not None]
    if row:
        b.row(*row)


def action_link_button(*, label: str, callback_data: str) -> InlineKeyboardButton:
    """Обычная callback-кнопка на всю ширину (без CopyText в одном ряду с другой кнопкой)."""
    return InlineKeyboardButton(text=label, callback_data=callback_data)


def _public_origin(settings: Settings) -> str:
    return (settings.vpn_public_https_origin or "").strip().rstrip("/")


def _mirror_origin(settings: Settings) -> str:
    return (settings.vpn_subscription_mirror_origin or "").strip().rstrip("/")


def backup_subscription_url(settings: Settings, opaque_token: str) -> str:
    origin = _public_origin(settings)
    tok = (opaque_token or "").strip()
    if not origin or not tok:
        return ""
    return f"{origin}/sub/{tok}"


def mirror_subscription_url(settings: Settings, opaque_token: str) -> str:
    origin = _mirror_origin(settings)
    tok = (opaque_token or "").strip()
    if not origin or not tok:
        return ""
    return f"{origin}/sub/{tok}"


async def resolve_backup_subscription_url(
    settings: Settings,
    telegram_user_id: int,
) -> str | None:
    vpath = settings.resolved_vpn_db_path()
    if vpath is None or not _public_origin(settings):
        return None
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return None
    if (row.get("status") or "").strip() != "vpn_active":
        return None
    opaque = (row.get("opaque_token") or "").strip()
    if not opaque:
        return None
    url = backup_subscription_url(settings, opaque)
    return url or None


async def resolve_mirror_subscription_url(
    settings: Settings,
    telegram_user_id: int,
) -> str | None:
    vpath = settings.resolved_vpn_db_path()
    if vpath is None or not _mirror_origin(settings):
        return None
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return None
    if (row.get("status") or "").strip() != "vpn_active":
        return None
    opaque = (row.get("opaque_token") or "").strip()
    if not opaque:
        return None
    url = mirror_subscription_url(settings, opaque)
    return url or None


def invite_ref_telegram_url(bot_username: str, user_id: int) -> str:
    """Каноническая ссылка приглашения (Stars, Premium, VPN) — как в профиле."""
    bu = (bot_username or "").strip() or "your_bot"
    return f"https://t.me/{bu}?start=ref_{user_id}"


async def resolve_friend_referral_url(bot: Bot, conn, user_id: int) -> str | None:
    _ = conn  # единая ссылка ref_; код r- в БД только для legacy /r/ редиректа
    me = await bot.get_me()
    bu = (me.username or "").strip()
    if not bu:
        return None
    return invite_ref_telegram_url(bu, user_id)


async def append_vpn_copy_link_rows(
    b: InlineKeyboardBuilder,
    *,
    settings: Settings,
    user_id: int,
) -> None:
    """Кнопки VPN-подписки (/sub/…) — только при vpn_active, без реферальной ссылки."""
    from bot.services.vpn_screen_nav import (
        VPN_XRAY_QR_PACK,
    )

    vpath = settings.resolved_vpn_db_path()
    if vpath is not None:
        row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, user_id)
        if not row or (row.get("status") or "").strip() != "vpn_active":
            return
    backup = await resolve_backup_subscription_url(settings, user_id)
    if backup:
        copy_btn = subscription_copy_button(backup)
        if copy_btn:
            b.row(copy_btn)
        # «Открыть ссылку» убрана: дублирует «Получить ключ VPN» / экран подключения.
        b.row(InlineKeyboardButton(text=VPN_QR_CONNECT_BTN, callback_data=VPN_XRAY_QR_PACK))


def subscription_link_reply_kb(
    subscription_url: str,
    *,
    settings: Settings | None = None,
    mirror_url: str = "",
    vless_mobile_rf: str = "",
    vless_bridge: str = "",
    vless_wifi: str = "",
) -> InlineKeyboardBuilder:
    from bot.services.vpn_screen_nav import VPN_NAV_MAIN, VPN_XRAY_QR_PACK

    b = InlineKeyboardBuilder()
    sub = (subscription_url or "").strip()
    if sub:
        copy_btn = subscription_copy_button(sub)
        if copy_btn:
            b.row(copy_btn)
        b.row(InlineKeyboardButton(text=VPN_QR_CONNECT_BTN, callback_data=VPN_XRAY_QR_PACK))
    b.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    return b
