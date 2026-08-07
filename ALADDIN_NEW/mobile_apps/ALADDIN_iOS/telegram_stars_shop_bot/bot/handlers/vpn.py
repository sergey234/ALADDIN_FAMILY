"""
Отдельный продуктовый модуль VPN (не checkout Stars, не поддержка).

Колбэки: корень nav:vpn; маркетинг vpn:y:*; дерево vpn:instr:*; локации vpn:loc:*;
платформы vpn:os:*; legacy vpn:wg:* (не в меню); основной экран vpn:flow:main. Продукт: Happ+ only.
"""

from __future__ import annotations

import json
import logging
import time
from urllib.parse import urlparse

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.services.ui_visibility import vpn_feature_allowed
from bot.config import Settings
from bot.states.vpn_devices import VpnDeviceStates
from bot.util_telegram import answer_callback_safe
from bot.services import analytics_repo, orders_repo, users_repo, vpn_admin_support_repo, vpn_api_client, vpn_referral_repo
from bot.services.vpn_connect_copy import (
    HAPP_APP_NAME,
    vpn_happ_android_steps_html,
    vpn_happ_appstore_region_guide_html,
    vpn_happ_install_screen_html,
    vpn_backup_link_short_html,
    vpn_checklist_short_html,
    vpn_client_import_matrix_html,
    vpn_extra_menu_html,
    vpn_happ_plus_steps_html,
    vpn_happ_tunnel_report_html,
    vpn_main_connect_steps_html,
    vpn_openvpn_fallback_html,
    vpn_tariffs_cta_label,
    vpn_post_payment_three_steps_html,
    vpn_sub_url_block_html,
    vpn_trial_started_html,
    vpn_trial_device_limit_html,
)
from bot.services.vpn_status_incident import vpn_incident_status_html
from bot.services.vpn_user_links import (
    COPY_SUB_LINK_BTN,
    VPN_QR_CONNECT_BTN,
    append_vpn_copy_link_rows,
    subscription_copy_button,
    subscription_link_reply_kb,
)
from bot.services.vpn_xray_delivery import send_xray_import_pack
from bot.services.vpn_legal_gate import (
    VPN_LEGAL_ACK_PRIVACY_CALLBACK,
    VPN_LEGAL_ACK_TERMS_CALLBACK,
    VPN_LEGAL_CONTINUE_CALLBACK,
    VPN_LEGAL_GATE_CALLBACK,
    present_vpn_checkout_or_legal,
    present_vpn_legal_gate,
    present_vpn_purchase_screen,
    present_vpn_trial_ready_screen,
    vpn_privacy_and_terms_urls,
)
from bot.services.catalog import Product
from bot.services.vpn_screen_nav import (
    HAPP_DOWNLOAD_BTN,
    VPN_CHECK_BTN,
    VPN_CHECKLIST_BTN,
    VPN_HAPP_REPORT_BTN,
    VPN_COPY_BRIDGE,
    VPN_COPY_FRIEND,
    VPN_BUY_BTN,
    VPN_GET_VPN,
    VPN_GET_VPN_BTN,
    VPN_HUB_BACK_BTN,
    VPN_TRIAL_GET_BTN,
    VPN_LOCATIONS_BTN,
    VPN_TRIAL_ACTIVATE,
    VPN_TRIAL_START,
    VPN_COPY_MRF,
    VPN_COPY_WIFI,
    VPN_HELP_MENU_BTN,
    VPN_HAPP_INSTALL_VIDEO,
    VPN_INSTR_APPSTORE_HELP,
    VPN_INSTR_HAPP_LEGACY,
    VPN_INSTR_HAPP_PLUS,
    VPN_INSTR_HAPP_REPORT,
    VPN_INSTR_HITWAVE,
    VPN_INSTR_IMPORT_MATRIX,
    VPN_INSTR_XRAY_ANDROID,
    VPN_INSTR_XRAY_IOS,
    VPN_NAV_CHECKLIST,
    VPN_NAV_EXTRA_MENU,
    VPN_NAV_FALLBACK_MENU,
    VPN_EXTRA_MENU_BTN,
    VPN_NAV_HELP_MENU,
    VPN_NAV_MAIN,
    VPN_INSTR_TRIAL_DEVICE,
    VPN_SUB_LINK,
    VPN_SUB_MIRROR,
    VPN_XRAY_QR_PACK,
    kb_back_help_menu,
    kb_back_main,
    kb_back_marketing,
    kb_happ_install_video_screen,
    append_happ_install_video_row,
)
from bot.services.vpn_tariffs import append_vpn_tariff_buy_rows
from bot.services.vpn_trial_service import (
    TrialEligibility,
    TrialProvisionError,
    append_vpn_trial_row,
    start_trial_flow,
    trial_eligibility,
    trial_eligibility_alert,
    trial_eligibility_message,
    trial_feature_visible,
)
from bot.services.vpn_media import send_happ_region_video
from bot.util_html import esc

router = Router(name="vpn")


def _docs_base(settings: Settings) -> str:
    return (settings.vpn_docs_public_base or "").strip().rstrip("/")


def _public_origin(settings: Settings) -> str:
    raw = (settings.vpn_public_https_origin or "").strip().rstrip("/")
    if raw:
        return raw
    b = _docs_base(settings)
    if not b:
        return ""
    u = urlparse(b)
    if u.scheme and u.netloc:
        return f"{u.scheme}://{u.netloc}"
    return ""


def _vpn_instructions_url(settings: Settings) -> str:
    """Хаб длинных инструкций (внешняя страница). Пусто = маркетинговый лендинг, если он задан."""
    u = (settings.vpn_instructions_url or "").strip()
    if u:
        return u
    return (settings.vpn_marketing_landing_url or "").strip()


# Короткий / полный список стран (fallback, если VPN_LOCATIONS_JSON пуст или невалиден).
_VPN_LOC_LINES_SHORT = """🇪🇺 Автовыбор
🇫🇷 Франция
🇩🇪 Германия"""

_VPN_LOC_LINES_FULL = """🇪🇺 Автовыбор
🇫🇷 Франция
🇩🇪 Германия
🇳🇱 Нидерланды
🇮🇹 Италия
🇭🇺 Венгрия
🇬🇧 Великобритания
🇺🇸 США
⚙ Подключение — профиль 🇷🇺 Вход RU в Happ"""

_LOC_DEFAULT_FOOTER = "Подключение: профиль 🇷🇺 Вход RU в Happ"

_VPN_UI_DISABLED_ALERT = f"{VPN_PRODUCT_NAME} недоступен — напишите в поддержку."
_VPN_CMD_DISABLED = (
    f"Команда /vpn сейчас недоступна. Напишите в поддержку, если нужен {VPN_PRODUCT_NAME}."
)

_VPN_BEGINNER_GUIDE_BTN = "📖 Как подключить (пошагово)"
_VPN_BUY_HINT = "выберите тариф ниже"

_LOC_API_CACHE: tuple[tuple[str, str], float] | None = None
_LOC_API_CACHE_TTL_SEC = 60.0


def _vpn_manage_card_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return f"<b>🛡 {p}</b>"


def _vpn_manage_inactive_copy_html() -> str:
    return "Выберите тариф или пригласите друга — кнопками ниже."


def _vpn_manage_active_hint_html() -> str:
    # Техтекст убран: действия только кнопками (ТЗ редизайна после покупки).
    return ""


def _location_bodies_from_local_env(settings: Settings) -> tuple[str, str]:
    """Короткий и полный текст для <pre> (plain, без HTML внутри строк)."""
    raw = (settings.vpn_locations_json or "").strip()
    if raw:
        try:
            data = json.loads(raw)
            preview_n = max(1, min(int(settings.vpn_locations_preview_n), 50))
            lines: list[str] = []
            if isinstance(data, dict):
                for x in data.get("lines", []):
                    s = str(x).strip()
                    if s:
                        lines.append(s)
                pn = data.get("preview_n")
                if pn is not None:
                    try:
                        preview_n = max(1, min(int(pn), 50))
                    except (TypeError, ValueError):
                        pass
            elif isinstance(data, list):
                for x in data:
                    s = str(x).strip()
                    if s:
                        lines.append(s)
            if lines:
                preview_n = min(preview_n, len(lines))
                short = "\n".join(lines[:preview_n])
                full_core = "\n".join(lines)
                full = full_core
                if _LOC_DEFAULT_FOOTER not in full_core:
                    full = full_core + "\n" + _LOC_DEFAULT_FOOTER
                return short, full
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            logging.getLogger(__name__).warning("VPN_LOCATIONS_JSON invalid, using built-in list: %s", e)
    return _VPN_LOC_LINES_SHORT, _VPN_LOC_LINES_FULL


async def _location_bodies_resolved(settings: Settings) -> tuple[str, str]:
    global _LOC_API_CACHE
    if settings.vpn_locations_from_api and (settings.vpn_api_base_url or "").strip():
        now = time.time()
        if _LOC_API_CACHE is not None:
            bodies, ts = _LOC_API_CACHE
            if now - ts < _LOC_API_CACHE_TTL_SEC:
                return bodies
        ok, lines, pn, _items = await vpn_api_client.get_locations_catalog(settings)
        if ok and lines:
            p = max(1, min(int(pn or 3), len(lines)))
            short = "\n".join(lines[:p])
            full = "\n".join(lines)
            _LOC_API_CACHE = ((short, full), now)
            return short, full
    return _location_bodies_from_local_env(settings)


def _subscription_url(settings: Settings, opaque_token: str) -> str:
    origin = _public_origin(settings)
    tok = (opaque_token or "").strip()
    if not origin or not tok:
        return ""
    return f"{origin}/sub/{tok}"


def _mirror_origin(settings: Settings) -> str:
    return (settings.vpn_subscription_mirror_origin or "").strip().rstrip("/")


async def _vpn_account_user_section_html(settings: Settings, telegram_user_id: int) -> str:
    from bot.services.vpn_user_status import vpn_user_status_block_html

    block = await vpn_user_status_block_html(
        settings, telegram_user_id, inactive_variant="vpn_section"
    )
    if not block:
        return ""
    return f"\n\n{block}"


def vpn_locations_html(*, expanded: bool, short_body: str, full_body: str) -> str:
    body = full_body if expanded else short_body
    return (
        "<b>🌏 Страны сервера</b>\n"
        f"<pre>{esc(body)}</pre>\n\n"
        "<i>Список для ориентира. Точный адрес сервера появится в файле после оплаты. "
        "Подробные гайды (ТВ, особые сети) — «Полная инструкция».</i>"
    )


def _vpn_locations_kb(settings: Settings, *, expanded: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if expanded:
        b.row(InlineKeyboardButton(text="📁 Свернуть список", callback_data="vpn:loc:short"))
    else:
        b.row(InlineKeyboardButton(text="📂 Показать все страны", callback_data="vpn:loc:full"))
    guide = _vpn_instructions_url(settings)
    if guide:
        b.row(InlineKeyboardButton(text="📖 Полная инструкция (сайт)", url=guide))
    else:
        b.row(InlineKeyboardButton(text="📖 Полная инструкция", callback_data="vpn:instr:url:none"))
    b.row(InlineKeyboardButton(text="🗑 Закрыть", callback_data="vpn:loc:dismiss"))
    return b.as_markup()


def _vpn_privacy_terms_links_html(settings: Settings) -> str:
    pu, tu = vpn_privacy_and_terms_urls(settings)
    lines: list[str] = []
    if pu:
        lines.append(f'<a href="{esc(pu)}">Политика конфиденциальности</a>')
    if tu:
        lines.append(f'<a href="{esc(tu)}">Пользовательское соглашение</a>')
    if not lines:
        return ""
    return "\n\n" + "\n".join(lines)


def vpn_marketing_title_html() -> str:
    """Шапка витрины отключена — статус идёт первым."""
    return ""


def vpn_marketing_html(settings: Settings) -> str:
    """Короткая витрина VPN: плюсы со смайлами, без дубль-абзаца и без техники."""
    return (
        "⚡ Высокая скорость\n"
        "🌍 Работает в России\n"
        "📱 Все популярные устройства\n"
        "🔒 Конфиденциальное соединение"
        f"{_vpn_privacy_terms_links_html(settings)}"
    )


def vpn_marketing_screen_html(settings: Settings, status: str) -> str:
    """Сборка текста витрины: при активной карточке плюсы не дублируем."""
    from bot.services.vpn_user_status import ACTIVE_STATUS_MARKER

    title = vpn_marketing_title_html()
    # Активная карточка уже содержит плюсы («Высокая скорость»…) — body не клеим.
    body = ""
    if ACTIVE_STATUS_MARKER not in (status or ""):
        body = vpn_marketing_html(settings)
    return "\n\n".join(p for p in (title, status, body) if p)


def _vpn_y_speed_html() -> str:
    return (
        "<b>⚡ Скорость</b>\n\n"
        "От чего зависит скорость:\n\n"
        "1. <b>Тариф оператора</b> — 4G/5G, лимиты, вечерний «затык».\n"
        "2. <b>Wi‑Fi дома</b> — роутер, расстояние, соседи на том же канале.\n"
        "3. <b>Загрузка сети</b> — вечер, праздники, метро.\n"
        "4. <b>Телефон или ноутбук</b> — старый Wi‑Fi, режим экономии батареи.\n"
        "5. <b>Расстояние до сервера</b> и маршрут в интернете.\n"
        "6. Иногда VPN <b>чуть замедляет</b> — это нормально для любого VPN.\n"
        "7. VPN даёт канал <b>до сервера</b>; до вашего устройства скорость "
        "не «гарантируется» цифрой.\n"
        "8. <b>10 Гбит/с</b> у нас — мощность линии на сервере, "
        "а не обещание «у вас будет столько мегабит».\n"
        "9. В отдельных сетях VPN могут <b>замедлять или ограничивать</b> — "
        "мы делаем всё возможное, чтобы подключение оставалось стабильным и быстрым.\n\n"
        "<i>Замер на вашем устройстве — кнопка «⚡ Замер скорости (Яндекс)» ниже "
        "(VPN должен быть включён).</i>"
    )


def _vpn_speed_card_kb() -> InlineKeyboardMarkup:
    """Карточка скорости: замер + назад к подключению (как было на проверке VPN)."""
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text="⚡ Замер скорости (Яндекс)",
            url="https://yandex.ru/internet/",
        )
    )
    b.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    return b.as_markup()


async def _vpn_edit_or_answer(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Редактирует то же сообщение (навигация VPN); при ошибке — новое сообщение."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
        return
    except TelegramBadRequest as exc:
        err = str(exc).lower()
        if "message is not modified" in err:
            return
    except TelegramNetworkError:
        logging.getLogger(__name__).warning("vpn_edit_text_timeout_fallback_answer")
    await message.answer(text, reply_markup=reply_markup)


def _vpn_y_devices_html(settings: Settings) -> str:
    """Совместимость: витрина платформ (гость). Не показывать /sub/ FAQ."""
    _ = settings
    from bot.services.vpn_devices_platform_hub import devices_hub_html

    return devices_hub_html()


def _vpn_y_privacy_html() -> str:
    return (
        "<b>🔒 Приватность</b>\n\n"
        "1. VPN <b>шифрует</b> трафик до сервера — провайдер не видит сайты, "
        "но видит, что вы в VPN.\n"
        "2. <b>Полной анонимности</b> у обычного VPN нет; важны сайты, пароли и вирусы.\n"
        "3. Мы <b>не собираем и не продаём</b> ваши персональные данные, "
        "как многие бесплатные сервисы.\n"
        "4. Соединение <b>шифруется</b>."
    )


def _vpn_beginner_guide_html(settings: Settings) -> str:
    from bot.services.vpn_connect_copy import vpn_beginner_guide_html

    return vpn_beginner_guide_html(settings)


def _vpn_beginner_guide_kb(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    gu = _vpn_instructions_url(settings)
    if gu:
        b.row(InlineKeyboardButton(text="🌍 Полная инструкция (сайт)", url=gu))
    b.row(InlineKeyboardButton(text="⬅️ К меню помощи", callback_data=VPN_NAV_HELP_MENU))
    return b.as_markup()


async def vpn_main_block_html(
    settings: Settings,
    products: list[Product],
    telegram_user_id: int | None = None,
) -> str:
    _ = products
    account_block = ""
    soft_nudge = ""
    if telegram_user_id is not None:
        account_block = await _vpn_account_user_section_html(settings, telegram_user_id)
        from bot.services import vpn_admin_support_repo
        from bot.services.vpn_user_status import vpn_soft_expiry_nudge_needed

        vpath = settings.resolved_vpn_db_path()
        if vpath is not None:
            row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(
                vpath, telegram_user_id
            )
            if vpn_soft_expiry_nudge_needed(row):
                soft_nudge = (
                    "⚠️ <b>Срок подписки заканчивается</b> — продлите или пригласите друга.\n\n"
                )
    from bot.services.vpn_user_status import ACTIVE_STATUS_MARKER

    has_active = ACTIVE_STATUS_MARKER in account_block
    incident_block = ""
    if has_active and (settings.vpn_api_base_url or "").strip():
        ok_ann, ann_text = await vpn_api_client.get_status_announce(settings)
        if ok_ann and ann_text:
            incident_block = vpn_incident_status_html(ann_text) + "\n\n"

    if not (settings.vpn_api_base_url or "").strip():
        return (
            f"<b>🔑 Управление {esc(VPN_PRODUCT_NAME)}</b>\n\n"
            f"Сервис {esc(VPN_PRODUCT_NAME)} временно недоступен. "
            "Попробуйте позже или напишите в поддержку."
        )

    title = _vpn_manage_card_html()
    if has_active:
        hint = _vpn_manage_active_hint_html()
        return (
            f"{title}\n\n"
            f"{soft_nudge}"
            f"{account_block}"
            f"{('' if not incident_block else chr(10) + chr(10) + incident_block.rstrip())}"
            f"{('' if not hint else chr(10) + chr(10) + hint)}"
        )
    # Нет подписки: статус + короткий призыв (без технического меню).
    return (
        f"{title}\n\n"
        f"{soft_nudge}"
        f"{account_block}\n\n"
        f"{_vpn_manage_inactive_copy_html()}"
    )


async def _build_vpn_marketing_kb(
    settings: Settings,
    conn,
    user_id: int,
    *,
    show_continue: bool,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if show_continue:
        active = await _vpn_root_user_active(settings, user_id)
        cta = vpn_tariffs_cta_label(active=active)
        b.row(InlineKeyboardButton(text=cta, callback_data=VPN_LEGAL_GATE_CALLBACK))
        append_happ_install_video_row(b)
    await append_vpn_trial_row(b, settings, conn, user_id)
    b.row(
        InlineKeyboardButton(text="⚡ Скорость", callback_data="vpn:y:speed"),
        InlineKeyboardButton(text="📱 Мои устройства", callback_data="vpn:y:dev"),
    )
    # Приватность перенесена в Управление VPN
    land = (settings.vpn_marketing_landing_url or "").strip()
    if land:
        b.row(InlineKeyboardButton(text="🌍 Подробнее на сайте", url=land))
    b.row(InlineKeyboardButton(text=VPN_HUB_BACK_BTN, callback_data="nav:hub"))
    return b.as_markup()


def _vpn_marketing_kb(settings: Settings, *, show_continue: bool) -> InlineKeyboardMarkup:
    """Клавиатура без user_id — CTA «Тарифы VPN», без trial (fallback)."""
    b = InlineKeyboardBuilder()
    if show_continue:
        b.row(
            InlineKeyboardButton(
                text=vpn_tariffs_cta_label(active=False),
                callback_data=VPN_LEGAL_GATE_CALLBACK,
            )
        )
        append_happ_install_video_row(b)
    b.row(
        InlineKeyboardButton(text="⚡ Скорость", callback_data="vpn:y:speed"),
        InlineKeyboardButton(text="📱 Мои устройства", callback_data="vpn:y:dev"),
    )
    # Приватность — только в Управление VPN
    land = (settings.vpn_marketing_landing_url or "").strip()
    if land:
        b.row(InlineKeyboardButton(text="🌍 Подробнее на сайте", url=land))
    b.row(InlineKeyboardButton(text=VPN_HUB_BACK_BTN, callback_data="nav:hub"))
    return b.as_markup()


def _vpn_root_kb_nav_rows(
    b: InlineKeyboardBuilder,
    settings: Settings,
    *,
    include_manage_prefix: bool = True,
) -> None:
    """Компактная навигация карточки управления (без технических дублей)."""
    _ = include_manage_prefix
    if (settings.vpn_api_base_url or "").strip():
        b.row(InlineKeyboardButton(text=VPN_CHECKLIST_BTN, callback_data=VPN_NAV_CHECKLIST))
        b.row(InlineKeyboardButton(text=VPN_EXTRA_MENU_BTN, callback_data=VPN_NAV_EXTRA_MENU))
    b.row(InlineKeyboardButton(text=VPN_HUB_BACK_BTN, callback_data="nav:hub"))


async def _vpn_root_user_active(settings: Settings, user_id: int) -> bool:
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return False
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, user_id)
    if not row or (row.get("status") or "").strip() != "vpn_active":
        return False
    from bot.services.vpn_subscription_dates import parse_paid_until_utc
    from datetime import datetime, timezone

    end = parse_paid_until_utc((row.get("paid_until") or "").strip())
    if end is None:
        return False
    return end > datetime.now(timezone.utc)


async def _vpn_legal_flow(state: FSMContext | None) -> str:
    if state is None:
        return "purchase"
    data = await state.get_data()
    flow = str(data.get("vpn_legal_flow") or "purchase").strip().lower()
    return flow if flow in ("purchase", "trial") else "purchase"


async def build_vpn_root_kb(
    bot,
    settings: Settings,
    conn,
    products: list[Product],
    user_id: int,
) -> InlineKeyboardMarkup:
    _ = bot
    from bot.services.vpn_devices_ux import VPN_DEVICES

    b = InlineKeyboardBuilder()
    active = await _vpn_root_user_active(settings, user_id)
    api_ok = bool((settings.vpn_api_base_url or "").strip())

    if active:
        # 🔑 Подключение
        b.row(InlineKeyboardButton(text=VPN_GET_VPN_BTN, callback_data=VPN_GET_VPN))
        await append_vpn_copy_link_rows(b, settings=settings, user_id=user_id)
        # 📱 Управление
        b.row(InlineKeyboardButton(text="📱 Мои устройства", callback_data=VPN_DEVICES))
        if api_ok:
            b.row(InlineKeyboardButton(text=VPN_EXTRA_MENU_BTN, callback_data=VPN_NAV_EXTRA_MENU))
            b.row(InlineKeyboardButton(text=VPN_CHECK_BTN, callback_data="vpn:check"))
            # 📚 Помощь
            b.row(InlineKeyboardButton(text=VPN_CHECKLIST_BTN, callback_data=VPN_NAV_CHECKLIST))
            b.row(InlineKeyboardButton(text=HAPP_DOWNLOAD_BTN, callback_data=VPN_HAPP_INSTALL_VIDEO))
            b.row(InlineKeyboardButton(text="🔒 Приватность", callback_data="vpn:y:priv"))
            b.row(InlineKeyboardButton(text=VPN_HELP_MENU_BTN, callback_data=VPN_NAV_HELP_MENU))
        # 💎 Подписка (тарифы без изменения цен/логики)
        append_vpn_tariff_buy_rows(b, products, settings)
        b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
        await append_vpn_trial_row(b, settings, conn, user_id)
        b.row(InlineKeyboardButton(text=VPN_HUB_BACK_BTN, callback_data="nav:hub"))
        return b.as_markup()

    # Нет VPN: покупка + trial + пригласить друга.
    b.row(InlineKeyboardButton(text=VPN_BUY_BTN, callback_data=VPN_LEGAL_GATE_CALLBACK))
    if trial_feature_visible(settings):
        elig = await trial_eligibility(settings, conn, user_id)
        if elig is TrialEligibility.OK:
            b.row(InlineKeyboardButton(text=VPN_TRIAL_GET_BTN, callback_data=VPN_TRIAL_START))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text=VPN_HUB_BACK_BTN, callback_data="nav:hub"))
    return b.as_markup()


def _vpn_root_kb(settings: Settings, products: list[Product]) -> InlineKeyboardMarkup:
    """Клавиатура без Copy Text (нет user_id) — для редких fallback-сценариев."""
    b = InlineKeyboardBuilder()
    append_vpn_tariff_buy_rows(b, products, settings)
    _vpn_root_kb_nav_rows(b, settings)
    return b.as_markup()


def _wg_help_html(settings: Settings) -> str:
    return (
        f"<b>🔧 WireGuard — файл или QR</b>\n\n"
        f"{vpn_wireguard_next_step_html()}\n\n"
        f"Запросить ключ:\n"
        f"• <b>📥 WireGuard — файл</b>\n"
        f"• <b>📷 WireGuard — QR</b>\n\n"
        f"Полный сценарий: «{_VPN_BEGINNER_GUIDE_BTN}»."
    )


def _os_steps_html(slug: str, settings: Settings) -> str:
    api_ok = bool((settings.vpn_api_base_url or "").strip())
    link_step = (
        f"«{COPY_SUB_LINK_BTN}» → Import в OneXray / v2rayNG"
        if api_ok
        else "ссылка VPN в меню бота"
    )
    if slug == "ios":
        return (
            f"{vpn_happ_plus_steps_html()}\n\n"
            f"<i>Основной клиент — <b>{esc(HAPP_APP_NAME)}</b> (App Store).</i>"
        )
    if slug == "android":
        return vpn_happ_android_steps_html()
    return (
        "<b>Windows / macOS / Linux</b>\n\n"
        "1) Оплата в боте → подождите 2 мин.\n"
        f"2) {link_step}.\n"
        "3) Windows: <b>v2rayN</b> · macOS: <b>V2Box</b> / Streisand · Linux: v2rayN / Hiddify.\n"
        f"4) iPhone/iPad — <b>{esc(HAPP_APP_NAME)}</b> + ссылка <code>/sub/…</code>."
    )


def _wg_conf_user_alert(err: str) -> str:
    low = (err or "").lower()
    if "circuit open" in low or "cooldown" in low:
        return f"Сервис {VPN_PRODUCT_NAME} временно недоступен. Попробуйте через минуту."
    if "403" in err or "not active" in low or "subscription ended" in low:
        return (
            f"Сначала {_VPN_BUY_HINT}, оплатите и подождите от 2 до 5 мин."
        )
    if "404" in err or "unknown telegram" in low:
        return f"Сначала купите {VPN_PRODUCT_NAME} — {_VPN_BUY_HINT}."
    if "503" in err or "missing" in low:
        return "Настройки готовятся. Подождите от 2 до 5 мин и повторите."
    return "Не удалось получить настройки. Попробуйте позже или напишите в поддержку."


async def _fetch_wg_conf(settings: Settings, telegram_user_id: int) -> tuple[bool, str | None, str]:
    return await vpn_api_client.post_wg_conf(settings, telegram_user_id=telegram_user_id)


def _wg_conf_filename(telegram_user_id: int) -> str:
    return f"aladdin-wg-{telegram_user_id}.conf"


def _vpn_check_kb(*, sub_url: str = "") -> InlineKeyboardMarkup:
    from bot.services.vpn_screen_nav import VPN_XRAY_QR_PACK

    b = InlineKeyboardBuilder()
    sub = (sub_url or "").strip()
    if sub:
        copy_btn = subscription_copy_button(sub)
        if copy_btn:
            b.row(copy_btn)
        b.row(InlineKeyboardButton(text=VPN_QR_CONNECT_BTN, callback_data=VPN_XRAY_QR_PACK))
    b.row(InlineKeyboardButton(text="🌍 Мой IP (ifconfig.me)", url="https://ifconfig.me/"))
    b.row(
        InlineKeyboardButton(
            text="⚡ Замер скорости (Яндекс)",
            url="https://yandex.ru/internet/",
        )
    )
    b.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    return b.as_markup()


async def _vpn_check_html(settings: Settings, telegram_user_id: int) -> str:
    from bot.services.vpn_subscription_dates import vpn_subscription_period_user_html

    p = esc(VPN_PRODUCT_NAME)

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return (
            f"<b>{esc(VPN_CHECK_BTN)}</b>\n\n"
            f"Сервис {p} временно недоступен."
        )
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return (
            f"<b>{esc(VPN_CHECK_BTN)}</b>\n\n"
            f"Подписка не найдена. {_VPN_BUY_HINT.capitalize()}."
        )
    status = (row.get("status") or "").strip()
    paid = (row.get("paid_until") or "").strip()
    created = (row.get("created_at") or "").strip()
    if status == "vpn_provisioning":
        return (
            f"<b>{esc(VPN_CHECK_BTN)}</b>\n\n"
            "<b>Подписка оформляется</b> — подождите от 2 до 5 мин и нажмите снова."
        )
    if status == "vpn_expired":
        period = vpn_subscription_period_user_html(created_at=created, paid_until=paid)
        extra = f"\n{period}\n" if period else "\n"
        return (
            f"<b>{esc(VPN_CHECK_BTN)}</b>\n\n"
            "<b>Срок подписки истёк</b> — VPN отключён."
            f"{extra}\n"
            f"Продлите: {esc(vpn_tariffs_cta_label(active=True))} → выберите тариф.\n"
            f"<i>После продления снова придут ключи; «{COPY_SUB_LINK_BTN}» — в личном кабинете.</i>"
        )
    if status != "vpn_active":
        return (
            f"<b>{esc(VPN_CHECK_BTN)}</b>\n\n"
            f"Статус: <code>{esc(status or 'нет')}</code>. Нужна оплата — {_VPN_BUY_HINT}."
        )

    period = vpn_subscription_period_user_html(created_at=created, paid_until=paid)
    lines = [
        f"<b>{esc(VPN_CHECK_BTN)}</b>",
        "",
        "<b>✅ Подписка активна</b>",
    ]
    if period:
        lines.append(period)
    lines.append("\n<b>yandex.ru/internet</b> — замер скорости.")
    return "\n".join(lines)


async def _vpn_log(
    conn,
    user_id: int,
    event_type: str,
    *,
    meta: dict | None = None,
) -> None:
    try:
        await analytics_repo.log_event(conn, user_id=user_id, event_type=event_type, meta=meta)
    except Exception:
        logger.debug("vpn analytics skip %s", event_type, exc_info=True)


async def _send_or_edit_vpn_marketing(
    target: Message,
    settings: Settings,
    conn,
    user_id: int,
    *,
    show_continue: bool,
) -> None:
    from bot.services.vpn_user_status import vpn_user_status_block_html

    status = await vpn_user_status_block_html(
        settings, user_id, inactive_variant="vpn_section"
    )
    text = vpn_marketing_screen_html(settings, status)
    kb = await _build_vpn_marketing_kb(settings, conn, user_id, show_continue=show_continue)
    await _vpn_edit_or_answer(target, text, kb)


@router.callback_query(F.data == "nav:vpn")
async def nav_vpn(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await cb.answer(_VPN_UI_DISABLED_ALERT, show_alert=True)
        return
    await answer_callback_safe(cb)
    await _vpn_log(conn, cb.from_user.id, "vpn_nav_marketing")
    await _vpn_log(
        conn,
        cb.from_user.id,
        "offer_impression",
        meta={"product_hint": "vpn", "positioning_variant": "utility"},
    )
    await _send_or_edit_vpn_marketing(cb.message, settings, conn, cb.from_user.id, show_continue=True)


@router.callback_query(F.data == "vpn:loc:open")
async def vpn_loc_open(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    short, full = await _location_bodies_resolved(settings)
    text = vpn_locations_html(expanded=False, short_body=short, full_body=full)
    if settings.vpn_locations_from_api and (settings.vpn_api_base_url or "").strip():
        ok, _lines, _pn, items = await vpn_api_client.get_locations_catalog(settings)
        if ok and items:
            b = InlineKeyboardBuilder()
            for it in items[:8]:
                b.row(
                    InlineKeyboardButton(
                        text=f"📍 {it['label'][:40]}",
                        callback_data=f"vpn:loc:pick:{it['slug']}",
                    )
                )
            b.row(InlineKeyboardButton(text="🗑 Закрыть", callback_data="vpn:loc:dismiss"))
            await cb.message.answer(text, reply_markup=b.as_markup())
            return
    await cb.message.answer(text, reply_markup=_vpn_locations_kb(settings, expanded=False))


@router.callback_query(F.data.in_({"vpn:loc:short", "vpn:loc:full"}))
async def vpn_loc_toggle(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    expanded = cb.data == "vpn:loc:full"
    await answer_callback_safe(cb)
    short, full = await _location_bodies_resolved(settings)
    try:
        await cb.message.edit_text(
            vpn_locations_html(expanded=expanded, short_body=short, full_body=full),
            reply_markup=_vpn_locations_kb(settings, expanded=expanded),
        )
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "vpn:loc:dismiss")
async def vpn_loc_dismiss(cb: CallbackQuery) -> None:
    await answer_callback_safe(cb)
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "vpn:instr:url:none")
async def vpn_instr_url_none(cb: CallbackQuery) -> None:
    await cb.answer(
        "Ссылка на полную инструкцию пока не настроена. Напишите в поддержку.",
        show_alert=True,
    )


async def _vpn_present_main_screen(
    message: Message,
    bot,
    settings: Settings,
    conn,
    products: list[Product],
    user_id: int,
) -> None:
    from bot.services.vpn_nav import build_vpn_main_screen

    body, kb = await build_vpn_main_screen(bot, settings, conn, products, user_id)
    await _vpn_edit_or_answer(message, body, kb)


@router.callback_query(F.data == VPN_LEGAL_GATE_CALLBACK)
async def vpn_legal_gate_entry(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_log(conn, cb.from_user.id, "vpn_legal_gate_open")
    await state.update_data(vpn_legal_flow="purchase")
    await present_vpn_checkout_or_legal(
        cb.message, settings, conn, cb.from_user.id, products, flow="purchase"
    )


@router.callback_query(F.data == VPN_TRIAL_START)
async def vpn_trial_start(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    elig = await trial_eligibility(settings, conn, cb.from_user.id)
    if elig is not TrialEligibility.OK:
        alert = trial_eligibility_alert(elig, settings)
        if alert:
            await cb.answer(alert, show_alert=True)
        else:
            await answer_callback_safe(cb)
            await cb.message.answer(trial_eligibility_message(elig, settings))
        return
    await answer_callback_safe(cb)
    await state.update_data(vpn_legal_flow="trial")
    await _vpn_log(conn, cb.from_user.id, "vpn_trial_start")
    await present_vpn_checkout_or_legal(
        cb.message, settings, conn, cb.from_user.id, products, flow="trial"
    )


@router.callback_query(F.data == VPN_TRIAL_ACTIVATE)
async def vpn_trial_activate(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    if not await users_repo.has_vpn_legal_accepted(conn, cb.from_user.id):
        await cb.answer(
            "Сначала нажмите «✅ Продолжить» и подтвердите документы VPN.",
            show_alert=True,
        )
        return
    await answer_callback_safe(cb)
    try:
        await start_trial_flow(settings, conn, telegram_user_id=cb.from_user.id)
    except TrialProvisionError as exc:
        await cb.message.answer(str(exc))
        return
    await state.update_data(vpn_legal_flow="purchase")
    await _vpn_log(conn, cb.from_user.id, "vpn_trial_activated")
    await cb.message.answer(vpn_trial_started_html(settings))


@router.callback_query(F.data == VPN_LEGAL_ACK_PRIVACY_CALLBACK)
async def vpn_legal_ack_privacy(
    cb: CallbackQuery, settings: Settings, conn, products: list[Product], state: FSMContext
) -> None:
    """Legacy: старые галочки → принять оба документа и открыть оплату/trial."""
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await users_repo.upsert_user(
        conn,
        user_id=cb.from_user.id,
        username=cb.from_user.username,
        first_name=cb.from_user.first_name,
    )
    await users_repo.accept_vpn_legal_both(conn, cb.from_user.id)
    await cb.answer("Документы приняты")
    flow = await _vpn_legal_flow(state)
    if flow == "trial":
        await present_vpn_trial_ready_screen(cb.message, settings)
    else:
        await present_vpn_purchase_screen(cb.message, settings, products)


@router.callback_query(F.data == VPN_LEGAL_ACK_TERMS_CALLBACK)
async def vpn_legal_ack_terms(
    cb: CallbackQuery, settings: Settings, conn, products: list[Product], state: FSMContext
) -> None:
    """Legacy: старые галочки → принять оба документа и открыть оплату/trial."""
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await users_repo.upsert_user(
        conn,
        user_id=cb.from_user.id,
        username=cb.from_user.username,
        first_name=cb.from_user.first_name,
    )
    await users_repo.accept_vpn_legal_both(conn, cb.from_user.id)
    await cb.answer("Документы приняты")
    flow = await _vpn_legal_flow(state)
    if flow == "trial":
        await present_vpn_trial_ready_screen(cb.message, settings)
    else:
        await present_vpn_purchase_screen(cb.message, settings, products)


@router.callback_query(F.data == VPN_LEGAL_CONTINUE_CALLBACK)
async def vpn_legal_continue(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await users_repo.upsert_user(
        conn,
        user_id=cb.from_user.id,
        username=cb.from_user.username,
        first_name=cb.from_user.first_name,
    )
    await users_repo.accept_vpn_legal_both(conn, cb.from_user.id)
    flow = await _vpn_legal_flow(state)
    await answer_callback_safe(cb)
    await _vpn_log(conn, cb.from_user.id, "vpn_legal_continue")
    if flow == "trial":
        await present_vpn_trial_ready_screen(cb.message, settings)
    else:
        await present_vpn_purchase_screen(cb.message, settings, products)


@router.callback_query(F.data == "vpn:flow:main")
async def vpn_flow_main(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await state.clear()
    if not await users_repo.has_vpn_legal_accepted(conn, cb.from_user.id):
        await present_vpn_legal_gate(cb.message, settings, conn, cb.from_user.id, products)
        return
    from bot.services.vpn_nav import build_vpn_main_screen

    body, kb = await build_vpn_main_screen(cb.bot, settings, conn, products, cb.from_user.id)
    try:
        await cb.message.edit_text(body, reply_markup=kb)
    except TelegramBadRequest as exc:
        err = str(exc).lower()
        if "message is not modified" in err:
            return
        await cb.message.answer(body, reply_markup=kb)


@router.callback_query(F.data.in_({"vpn:y:speed", "vpn:y:dev", "vpn:y:priv"}))
async def vpn_why_detail(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    key = (cb.data or "").split(":")[-1]
    uid = int(cb.from_user.id)

    # Для speed/priv — сначала pending-alert (единственный cb.answer).
    if key in ("speed", "priv"):
        pending = await orders_repo.list_user_pending_payment_order_ids(conn, uid, limit=3)
        if pending:
            ids = ", ".join(f"#{i}" for i in pending[:3])
            await cb.answer(
                f"Сначала завершите оплату ({ids}). «Мои заказы» → «Вернуться к оплате».",
                show_alert=True,
            )
            return

    # Сразу гасим «часики» — до DB/API.
    await answer_callback_safe(cb)

    # Гибрид: оплативший с «Все устройства» → пульт слота (B), не FAQ.
    if key == "dev" and await _vpn_root_user_active(settings, uid):
        await _vpn_log(conn, uid, "vpn_devices_from_marketing")
        await _render_device_card(cb.message, settings, uid, 0, as_edit=True)
        return

    if key == "speed":
        text = _vpn_y_speed_html()
    elif key == "dev":
        from bot.services.vpn_devices_platform_hub import devices_hub_html, devices_hub_kb

        await _vpn_log(conn, uid, "vpn_marketing_card", meta={"card": "dev"})
        await _vpn_edit_or_answer(cb.message, devices_hub_html(), devices_hub_kb())
        return
    elif key == "priv":
        text = _vpn_y_privacy_html()
    else:
        return
    await _vpn_log(conn, uid, "vpn_marketing_card", meta={"card": key})
    if key == "speed":
        await _vpn_edit_or_answer(cb.message, text, _vpn_speed_card_kb())
    else:
        await _vpn_edit_or_answer(cb.message, text, kb_back_marketing())


@router.callback_query(
    F.data.in_({"vpn:y:dev:iphone", "vpn:y:dev:android", "vpn:y:dev:ipad"})
)
async def vpn_devices_platform_card(
    cb: CallbackQuery,
    settings: Settings,
    conn,
) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    uid = int(cb.from_user.id)
    if await _vpn_root_user_active(settings, uid):
        await _render_device_card(cb.message, settings, uid, 0, as_edit=True)
        return
    slug = (cb.data or "").rsplit(":", 1)[-1]
    from bot.services.vpn_devices_platform_hub import platform_card_html, platform_card_kb

    await _vpn_log(conn, uid, "vpn_devices_platform", meta={"platform": slug})
    await _vpn_edit_or_answer(
        cb.message,
        platform_card_html(slug),
        await platform_card_kb(slug, settings, conn, uid),
    )


@router.callback_query(F.data.in_({"vpn:y:whitelist", "vpn:y:bypass"}))
async def vpn_legacy_whitelist_removed(
    cb: CallbackQuery,
    settings: Settings,
    conn,
) -> None:
    """Старые кнопки «Обход блокировок» — возврат на витрину VPN."""
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _send_or_edit_vpn_marketing(cb.message, settings, conn, cb.from_user.id, show_continue=True)


@router.callback_query(F.data == "vpn:instr:guide")
async def vpn_instr_guide(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_edit_or_answer(
        cb.message,
        _vpn_beginner_guide_html(settings),
        _vpn_beginner_guide_kb(settings),
    )


@router.callback_query(F.data.in_({VPN_NAV_CHECKLIST, "vpn:instr:checklist"}))
async def vpn_checklist_open(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    back = kb_back_help_menu() if cb.data == "vpn:instr:checklist" else kb_back_main()
    await _vpn_edit_or_answer(
        cb.message,
        vpn_checklist_short_html(settings),
        back,
    )


@router.callback_query(F.data == "vpn:instr:menu")
async def vpn_instr_menu(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_log(conn, cb.from_user.id, "vpn_help_menu_open")
    kb = InlineKeyboardBuilder()
    from bot.assistant.access import assistant_menu_visible

    if assistant_menu_visible(cb.from_user.id if cb.from_user else None, settings):
        kb.row(InlineKeyboardButton(text="🤖 AI Помощник", callback_data="nav:assistant"))
    kb.row(InlineKeyboardButton(text=HAPP_DOWNLOAD_BTN, callback_data=VPN_HAPP_INSTALL_VIDEO))
    kb.row(InlineKeyboardButton(text=_VPN_BEGINNER_GUIDE_BTN, callback_data="vpn:instr:guide"))
    kb.row(InlineKeyboardButton(text=VPN_CHECKLIST_BTN, callback_data="vpn:instr:checklist"))
    kb.row(InlineKeyboardButton(text=VPN_HAPP_REPORT_BTN, callback_data=VPN_INSTR_HAPP_REPORT))
    if settings.vpn_trial_enabled:
        from bot.services.vpn_trial_copy import vpn_trial_period_phrase

        kb.row(
            InlineKeyboardButton(
                text=f"📱 1 устройство / пробный период {vpn_trial_period_phrase(settings)}",
                callback_data=VPN_INSTR_TRIAL_DEVICE,
            )
        )
    gu = _vpn_instructions_url(settings)
    if gu:
        kb.row(InlineKeyboardButton(text="🌍 Полная инструкция (сайт)", url=gu))
    kb.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    await _vpn_edit_or_answer(
        cb.message,
        f"<b>{esc(VPN_HELP_MENU_BTN)}</b>\n\nВыберите раздел — подсказка простым языком.",
        kb.as_markup(),
    )


@router.callback_query(F.data == VPN_INSTR_TRIAL_DEVICE)
async def vpn_instr_trial_device(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    body = vpn_trial_device_limit_html()
    if settings.vpn_trial_enabled:
        from bot.services.vpn_connect_copy import vpn_trial_offer_html

        body = f"{vpn_trial_offer_html(settings)}\n\n{body}"
    await _vpn_edit_or_answer(cb.message, body, kb_back_help_menu())


@router.callback_query(F.data == VPN_INSTR_HAPP_REPORT)
async def vpn_instr_happ_report(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_edit_or_answer(cb.message, vpn_happ_tunnel_report_html(), kb_back_help_menu())


@router.callback_query(F.data.in_({VPN_NAV_EXTRA_MENU, VPN_NAV_FALLBACK_MENU}))
async def vpn_extra_menu(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=HAPP_DOWNLOAD_BTN, callback_data=VPN_HAPP_INSTALL_VIDEO))
    kb.row(InlineKeyboardButton(text=VPN_CHECK_BTN, callback_data="vpn:check"))
    kb.row(InlineKeyboardButton(text="⚡ Скорость", callback_data="vpn:y:speed"))
    kb.row(InlineKeyboardButton(text=VPN_LOCATIONS_BTN, callback_data="vpn:loc:open"))
    kb.row(InlineKeyboardButton(text=VPN_HELP_MENU_BTN, callback_data=VPN_NAV_HELP_MENU))
    kb.row(InlineKeyboardButton(text="📱 Другие Xray-клиенты", callback_data=VPN_INSTR_IMPORT_MATRIX))
    pu, tu = vpn_privacy_and_terms_urls(settings)
    if pu:
        kb.row(InlineKeyboardButton(text="📄 Политика конфиденциальности", url=pu))
    if tu:
        kb.row(InlineKeyboardButton(text="📄 Пользовательское соглашение", url=tu))
    kb.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    await _vpn_edit_or_answer(cb.message, vpn_extra_menu_html(), kb.as_markup())


@router.callback_query(F.data == "vpn:wg:help")
async def vpn_wg_help(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_edit_or_answer(cb.message, _wg_help_html(settings), kb_back_main())


@router.callback_query(F.data == "vpn:fallback:openvpn")
async def vpn_openvpn_help(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_edit_or_answer(cb.message, vpn_openvpn_fallback_html(), kb_back_main())


@router.callback_query(F.data == VPN_INSTR_IMPORT_MATRIX)
async def vpn_import_matrix(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_edit_or_answer(cb.message, vpn_client_import_matrix_html(), kb_back_main())


@router.callback_query(
    F.data.in_({VPN_HAPP_INSTALL_VIDEO, VPN_INSTR_APPSTORE_HELP, VPN_INSTR_HAPP_PLUS})
)
async def vpn_happ_install_video(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    """Фото + полный канон шагов + кнопки, затем видео (file_id, без дубля текста)."""
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    if not cb.message:
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    flow = await _vpn_legal_flow(state)
    from_payment = cb.data in {VPN_HAPP_INSTALL_VIDEO, VPN_INSTR_HAPP_PLUS} or flow == "purchase"
    text = vpn_happ_install_screen_html()
    kb = kb_happ_install_video_screen(from_payment=from_payment)
    sent = await send_happ_region_video(cb.message, settings, reply_markup=kb)
    if not sent:
        # Медиа недоступно — тот же канон + кнопки текстом.
        note = (
            "\n\n<i>⚠️ Видео временно недоступно на сервере. "
            "Следуйте текстовой инструкции выше или напишите в поддержку.</i>"
        )
        await _vpn_edit_or_answer(cb.message, text + note, kb)


_LEGACY_HAPP_REDIRECT = (
    "vpn:instr:file",
    "vpn:instr:qr",
    "vpn:instr:wg",
    "vpn:os:ios",
    "vpn:os:android",
    "vpn:os:desktop",
    "vpn:wg:download",
    "vpn:wg:qr",
    "vpn:ovpn:download",
    VPN_INSTR_XRAY_IOS,
    VPN_INSTR_XRAY_ANDROID,
    VPN_INSTR_HITWAVE,
    VPN_INSTR_HAPP_LEGACY,
    VPN_COPY_BRIDGE,
    VPN_COPY_WIFI,
    VPN_COPY_MRF,
    VPN_SUB_MIRROR,
)


@router.callback_query(F.data.in_(_LEGACY_HAPP_REDIRECT))
async def vpn_legacy_redirect_happ_plus(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _vpn_edit_or_answer(cb.message, vpn_happ_plus_steps_html(), kb_back_main())


async def _resolve_active_sub_url(settings: Settings, telegram_user_id: int) -> str:
    origin = _public_origin(settings)
    if not origin:
        return ""
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return ""
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return ""
    status = (row.get("status") or "").strip()
    opaque = (row.get("opaque_token") or "").strip()
    if status != "vpn_active" or not opaque:
        return ""
    return _subscription_url(settings, opaque)


async def _send_subscription_link_message(
    message: Message,
    settings: Settings,
    telegram_user_id: int,
) -> None:
    origin = _public_origin(settings)
    if not origin:
        await message.answer("Ссылка VPN пока недоступна. Напишите в поддержку.")
        return
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        await message.answer(
            f"Ссылка появится после оплаты. {_VPN_BUY_HINT.capitalize()} → подождите 2 мин."
        )
        return
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        await message.answer(f"Сначала {_VPN_BUY_HINT} в меню {VPN_PRODUCT_NAME}.")
        return
    status = (row.get("status") or "").strip()
    opaque = (row.get("opaque_token") or "").strip()
    if status == "vpn_provisioning":
        await message.answer("Подписка оформляется — подождите 2 мин и нажмите снова.")
        return
    if status != "vpn_active" or not opaque:
        await message.answer(f"Сначала {_VPN_BUY_HINT} и подождите 2 мин.")
        return
    sub_url = _subscription_url(settings, opaque)
    kb = subscription_link_reply_kb(sub_url, settings=settings).as_markup()
    await message.answer(
        vpn_sub_url_block_html(
            sub_url,
            ux_auto=bool(settings.vpn_ux_auto_enabled),
        ),
        reply_markup=kb,
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == VPN_XRAY_QR_PACK)
async def vpn_xray_qr_pack(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    if not cb.message:
        await cb.answer("Откройте /vpn и нажмите снова.", show_alert=True)
        return
    await cb.answer("Отправляю QR…")
    sub_url = await _resolve_active_sub_url(settings, int(cb.from_user.id))
    if not sub_url:
        await cb.message.answer(f"Сначала {_VPN_BUY_HINT} и подождите 2 мин.")
        return
    vless_mrf = ""
    await send_xray_import_pack(cb.message, sub_url=sub_url, vless_mobile_rf=vless_mrf)


@router.callback_query(F.data == VPN_GET_VPN)
async def vpn_get_vpn(cb: CallbackQuery, settings: Settings, conn, products: list[Product], state: FSMContext) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    if not cb.message:
        await answer_callback_safe(cb)
        return
    uid = int(cb.from_user.id)
    sub_url = await _resolve_active_sub_url(settings, uid)
    if sub_url:
        await cb.answer("Отправляю ссылку…")
        await _send_subscription_link_message(cb.message, settings, uid)
        return
    elig = await trial_eligibility(settings, conn, uid)
    if elig is not TrialEligibility.OK:
        alert = trial_eligibility_alert(elig, settings)
        if alert:
            await cb.answer(alert, show_alert=True)
        else:
            await answer_callback_safe(cb)
            await cb.message.answer(trial_eligibility_message(elig, settings))
        return
    if not await users_repo.has_vpn_legal_accepted(conn, uid):
        await answer_callback_safe(cb)
        await state.update_data(vpn_legal_flow="trial")
        await present_vpn_legal_gate(cb.message, settings, conn, uid, products, flow="trial")
        return
    await cb.answer("Активирую пробный период…")
    try:
        await start_trial_flow(settings, conn, telegram_user_id=uid)
    except TrialProvisionError as exc:
        await cb.message.answer(str(exc))
        return
    await cb.message.answer(vpn_trial_started_html(settings))


@router.callback_query(F.data == VPN_SUB_LINK)
async def vpn_sub_link(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _send_subscription_link_message(cb.message, settings, int(cb.from_user.id))


@router.callback_query(F.data == VPN_COPY_FRIEND)
async def vpn_copy_friend_legacy(cb: CallbackQuery, settings: Settings) -> None:
    """Старые клавиатуры: рефералка только в «Пригласить друга» / профиле."""
    if not settings.ui_show_vpn or not cb.message:
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="👤 Личный кабинет", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="⬅️ К VPN", callback_data=VPN_NAV_MAIN))
    await cb.message.answer(
        "<b>Реферальная ссылка</b> — в меню «👥 Пригласить друга» или «👤 Личный кабинет».\n"
        "Там можно скопировать или отправить ссылку отдельным сообщением.\n\n"
        "<i>Это ссылка в бот (<code>ref_…</code>), не ключ VPN <code>/sub/…</code>.</i>",
        reply_markup=b.as_markup(),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "vpn:reality:hint")
async def vpn_reality_hint(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _send_subscription_link_message(cb.message, settings, int(cb.from_user.id))


@router.callback_query(F.data == "vpn:check")
async def vpn_check(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    text = await _vpn_check_html(settings, int(cb.from_user.id))
    sub_url = await _resolve_active_sub_url(settings, int(cb.from_user.id))
    await cb.message.answer(
        text,
        reply_markup=_vpn_check_kb(sub_url=sub_url or ""),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("vpn:loc:pick:"))
async def vpn_loc_pick(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    slug = (cb.data or "").split(":", maxsplit=3)[-1].strip()
    if not slug:
        await cb.answer("Некорректная локация.", show_alert=True)
        return
    ok, msg = await vpn_api_client.post_location_select(
        settings, telegram_user_id=int(cb.from_user.id), location_slug=slug
    )
    if not ok:
        await cb.answer(_wg_conf_user_alert(msg), show_alert=True)
        return
    host_hint = ""
    try:
        data = json.loads(msg)
        host = str(data.get("wg_endpoint_host") or "").strip()
        if host:
            host_hint = f" Сервер: {host}."
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    await cb.answer(
        f"Локация сохранена.{host_hint} Запросите 📥 или 📷 заново.",
        show_alert=bool(host_hint),
    )


@router.message(Command("vpn"))
async def cmd_vpn(message: Message, settings: Settings, conn, products: list[Product]) -> None:
    if not vpn_feature_allowed(message.from_user.id, settings):
        await message.answer(_VPN_CMD_DISABLED)
        return
    uid = message.from_user.id
    if await users_repo.has_vpn_legal_accepted(conn, uid):
        body = await vpn_main_block_html(settings, products, uid)
        kb = await build_vpn_root_kb(message.bot, settings, conn, products, uid)
        await message.answer(body, reply_markup=kb)
        return
    from bot.services.vpn_user_status import vpn_user_status_block_html

    status = await vpn_user_status_block_html(settings, uid, inactive_variant="vpn_section")
    await message.answer(
        vpn_marketing_screen_html(settings, status),
        reply_markup=await _build_vpn_marketing_kb(
            settings, conn, uid, show_continue=True
        ),
    )


async def _render_device_card(
    message: Message,
    settings: Settings,
    user_id: int,
    index: int = 0,
    *,
    as_edit: bool = False,
) -> None:
    from bot.services.vpn_devices_ux import (
        device_card_html,
        device_card_keyboard,
        devices_panel_url,
        normalize_device_index,
    )

    ok, data = await vpn_api_client.post_devices_list(settings, telegram_user_id=user_id)
    if not ok or not isinstance(data, dict):
        await message.answer(
            "Не удалось загрузить список устройств. Попробуйте позже или напишите в поддержку."
        )
        return
    idx = normalize_device_index(data, index)
    origin = getattr(settings, "web_checkout_public_origin", None) or "https://aimonkeystars.ru"
    text = device_card_html(data, idx)
    kb = device_card_keyboard(data, idx, panel_url=devices_panel_url(str(origin)))
    # Через общий helper: edit → иначе новое сообщение (фото/старые сообщения).
    if as_edit:
        await _vpn_edit_or_answer(message, text, kb)
        return
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)


@router.callback_query(F.data.startswith("vpn:devices:openhapp:"))
async def vpn_devices_open_happ(cb: CallbackQuery, settings: Settings) -> None:
    """Telegram url-кнопки не принимают happ:// — отдаём ссылку текстом."""
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    raw = (cb.data or "").rsplit(":", 1)[-1]
    try:
        device_id = int(raw)
    except ValueError:
        await answer_callback_safe(cb)
        return
    uid = int(cb.from_user.id)
    ok, data = await vpn_api_client.post_devices_list(settings, telegram_user_id=uid)
    if not ok or not isinstance(data, dict):
        await cb.answer("Не удалось загрузить ссылку.", show_alert=True)
        return
    url = ""
    for d in list(data.get("devices") or []):
        if int(d.get("id") or 0) == device_id:
            url = str(d.get("subscription_url") or "").strip()
            break
    if not url:
        await cb.answer("Ссылка пока недоступна.", show_alert=True)
        return
    await answer_callback_safe(cb)
    from bot.services.vpn_devices_platform_hub import happ_open_message_html

    await cb.message.answer(happ_open_message_html(url), disable_web_page_preview=True)


@router.callback_query(F.data == "vpn:devices")
async def vpn_devices(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _render_device_card(cb.message, settings, int(cb.from_user.id), 0, as_edit=True)


@router.callback_query(F.data.startswith("vpn:devices:nav:"))
async def vpn_devices_nav(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    raw = (cb.data or "").rsplit(":", 1)[-1]
    try:
        index = int(raw)
    except ValueError:
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _render_device_card(cb.message, settings, int(cb.from_user.id), index, as_edit=True)


@router.callback_query(F.data.startswith("vpn:devices:qr:"))
async def vpn_devices_qr(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    raw = (cb.data or "").rsplit(":", 1)[-1]
    try:
        device_id = int(raw)
    except ValueError:
        await answer_callback_safe(cb)
        return
    uid = int(cb.from_user.id)
    ok, data = await vpn_api_client.post_devices_list(settings, telegram_user_id=uid)
    if not ok or not isinstance(data, dict):
        await cb.answer("Не удалось загрузить устройство.", show_alert=True)
        return
    url = ""
    for d in list(data.get("devices") or []):
        if int(d.get("id") or 0) == device_id:
            url = str(d.get("subscription_url") or "").strip()
            break
    if not url:
        await cb.answer("Ссылка пока недоступна.", show_alert=True)
        return
    await answer_callback_safe(cb)
    from bot.services.vpn_xray_delivery import send_xray_import_pack

    await send_xray_import_pack(cb.message, sub_url=url)


@router.callback_query(F.data.startswith("vpn:devices:ren:"))
async def vpn_devices_rename_ask(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    raw = (cb.data or "").rsplit(":", 1)[-1]
    try:
        device_id = int(raw)
    except ValueError:
        await answer_callback_safe(cb)
        return
    await state.set_state(VpnDeviceStates.waiting_rename)
    await state.update_data(vpn_rename_device_id=device_id)
    await answer_callback_safe(cb)
    await cb.message.answer(
        "<b>Переименовать устройство</b>\n\n"
        "Введите новое имя одним сообщением (например, <i>Телефон жены</i>).\n"
        "Отмена: /cancel"
    )


@router.message(VpnDeviceStates.waiting_rename, F.text)
async def vpn_devices_rename_apply(message: Message, settings: Settings, state: FSMContext) -> None:
    if not vpn_feature_allowed(message.from_user.id, settings):
        await state.clear()
        return
    data = await state.get_data()
    device_id = int(data.get("vpn_rename_device_id") or 0)
    name = (message.text or "").strip()[:64]
    if name.startswith("/"):
        return
    if device_id <= 0 or not name:
        await message.answer("Имя не распознано. Попробуйте ещё раз или /cancel.")
        return
    uid = int(message.from_user.id)
    ok, msg = await vpn_api_client.post_devices_rename(
        settings,
        telegram_user_id=uid,
        device_id=device_id,
        display_name=name,
    )
    await state.clear()
    if not ok:
        await message.answer(f"Не удалось переименовать: {str(msg)[:200]}")
        return
    await message.answer(f"Готово: «{name}».")
    ok_list, pack = await vpn_api_client.post_devices_list(settings, telegram_user_id=uid)
    idx = 0
    if ok_list and isinstance(pack, dict):
        from bot.services.vpn_devices_ux import index_of_device

        idx = index_of_device(pack, device_id)
    await _render_device_card(message, settings, uid, idx)


@router.callback_query(F.data == "vpn:devices:add")
async def vpn_devices_add(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    uid = int(cb.from_user.id)
    ok, data = await vpn_api_client.post_devices_create(
        settings,
        telegram_user_id=uid,
        idempotency_key=f"dev-add-{uid}-{int(time.time())}",
    )
    if not ok:
        detail = data if isinstance(data, str) else str(data)
        if "device_limit_reached" in detail:
            await cb.answer(
                "Подписка включает одно устройство. Отвяжите текущее, чтобы подключить другое.",
                show_alert=True,
            )
            return
        await cb.answer("Не удалось добавить устройство.", show_alert=True)
        return
    await answer_callback_safe(cb)
    device = (data or {}).get("device") if isinstance(data, dict) else None
    url = ""
    new_id = 0
    if isinstance(device, dict):
        url = str(device.get("subscription_url") or "").strip()
        new_id = int(device.get("id") or 0)
    text = (
        "<b>✨ Устройство добавлено</b>\n\n"
        "Статус: ⚪️ ожидает подключения\n"
        "Импортируйте ссылку в Happ (Proxy Utility+)."
    )
    b = InlineKeyboardBuilder()
    if url:
        from bot.services.vpn_user_links import copy_text_button

        copy_btn = copy_text_button(label="🔗 Скопировать", text=url)
        if copy_btn:
            b.row(copy_btn)
        b.row(
            InlineKeyboardButton(
                text="📷 QR",
                callback_data=f"vpn:devices:qr:{new_id}" if new_id else "vpn:devices",
            )
        )
    b.row(InlineKeyboardButton(text="📱 К карточке", callback_data="vpn:devices"))
    b.row(InlineKeyboardButton(text="⬅️ К VPN", callback_data=VPN_NAV_MAIN))
    await cb.message.answer(text, reply_markup=b.as_markup(), disable_web_page_preview=True)
    idx = 0
    if new_id:
        ok_list, pack = await vpn_api_client.post_devices_list(settings, telegram_user_id=uid)
        if ok_list and isinstance(pack, dict):
            from bot.services.vpn_devices_ux import index_of_device

            idx = index_of_device(pack, new_id)
    await _render_device_card(cb.message, settings, uid, idx)


@router.callback_query(F.data.startswith("vpn:devices:rev:"))
async def vpn_devices_revoke_ask(cb: CallbackQuery, settings: Settings) -> None:
    from bot.services.vpn_devices_ux import devices_revoke_confirm_html, devices_revoke_confirm_kb

    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    raw = (cb.data or "").rsplit(":", 1)[-1]
    try:
        device_id = int(raw)
    except ValueError:
        await answer_callback_safe(cb)
        return
    display_name = ""
    ok, data = await vpn_api_client.post_devices_list(
        settings, telegram_user_id=int(cb.from_user.id)
    )
    if ok and isinstance(data, dict):
        for d in list(data.get("devices") or []):
            if int(d.get("id") or 0) == device_id:
                display_name = str(d.get("display_name") or "")
                break
    await answer_callback_safe(cb)
    await cb.message.answer(
        devices_revoke_confirm_html(display_name=display_name),
        reply_markup=devices_revoke_confirm_kb(device_id),
    )


@router.callback_query(F.data.startswith("vpn:devices:revyes:"))
async def vpn_devices_revoke_yes(cb: CallbackQuery, settings: Settings) -> None:
    if not vpn_feature_allowed(cb.from_user.id, settings):
        await answer_callback_safe(cb)
        return
    raw = (cb.data or "").rsplit(":", 1)[-1]
    try:
        device_id = int(raw)
    except ValueError:
        await answer_callback_safe(cb)
        return
    uid = int(cb.from_user.id)
    ok, _data = await vpn_api_client.post_devices_revoke(
        settings,
        telegram_user_id=uid,
        device_id=device_id,
        idempotency_key=f"dev-rev-{uid}-{device_id}-{int(time.time())}",
    )
    if not ok:
        await cb.answer("Не удалось отвязать.", show_alert=True)
        return
    await answer_callback_safe(cb)
    await cb.message.answer("Устройство отвязано. Ссылка больше не действует.")
    await _render_device_card(cb.message, settings, uid, 0, as_edit=False)
