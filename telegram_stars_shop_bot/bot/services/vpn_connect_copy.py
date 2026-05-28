"""Тексты подключения AiMonkeyVPN: файл, QR, пошаговый гайд."""

from __future__ import annotations

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.util_html import esc


def vpn_payment_button_label() -> str:
    return "🟢 Оплата"


def vpn_what_is_what_html() -> str:
    """Простое объяснение «бот vs WireGuard» для обычного пользователя."""
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>Коротко, что где:</b>\n"
        f"• <b>{p} в Telegram</b> — оплата и <b>настройки</b> (файл/QR). Это «ключ».\n"
        "• <b>WireGuard</b> и другие из списка — бесплатное <b>приложение</b>; "
        "<b>включаете и выключаете</b> VPN.\n"
        f"<i>Итого: ключ выдаёт {p}, дверь открывает WireGuard.</i>"
    )


def _vpn_client_apps_phrase() -> str:
    return (
        "<b>WireGuard</b>, <b>Happ</b> / <b>Happ Plus</b>, <b>OpenVPN Connect</b> "
        "и другие — в зависимости от того, какое приложение вы установили"
    )


def vpn_conf_qr_glossary_html() -> str:
    """Краткая расшифровка .conf и QR простым языком."""
    apps = _vpn_client_apps_phrase()
    return (
        "📥 <b>Файл <code>.conf</code></b> — маленький документ с <b>настройками вашего VPN</b> "
        "(личный ключ, адрес сервера).\n"
        f"<b>Открывается</b> в приложении на устройстве: {apps}.\n"
        "📷 <b>QR</b> — <b>та же настройка</b>, но картинкой: наведите камеру того же приложения "
        f"({apps}) на квадратный код в чате.\n"
        "<i>Файл и QR — один VPN. Хватит любого одного способа.</i>"
    )


def vpn_after_payment_expect_html() -> str:
    """Одна формулировка после оплаты: куда, когда, что такое файл и QR."""
    return (
        "Оплатили → подождите <b>~2 мин</b> → в <b>этот чат</b> с ботом придут "
        "<b>документ <code>.conf</code></b> и <b>картинка QR</b>.\n\n"
        f"{vpn_conf_qr_glossary_html()}"
    )


def vpn_what_are_keys_html() -> str:
    """Что за файл/QR, когда появляются и куда приходят."""
    return (
        "<b>Что это за «файлы»?</b>\n"
        "После оплаты личный ключ отправляется <b>вам в этот чат</b>.\n\n"
        f"{vpn_conf_qr_glossary_html()}"
    )


def vpn_checklist_short_html(settings: Settings) -> str:
    """Экран чеклиста с пульта (между QR и «Проверить VPN»)."""
    return (
        "<b>📋 Чеклист правильного подключения VPN</b>\n\n"
        f"{vpn_checklist_body_html(settings)}"
    )


def vpn_checklist_body_html(settings: Settings) -> str:
    p = esc(VPN_PRODUCT_NAME)
    pay = esc(vpn_payment_button_label())
    return (
        f"☐ <b>Оплата</b> ({pay})\n"
        f"Меню → 🌐 {p} → тариф. Подождите <b>от 2 до 5 мин</b>.\n\n"
        "☐ <b>📥 или 📷 в боте</b>\n"
        "Ожидание файла или QR в чате.\n\n"
        "☐ <b>WireGuard или другие приложения из списка — установлены</b>\n"
        "App Store / Google Play / wireguard.com\n\n"
        "☐ <b>Импорт выполнен</b>\n"
        "«<b>+</b>» → файл или скан QR <b>из этого чата</b>.\n\n"
        "☐ <b>VPN включён</b>\n"
        "Переключатель в приложении — вверху экрана 🔒 VPN."
    )


def vpn_checklist_html(settings: Settings) -> str:
    p = esc(VPN_PRODUCT_NAME)
    site = _site_link_html(settings)
    return (
        f"<b>🚀 Как подключить {p}</b>\n\n"
        f"{vpn_what_is_what_html()}\n\n"
        f"{vpn_what_are_keys_html()}\n\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "<b>📋 Чеклист — отмечайте по порядку</b>\n\n"
        f"{vpn_checklist_body_html(settings)}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        f"<b>WireGuard не подошёл?</b>\n{vpn_wg_vs_backup_table_html()}\n\n"
        f"<b>Не получилось?</b> «{_esc_alt_connect()}» → «📋 Запасная ссылка»."
        f"{site}"
    )


def vpn_file_import_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>📥 Файл настроек — по шагам</b>\n\n"
        f"{vpn_what_is_what_html()}\n\n"
        f"{vpn_what_are_keys_html()}\n\n"
        "<b>Когда что делать</b>\n\n"
        f"<b>1.</b> <b>После оплаты</b> (~2 мин) нажмите «📥 Файл для подключения» в {p}.\n"
        "<b>2.</b> <b>Когда в чат пришёл документ</b> — это ваш файл <code>.conf</code>: "
        "личный ключ VPN, <b>не программа</b> и не вирус.\n"
        "<b>3.</b> <b>Сохранить в телефон</b> (если WireGuard просит файл из памяти):\n"
        "   • iPhone: нажмите на документ → <b>Поделиться</b> → <b>Сохранить в «Файлы»</b>\n"
        "   • Android: <b>Скачать</b> или «Открыть в…» → WireGuard\n"
        "   <i>Часто можно сразу «Открыть в WireGuard» — без отдельного сохранения.</i>\n"
        "<b>4.</b> <b>Если WireGuard ещё нет</b> — установите из App Store / Google Play.\n"
        "<b>5.</b> <b>Импорт в WireGuard:</b> откройте WireGuard → кнопка «<b>+</b>» "
        "(добавить) → <b>Импорт из файла</b> / «Создать из файла» → выберите ваш <code>.conf</code>.\n"
        "<b>6.</b> <b>Включите VPN</b> — переключатель станет синим/зелёным.\n\n"
        "<i>Проще с телефона? Попробуйте «📷 QR» — без сохранения файла.</i>"
    )


def vpn_file_document_caption_html() -> str:
    return (
        "<b>📥 Ваш ключ VPN</b>\n"
        "Файл <code>.conf</code>: ваш приватный ключ и настройки. "
        "Присылаются <b>в этот чат после оплаты</b>!\n"
        "WireGuard → «<b>+</b>» → импорт из файла.\n"
        "<i>Тот же ключ можно получить как 📷 QR в меню.</i>"
    )


def vpn_qr_import_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>📷 QR — по шагам</b>\n\n"
        f"{vpn_what_is_what_html()}\n\n"
        f"{vpn_what_are_keys_html()}\n\n"
        "<b>Когда что делать</b>\n\n"
        f"<b>1.</b> <b>После оплаты</b> (~2 мин) нажмите «📷 QR для подключения» в {p}.\n"
        "<b>2.</b> <b>Когда в чат пришла картинка</b> — это тот же ключ VPN, "
        "только в виде QR. Не закрывайте чат, оставьте её на экране.\n"
        "<b>3.</b> <b>Сначала установите WireGuard</b> (App Store / Google Play), если ещё нет.\n"
        "<b>4.</b> <b>Откройте WireGuard</b> → нажмите «<b>+</b>» "
        "(плюс внизу или «Добавить туннель»).\n"
        "<b>5.</b> Выберите «<b>Сканировать QR-код</b>» → разрешите камеру → "
        "<b>наведите на картинку в Telegram</b> (лучше без скриншота).\n"
        "<b>6.</b> Нажмите «Создать» / «Добавить» → <b>включите переключатель</b> VPN.\n\n"
        "<i>QR не читается? Запросите «📥 Файл» — тот же VPN, другой способ.</i>"
    )


def vpn_qr_photo_caption_html() -> str:
    return (
        "<b>📷 Ваш ключ VPN (QR)</b>\n"
        "На картинке — <b>тот же текст</b>, что в файле <code>.conf</code>. "
        "Отправляется <b>в этот чат автоматически после оплаты</b>.\n"
        "WireGuard → «<b>+</b>» → «<b>Сканировать QR-код</b>» → наведите камеру сюда.\n"
        "<i>Шаги — в сообщении выше.</i>"
    )


def vpn_beginner_guide_html(settings: Settings) -> str:
    return vpn_checklist_html(settings)


def _esc_alt_connect() -> str:
    return "🔀 Другой способ подключения"


def _site_link_html(settings: Settings) -> str:
    u = (settings.vpn_instructions_url or "").strip()
    if not u:
        u = (settings.vpn_marketing_landing_url or "").strip()
    if not u:
        return ""
    return f'\n\n<a href="{esc(u)}">🌍 Полная инструкция на сайте</a>.'


def vpn_main_connect_steps_html() -> str:
    return (
        "<b>📥 Шаг 2 — получить ключ</b> (после оплаты)\n"
        f"{vpn_after_payment_expect_html()}\n"
        "<i>Дальше — импорт и включение VPN в приложении из списка выше, не в боте.</i>"
    )


def vpn_backup_apps_one_method_html() -> str:
    """Happ — рекомендуемый клиент запасного способа; остальные — альтернативы."""
    return (
        "<i>Запасной способ — <b>один</b> (одна ссылка из бота). Рекомендуем приложение "
        "<b>Happ</b> (iPhone и Android). Альтернативы: Streisand, V2Box, v2rayNG — "
        "не другие VPN, а другие программы для той же ссылки.</i>"
    )


def vpn_wg_vs_backup_table_html() -> str:
    """Сравнение основного и запасного способа — одна карточка для пользователя."""
    return (
        "<b>Два способа подключиться — что выбрать?</b>\n\n"
        "<b>📥 Способ 1 — WireGuard</b> <i>(рекомендуем начать с него)</i>\n"
        "• <b>Что получите:</b> файл <code>.conf</code> или картинку 📷 QR — "
        "это <b>ключ доступа</b>, как пароль к вашему VPN.\n"
        "• <b>Куда идти:</b> в бесплатное приложение <b>WireGuard</b> "
        "(скачать в App Store или Google Play).\n"
        "• <b>Когда брать:</b> сразу после оплаты — так подключаются почти все. "
        "Сначала 📥 файл или 📷 QR, потом включить VPN в WireGuard.\n\n"
        "<b>📋 Способ 2 — Happ Plus</b> <i>(если WireGuard не помог)</i>\n"
        "• <b>Что получите:</b> одну ссылку <code>https://…/sub/…</code> — "
        "те же оплаченные дни, вход через <b>Happ Plus</b> (не WireGuard).\n"
        "• <b>Куда идти:</b> установите <b>Happ Plus</b> из <b>App Store</b> или <b>Google Play</b>.\n"
        "   <i>Не подошёл Happ Plus?</i> Та же ссылка в Happ, Streisand или V2Box / v2rayNG.\n"
        f"{vpn_backup_apps_one_method_html()}\n"
        "• <b>Когда брать:</b> если WireGuard не подключается, "
        "часто обрывается или интернет с VPN «не едет»."
    )


def vpn_backup_link_short_html() -> str:
    """Короткий блок на главном экране VPN (уровень 3)."""
    return (
        "\n\n<b>Если WireGuard не подошёл:</b> «🔀 Запасные способы» → Happ или OpenVPN. "
        "Подробные шаги — в «📖 Помощь»."
    )


def vpn_wireguard_next_step_html() -> str:
    """Короткое сообщение сразу после выдачи .conf (не полный чеклист)."""
    return (
        "<b>Следующий шаг</b>\n"
        "Откройте <b>WireGuard</b> или другое приложение на выбор → импорт → "
        "включите VPN.\n"
        "<i>Подробно — «📖 Помощь» в меню AiMonkeyVPN.</i>"
    )


def vpn_backup_link_explainer_html(*, show_url: bool = False, subscription_url: str = "") -> str:
    """
    Запасная ссылка: не WireGuard, протокол Xray/VLESS (подписка в стороннем приложении).
  """
    url_part = ""
    if show_url and (subscription_url or "").strip():
        url_part = (
            f"\n\n<b>Ваша ссылка</b> (скопируйте целиком, ничего не добавляйте):\n"
            f"<code>{esc(subscription_url.strip())}</code>\n"
        )
    return (
        "<b>📋 Запасная ссылка — пошагово</b>\n\n"
        f"{vpn_wg_vs_backup_table_html()}\n\n"
        f"{vpn_backup_apps_one_method_html()}\n\n"
        "<b>Что сделать:</b>\n"
        "1) Установите <b>Happ</b> (App Store / Google Play).\n"
        "2) Нажмите «<b>📋 Скопировать запасную</b>».\n"
        "3) В <b>Happ</b>: «Добавить» / «Подписка» / «Import» → вставьте ссылку.\n"
        "4) Включите VPN в <b>Happ</b>.\n\n"
        "<i>Оплата та же. Ссылку никому не отправляйте.</i>\n"
        "<i>После окончания срока ссылка не обновляется — удалите профиль в <b>Happ</b>.</i>"
        f"{url_part}"
    )


def vpn_friend_link_blurb_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"\n\n<b>👥 Приглашение в бот ({p})</b>\n"
        "Та же ссылка, что в «Мой профиль» — <b>не</b> для VPN-подключения. "
        "Скидка другу на первую выдачу; если он впервые получит VPN — бонусные дни вам и ему.\n"
        "<i>Скопируйте кнопкой «👥 Скопировать приглашение» ниже. "
        "Не путать с запасной ссылкой подписки.</i>"
    )
