"""Колбэки и клавиатуры «Назад» для экранов AiMonkeyVPN (уровни 1 / 3 / Помощь)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

VPN_NAV_MARKETING = "nav:vpn"
VPN_NAV_MAIN = "vpn:flow:main"
VPN_NAV_HELP_MENU = "vpn:instr:menu"
VPN_NAV_FALLBACK_MENU = "vpn:fallback:menu"

VPN_HELP_MENU_BTN = "📖 Помощь"
VPN_FALLBACK_MENU_BTN = "🔀 Запасные способы"
VPN_CHECKLIST_BTN = "📋 Чеклист подключения VPN"
VPN_NAV_CHECKLIST = "vpn:checklist:open"

BTN_OK_MARKETING = "✅ Понятно"
BTN_BACK_MAIN = "⬅️ К подключению"
BTN_BACK_HELP = "⬅️ К меню помощи"
BTN_BACK_FALLBACK = "⬅️ К запасным способам"


def kb_back_marketing() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=BTN_OK_MARKETING, callback_data=VPN_NAV_MARKETING))
    return b.as_markup()


def kb_back_main() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=BTN_BACK_MAIN, callback_data=VPN_NAV_MAIN))
    return b.as_markup()


def kb_back_help_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=BTN_BACK_HELP, callback_data=VPN_NAV_HELP_MENU))
    return b.as_markup()


def kb_back_fallback_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=BTN_BACK_FALLBACK, callback_data=VPN_NAV_FALLBACK_MENU))
    return b.as_markup()
