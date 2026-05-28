"""Персональные ссылки VPN: запасная подписка и реферал для друга + Copy Text кнопки."""

from __future__ import annotations

from aiogram import Bot
from aiogram.types import CopyTextButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services import vpn_admin_support_repo

_COPY_TEXT_MAX = 256


def _clip_copy_text(text: str) -> str:
    t = (text or "").strip()
    if len(t) <= _COPY_TEXT_MAX:
        return t
    return t[:_COPY_TEXT_MAX]


def copy_text_button(*, label: str, text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=label,
        copy_text=CopyTextButton(text=_clip_copy_text(text)),
    )


def _public_origin(settings: Settings) -> str:
    return (settings.vpn_public_https_origin or "").strip().rstrip("/")


def backup_subscription_url(settings: Settings, opaque_token: str) -> str:
    origin = _public_origin(settings)
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
    bot: Bot,
    settings: Settings,
    conn,
    user_id: int,
) -> None:
    """Кнопки «Скопировать запасную» / «Скопировать для друга» — только при vpn_active."""
    vpath = settings.resolved_vpn_db_path()
    if vpath is not None:
        row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, user_id)
        if not row or (row.get("status") or "").strip() != "vpn_active":
            return
    backup = await resolve_backup_subscription_url(settings, user_id)
    friend = await resolve_friend_referral_url(bot, conn, user_id)
    if backup and friend:
        b.row(
            copy_text_button(label="📋 Скопировать запасную", text=backup),
            copy_text_button(label="👥 Скопировать приглашение", text=friend),
        )
    elif backup:
        b.row(copy_text_button(label="📋 Скопировать запасную", text=backup))
    elif friend:
        b.row(copy_text_button(label="👥 Скопировать приглашение", text=friend))


def subscription_link_reply_kb(subscription_url: str) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    if subscription_url.strip():
        b.row(copy_text_button(label="📋 Скопировать запасную", text=subscription_url))
    from bot.services.vpn_screen_nav import VPN_NAV_MAIN

    b.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    return b
