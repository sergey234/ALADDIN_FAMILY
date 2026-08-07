from __future__ import annotations

import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import brand_constants as brand
from bot.config import Settings
from bot.services.admin_crypto_paid_gate import crypto_manual_paid_gate_applies
from bot.services.admin_order_ff import AdminOrderFfContext, fulfillment_controls_allowed
from bot.services.catalog import Product

# Legacy reply-клавиатура (ux-03). Больше не показываем, но тексты ловим, чтобы снять «липкие» кнопки.
REPLY_BTN_MENU = "🏠 Меню"
REPLY_BTN_PROFILE = "👤 Профиль"
REPLY_BTN_FRIENDS = "👥 Друзья"
REPLY_BTN_HELP = "❓ Помощь"
REPLY_BTN_MENU_ALT = "🏠 Главная"
REPLY_BTN_PROFILE_ALT = "👤 Мой профиль"
REPLY_BTN_FRIENDS_ALT = "👥 Пригласить друга"
LEGACY_REPLY_BUTTON_TEXTS: frozenset[str] = frozenset(
    {
        REPLY_BTN_MENU,
        REPLY_BTN_PROFILE,
        REPLY_BTN_FRIENDS,
        REPLY_BTN_HELP,
        REPLY_BTN_MENU_ALT,
        REPLY_BTN_PROFILE_ALT,
        REPLY_BTN_FRIENDS_ALT,
    }
)


def reply_keyboard_remove() -> ReplyKeyboardRemove:
    """Снять нижние reply-кнопки у клиента (они живут в чате, пока бот явно не снимет)."""
    return ReplyKeyboardRemove(remove_keyboard=True)


def news_channel_url(settings: Settings | None) -> str:
    """URL кнопки «Новости» в главном меню — канал AiMonkey (VPN/Stars/Premium), не сайт Aladdin."""
    if settings is None:
        return ""
    # Приоритет: явный news URL только если это t.me; иначе официальный/required канал.
    for attr in (
        "official_channel_invite_url",
        "required_channel_invite_url",
        "vpn_news_channel_url",
        "news_channel_page_url",
    ):
        u = (getattr(settings, attr, None) or "").strip()
        if not u:
            continue
        # Не уводить на витрину Aladdin, если задан только устаревший NEWS_CHANNEL_PAGE_URL.
        if attr == "news_channel_page_url" and "aladdin-ai.ru" in u.lower():
            continue
        return u
    return ""


def profile_inline_kb_rows_prefix(settings: Settings | None = None) -> list[list[InlineKeyboardButton]]:
    """Второстепенные разделы в профиле (ТЗ menu 2026-07-30): заказы/конкурс/новости/пополнить."""
    from bot.services.ui_visibility import gifts_menu_visible

    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data="nav:orders:0")],
        [InlineKeyboardButton(text="🎁 Промокод", callback_data="nav:promo")],
        [InlineKeyboardButton(text="🏆 Конкурс", callback_data="nav:contest")],
        [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="nav:topup")],
    ]
    news = news_channel_url(settings)
    if news:
        rows.insert(2, [InlineKeyboardButton(text="📢 Новости Бота", url=news)])
    rows.append([InlineKeyboardButton(text="🛟 Поддержка", callback_data="nav:supp")])
    # Партнёры / подарки / API — не в хабе; доступ из профиля при включённых флагах.
    extra: list[InlineKeyboardButton] = []
    if _ui_card_visible(settings, "ui_show_partners", "UI_SHOW_PARTNERS"):
        extra.append(InlineKeyboardButton(text="🤝 Партнёрам", callback_data="nav:partners"))
    if settings is not None and gifts_menu_visible(settings):
        extra.append(InlineKeyboardButton(text="🎁 Подарки", callback_data="nav:gifts"))
    if _ui_card_visible(settings, "ui_show_api", "UI_SHOW_API"):
        extra.append(InlineKeyboardButton(text="🔌 API", callback_data="nav:api"))
    if extra:
        rows.append(extra[:2])
        if len(extra) > 2:
            rows.append(extra[2:])
    return rows


def channel_subscribe_kb(settings: Settings) -> InlineKeyboardMarkup:
    """Кнопки подписки и повторной проверки (жёсткая стена и /menu)."""
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv:
        b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
    b.row(InlineKeyboardButton(text="✅ Я подписался - открыть меню", callback_data="start:hub"))
    return b.as_markup()


def channel_member_open_menu_kb(settings: Settings) -> InlineKeyboardMarkup:
    """/start, когда подписка на канал уже есть: ссылка на канал + вход в хаб (не пускаем «молча»)."""
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv:
        b.row(InlineKeyboardButton(text="📢 Канал магазина", url=inv))
    b.row(InlineKeyboardButton(text="🚀 Открыть меню", callback_data="start:hub"))
    return b.as_markup()


def onboarding_language_kb() -> InlineKeyboardMarkup:
    """Шаг 0 онбординга: язык (фото — тот же START_PHOTO_FILE_ID, что и для hero)."""
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="onb:lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="onb:lang:en"),
    )
    return b.as_markup()


def onboarding_terms_kb() -> InlineKeyboardMarkup:
    """Legacy: старые сообщения «Принять / Отклонить» в чате."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Принять", callback_data="onb:terms:yes"))
    b.row(InlineKeyboardButton(text="❌ Отклонить", callback_data="onb:terms:no"))
    return b.as_markup()


def onboarding_combined_kb(settings: Settings) -> InlineKeyboardMarkup:
    """Один экран: канал + «Проверить и продолжить» (документы — ссылки в тексте)."""
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv:
        b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
    b.row(InlineKeyboardButton(text="✅ Проверить и продолжить", callback_data="onb:ch:check"))
    return b.as_markup()


def onboarding_channel_kb(settings: Settings) -> InlineKeyboardMarkup:
    """Alias: combined KB (legacy name для тестов / старых вызовов)."""
    return onboarding_combined_kb(settings)


def onboarding_step1_kb(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    inv = (settings.required_channel_invite_url or "").strip()
    if inv and (settings.required_channel_id or "").strip():
        b.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=inv))
    b.row(InlineKeyboardButton(text="Далее »", callback_data="start:hub"))
    return b.as_markup()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    s = raw.strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return default


def _ui_card_visible(settings: Settings | None, attr_name: str, env_name: str) -> bool:
    if settings is not None and hasattr(settings, attr_name):
        return bool(getattr(settings, attr_name))
    return _env_bool(env_name, True)


from bot.services.ui_visibility import gifts_menu_visible, vpn_menu_visible


def hub_menu_kb(settings: Settings | None = None, *, user_id: int | None = None) -> InlineKeyboardMarkup:
    """Главное меню: VPN / Premium / Stars / Личный кабинет / Пригласить друга."""
    b = InlineKeyboardBuilder()
    show_vpn = False
    if settings is not None:
        if user_id is not None:
            show_vpn = vpn_menu_visible(user_id, settings)
        else:
            show_vpn = bool(settings.ui_show_vpn)
    # Ключевые разделы только. Заказы/Конкурс/Новости/Пополнить/AI — в кабинете или скрыты.
    if show_vpn:
        b.row(
            InlineKeyboardButton(text="🛡 VPN", callback_data="nav:vpn"),
            InlineKeyboardButton(text="💎 Premium", callback_data="nav:premium"),
        )
        b.row(InlineKeyboardButton(text="⭐ Stars", callback_data="nav:buy_stars"))
    else:
        b.row(
            InlineKeyboardButton(text="⭐ Stars", callback_data="nav:buy_stars"),
            InlineKeyboardButton(text="💎 Premium", callback_data="nav:premium"),
        )
    b.row(InlineKeyboardButton(text="👤 Личный кабинет", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    # 🤖 AI Помощник — временно скрыт из UI (handlers/код сохранены).
    return b.as_markup()


def premium_dest_kb(product_id: str) -> InlineKeyboardMarkup:
    """Legacy alias — тот же выбор получателя, что и recipient_dest_kb."""
    return recipient_dest_kb(product_id)


def recipient_dest_kb(product_id: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👤 Себе", callback_data=f"dest:slf:{product_id}"))
    b.row(InlineKeyboardButton(text="👥 Другому", callback_data=f"dest:oth:{product_id}"))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def go_to_payment_kb(product_id: str, *, gift: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Перейти к оплате", callback_data=f"go:pay:{product_id}"))
    if gift:
        b.row(InlineKeyboardButton(text="✏️ Изменить получателя", callback_data=f"dest:edit:{product_id}"))
    else:
        b.row(InlineKeyboardButton(text="⬅️ К выбору получателя", callback_data=f"buy:{product_id}"))
    return b.as_markup()


def products_kb(products: list[Product]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        b.row(
            InlineKeyboardButton(
                text=f"{p.emoji} {p.title}",
                callback_data=f"buy:{p.id}",
            )
        )
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def stars_menu_kb(products: list[Product]) -> InlineKeyboardMarkup:
    """Витрина Stars: фиксированные пакеты + своё количество."""
    b = InlineKeyboardBuilder()
    for p in products:
        if p.hide_from_menu:
            continue
        b.row(
            InlineKeyboardButton(
                text=f"{p.emoji} {p.title}",
                callback_data=f"buy:{p.id}",
            )
        )
    b.row(InlineKeyboardButton(text="✏️ Своё количество", callback_data="stars:custom"))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def payment_methods_kb(
    product_id: str,
    *,
    show_full_balance: bool,
    show_partial_mix: bool,
    balance: float,
    rub_final: float,
    back_callback: str | None = None,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    apply_preview = min(max(0.0, balance), rub_final)
    rem_preview = max(0.0, rub_final - apply_preview)
    if show_full_balance:
        b.row(
            InlineKeyboardButton(
                text=f"💰 С баланса ({rub_final:.0f} ₽)",
                callback_data=f"pay:bal:{product_id}",
            )
        )
    if show_partial_mix and apply_preview > 0 and rem_preview > 0.01:
        b.row(
            InlineKeyboardButton(
                text=f"💰 Баланс + СБП (−{apply_preview:.0f} ₽)",
                callback_data=f"pay:mixfi:{product_id}",
            )
        )
        b.row(
            InlineKeyboardButton(
                text=f"💰 Баланс + крипта (−{apply_preview:.0f} ₽)",
                callback_data=f"pay:mixcr:{product_id}",
            )
        )
    b.row(InlineKeyboardButton(text="💳 Карта / СБП (онлайн)", callback_data=f"pay:fiat:{product_id}"))
    b.row(InlineKeyboardButton(text="₿ USDT / крипта", callback_data=f"pay:crypto:{product_id}"))
    b.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=back_callback or f"buy:{product_id}",
        )
    )
    return b.as_markup()


def lava_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка на страницу оплаты LAVA (СБП, карты и др. по тарифам магазина)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Оплатить в ₽ (LAVA)", url=pay_url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def ckassa_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка на платёжную форму Ckassa (карты, СБП, SberPay и др. по тарифам ЦК)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Оплатить в ₽ (карта / СБП)", url=pay_url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def cardlink_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Кнопка на страницу оплаты Cardlink (карта / СБП)."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💳 Оплатить в ₽ (Cardlink)", url=pay_url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def fiat_checkout_options_kb(
    *,
    universal_url: str | None,
    ckassa_shop_url: str | None,
    lava_url: str | None,
    cardlink_url: str | None = None,
    bc_claim_order_id: int | None = None,
    support_order_url: str | None = None,
) -> InlineKeyboardMarkup:
    """
    До трёх URL-способов ₽: LAVA (основной), универсальная страница Ckassa BC, счёт Shop API Ckassa.
    Порядок: сначала LAVA (если есть), затем универсальная Ckassa BC.
    После оплаты на универсальной странице Ckassa — callback «Я оплатил» (уведомление админам).
    """
    b = InlineKeyboardBuilder()
    if lava_url:
        b.row(InlineKeyboardButton(text="💳 LAVA: карта / СБП (основной)", url=lava_url))
    if universal_url:
        b.row(
            InlineKeyboardButton(
                text="⭐ Ckassa: сумма вручную",
                url=universal_url,
            )
        )
    if ckassa_shop_url:
        b.row(
            InlineKeyboardButton(
                text="💳 Ckassa: фикс. сумма по заказу",
                url=ckassa_shop_url,
            )
        )
    if cardlink_url:
        b.row(InlineKeyboardButton(text="💳 Cardlink: карта / СБП", url=cardlink_url))
    if universal_url and bc_claim_order_id is not None and bc_claim_order_id > 0:
        b.row(
            InlineKeyboardButton(
                text="📨 Я оплатил",
                callback_data=f"pay:bcc:{bc_claim_order_id}",
            )
        )
    if (support_order_url or "").strip():
        b.row(InlineKeyboardButton(text="💬 Поддержка по заказу", url=(support_order_url or "").strip()))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def crypto_pay_invoice_kb(pay_url: str) -> InlineKeyboardMarkup:
    """Одна ссылка на счёт Crypto Pay (совместимость)."""
    return crypto_providers_kb([("💎 Crypto Pay (USDT)", pay_url)])


def crypto_providers_kb(url_pairs: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Несколько URL-кнопок (Crypto Pay, xRocket, …) + домой."""
    b = InlineKeyboardBuilder()
    for text, url in url_pairs:
        b.row(InlineKeyboardButton(text=text, url=url))
    b.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def verify_username_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="✅ Всё верно", callback_data="usr:ok"),
        InlineKeyboardButton(text="✏️ Исправить", callback_data="usr:ed"),
    )
    return b.as_markup()


def order_invoice_kb(
    settings,
    order_id: int,
    payment_method: str,
    *,
    lava_pay_url: str | None = None,
) -> InlineKeyboardMarkup:
    """Кнопки экрана счёта: СБП / карта / крипта / Ckassa / отмена (все товары).

    Если lavа_pay_url задан — Карта/СБП открывают страницу оплаты сразу (url=),
    без callback и без крутилки.
    """
    from bot.services.ckassa_api import ckassa_checkout_configured
    from bot.services.crypto_pay_api import crypto_pay_invoice_api_ready
    from bot.services.lava_api import lava_checkout_configured
    from bot.services.vpn_payment_copy import VPN_CARD_INVOICE_BTN, VPN_SBP_INVOICE_BTN
    from bot.services.xrocket_pay_api import xrocket_invoice_api_ready

    b = InlineKeyboardBuilder()
    pm = (payment_method or "").strip().lower()
    show_fiat = pm in ("fiat", "mix_fiat", "mixfi")
    show_crypto = pm in ("crypto", "mix_crypto", "mixcr")
    has_lava = lava_checkout_configured(settings)
    has_ck = ckassa_checkout_configured(settings)
    univers = bool((getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip())
    pay_url = (lava_pay_url or "").strip() or None

    if show_fiat:
        if has_lava:
            if pay_url:
                # Один клик → браузер / страница LAVA (карта и СБП на ней).
                b.row(
                    InlineKeyboardButton(text=VPN_SBP_INVOICE_BTN, url=pay_url),
                    InlineKeyboardButton(text=VPN_CARD_INVOICE_BTN, url=pay_url),
                )
            else:
                # Fallback: создать счёт по нажатию (старый путь).
                b.row(
                    InlineKeyboardButton(text=VPN_SBP_INVOICE_BTN, callback_data=f"pay:inv:sbp:{order_id}"),
                    InlineKeyboardButton(text=VPN_CARD_INVOICE_BTN, callback_data=f"pay:inv:card:{order_id}"),
                )
        if has_ck:
            label = "💳 Ckassa" if not has_lava else "💳 Ckassa (альт.)"
            b.row(InlineKeyboardButton(text=label, callback_data=f"pay:inv:ckassa:{order_id}"))
        if univers and not has_lava and not has_ck:
            b.row(InlineKeyboardButton(text="⭐ Оплата по ссылке", callback_data=f"pay:inv:bc:{order_id}"))

    has_crypto_api = crypto_pay_invoice_api_ready(settings) or xrocket_invoice_api_ready(settings)
    if has_crypto_api and (show_crypto or show_fiat):
        b.row(InlineKeyboardButton(text="₿ USDT / крипта", callback_data=f"pay:inv:crypto:{order_id}"))

    b.row(InlineKeyboardButton(text="⬅️ Отмена", callback_data=f"pay:inv:cancel:{order_id}"))
    return b.as_markup()


def vpn_order_invoice_kb(
    settings,
    order_id: int,
    payment_method: str,
) -> InlineKeyboardMarkup:
    """Алиас для совместимости."""
    return order_invoice_kb(settings, order_id, payment_method)


def vpn_invoice_pay_url_kb(
    pay_url: str,
    *,
    back_callback: str,
    channel: str = "default",
) -> InlineKeyboardMarkup:
    """После выбора СБП/карта/Ckassa — одна ссылка на оплату."""
    from bot.services.vpn_payment_copy import vpn_invoice_pay_url_button_label

    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text=vpn_invoice_pay_url_button_label(channel=channel),
            url=pay_url,
        )
    )
    b.row(InlineKeyboardButton(text="⬅️ Назад к счёту", callback_data=back_callback))
    return b.as_markup()


def confirm_order_kb(*, cancel_callback: str = "order:cancel") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Создать заказ", callback_data="order:submit"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=cancel_callback))
    return b.as_markup()


def feedback_nps_kb(order_id: int | None = None) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    prefix = f"fb:n:{int(order_id)}:" if order_id is not None else "fb:nps:"
    b.row(*(InlineKeyboardButton(text=str(i), callback_data=f"{prefix}{i}") for i in range(0, 6)))
    b.row(*(InlineKeyboardButton(text=str(i), callback_data=f"{prefix}{i}") for i in range(6, 11)))
    return b.as_markup()


def feedback_wishes_kb(order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    oid = int(order_id)
    b.row(InlineKeyboardButton(text="✍️ Пожелания и рекомендации", callback_data=f"fb:w:{oid}"))
    b.row(InlineKeyboardButton(text="Пропустить", callback_data=f"fb:sk:{oid}"))
    return b.as_markup()


def feedback_csat_kb() -> InlineKeyboardMarkup:
    """Deprecated: CSAT 1–5 после фонового NPS отключён. Клавиатура не используется в UI."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="OK", callback_data="fb:csat:0"))
    return b.as_markup()


def admin_order_kb(
    order_id: int,
    *,
    settings: Settings | None = None,
    actor_id: int | None = None,
    order_ff: AdminOrderFfContext | None = None,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    restricted = (
        settings is not None
        and actor_id is not None
        and settings.admin_roles_restricted()
        and not settings.is_super_admin(actor_id)
    )
    if not restricted and order_ff is not None:
        st = (order_ff.status or "").strip().lower()
        if st == "pending_payment":
            paid_label = "✅ Оплачен"
            paid_cb = f"adm:paid:{order_id}"
            if (
                settings is not None
                and crypto_manual_paid_gate_applies(
                    {
                        "status": order_ff.status,
                        "payment_method": order_ff.payment_method or "",
                    },
                    settings,
                )
            ):
                paid_label = "⚠️ Оплачен (break-glass)"
                paid_cb = f"adm:paidbg:{order_id}"
            b.row(InlineKeyboardButton(text=paid_label, callback_data=paid_cb))
        elif st == "paid":
            b.row(
                InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"),
                InlineKeyboardButton(text="🎁 Выдан", callback_data=f"adm:done:{order_id}"),
            )
        elif st == "processing":
            b.row(InlineKeyboardButton(text="🎁 Выдан", callback_data=f"adm:done:{order_id}"))
        elif st not in ("completed", "refunded", "expired", "payment_disputed"):
            b.row(
                InlineKeyboardButton(text="✅ Оплачен", callback_data=f"adm:paid:{order_id}"),
                InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"),
            )
            b.row(InlineKeyboardButton(text="🎁 Выдан", callback_data=f"adm:done:{order_id}"))
    elif not restricted:
        b.row(
            InlineKeyboardButton(text="✅ Оплачен", callback_data=f"adm:paid:{order_id}"),
            InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"),
        )
        b.row(InlineKeyboardButton(text="🎁 Выдан", callback_data=f"adm:done:{order_id}"))
    else:
        b.row(InlineKeyboardButton(text="⚙️ В работе", callback_data=f"adm:proc:{order_id}"))

    if (
        settings is not None
        and actor_id is not None
        and settings.is_super_admin(actor_id)
        and order_ff is not None
    ):
        st = (order_ff.status or "").strip().lower()
        if st in ("pending_payment", "paid", "processing", "expired"):
            b.row(InlineKeyboardButton(text="💸 Возврат", callback_data=f"adm:refund:{order_id}"))
        if st in ("paid", "processing"):
            b.row(InlineKeyboardButton(text="⚖️ Спор", callback_data=f"adm:disp:{order_id}"))
        if st == "payment_disputed":
            b.row(InlineKeyboardButton(text="↩️ Снять спор → оплачен", callback_data=f"adm:dispok:{order_id}"))

    if (
        settings is not None
        and actor_id is not None
        and order_ff is not None
        and fulfillment_controls_allowed(order_ff)
    ):
        manual = str(order_ff.fulfillment_mode_raw or "").strip().lower() == "manual_only"
        if not manual:
            b.row(InlineKeyboardButton(text="🤚 Только вручную", callback_data=f"adm:ffman:{order_id}"))
        elif settings.is_super_admin(actor_id):
            b.row(InlineKeyboardButton(text="🤖 Снова авто", callback_data=f"adm:ffauto:{order_id}"))
        if settings.is_super_admin(actor_id) and order_ff.status == "paid":
            b.row(InlineKeyboardButton(text="🔄 Сброс авто-полей", callback_data=f"adm:ffrst:{order_id}"))
    return b.as_markup()


def admin_topup_kb(
    topup_id: int,
    *,
    settings: Settings | None = None,
    actor_id: int | None = None,
) -> InlineKeyboardMarkup:
    restricted = (
        settings is not None
        and actor_id is not None
        and settings.admin_roles_restricted()
        and not settings.is_super_admin(actor_id)
    )
    if restricted:
        return InlineKeyboardMarkup(inline_keyboard=[])
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Зачислить баланс", callback_data=f"top:ok:{topup_id}"))
    return b.as_markup()


def admin_order_reply_markup_for_api(
    order_id: int,
    *,
    settings: Settings,
    actor_id: int,
    order_ff: AdminOrderFfContext | None = None,
) -> dict:
    """Слово `reply_markup` для Telegram Bot API (sendMessage)."""
    m = admin_order_kb(order_id, settings=settings, actor_id=actor_id, order_ff=order_ff)
    dumped = m.model_dump(mode="python", exclude_none=True)
    return {"inline_keyboard": dumped.get("inline_keyboard") or []}


def admin_topup_reply_markup_for_api(topup_id: int, *, settings: Settings, actor_id: int) -> dict | None:
    m = admin_topup_kb(topup_id, settings=settings, actor_id=actor_id)
    dumped = m.model_dump(mode="python", exclude_none=True)
    rows = dumped.get("inline_keyboard") or []
    if not rows:
        return None
    return {"inline_keyboard": rows}


def orders_list_kb(page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    row: list[InlineKeyboardButton] = []
    if has_prev:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav:orders:{page - 1}"))
    row.append(InlineKeyboardButton(text=f"· {page + 1} ·", callback_data="nav:orders:noop"))
    if has_next:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"nav:orders:{page + 1}"))
    if row:
        b.row(*row)
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def pending_order_cap_kb() -> InlineKeyboardMarkup:
    """Экран при лимите неоплаченных заказов — сразу ведёт в «Мои заказы»."""
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📦 Заказы", callback_data="nav:orders:0"))
    b.row(
        InlineKeyboardButton(
            text="🗑 Отменить все неоплаченные",
            callback_data="orders:cancel_all_confirm",
        )
    )
    b.row(InlineKeyboardButton(text="🏠 В меню", callback_data="nav:hub"))
    return b.as_markup()


def orders_cancel_all_confirm_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="✅ Да, отменить все", callback_data="orders:cancel_all:yes"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:orders:0"),
    )
    return b.as_markup()


def order_detail_kb(
    order_id: int,
    support_url: str | None,
    *,
    pending_payment: bool = False,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if pending_payment:
        b.row(
            InlineKeyboardButton(
                text="💳 Вернуться к оплате",
                callback_data=f"pay:inv:view:{order_id}",
            )
        )
        b.row(
            InlineKeyboardButton(
                text="❌ Отменить заказ",
                callback_data=f"ord:cancel:{order_id}",
            )
        )
    if support_url:
        b.row(InlineKeyboardButton(text="💬 Поддержка по заказу", url=support_url))
    else:
        b.row(InlineKeyboardButton(text="💬 Раздел поддержки", callback_data="nav:supp"))
    b.row(InlineKeyboardButton(text="⬅️ К списку", callback_data="nav:orders:0"))
    b.row(InlineKeyboardButton(text="🏠 В меню", callback_data="nav:hub"))
    return b.as_markup()
