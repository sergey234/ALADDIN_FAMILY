"""
Отдельный продуктовый модуль VPN (не checkout Stars, не поддержка).

Колбэки: корень nav:vpn; маркетинг vpn:y:*; дерево vpn:instr:*; локации vpn:loc:*;
платформы vpn:os:*; WireGuard vpn:wg:help; fallback vpn:fallback:*; основной экран vpn:flow:main.
"""

from __future__ import annotations

import json
import logging
import time
from urllib.parse import urlparse

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services import analytics_repo, users_repo, vpn_admin_support_repo, vpn_api_client, vpn_referral_repo
from bot.services.vpn_connect_copy import (
    vpn_backup_link_explainer_html,
    vpn_backup_link_short_html,
    vpn_wg_vs_backup_table_html,
    vpn_beginner_guide_html as vpn_beginner_guide_body_html,
    vpn_file_document_caption_html,
    vpn_file_import_html,
    vpn_friend_link_blurb_html,
    vpn_main_connect_steps_html,
    vpn_payment_button_label,
    vpn_qr_import_html,
    vpn_qr_photo_caption_html,
    vpn_checklist_short_html,
)
from bot.services.vpn_user_links import append_vpn_copy_link_rows, subscription_link_reply_kb
from bot.services.wg_qr_util import wg_qr_filename, wg_qr_png_bytes
from bot.services.vpn_legal_gate import (
    VPN_LEGAL_ACK_PRIVACY_CALLBACK,
    VPN_LEGAL_ACK_TERMS_CALLBACK,
    VPN_LEGAL_CONTINUE_CALLBACK,
    VPN_LEGAL_GATE_CALLBACK,
    present_vpn_legal_gate,
    vpn_privacy_and_terms_urls,
)
from bot.services.catalog import Product
from bot.services.vpn_screen_nav import (
    VPN_CHECKLIST_BTN,
    VPN_FALLBACK_MENU_BTN,
    VPN_HELP_MENU_BTN,
    VPN_NAV_CHECKLIST,
    VPN_NAV_FALLBACK_MENU,
    VPN_NAV_HELP_MENU,
    VPN_NAV_MAIN,
    kb_back_fallback_menu,
    kb_back_help_menu,
    kb_back_main,
    kb_back_marketing,
)
from bot.services.vpn_tariffs import (
    append_vpn_tariff_buy_rows,
    vpn_referral_blurb_html,
    vpn_tariffs_html,
)
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


def _vpn_news_url(settings: Settings) -> str:
    u = (settings.vpn_news_channel_url or "").strip()
    if u:
        return u
    u = (settings.required_channel_invite_url or "").strip()
    if u:
        return u
    return (settings.official_channel_invite_url or "").strip()


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
⚙ Профили «белые списки» — см. полную инструкцию на сайте"""

_LOC_DEFAULT_FOOTER = "⚙ Особые режимы — в полной инструкции на сайте"

_VPN_UI_DISABLED_ALERT = f"{VPN_PRODUCT_NAME} недоступен — напишите в поддержку."
_VPN_CMD_DISABLED = (
    f"Команда /vpn сейчас недоступна. Напишите в поддержку, если нужен {VPN_PRODUCT_NAME}."
)

_VPN_BEGINNER_GUIDE_BTN = "📖 Как подключить (пошагово)"
_VPN_PAYMENT_BTN = vpn_payment_button_label()
_VPN_BUY_HINT = "выберите тариф ниже"
_VPN_CHECK_BTN = "🧪 Проверить VPN"

_LOC_API_CACHE: tuple[tuple[str, str], float] | None = None
_LOC_API_CACHE_TTL_SEC = 60.0


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


async def _vpn_account_user_section_html(settings: Settings, telegram_user_id: int) -> str:
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return ""
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return ""
    status = (row.get("status") or "").strip()
    opaque = (row.get("opaque_token") or "").strip()
    paid = (row.get("paid_until") or "").strip()
    if status == "vpn_provisioning":
        return (
            "\n\n<b>Подписка оформляется</b> — обычно <b>от 2 до 5 минут</b>. "
            "Затем получите файл или QR ниже."
        )
    if status != "vpn_active":
        return ""
    lines: list[str] = ["\n\n<b>✅ Подписка активна</b>"]
    if paid:
        lines.append(f" до <code>{esc(paid[:19])}</code>.")
    else:
        lines.append(".")
    if _subscription_url(settings, opaque):
        lines.append(
            "\n\n<b>Запасная ссылка</b> — если WireGuard не подошёл: "
            "кнопки «📋 Запасная ссылка» и «📋 Скопировать запасную» ниже."
        )
    return "".join(lines)


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


def vpn_marketing_html(settings: Settings) -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>Привет! Я {p}.</b>\n\n"
        "Наш VPN использует современный протокол, который обеспечивает высокую скорость "
        "и стабильное соединение. Все наши сервера подключены к каналу до "
        "<b>10 Гбит/с</b>, чтобы выдерживать нагрузку и не терять скорость в часы пик.\n\n"
        "Мы <b>не храним</b> историю посещений и <b>не собираем</b> данные о том, какие сайты "
        "вы открываете. Мы <b>не продаём</b> никакие данные о вас — в отличие от многих "
        "бесплатных сервисов.\n\n"
        "Доступ к VPN выдаётся через <b>Telegram</b>, поэтому сервис не зависит от App Store "
        "и других площадок, и его сложнее ограничить через удаление приложения."
        f"{_vpn_privacy_terms_links_html(settings)}"
    )


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
        "мы делаем всё возможное, чтобы подключение оставалось стабильным и быстрым."
    )


async def _vpn_edit_or_answer(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Редактирует то же сообщение (навигация VPN); при ошибке — новое сообщение."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        err = str(exc).lower()
        if "message is not modified" in err:
            return
        await message.answer(text, reply_markup=reply_markup)


def _vpn_y_devices_html(settings: Settings) -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        "<b>📱 Все устройства</b>\n\n"
        f"<b>Одна оплата</b> {p} — настройте VPN на любом из устройств:\n"
        "смартфон (iPhone, Android), планшет (iPad, Android), "
        "ноутбук или ПК (Windows, macOS, Linux).\n\n"
        "1. <b>Одна оплата</b> = один аккаунт/подписка в боте.\n"
        "2. На каждом устройстве — <b>свой импорт</b> (тот же ключ можно добавить "
        "в WireGuard на телефоне или на ПК — по правилам сервиса).\n"
        "3. Нужно установить <b>WireGuard</b> (или другой запасной способ из указанных) "
        "<b>на каждом устройстве отдельно</b>."
    )


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


def _vpn_y_bypass_html() -> str:
    return (
        "<b>🌐 Если блокируют</b>\n\n"
        "От чего зависит, что VPN не работает:\n\n"
        "1. <b>Оператор или сеть</b> режет VPN-протоколы (WireGuard).\n"
        "2. <b>Строгий Wi‑Fi</b> — офис, отель, школа.\n"
        "3. <b>Регион и время</b> — доступность бывает разной.\n"
        "4. <b>Не тот способ</b> — сначала WireGuard; если не идёт — "
        "запасной (Happ и т.д.).\n"
        "5. Всё это <b>после оплаты</b> — в боте есть второй путь на те же дни."
    )


def _vpn_beginner_guide_html(settings: Settings) -> str:
    return vpn_beginner_guide_body_html(settings)


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
    account_block = ""
    if telegram_user_id is not None:
        account_block = await _vpn_account_user_section_html(settings, telegram_user_id)
    tariffs = vpn_tariffs_html(settings, products)
    referral = vpn_referral_blurb_html(settings)
    if (settings.vpn_api_base_url or "").strip():
        return (
            f"<b>🌐 {esc(VPN_PRODUCT_NAME)} — подключение</b>\n\n"
            f"{tariffs}"
            f"{referral}\n\n"
            f"<b>🟢 Шаг 1 — оплата</b>\n"
            f"{_VPN_BUY_HINT.capitalize()} → оплатите → подождите <b>2 мин</b>.\n\n"
            f"{vpn_main_connect_steps_html()}\n"
            "<b>Шаг 3</b> — <b>WireGuard</b>, <b>Happ / Happ Plus</b> или другое приложение "
            "из инструкции: импорт настроек и включение VPN.\n"
            f"{vpn_backup_link_short_html()}"
            f"{account_block}\n\n"
            f"<i>Подробные инструкции — «{esc(VPN_HELP_MENU_BTN)}».</i>"
        )
    return (
        f"<b>🌐 {esc(VPN_PRODUCT_NAME)} — подключение</b>\n\n"
        f"Сервис {esc(VPN_PRODUCT_NAME)} временно недоступен. "
        "Попробуйте позже или напишите в поддержку."
    )


def _vpn_marketing_kb(settings: Settings, *, show_continue: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if show_continue:
        b.row(InlineKeyboardButton(text=_VPN_PAYMENT_BTN, callback_data=VPN_LEGAL_GATE_CALLBACK))
    b.row(
        InlineKeyboardButton(text="⚡ Скорость", callback_data="vpn:y:speed"),
        InlineKeyboardButton(text="📱 Все устройства", callback_data="vpn:y:dev"),
    )
    b.row(
        InlineKeyboardButton(text="🔒 Приватность", callback_data="vpn:y:priv"),
        InlineKeyboardButton(text="🌐 Если блокируют", callback_data="vpn:y:bypass"),
    )
    news = _vpn_news_url(settings)
    if news:
        b.row(InlineKeyboardButton(text="📋 Новостной канал", url=news))
    else:
        b.row(InlineKeyboardButton(text="📋 Новости", callback_data="vpn:news:none"))
    land = (settings.vpn_marketing_landing_url or "").strip()
    if land:
        b.row(InlineKeyboardButton(text="🌍 Подробнее на сайте", url=land))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def _vpn_root_kb_base(b: InlineKeyboardBuilder, settings: Settings, products: list[Product]) -> None:
    append_vpn_tariff_buy_rows(b, products, settings)
    if (settings.vpn_api_base_url or "").strip():
        b.row(InlineKeyboardButton(text="📥 Файл для подключения", callback_data="vpn:wg:download"))
        b.row(InlineKeyboardButton(text="📷 QR для подключения", callback_data="vpn:wg:qr"))
        b.row(InlineKeyboardButton(text=VPN_CHECKLIST_BTN, callback_data=VPN_NAV_CHECKLIST))
        b.row(InlineKeyboardButton(text=_VPN_CHECK_BTN, callback_data="vpn:check"))
        b.row(InlineKeyboardButton(text=VPN_HELP_MENU_BTN, callback_data=VPN_NAV_HELP_MENU))
        b.row(InlineKeyboardButton(text=VPN_FALLBACK_MENU_BTN, callback_data=VPN_NAV_FALLBACK_MENU))
        b.row(InlineKeyboardButton(text="🌏 Локации (обзор)", callback_data="vpn:loc:open"))
        doc = _docs_base(settings)
        if doc:
            b.row(InlineKeyboardButton(text="⚠️ Правила (AUP)", url=f"{doc}/vpn-aup"))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))


async def build_vpn_root_kb(
    bot,
    settings: Settings,
    conn,
    products: list[Product],
    user_id: int,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    _vpn_root_kb_base(b, settings, products)
    await append_vpn_copy_link_rows(b, bot=bot, settings=settings, conn=conn, user_id=user_id)
    return b.as_markup()


def _vpn_root_kb(settings: Settings, products: list[Product]) -> InlineKeyboardMarkup:
    """Клавиатура без Copy Text (нет user_id) — для редких fallback-сценариев."""
    b = InlineKeyboardBuilder()
    _vpn_root_kb_base(b, settings, products)
    return b.as_markup()


def _wg_help_html(settings: Settings) -> str:
    return (
        f"<b>🔧 Файл или QR — кратко</b>\n\n"
        f"{vpn_main_connect_steps_html()}\n\n"
        f"Подробно:\n"
        f"• нажмите <b>📥 Файл</b> — придут шаги и документ настроек;\n"
        f"• или <b>📷 QR</b> — шаги и картинка для сканирования.\n\n"
        f"Полный сценарий: «{_VPN_BEGINNER_GUIDE_BTN}»."
    )


def _os_steps_html(slug: str, settings: Settings) -> str:
    if slug == "ios":
        wg_store = "App Store"
        title = "iOS / iPadOS"
    elif slug == "android":
        wg_store = "Google Play"
        title = "Android"
    else:
        wg_store = "wireguard.com"
        title = "Windows / macOS / Linux"
    api_ok = bool((settings.vpn_api_base_url or "").strip())
    file_step = (
        "«📥 Файл для подключения» или «📷 QR для подключения»"
        if api_ok
        else "файл или QR в меню бота"
    )
    return (
        f"<b>{esc(title)}</b>\n\n"
        f"1) {_VPN_BUY_HINT.capitalize()} → оплата → 2 мин.\n"
        f"2) В боте: {file_step}.\n"
        f"3) Установите <b>WireGuard</b> ({wg_store}) — это бесплатное приложение, не {esc(VPN_PRODUCT_NAME)}.\n"
        "4) Импортируйте файл или QR → включите VPN.\n"
        "5) <b>Дополнительно:</b> «📋 Запасная ссылка» или «🧱 OpenVPN (файл)» + OpenVPN Connect."
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


def _vpn_check_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🌍 Мой IP (ifconfig.me)", url="https://ifconfig.me/"))
    b.row(InlineKeyboardButton(text="⚡ Замер скорости (fast.com)", url="https://fast.com/"))
    b.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    return b.as_markup()


async def _vpn_check_html(settings: Settings, telegram_user_id: int) -> str:
    p = esc(VPN_PRODUCT_NAME)

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return (
            f"<b>{esc(_VPN_CHECK_BTN)}</b>\n\n"
            f"Сервис {p} временно недоступен."
        )
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return (
            f"<b>{esc(_VPN_CHECK_BTN)}</b>\n\n"
            f"Подписка не найдена. {_VPN_BUY_HINT.capitalize()}."
        )
    status = (row.get("status") or "").strip()
    paid = (row.get("paid_until") or "").strip()
    if status == "vpn_provisioning":
        return (
            f"<b>{esc(_VPN_CHECK_BTN)}</b>\n\n"
            "<b>Подписка оформляется</b> — подождите от 2 до 5 мин и нажмите снова."
        )
    if status == "vpn_expired":
        return (
            f"<b>{esc(_VPN_CHECK_BTN)}</b>\n\n"
            "<b>Срок подписки истёк</b> — VPN отключён.\n"
            f"Продлите: {esc(vpn_payment_button_label())} → выберите тариф.\n"
            "<i>После продления снова 📥 или 📷; в Happ — заново «Скопировать запасную».</i>"
        )
    if status != "vpn_active":
        return (
            f"<b>{esc(_VPN_CHECK_BTN)}</b>\n\n"
            f"Статус: <code>{esc(status or 'нет')}</code>. Нужна оплата — {_VPN_BUY_HINT}."
        )

    wg_ok = False
    if (settings.vpn_api_base_url or "").strip():
        ok, _conf, _err = await _fetch_wg_conf(settings, telegram_user_id)
        wg_ok = bool(ok)

    lines = [
        f"<b>{esc(_VPN_CHECK_BTN)}</b>",
        "",
        "<b>✅ Подписка активна</b>",
    ]
    if paid:
        lines.append(f" до <code>{esc(paid[:19])}</code>.")
    else:
        lines.append(".")
    if wg_ok:
        lines.append("\n<b>Файл на сервере:</b> готов.")
    else:
        lines.append("\n<b>Файл на сервере:</b> ещё готовится.")
    lines.append("\n\n<b>fast.com</b> — замер скорости.")
    return "".join(lines)


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
    *,
    show_continue: bool,
) -> None:
    text = vpn_marketing_html(settings)
    kb = _vpn_marketing_kb(settings, show_continue=show_continue)
    await _vpn_edit_or_answer(target, text, kb)


@router.callback_query(F.data == "nav:vpn")
async def nav_vpn(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not settings.ui_show_vpn:
        await cb.answer(_VPN_UI_DISABLED_ALERT, show_alert=True)
        return
    await cb.answer()
    await _vpn_log(conn, cb.from_user.id, "vpn_nav_marketing")
    await _send_or_edit_vpn_marketing(cb.message, settings, show_continue=True)


@router.callback_query(F.data == "vpn:loc:open")
async def vpn_loc_open(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
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
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    expanded = cb.data == "vpn:loc:full"
    await cb.answer()
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
    await cb.answer()
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
    cb: CallbackQuery, settings: Settings, conn, products: list[Product]
) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_log(conn, cb.from_user.id, "vpn_legal_gate_open")
    await present_vpn_legal_gate(cb.message, settings, conn, cb.from_user.id, products)


@router.callback_query(F.data == VPN_LEGAL_ACK_PRIVACY_CALLBACK)
async def vpn_legal_ack_privacy(
    cb: CallbackQuery, settings: Settings, conn, products: list[Product]
) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await users_repo.upsert_user(
        conn,
        user_id=cb.from_user.id,
        username=cb.from_user.username,
        first_name=cb.from_user.first_name,
    )
    await users_repo.accept_vpn_privacy(conn, cb.from_user.id)
    await cb.answer("Отмечено: политика конфиденциальности")
    await present_vpn_legal_gate(cb.message, settings, conn, cb.from_user.id, products)


@router.callback_query(F.data == VPN_LEGAL_ACK_TERMS_CALLBACK)
async def vpn_legal_ack_terms(
    cb: CallbackQuery, settings: Settings, conn, products: list[Product]
) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await users_repo.upsert_user(
        conn,
        user_id=cb.from_user.id,
        username=cb.from_user.username,
        first_name=cb.from_user.first_name,
    )
    await users_repo.accept_vpn_terms(conn, cb.from_user.id)
    await cb.answer("Отмечено: пользовательское соглашение")
    await present_vpn_legal_gate(cb.message, settings, conn, cb.from_user.id, products)


@router.callback_query(F.data == VPN_LEGAL_CONTINUE_CALLBACK)
async def vpn_legal_continue(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    if not await users_repo.has_vpn_legal_accepted(conn, cb.from_user.id):
        await cb.answer(
            "Сначала отметьте обе галочки: политика и соглашение.",
            show_alert=True,
        )
        return
    await state.clear()
    await cb.answer()
    await _vpn_log(conn, cb.from_user.id, "vpn_legal_continue")
    await _vpn_present_main_screen(
        cb.message, cb.bot, settings, conn, products, cb.from_user.id
    )


@router.callback_query(F.data == "vpn:flow:main")
async def vpn_flow_main(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await state.clear()
    await cb.answer()
    if not await users_repo.has_vpn_legal_accepted(conn, cb.from_user.id):
        await present_vpn_legal_gate(cb.message, settings, conn, cb.from_user.id, products)
        return
    await _vpn_present_main_screen(
        cb.message, cb.bot, settings, conn, products, cb.from_user.id
    )


@router.callback_query(F.data.in_({"vpn:y:speed", "vpn:y:dev", "vpn:y:priv", "vpn:y:bypass"}))
async def vpn_why_detail(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    key = (cb.data or "").split(":")[-1]
    if key == "speed":
        text = _vpn_y_speed_html()
    elif key == "dev":
        text = _vpn_y_devices_html(settings)
    elif key == "priv":
        text = _vpn_y_privacy_html()
    else:
        text = _vpn_y_bypass_html()
    await cb.answer()
    await _vpn_log(conn, cb.from_user.id, "vpn_marketing_card", meta={"card": key})
    await _vpn_edit_or_answer(cb.message, text, kb_back_marketing())


@router.callback_query(F.data == "vpn:news:none")
async def vpn_news_none(cb: CallbackQuery) -> None:
    await cb.answer(
        "Канал с новостями пока не подключён. Следите за объявлениями в поддержке.",
        show_alert=True,
    )


@router.callback_query(F.data == "vpn:instr:guide")
async def vpn_instr_guide(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_edit_or_answer(
        cb.message,
        _vpn_beginner_guide_html(settings),
        _vpn_beginner_guide_kb(settings),
    )


@router.callback_query(F.data.in_({VPN_NAV_CHECKLIST, "vpn:instr:checklist"}))
async def vpn_checklist_open(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    back = kb_back_help_menu() if cb.data == "vpn:instr:checklist" else kb_back_main()
    await _vpn_edit_or_answer(
        cb.message,
        vpn_checklist_short_html(settings),
        back,
    )


@router.callback_query(F.data == "vpn:instr:menu")
async def vpn_instr_menu(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_log(conn, cb.from_user.id, "vpn_help_menu_open")
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=_VPN_BEGINNER_GUIDE_BTN, callback_data="vpn:instr:guide"))
    kb.row(InlineKeyboardButton(text=VPN_CHECKLIST_BTN, callback_data="vpn:instr:checklist"))
    gu = _vpn_instructions_url(settings)
    if gu:
        kb.row(InlineKeyboardButton(text="🌍 Полная инструкция (сайт)", url=gu))
    kb.row(InlineKeyboardButton(text="📥 Как импортировать файл", callback_data="vpn:instr:file"))
    kb.row(InlineKeyboardButton(text="📷 Как сканировать QR", callback_data="vpn:instr:qr"))
    kb.row(InlineKeyboardButton(text="🔧 Файл или QR (кратко)", callback_data="vpn:instr:wg"))
    kb.row(
        InlineKeyboardButton(text="🍎 iOS", callback_data="vpn:os:ios"),
        InlineKeyboardButton(text="🤖 Android", callback_data="vpn:os:android"),
    )
    kb.row(InlineKeyboardButton(text="💻 ПК (Win/mac/Linux)", callback_data="vpn:os:desktop"))
    kb.row(InlineKeyboardButton(text="📋 Запасная ссылка", callback_data="vpn:reality:hint"))
    kb.row(InlineKeyboardButton(text="🧱 OpenVPN (файл)", callback_data="vpn:fallback:openvpn"))
    kb.row(InlineKeyboardButton(text=VPN_FALLBACK_MENU_BTN, callback_data=VPN_NAV_FALLBACK_MENU))
    kb.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    await _vpn_edit_or_answer(
        cb.message,
        f"<b>{esc(VPN_HELP_MENU_BTN)}</b>\n\nВыберите раздел — подсказка простым языком.",
        kb.as_markup(),
    )


@router.callback_query(F.data == "vpn:instr:file")
async def vpn_instr_file_help(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_edit_or_answer(cb.message, vpn_file_import_html(), kb_back_help_menu())


@router.callback_query(F.data == "vpn:instr:qr")
async def vpn_instr_qr_help(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_edit_or_answer(cb.message, vpn_qr_import_html(), kb_back_help_menu())


@router.callback_query(F.data == "vpn:instr:wg")
async def vpn_instr_wg(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_edit_or_answer(cb.message, _wg_help_html(settings), kb_back_help_menu())


@router.callback_query(F.data.in_({"vpn:os:ios", "vpn:os:android", "vpn:os:desktop"}))
async def vpn_os_choice(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    slug = (cb.data or "").split(":")[-1]
    await cb.answer()
    await _vpn_edit_or_answer(cb.message, _os_steps_html(slug, settings), kb_back_help_menu())


@router.callback_query(F.data == "vpn:fallback:menu")
async def vpn_fallback_menu(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📋 Запасная ссылка", callback_data="vpn:reality:hint"))
    kb.row(InlineKeyboardButton(text="🧱 OpenVPN (файл)", callback_data="vpn:fallback:openvpn"))
    kb.row(InlineKeyboardButton(text="⬅️ К подключению", callback_data=VPN_NAV_MAIN))
    await _vpn_edit_or_answer(
        cb.message,
        f"<b>{esc(VPN_FALLBACK_MENU_BTN)}</b>\n\n"
        "Если <b>WireGuard</b> (📥 файл / 📷 QR) не работает — те же оплаченные дни.\n\n"
        "1) <b>📋 Запасная ссылка</b> — приложение <b>Happ</b>\n"
        "2) <b>🧱 OpenVPN (файл)</b> + OpenVPN Connect\n\n"
        "<i>На экране подключения — «Скопировать запасную» при активной подписке.</i>",
        kb.as_markup(),
    )


@router.callback_query(F.data == "vpn:fallback:openvpn")
async def vpn_fallback_openvpn(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_edit_or_answer(
        cb.message,
        "<b>OpenVPN (дополнительно)</b>\n\n"
        "1) Установите <b>OpenVPN Connect</b>.\n"
        f"2) В меню {esc(VPN_PRODUCT_NAME)}: <b>«🧱 OpenVPN (файл)»</b>.\n"
        "3) Откройте файл в приложении и включите VPN.",
        kb_back_fallback_menu(),
    )


async def _send_subscription_link_message(
    message: Message,
    settings: Settings,
    telegram_user_id: int,
) -> None:
    origin = _public_origin(settings)
    if not origin:
        await message.answer("Запасная ссылка пока недоступна. Напишите в поддержку.")
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
    kb = subscription_link_reply_kb(sub_url).as_markup()
    await message.answer(
        vpn_backup_link_explainer_html(show_url=True, subscription_url=sub_url),
        reply_markup=kb,
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "vpn:sub:link")
async def vpn_sub_link(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _send_subscription_link_message(cb.message, settings, int(cb.from_user.id))


@router.callback_query(F.data == "vpn:reality:hint")
async def vpn_reality_hint(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _send_subscription_link_message(cb.message, settings, int(cb.from_user.id))


@router.callback_query(F.data == "vpn:check")
async def vpn_check(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    text = await _vpn_check_html(settings, int(cb.from_user.id))
    await cb.message.answer(text, reply_markup=_vpn_check_kb(), disable_web_page_preview=True)


@router.callback_query(F.data == "vpn:wg:help")
async def vpn_wg_help(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    await cb.answer()
    await _vpn_edit_or_answer(cb.message, _wg_help_html(settings), kb_back_help_menu())


@router.callback_query(F.data == "vpn:wg:download")
async def vpn_wg_download(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    if not (settings.vpn_api_base_url or "").strip():
        await cb.answer(f"Сервис {VPN_PRODUCT_NAME} временно недоступен.", show_alert=True)
        return
    await cb.answer()
    tid = int(cb.from_user.id)
    await cb.message.answer(vpn_file_import_html(), disable_web_page_preview=True)
    ok, conf, err = await _fetch_wg_conf(settings, tid)
    if not ok or not conf:
        await cb.message.answer(f"❌ {_wg_conf_user_alert(err)}")
        return
    doc = BufferedInputFile(conf.encode("utf-8"), filename=_wg_conf_filename(tid))
    await cb.message.answer_document(doc, caption=vpn_file_document_caption_html())


@router.callback_query(F.data.startswith("vpn:loc:pick:"))
async def vpn_loc_pick(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
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


@router.callback_query(F.data == "vpn:ovpn:download")
async def vpn_ovpn_download(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    if not (settings.vpn_api_base_url or "").strip():
        await cb.answer(f"Сервис {VPN_PRODUCT_NAME} временно недоступен.", show_alert=True)
        return
    await cb.answer()
    tid = int(cb.from_user.id)
    ok, text, err = await vpn_api_client.post_ovpn_conf(settings, telegram_user_id=tid)
    if not ok or not text:
        await cb.message.answer(
            f"❌ {_wg_conf_user_alert(err) if err else 'Запасной OpenVPN временно недоступен. Напишите в поддержку.'}"
        )
        return
    doc = BufferedInputFile(text.encode("utf-8"), filename=f"aladdin-ovpn-{tid}.ovpn")
    await cb.message.answer_document(
        doc,
        caption="<b>OpenVPN</b>\nОткройте файл в OpenVPN Connect и включите VPN.",
    )


@router.callback_query(F.data == "vpn:wg:qr")
async def vpn_wg_qr(cb: CallbackQuery, settings: Settings) -> None:
    if not settings.ui_show_vpn:
        await cb.answer()
        return
    if not (settings.vpn_api_base_url or "").strip():
        await cb.answer(f"Сервис {VPN_PRODUCT_NAME} временно недоступен.", show_alert=True)
        return
    await cb.answer()
    tid = int(cb.from_user.id)
    await cb.message.answer(vpn_qr_import_html(), disable_web_page_preview=True)
    ok, conf, err = await _fetch_wg_conf(settings, tid)
    if not ok or not conf:
        await cb.message.answer(f"❌ {_wg_conf_user_alert(err)}")
        return
    png = wg_qr_png_bytes(conf)
    photo = BufferedInputFile(png, filename=wg_qr_filename(tid))
    await cb.message.answer_photo(photo, caption=vpn_qr_photo_caption_html())


@router.message(Command("vpn"))
async def cmd_vpn(message: Message, settings: Settings, conn, products: list[Product]) -> None:
    if not settings.ui_show_vpn:
        await message.answer(_VPN_CMD_DISABLED)
        return
    uid = message.from_user.id
    if await users_repo.has_vpn_legal_accepted(conn, uid):
        body = await vpn_main_block_html(settings, products, uid) + vpn_friend_link_blurb_html()
        kb = await build_vpn_root_kb(message.bot, settings, conn, products, uid)
        await message.answer(body, reply_markup=kb)
        return
    await message.answer(
        vpn_marketing_html(settings),
        reply_markup=_vpn_marketing_kb(settings, show_continue=True),
    )
