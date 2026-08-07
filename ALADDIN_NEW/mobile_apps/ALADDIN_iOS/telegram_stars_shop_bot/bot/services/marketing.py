from __future__ import annotations

from bot import brand_constants as brand
from bot.config import Settings
from bot.services.fiat_checkout import fiat_bc_universal_url_active, fiat_primary_provider_label
from bot.services.lava_api import lava_checkout_configured
from bot.util_html import esc

# Подпись к фото в Telegram - до 1024 символов; оставляем запас под сущности HTML.
CHANNEL_GATE_PHOTO_CAPTION_MAX = 1000


def _services_menu_phrase(settings: Settings) -> str:
    if settings.ui_show_vpn:
        return f"Stars, Premium, {brand.VPN_PRODUCT_NAME}, заказы, пополнение и поддержка"
    return "Stars, Premium, заказы, пополнение и поддержка"


def _services_short(settings: Settings) -> str:
    if settings.ui_show_vpn:
        return f"Stars, Premium и {brand.VPN_PRODUCT_NAME}"
    return "Stars и Premium"


def shop_services_hero_html(settings: Settings) -> str:
    if settings.ui_show_vpn:
        return (
            f"<b>⭐ Telegram Stars, Premium и {esc(brand.VPN_PRODUCT_NAME)} — быстро и надёжно!</b>\n"
            f"{esc(brand.VPN_PRODUCT_NAME)}: стабильное соединение, пробный период <b>3 дня</b>, бонус за друзей.\n"
            "Оформляйте заказ в пару кликов прямо в Telegram.\n"
            "Надёжно. Удобно. Быстро."
        )
    return (
        "<b>⭐ Telegram Stars и Premium - быстро и надёжно!</b>\n"
        "Оформляйте заказ в пару кликов прямо в Telegram.\n"
        "Надёжно. Удобно. Быстро."
    )


def why_us_block_html(settings: Settings) -> str:
    """Блок «почему мы» на первом экране (бренд + доверие)."""
    vpn_line = ""
    if settings.ui_show_vpn:
        vpn_line = (
            f"• {esc(brand.VPN_PRODUCT_NAME)} — быстрый и стабильный; пробный период <b>3 дня</b>; "
            "бонусные дни за приглашение друзей.\n"
        )
    return (
        "<b>Почему мы</b>\n"
        "• Честные цены и понятный чек-аут в Telegram.\n"
        f"• {_services_short(settings)} — одна команда выдачи, статусы заказа в боте.\n"
        f"{vpn_line}"
        "• Реферальная программа и партнёрский API для тех, кто хочет масштабировать продажи.\n"
        "• Поддержка, инструкция по оплате и <b>закреп канала</b> (FAQ) - в меню «Поддержка» / «Оплата и зачисление»."
    )


def _channel_gate_marketing_mode(settings: Settings) -> str:
    raw = (settings.required_channel_gate_marketing or "short").strip().lower()
    if raw in ("full", "short", "title_only"):
        return raw
    return "short"


def channel_start_member_ack_html(settings: Settings) -> str:
    """Сообщение на /start, если гейт включён и пользователь уже в канале (без мгновенного «втихаря» в хаб)."""
    raw = (settings.required_channel_display_name or "").strip()
    name = esc(raw) if raw else "канал магазина"
    return (
        f"<b>Доступ к {name} уже есть</b> - вы в канале.\n\n"
        f"Нажмите <b>«Открыть меню»</b> ниже: {_services_menu_phrase(settings)}. "
        f"Прайс, скидки и FAQ - в <b>закрепе</b> канала."
    )


def channel_subscribe_after_greeting_html(settings: Settings) -> str:
    """Короткий второй шаг после приветствия на /start: только подписка и проверка кнопкой."""
    raw = (settings.required_channel_display_name or "").strip()
    title = esc(raw) if raw else "Канал магазина"
    return (
        f"<b>{title}</b>\n\n"
        "Чтобы открыть покупки и меню бота, подпишитесь на канал.\n"
        "После подписки нажмите «✅ Я подписался - открыть меню»."
    )


def channel_gate_short_punch_html(settings: Settings) -> str:
    """
    Короткий «wow»-экран до подписки: Stars/Premium, скидки из .env, призыв на канал.
    Детали вынесены в канал (закреп) - здесь только крючок и 2 кнопки.
    """
    raw = (settings.required_channel_display_name or "").strip()
    title = esc(raw) if raw else f"канал {brand.BRAND_SHORT}"
    svc = _services_short(settings)
    vpn_hook = ""
    if settings.ui_show_vpn:
        vpn_hook = (
            f"\n{esc(brand.VPN_PRODUCT_NAME)}: быстрый и стабильный; пробный период <b>3 дня</b>; бонус за друзей.\n"
        )
    return (
        f"<b>⭐ {brand.BRAND_SHORT}: {svc} за минуты</b>\n"
        f"<b>Официальный бот:</b> {esc(brand.SHOP_BOT_HANDLE)}\n"
        "Быстрое оформление, прозрачный статус и живая поддержка без квестов.\n"
        f"Честные цены по прайсу — без скрытых скидок на {svc}.\n"
        f"{vpn_hook}"
        f"👉 Подпишитесь на <b>{title}</b> - сразу откроем меню: оплата, заказы, поддержка.\n"
        "Прайс и подробный FAQ - в закрепе канала. Дальше: «Подписаться» → "
        "«✅ Я подписался - открыть меню»."
    )


def channel_hard_wall_html(settings: Settings) -> str:
    """Текст экрана подписки (жёсткая стена). Режим REQUIRED_CHANNEL_GATE_MARKETING: full | short | title_only."""
    raw = (settings.required_channel_display_name or "").strip()
    title = esc(raw) if raw else "Канал магазина"
    mode = _channel_gate_marketing_mode(settings)
    if mode == "title_only":
        return (
            f"<b>{title}</b>\n\n"
            f"Подпишитесь на канал - так откроется меню бота: {_services_menu_phrase(settings)}. "
            "После подписки нажмите кнопку ниже: мы проверим доступ и покажем основное меню."
        )
    gate_footer = (
        f"\n\n<b>{title}</b>\n"
        f"Чтобы открыть меню бота ({_services_menu_phrase(settings)}), подпишитесь на канал. "
        "После подписки нажмите «Я подписался - открыть меню» - проверим доступ автоматически."
    )
    hero = onboarding_screen_1_html(settings)
    if mode == "short":
        return channel_gate_short_punch_html(settings)
    return hero + "\n\n" + why_us_block_html(settings) + gate_footer


def channel_hint_html(settings: Settings) -> str:
    if not (settings.required_channel_id or "").strip():
        return ""
    if (settings.required_channel_invite_url or "").strip():
        return (
            "\n\n<b>Канал магазина</b>\n"
            "Подпишитесь на наш канал - так вы не пропустите акции и сроки конкурсов для партнёров. "
            "Перед покупкой Stars / Premium / VPN / подарков подписка обязательна."
        )
    return (
        "\n\n<b>Канал магазина</b>\n"
        "Перед покупкой подписка на канал обязательна - добавьте <code>REQUIRED_CHANNEL_INVITE_URL</code> в .env для кнопки «Подписаться»."
    )


def onboarding_screen_1_html(settings: Settings) -> str:
    """Короткий hero-экран для первого касания (2-3 строки)."""
    return shop_services_hero_html(settings)


def onboarding_combined_caption_html(settings: Settings) -> str:
    """Один стартовый экран: канал + согласие (ссылки в тексте, без фото)."""
    pu = (settings.privacy_policy_url or "").strip()
    tu = (settings.terms_of_service_url or "").strip()
    if tu:
        terms_part = f'<a href="{esc(tu)}">Пользовательское соглашение</a>'
    else:
        terms_part = "Пользовательское соглашение"
    if pu:
        privacy_part = f'<a href="{esc(pu)}">Политику конфиденциальности</a>'
    else:
        privacy_part = "Политику конфиденциальности"
    return (
        "<b>🐵 Добро пожаловать в Ai Monkey Stars</b>\n\n"
        "Всё для Telegram в одном месте:\n"
        "⭐ Stars\n"
        "💎 Premium\n"
        "🛡 VPN\n\n"
        "Для продолжения:\n\n"
        "📢 Подпишитесь на наш канал.\n\n"
        "Нажимая «✅ Проверить и продолжить», вы подтверждаете, что ознакомились "
        f"и принимаете {terms_part} и {privacy_part}."
    )


def onboarding_terms_caption_html(settings: Settings) -> str:
    """Legacy экран оферты (старые сообщения / тесты). Новый путь — combined."""
    pu = (settings.privacy_policy_url or "").strip()
    tu = (settings.terms_of_service_url or "").strip()
    hero = shop_services_hero_html(settings) + (
        "\n\n"
        "Используя бота, совершая в нём покупки и вводя персональные данные, вы соглашаетесь "
        "с публичной офертой:\n\n"
    )
    links: list[str] = []
    if pu:
        links.append(f'📜 <a href="{pu}">Политика конфиденциальности</a>')
    if tu:
        links.append(f'‼️ <a href="{tu}">Правила использования</a>')
    if links:
        hero += "\n".join(links) + "\n\n"
    hero += "Ссылки 🔗 кликабельны."
    hero += f'\n\n🤖 <b>Официальный бот магазина:</b> {esc(brand.SHOP_BOT_HANDLE)}'
    ch_url = (settings.required_channel_invite_url or settings.official_channel_invite_url or "").strip()
    if ch_url:
        dn = (settings.required_channel_display_name or "").strip() or brand.CHANNEL_DISPLAY_NAME_DEFAULT
        hero += f'\n\n📢 <b>Официальный канал магазина:</b> <a href="{ch_url}">{esc(dn)}</a>'
    return hero


def onboarding_channel_caption_html(settings: Settings) -> str:
    """Legacy экран канала. Новый путь — onboarding_combined_caption_html."""
    return onboarding_combined_caption_html(settings)


def partner_onboarding_html(settings: Settings) -> str:
    """Короткий онбординг: реф-ссылка vs API для своего бота/сайта."""
    api = (settings.api_docs_url or "").strip()
    api_line = (
        f"\n<b>Документация API:</b> <a href=\"{api}\">открыть OpenAPI</a>\n"
        if api
        else "\n<b>Документация API:</b> файл <code>docs/openapi_v1.yaml</code> в репозитории бота.\n"
    )
    return (
        "<b>Партнёрам</b>\n\n"
        "<b>1. Приглашение друзей</b> (простой старт)\n"
        "Кнопка «Пригласить друга» в меню или «Мой профиль» — персональная ссылка. "
        "После первой <b>выданной</b> покупки друга вам начисляется % на "
        "<b>реферальный баланс</b> (тратить на VPN, Stars и Premium; вывод по правилам).\n"
        "Идеально для блогеров и личных рекомендаций.\n\n"
        "<b>2. API для своего бота или сайта</b>\n"
        "Если у вас свой Telegram-бот, сайт или приложение: выпустите ключ в разделе «Наш API», "
        "подключайте заказы и вебхуки server-to-server (заголовок <code>X-API-KEY</code>). "
        "Трафик идёт через ваш продукт, исполнение и выдача - на нашей стороне по договорённости с поддержкой."
        + api_line
        + "\n<i>Раздел «Наш API» в главном меню ведёт к выпуску ключа и заявке оператору.</i>"
    )


def referral_faq_html(settings: Settings) -> str:
    from bot.brand_constants import VPN_PRODUCT_NAME
    from bot.services.ref_withdraw_repo import MIN_WITHDRAW_RUB
    from bot.services.referral_partner import QUALIFY_VPN_MIN_DAYS, WITHDRAW_MIN_QUALIFIED_VPN

    rb = esc(settings.ref_buyer_discount_percent)
    rf = int(settings.vpn_referral_referrer_days)
    ff = int(settings.vpn_referral_friend_days)
    vpn_extra = ""
    if settings.ui_show_vpn and (ff > 0 or rf > 0):
        vpn_extra = (
            f"• Если друг впервые оформил платный {esc(VPN_PRODUCT_NAME)} — "
            f"бонусные дни ему (+{ff}) и вам (+{rf}). Это дни, не рубли.\n"
        )
    buyer_discount_line = ""
    if settings.ui_show_vpn and float(settings.ref_buyer_discount_percent) > 0:
        buyer_discount_line = (
            f"• На первый заказ <b>{esc(VPN_PRODUCT_NAME)}</b> у друга может действовать скидка <b>{rb}%</b> "
            "(если ещё не было выданных покупок).\n"
        )
    min_w = esc(f"{MIN_WITHDRAW_RUB:.0f}")
    return (
        "<b>Как работает приглашение друзей</b>\n\n"
        "• <b>Реферальный баланс</b> — % с покупок друзей (один кошелёк).\n"
        "• <b>Основной баланс</b> — ваши пополнения; тратится на всё.\n"
        "• Реферальный можно потратить на <b>VPN, Stars и Premium</b> "
        f"или вывести от <b>{min_w} ₽</b> (карта или крипта, проверка админом).\n"
        f"{buyer_discount_line}"
        "• <b>VPN:</b> % один раз с первой покупки друга (по уровню 15–30%).\n"
        "• <b>Stars и Premium:</b> % с каждой выданной покупки друга (по уровню 1–3%).\n"
        f"• Уровень растёт от числа друзей с VPN ≥{QUALIFY_VPN_MIN_DAYS} дн. "
        "(7 дней и пробник не считаются).\n"
        f"{vpn_extra}"
        "• Самоприглашение не засчитывается.\n"
        f"• Вывод: ≥{min_w} ₽, ≥{WITHDRAW_MIN_QUALIFIED_VPN} друзей с VPN "
        f"≥{QUALIFY_VPN_MIN_DAYS} дн., свой VPN ≥{QUALIFY_VPN_MIN_DAYS} дн., "
        "не чаще 1 раза в неделю.\n\n"
        "<i>Уровень и проценты пересчитываются каждый раз, когда вы открываете экран.</i>"
    )


def refund_policy_table_html(settings: Settings) -> str:
    """Таблица сроков Lava/шаблон — для экрана «Сроки возврата» в боте."""
    ru = esc((settings.refund_policy_url or "https://aimonkeystars.ru/v1/legal/refund").strip())
    return (
        "<b>Сроки возврата</b>\n\n"
        "• После выдачи («выдан») — <b>возврату не подлежат</b>\n"
        "• Оказание услуги — факт <b>от 5 минут до 24 часов</b>; максимум — "
        "<b>3 календарных дня</b> с момента оплаты\n"
        "• Подача заявки — <b>14 календарных дней</b> после просрочки 3-дневного срока, "
        "если заказ не «выдан»\n"
        "• Рассмотрение — до <b>10 рабочих дней</b>\n"
        "• Возврат денег — до <b>14 рабочих дней</b> после одобрения, "
        "<b>на те же реквизиты, в полном объёме</b>\n\n"
        f"Полный текст: <a href=\"{ru}\">политика возвратов</a>.\n"
        "Заявка — «Написать оператору» в разделе Поддержка (с номером заказа)."
    )


def refund_policy_blurb_html(settings: Settings) -> str:
    """Единый текст о возвратах для FAQ бота."""
    ru = esc((settings.refund_policy_url or "https://aimonkeystars.ru/v1/legal/refund").strip())
    return (
        "<b>Возвраты</b>\n"
        "Цифровые товары, оказанные в полном объёме (<b>«выдан»</b>), — <b>возврату не подлежат</b>.\n"
        "До выдачи: факт 5 мин–24 ч (макс. 3 кал. дня); заявка 14 кал. дней после просрочки; "
        "рассмотрение до 10 раб. дн.; возврат до 14 раб. дн. на те же реквизиты в полном объёме. "
        f"<a href=\"{ru}\">Политика возвратов</a> · в боте — «Сроки возврата»."
    )


def payment_faq_html(settings: Settings) -> str:
    """Текст для кнопки «Оплата и зачисление» (Поддержка): без имён .env, для покупателей и партнёров-юзеров."""
    uni = fiat_bc_universal_url_active(settings)
    provider_extra = ""
    if lava_checkout_configured(settings):
        provider_extra = (
            "<b>Оплата через LAVA</b>\n"
            "Нажмите кнопку <b>«Оплатить в ₽ (LAVA)»</b> — откроется страница с картой или СБП. "
            "Сумма на странице должна совпасть с заказом. Статус <b>«Оплачен»</b> обычно появляется за 1–3 минуты. "
            "Выдача — после «Оплачен».\n\n"
        )
    elif uni:
        bm = float(getattr(settings, "ckassa_bc_display_min_rub", 50.0) or 50.0)
        if bm < 1.0:
            bm = 50.0
        bms = esc(f"{bm:.0f}")
        provider_extra = (
            "<b>Оплата по ссылке Ckassa</b>\n"
            f"Обычно на странице действует минимум <b>{bms} ₽</b>. Сумма в поле оплаты должна совпасть с заказом. "
            "В «назначение платежа» (если есть) вставьте код <code>ORDER…</code> из экрана оплаты. "
            "Один платёж, затем <b>«Я оплатил»</b> или поддержка с номером заказа. Выдача — после статуса «Оплачен».\n\n"
        )
    head = (
        f"<b>Оплата и зачисление ({_services_short(settings)}, подарки)</b>\n\n"
        "<b>Как оплатить</b>\n"
        f"В корзине: <b>карта / СБП (онлайн через {esc(fiat_primary_provider_label(settings))})</b> — "
        "откроется защищённая страница оплаты, "
        "или <b>крипта (USDT)</b> — "
        "счёт в Telegram, или оплата с <b>баланса</b> в ₽, если накопили. "
        "Сумма в боте и на странице/в счёте к оплате должна <b>совпадать</b> с суммой заказа.\n\n"
    )
    tail = (
        "<b>Что значит «Оплачен»</b>\n"
        "Средства дошли, заказ <b>встал в очередь</b> на выдачу. Дальше, по готовности, статусы <b>«В работе»</b> и <b>«Выдан»</b> - "
        "как настроено у магазина: часто авто, иначе вручную.\n\n"
        "<b>Когда ждать выдачу</b>\n"
        "Stars и Premium — от очереди магазина. VPN — доступ обычно сразу после «Оплачен».\n"
        "Дольше ожидаемого - раздел <b>«Поддержка»</b> с <b>номером заказа</b>.\n\n"
        "<b>СБП и банк</b>\n"
        "Обычно быстро; в редких случаях банк держит до ~<b>30 минут</b>. Не зачислилось - поддержка, квитанция (PDF) и номер заказа.\n\n"
        "<b>Статус «срок оплаты истёк»</b>\n"
        "Сработал таймер, пока ждали. Можно оформить заказ снова; если уже оплатили - <b>Поддержка</b> с номером заказа.\n\n"
        "<b>Крипта, ручной перевод (адрес из текста бота)</b>\n"
        "В комментарии / memo к переводу укажите код <code>ORDER…</code> из сообщения. Без этого - только поддержка с "
        "<b>номером заказа</b> и <b>tx</b> (хэш).\n"
        "Если в кошельке «Unverified token» / «Unknown token» - перевод <b>не</b> принимаем, оформите через "
        "счёт в Telegram (кнопка в боте).\n\n"
        "<b>USDT в счёте (Crypto Pay / xRocket)</b>\n"
        "Итог в USDT берите из <b>готового счёта</b> - он может чуть отличаться от ориентира в рублях в боте (курс ставит сервис счёта).\n\n"
        "<b>Приглашение друзей, скидка, бонус на покупки</b> — в «Мой профиль» / «Как работает приглашение».\n\n"
        f"{refund_policy_blurb_html(settings)}\n"
    )
    return head + provider_extra + tail


def privacy_screen_html(settings: Settings) -> str:
    """Экран «Данные и политика» магазина Stars/Premium (не путать с документами AiMonkeyVPN)."""
    parts: list[str] = [
        f"<b>Данные и политика</b> <i>(магазин {_services_short(settings)})</i>\n",
    ]
    pu = (settings.privacy_policy_url or "").strip()
    tu = (settings.terms_of_service_url or "").strip()
    ou = (settings.public_offer_url or "").strip()
    ru = (settings.refund_policy_url or "").strip()
    if pu or tu or ou or ru:
        parts.append("<b>Документы</b> (публичные страницы, как в аналогичных сервисах):\n")
        if ou:
            parts.append(f"• <a href=\"{esc(ou)}\">Публичная оферта</a>\n")
        if ru:
            parts.append(f"• <a href=\"{esc(ru)}\">Политика возвратов</a>\n")
        if pu:
            parts.append(f"• <a href=\"{esc(pu)}\">Политика конфиденциальности</a>\n")
        if tu:
            parts.append(f"• <a href=\"{esc(tu)}\">Пользовательское соглашение</a>\n")
        parts.append("\n")
        parts.append(refund_policy_table_html(settings))
        parts.append(
            "\n\n<i>Полные юридические формулировки - в документах по ссылкам; ниже - кратко о данных сервиса.</i>\n\n"
        )
    parts.extend(
        [
            "Мы храним в сервисе: ваш Telegram ID, ник (если есть), историю заказов, "
            "баланс и реферальные начисления, заявки на пополнение - для оказания услуги.\n\n",
            "Данные не передаём третьим лицам для рекламы. Срок хранения - пока нужен для учёта и поддержки.\n\n",
            "По вопросам удаления или выгрузки данных напишите в раздел «Поддержка» с темой "
            "<code>персональные данные</code>.\n\n",
            "Типовые вопросы по оплате, рефералке и возвратам - в разделе <b>«Поддержка»</b> в главном меню.\n\n"
            "В боте может отвечать <b>AI Помощник</b> (кнопка «🤖 AI Помощник»): кратко по гайдам и статусу "
            "ваших заказов из нашей базы. Полные ссылки VPN (/sub/) помощник в чат не вставляет — только кнопкой. "
            "В любой момент можно перейти к человеку через «Поддержку».\n\n",
        ]
    )
    vpn_base = (settings.vpn_docs_public_base or "").strip().rstrip("/")
    if vpn_base:
        parts.append(
            f"<b>AiMonkeyVPN</b> — отдельный продукт с <b>своими</b> документами "
            f"(<a href=\"{esc(vpn_base)}/vpn-data\">политика VPN</a>, "
            f"<a href=\"{esc(vpn_base)}/vpn-terms\">соглашение VPN</a>). "
            "Их принимают на шаге <b>🌐 Тарифы VPN</b> в разделе <b>🌐 VPN</b> главного меню — "
            "это не те же страницы, что для Stars выше."
        )
    elif settings.ui_show_vpn:
        parts.append(
            "<b>AiMonkeyVPN</b> — отдельные документы; принимаются в разделе "
            "<b>🌐 VPN</b> → <b>🌐 Тарифы VPN</b> (не путать с политикой магазина Stars)."
        )
    return "".join(parts)


def channel_pin_bc_checkout_html(settings: Settings) -> str:
    """
    Текст для закрепля в Telegram-канале: тот же алгоритм, что покупатель видит при оплате по ссылке bc (без номера заказа).
    Админы получают копию командой /channel_checkout_pin (удобно переслать в канал и закрепить).
    """
    uni = fiat_bc_universal_url_active(settings)
    if lava_checkout_configured(settings):
        return (
            "<b>Оплата через LAVA (кратко)</b>\n\n"
            "• В боте нажмите <b>«Оплатить в ₽ (LAVA)»</b> — откроется страница оплаты.\n"
            "• Сумма на странице — <b>как в заказе</b> в боте.\n"
            "• Оплатите картой или СБП.\n"
            "• Статус <b>«Оплачен»</b> смотрите в <b>«Заказы»</b> (обычно 1–3 минуты).\n"
            "• Выдача Stars / Premium / VPN — после «Оплачен».\n"
            "• Сохраните квитанцию из банка до получения услуги.\n\n"
            "<i>Всё оформление — в боте: меню, «Заказы», «Поддержка».</i>"
        )
    bm = float(getattr(settings, "ckassa_bc_display_min_rub", 50.0) or 50.0)
    if bm < 1.0:
        bm = 50.0
    bms = esc(f"{bm:.0f}")
    if not uni:
        return (
            "<b>Оплата по ссылке Ckassa</b>\n\n"
            "В боте не задана ссылка на универсальную оплату - попросите владельца магазина включить "
            "<code>CKASSA_BC_UNIVERSAL_PAYMENT_URL</code>, затем снова выполните команду /channel_checkout_pin."
        )
    return (
        "<b>Оплата по ссылке Ckassa (кратко)</b>\n\n"
        f"• Обычно минимум на странице оплаты <b>{bms} ₽</b>.\n"
        "• Сумма на странице - <b>как в заказе</b> в боте, без ошибок в копейках.\n"
        "• <b>Один платёж</b> - не оплачивайте дважды.\n"
        "• В «назначение платежа» (если банк показывает поле) вставьте код из бота: <code>ORDER</code> и номер заказа без пробела.\n"
        "• После оплаты в боте нажмите <b>«Я оплатил»</b> или напишите в поддержку с номером заказа.\n"
        "• Статус <b>«Оплачен»</b> смотрите в <b>«Заказы»</b>; выдача Stars / Premium / VPN - после «Оплачен».\n"
        "• Сохраните квитанцию из банка до получения услуги.\n\n"
        "<i>Всё оформление - в боте: меню, «Заказы», «Поддержка».</i>"
    )


def faq_comprehensive_html(settings: Settings) -> str:
    """
    Единый блок «Ответы на часто задаваемые вопросы» (как в публичных сервисах),
    с цифрами из настроек бота (рефералка), без привязки к «% от маржи».
    """
    rc = esc(settings.ref_commission_percent)
    return (
        "<b>ℹ️ Частые вопросы</b>\n"
        "<i>Коротко здесь, подробный раздел <b>«Оплата и зачисление»</b> и <b>закреп канала</b> (FAQ).</i>\n\n"
        "<b>• Крипта без комментария / неверная сумма</b>\n"
        "Автозачисление невозможно. В поддержку: <b>номер заказа</b> и <b>tx</b> (заявка на пополнение - номер заявки).\n\n"
        "<b>• СБП / банк: оплатил, в боте не видно</b>\n"
        "Редко до <b>30 минут</b> задержка банка. Потом не зачислилось - <b>PDF-квитанция</b> + номер заказа в поддержку.\n\n"
        "<b>• Оплата через LAVA (карта / СБП)</b>\n"
        "Статус обновляется автоматически. Если «Оплачен» не появился за 15 минут — в поддержку с номером заказа и квитанцией.\n\n"
        "<b>• Оплата через страницу с суммой вручную (Ckassa)</b>\n"
        "Только если в боте показана такая кнопка. Сверка по сумме и номеру заказа.\n\n"
        "<b>• «Фейковая» / непроверенная крипта</b>\n"
        "Если в кошельке «Unverified token» / «Unknown token» - такой перевод <b>не</b> принимаем; "
        "оформите оплату через счёт в боте или напишите в поддержку.\n\n"
        "<b>• Как пригласить друга</b>\n"
        "В <b>«Мой профиль»</b> (<code>/menu</code> → «Мой профиль») ваша ссылка; приглашённые закрепляются за вами.\n"
        f"Stars и Premium — по прайсу без скидок. "
        + (
            f"{esc(brand.VPN_PRODUCT_NAME)} — пробный период <b>3 дня</b> и бонус за друзей (см. раздел VPN). "
            if settings.ui_show_vpn
            else ""
        )
        + f"После первой <b>выданной</b> покупки друга — бонус <b>{rc}%</b> на ваши покупки в магазине "
        "(см. «Как работает приглашение» в профиле).\n\n"
        "<b>• Баланс и бонус на покупки</b>\n"
        "В меню: «С баланса» / «С баланса частично» при оформлении.\n\n"
        "<b>• Розыгрыши в каналах</b>\n"
        "Не ведём от имени бота; к админам того канала.\n\n"
        f"{refund_policy_blurb_html(settings).replace('<b>Возвраты', '<b>• Возвраты', 1)}\n\n"
        "<i>Юридика - кнопки в «Поддержка» (оферта, политика возвратов).</i>"
    )
