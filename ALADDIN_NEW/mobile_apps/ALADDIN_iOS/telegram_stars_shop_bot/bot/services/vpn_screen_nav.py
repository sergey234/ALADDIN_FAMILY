"""Колбэки и клавиатуры «Назад» для экранов AiMonkeyVPN (уровни 1 / 3 / Помощь)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

VPN_NAV_MARKETING = "nav:vpn"
VPN_NAV_MAIN = "vpn:flow:main"
VPN_MANAGE_BTN = "🔑 Управление VPN"
VPN_NAV_HELP_MENU = "vpn:instr:menu"

VPN_HELP_MENU_BTN = "❓ Помощь"
VPN_CHECKLIST_BTN = "📖 Инструкция"
VPN_NAV_CHECKLIST = "vpn:checklist:open"

VPN_INSTR_HAPP_PLUS = "vpn:instr:happ:plus"
VPN_INSTR_HAPP_REPORT = "vpn:instr:happ:report"
HAPP_PLUS_BTN = "🎬 Скачать Happ"
VPN_HAPP_REPORT_BTN = "📋 Как прислать лог"

VPN_SUB_LINK = "vpn:sub:link"
VPN_SUB_MIRROR = "vpn:sub:mirror"
VPN_XRAY_QR_PACK = "vpn:xray:qr"
VPN_COPY_FRIEND = "vpn:copy:friend"

# Legacy callbacks — оставлены для старых сообщений в чате.
VPN_NAV_EXTRA_MENU = "vpn:extra:menu"
VPN_NAV_FALLBACK_MENU = "vpn:fallback:menu"
VPN_EXTRA_MENU_BTN = "⚙️ Настройки"
VPN_FALLBACK_MENU_BTN = VPN_EXTRA_MENU_BTN
VPN_INSTR_XRAY_IOS = "vpn:instr:xray:ios"
VPN_INSTR_XRAY_ANDROID = "vpn:instr:xray:android"
VPN_INSTR_HAPP_LEGACY = "vpn:instr:happ:legacy"
VPN_INSTR_HITWAVE = "vpn:instr:hitwave"
VPN_INSTR_APPSTORE_HELP = "vpn:instr:appstore:help"
VPN_HAPP_INSTALL_VIDEO = "vpn:happ:install:video"
# Единая кнопка экрана установки (legacy-имя сохранено для импортов).
VPN_HAPP_INSTALL_VIDEO_BTN = HAPP_PLUS_BTN
VPN_INSTR_IMPORT_MATRIX = "vpn:instr:import:matrix"
VPN_COPY_BRIDGE = "vpn:copy:bridge"
VPN_COPY_WIFI = "vpn:copy:wifi"
VPN_COPY_MRF = "vpn:copy:mrf"

VPN_GET_VPN_BTN = "🔑 Получить ключ VPN"
VPN_GET_VPN = "vpn:get:vpn"

VPN_BUY_BTN = "💳 Купить VPN"
VPN_TRIAL_GET_BTN = "🎁 Получить пробный период"
VPN_TRIAL_BTN = "🎁 Активировать пробный период"  # legacy; используйте vpn_trial_button_text(settings)
VPN_CHECK_BTN = "⚡ Проверить подключение"
VPN_LOCATIONS_BTN = "🌍 Доступные локации"
VPN_HUB_BACK_BTN = "⬅️ Главное меню"
VPN_QR_CONNECT_BTN = "📷 QR-код подключения VPN"
HAPP_DOWNLOAD_BTN = "🎬 Скачать Happ"
VPN_TRIAL_START = "vpn:trial:start"
VPN_TRIAL_ACTIVATE = "vpn:trial:activate"
VPN_INSTR_TRIAL_DEVICE = "vpn:instr:trial:device"

BTN_OK_MARKETING = "✅ Понятно"
BTN_BACK_MAIN = "⬅️ К подключению"
BTN_BACK_HELP = "⬅️ К меню помощи"


def append_happ_install_video_row(b: InlineKeyboardBuilder) -> None:
    """Один экран: иконка + видео + текст шагов + App Store / оплата / подключение."""
    b.row(
        InlineKeyboardButton(
            text=HAPP_DOWNLOAD_BTN,
            callback_data=VPN_HAPP_INSTALL_VIDEO,
        )
    )


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


def kb_happ_install_video_screen(*, from_payment: bool = True) -> InlineKeyboardMarkup:
    """Экран видео Happ: App Store + назад к оплате или к подключению."""
    from bot.services.vpn_happ_constants import HAPP_IOS_APP_STORE_GLOBAL_URL

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📲 Открыть Happ в App Store", url=HAPP_IOS_APP_STORE_GLOBAL_URL))
    if from_payment:
        b.row(InlineKeyboardButton(text="⬅️ К оплате", callback_data="vpn:legal:gate"))
    b.row(InlineKeyboardButton(text="⬅️ К подключению VPN", callback_data=VPN_NAV_MAIN))
    return b.as_markup()
