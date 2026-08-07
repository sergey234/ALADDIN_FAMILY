"""Тексты подключения AiMonkeyVPN: файл, QR, пошаговый гайд."""

from __future__ import annotations

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services.vpn_happ_constants import (
    HAPP_ANDROID_APP_NAME,
    HAPP_APP_NAME,
    HAPP_DEVELOPER,
    HAPP_IOS_APP_STORE_GLOBAL_URL,
    HAPP_IOS_APP_STORE_URL,
    HAPP_PLUS_IOS_APP_STORE_URL,
)
from bot.services.vpn_user_links import COPY_SUB_LINK_BTN, VPN_QR_CONNECT_BTN
from bot.services.vpn_screen_nav import HAPP_DOWNLOAD_BTN
from bot.util_html import esc

VPN_PROFILE_WIFI = "🇪🇺 Авто WiFi ⚡"
VPN_PROFILE_LTE = "🇪🇺 Авто 4G 📶"
VPN_PROFILE_BRIDGE = "🇷🇺 Вход RU"
VPN_PROFILE_XHTTP = "🇪🇺 Запасной (xhttp)"
UX_AUTO_WIFI_DISPLAY_NAME = VPN_PROFILE_WIFI
UX_AUTO_LTE_DISPLAY_NAME = VPN_PROFILE_LTE
UX_FALLBACK_XHTTP_DISPLAY_NAME = VPN_PROFILE_XHTTP


def vpn_happ_scam_warning_html() -> str:
    """Предупреждение о подделках «Happ VPN» + где брать ключ."""
    return (
        "<b>⚠️ О подделках в App Store и интернете</b>\n"
        "Встречаются приложения и сайты «<b>Happ VPN</b>» с <b>платной подпиской на VPN</b>. "
        "Это <b>не</b> официальный клиент "
        f"<b>{esc(HAPP_APP_NAME)}</b> ({esc(HAPP_DEVELOPER)}), иконка — чёрный квадрат с «H».\n"
        "Мы <b>не продаём</b> VPN через Happ. "
        "<b>Ключ выдаётся в этом боте</b> после оплаты тарифа."
    )


def vpn_happ_plus_app_store_link_html() -> str:
    return (
        f'<a href="{esc(HAPP_IOS_APP_STORE_GLOBAL_URL)}">'
        f"📲 Happ в глобальном App Store</a>"
    )


def vpn_happ_region_classic_steps_html() -> str:
    """Legacy short steps (не используется на экране «Скачать Happ»)."""
    app = esc(HAPP_APP_NAME)
    return (
        f"<b>📱 Скачать {app}</b>\n\n"
        "Если приложения нет в App Store вашего региона — воспользуйтесь "
        "инструкцией по смене региона.\n\n"
        "Временно смените <b>страну Apple ID</b>:\n\n"
        "1. <b>Настройки</b> → ваше имя (<b>Apple ID</b>) → "
        "<b>Контент и покупки</b> → <b>Просмотреть</b>\n"
        "2. <b>Страна/регион</b> → <b>Сменить…</b> → любой регион, "
        "например <b>Казахстан</b> или <b>США</b>\n"
        "3. Примите условия (для Happ можно «<b>без способа оплаты</b>»)\n"
        f"4. Откройте <b>App Store</b> (уже не из РФ) → <b>Happ+</b> или <b>{app}</b> — "
        "иконка <b>«H» на чёрном фоне</b> (см. картинку выше) → <b>Загрузить</b>\n"
        "5. <b>Готово:</b> регион РФ можно вернуть — <b>Happ останется</b> на телефоне"
    )


def vpn_happ_region_detailed_steps_html() -> str:
    """Канон экрана «Скачать Happ»: адрес + RU/EN подписи полей Apple ID."""
    app = esc(HAPP_APP_NAME)
    return (
        f"<b>📱 Скачать {app}</b>\n\n"
        "Нет в App Store вашего региона? Временно смените <b>страну Apple ID</b>:\n\n"
        "1️⃣ <b>Настройки</b> → ваше имя сверху (с фото) → "
        "<b>Контент и покупки</b> (<i>Content &amp; Purchases</i>) → "
        "<b>Просмотреть</b> (<i>View</i>)\n"
        "2️⃣ <b>Страна/регион</b> (<i>Country/Region</i>) → "
        "<b>Сменить…</b> (<i>Change…</i>) → <b>Казахстан</b> (или США)\n"
        "3️⃣ <b>Способ оплаты</b> (<i>Payment Method</i>) → "
        "<b>Нет</b> (<i>None</i>)\n"
        "4️⃣ <b>Адрес</b> (<i>Billing Address</i>) — можно любой пример:\n"
        "• <b>улица</b> (<i>Street</i>): <code>ул. Абая, д. 150</code>\n"
        "• <b>город</b> (<i>City/Town</i>): <b>Алматы</b> или <b>Астана</b>\n"
        "• <b>регион</b> (<i>Region</i>): Алматинская область · "
        "<b>индекс</b> (<i>Postcode</i>): <code>050000</code>\n"
        f"5️⃣ Откройте <b>App Store</b> → <b>Happ+</b> / <b>{app}</b> "
        "(иконка <b>«H» на чёрном</b>) → <b>Загрузить</b>\n"
        "6️⃣ Готово: страну РФ можно вернуть — <b>Happ останется</b> на телефоне"
    )


def vpn_happ_region_short_steps_html() -> str:
    """Канон: только подробный текст (RU/EN + адрес)."""
    return vpn_happ_region_detailed_steps_html()


def vpn_happ_region_video_caption_html() -> str:
    """Подпись к фото/видео = канон шагов (лимит Telegram ≤1024)."""
    return (
        f"{vpn_happ_region_detailed_steps_html()}\n\n"
        "<i>Удержите видео → «Сохранить» или перешлите себе в «Избранное».</i>"
    )


def vpn_happ_install_screen_html() -> str:
    """Экран «Скачать Happ» — только канонический текст."""
    return vpn_happ_region_detailed_steps_html()


def vpn_happ_appstore_region_guide_html() -> str:
    """Тот же канон + ссылка App Store + антискам."""
    return (
        f"{vpn_happ_region_detailed_steps_html()}\n\n"
        f"{vpn_happ_plus_app_store_link_html()}\n\n"
        f"{vpn_happ_scam_warning_html()}"
    )


def vpn_one_profile_stale_note_html() -> str:
    """Короткая пометка про устаревший список профилей."""
    bridge = esc(VPN_PROFILE_BRIDGE)
    return (
        f"<i>В Happ больше одного профиля? VPN выкл → удалите подписку → "
        f"добавьте ссылку заново → оставьте только <b>{bridge}</b>.</i>"
    )


# Совместимость: старое имя функции
vpn_one_profile_reimport_html = vpn_one_profile_stale_note_html


def vpn_happ_android_steps_html() -> str:
    """Android Happ — шаги из docs/VPN_HAPP_ANDROID_CONNECT_GUIDE.md (SSOT)."""
    from bot.services.vpn_happ_constants import HAPP_ANDROID_PLAY_URL

    bridge = esc(VPN_PROFILE_BRIDGE)
    play = esc(HAPP_ANDROID_PLAY_URL)
    return (
        f"<b>🤖 Android — {esc(HAPP_ANDROID_APP_NAME)}</b>\n\n"
        f"<b>1.</b> Google Play → установите <b>{esc(HAPP_ANDROID_APP_NAME)}</b> "
        f"(Flyfrog LLC).\n"
        f"<a href=\"{play}\">Открыть в Google Play</a>\n"
        "<i>Не ставьте «Happ VPN» с платной подпиской внутри — ключ только из бота.</i>\n\n"
        f"<b>2.</b> {esc(HAPP_ANDROID_APP_NAME)} → <b>Настройки</b> → <b>HWID</b> → "
        "<b>включить</b> (до импорта ссылки).\n\n"
        f"<b>3.</b> В боте: VPN → оплатите → через ~2 мин придёт <code>/sub/…</code> "
        f"(кнопка «{COPY_SUB_LINK_BTN}»). Ссылку никому не отправляйте.\n\n"
        "<b>4.</b> Happ → «<b>+</b>» → <b>Добавить подписку</b> → вставьте ссылку → "
        "<b>обновите</b> список 🔄.\n\n"
        f"<b>5.</b> Профиль <b>{bridge}</b> → включите VPN (разрешите Android, если спросит).\n\n"
        "<b>6.</b> Проверка: браузер → любой сайт или <code>ifconfig.me</code>. "
        "Включите <b>автообновление подписки</b> в Happ, если есть.\n\n"
        f"{vpn_one_profile_stale_note_html()}\n\n"
        "<i>Меню Routing не меняйте.</i>"
    )


def vpn_happ_android_wip_html() -> str:
    """Compat alias — канон: vpn_happ_android_steps_html."""
    return vpn_happ_android_steps_html()


def vpn_happ_hwid_prereq_html() -> str:
    """p3-bot-hwid-copy: включить HWID до импорта подписки."""
    return (
        "<b>⚠️ Сначала включите HWID</b>\n"
        f"{esc(HAPP_APP_NAME)} → <b>Настройки</b> → <b>HWID</b> → <b>включить</b>.\n"
        "<i>Без HWID подписка не загрузится — защита от копирования ссылки.</i>"
    )


def vpn_happ_plus_steps_html() -> str:
    """Пошаговое подключение Happ — один профиль 🇷🇺 Вход RU."""
    bridge = esc(VPN_PROFILE_BRIDGE)
    return (
        f"<b>📱 Скачать {esc(HAPP_APP_NAME)}</b>\n\n"
        "Если приложения нет в App Store вашего региона — откройте "
        f"кнопку «{esc(HAPP_DOWNLOAD_BTN)}» (видео + шаги).\n\n"
        f"<b>Подключение VPN ({esc(HAPP_APP_NAME)})</b>\n\n"
        f"<b>0.</b> Установите Happ.\n"
        f"<b>1.</b> {esc(HAPP_APP_NAME)} → <b>Настройки</b> → <b>HWID</b> → <b>включить</b> "
        "(до добавления подписки).\n"
        f"<b>2.</b> Оплатите тариф в боте → в чат придёт ссылка <code>/sub/…</code> "
        f"(кнопка «{COPY_SUB_LINK_BTN}»).\n"
        "<b>3.</b> Happ → «<b>+</b>» → <b>Добавить подписку</b> → вставьте ссылку → "
        "<b>обновите</b> список 🔄.\n"
        f"<b>4.</b> Выберите <b>{bridge}</b> → включите VPN (Wi‑Fi и 4G — один профиль).\n"
        "<b>5.</b> Проверка: Safari → <code>ifconfig.me</code> — страница должна открыться.\n"
        "<b>6.</b> Включите <b>автообновление подписки</b> в Happ (если есть).\n\n"
        f"{vpn_one_profile_stale_note_html()}\n\n"
        "<i>Меню Routing в Happ не трогайте. Ссылку никому не отправляйте.</i>\n\n"
        f"{vpn_happ_scam_warning_html()}"
    )


def vpn_payment_button_label() -> str:
    """Совместимость: CTA без статуса = тарифы (не «Оплата»)."""
    return vpn_tariffs_cta_label(active=False)


def vpn_tariffs_cta_label(*, active: bool) -> str:
    """
    Динамическая кнопка витрины VPN (ТЗ3):
    нет подписки → тарифы; есть → продлить. Callback тот же (legal gate → тарифы).
    """
    if active:
        return "💎 Продлить VPN"
    return "🌐 Тарифы VPN"


def vpn_sub_url_not_for_wg_html() -> str:
    """Устаревший блок — оставлен для совместимости импортов."""
    return ""


def vpn_what_is_what_html() -> str:
    """Простое объяснение «бот vs приложение»."""
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>Коротко, что где:</b>\n"
        f"• <b>{p} в Telegram</b> — оплата и выдача <b>личной ссылки</b> <code>/sub/…</code>.\n"
        f"• <b>{esc(HAPP_APP_NAME)}</b> (iPhone) / <b>{esc(HAPP_ANDROID_APP_NAME)}</b> (Android) — "
        "бесплатный клиент; вставляете ссылку из бота и подключаетесь.\n"
        f"<i>Ключ выдаётся здесь после оплаты — не покупайте VPN внутри Happ.</i>"
    )


def _vpn_client_apps_phrase() -> str:
    return f"<b>{esc(HAPP_APP_NAME)}</b> (iPhone / iPad) — официальный клиент для ссылки <code>/sub/…</code>"


def vpn_conf_qr_glossary_html() -> str:
    """QR подписки Happ — не путать с другими форматами."""
    return (
        f"📷 <b>QR</b> — та же ссылка <code>/sub/…</code> для <b>{esc(HAPP_APP_NAME)}</b>.\n"
        f"<i>Импортируйте в {esc(HAPP_APP_NAME)}, не в другие VPN-приложения.</i>"
    )


def vpn_after_payment_expect_html() -> str:
    """После оплаты: в чат приходит ссылка /sub/ для Happ."""
    return (
        "Оплатили → подождите <b>~2 мин</b> → в <b>этот чат</b> придёт:\n"
        f"• <b>ссылка</b> <code>https://…/sub/…</code> — для <b>{esc(HAPP_APP_NAME)}</b>;\n"
        "• <b>QR</b> — тот же ключ картинкой.\n\n"
        f"{vpn_happ_scam_warning_html()}"
    )


def vpn_what_are_keys_html() -> str:
    """Что за ссылку/QR, когда появляются и куда приходят."""
    return (
        "<b>Что это за ключ?</b>\n"
        "После оплаты личная ссылка <code>/sub/…</code> и QR отправляются <b>вам в этот чат</b>.\n"
        f"Вставляете в <b>{esc(HAPP_APP_NAME)}</b>."
    )


def vpn_checklist_short_html(settings: Settings) -> str:
    """Экран инструкции с пульта (между QR и «Проверить подключение»)."""
    return (
        "<b>📖 Инструкция по подключению</b>\n\n"
        f"{vpn_checklist_body_html(settings)}"
    )


def vpn_checklist_body_html(settings: Settings) -> str:
    p = esc(VPN_PRODUCT_NAME)
    pay = esc(vpn_tariffs_cta_label(active=False))
    bridge = esc(VPN_PROFILE_BRIDGE)
    return (
        f"☐ <b>1. Тариф</b> ({pay})\n"
        f"🌐 {p} → тариф → подождите <b>2–5 мин</b>.\n\n"
        "☐ <b>2. Happ</b>\n"
        f"• <b>iPhone:</b> App Store / «📲 Happ — 🎬 видео» в <b>Помощь</b>.\n"
        f"• <b>Android:</b> Google Play → <b>{esc(HAPP_ANDROID_APP_NAME)}</b> "
        "(в боте: OS → Android — пошаговая инструкция).\n\n"
        "☐ <b>3. HWID</b>\n"
        "Happ → Настройки → HWID → <b>вкл</b> (до импорта ссылки).\n\n"
        "☐ <b>4. Ссылка в Happ</b>\n"
        f"«{COPY_SUB_LINK_BTN}» / «{VPN_QR_CONNECT_BTN}» → Happ → «+» → подписка → обновить 🔄.\n\n"
        f"☐ <b>5. Профиль {bridge}</b>\n"
        "Включите VPN (Wi‑Fi и 4G — один профиль).\n\n"
        "☐ <b>6. Проверка</b>\n"
        "Браузер / Safari → <code>ifconfig.me</code> — страница открывается.\n\n"
        f"{vpn_one_profile_stale_note_html()}"
    )


def vpn_checklist_html(settings: Settings) -> str:
    p = esc(VPN_PRODUCT_NAME)
    site = _site_link_html(settings)
    return (
        f"<b>🚀 Как подключить {p}</b>\n\n"
        f"{vpn_what_is_what_html()}\n\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "<b>📋 Чеклист — отмечайте по порядку</b>\n\n"
        f"{vpn_checklist_body_html(settings)}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        f"{vpn_happ_plus_steps_html()}"
        f"{site}"
    )


def vpn_file_import_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>📥 Файл настроек — по шагам</b>\n\n"
        f"{vpn_what_is_what_html()}\n\n"
        f"{vpn_what_are_keys_html()}\n\n"
        "<b>Когда что делать</b>\n\n"
        f"<b>1.</b> <b>После оплаты</b> (~2 мин) файл придёт в чат или нажмите «📥 WireGuard — файл» в {p}.\n"
        "<b>2.</b> <b>Когда в чат пришёл документ</b> — это ваш файл <code>.conf</code>: "
        "личный ключ VPN, <b>не программа</b> и не вирус.\n"
        "<b>3.</b> <b>Сохранить в телефон</b> (если WireGuard просит файл из памяти):\n"
        "   • iPhone: нажмите на документ → <b>Поделиться</b> → <b>Сохранить в «Файлы»</b>\n"
        "   • Android: <b>Скачать</b> или «Открыть в…» → WireGuard\n"
        "   <i>Часто можно сразу «Открыть в WireGuard» — без отдельного сохранения.</i>\n"
        "<b>4.</b> <b>Если WireGuard ещё нет</b> — установите из App Store / Google Play.\n"
        "<b>5.</b> <b>Импорт в WireGuard:</b> откройте WireGuard → кнопка «<b>+</b>» "
        "(добавить) → <b>Импорт из файла</b> / «Создать из файла» → выберите ваш <code>.conf</code>.\n"
        "<b>6.</b> <b>Удалите старый туннель</b>, если он уже был — иначе останется "
        "устаревший Endpoint <code>:51820</code> или <code>::/0</code>.\n"
        "<b>7.</b> <b>Включите VPN</b> — переключатель станет синим/зелёным.\n\n"
        "<i>Сервер WireGuard: UDP <b>443</b>. На 4G может не работать у части операторов.</i>"
    )


def vpn_file_document_caption_html(*, conf_validation: str = "") -> str:
    extra = f"\n\n{conf_validation}" if conf_validation.strip() else ""
    return (
        "<b>📥 Ваш ключ WireGuard</b>\n"
        "Файл <code>.conf</code>: приватный ключ и настройки.\n"
        "WireGuard → «<b>+</b>» → импорт из файла.\n"
        "<i>Удалите старый туннель перед импортом. Endpoint должен быть "
        "<code>:443</code>, без <code>::/0</code>.</i>"
        f"{extra}"
    )


def vpn_qr_import_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"<b>📷 QR — по шагам</b>\n\n"
        f"{vpn_what_is_what_html()}\n\n"
        f"{vpn_what_are_keys_html()}\n\n"
        "<b>Когда что делать</b>\n\n"
        f"<b>1.</b> <b>После оплаты</b> (~2 мин) QR придёт в чат или нажмите «📷 WireGuard — QR» в {p}.\n"
        "<b>2.</b> <b>Когда в чат пришла картинка</b> — это тот же ключ WireGuard, "
        "только в виде QR. Не закрывайте чат, оставьте её на экране.\n"
        "<b>3.</b> <b>Сначала установите WireGuard</b> (App Store / Google Play), если ещё нет.\n"
        "<b>4.</b> <b>Откройте WireGuard</b> → нажмите «<b>+</b>» "
        "(плюс внизу или «Добавить туннель»).\n"
        "<b>5.</b> Выберите «<b>Сканировать QR-код</b>» → разрешите камеру → "
        "<b>наведите на картинку в Telegram</b> (лучше без скриншота).\n"
        "<b>6.</b> Нажмите «Создать» / «Добавить» → <b>включите переключатель</b> VPN.\n\n"
        "<i>QR не читается? Запросите «📥 Файл» — тот же VPN, другой способ.</i>"
    )


def vpn_qr_photo_caption_html(*, conf_validation: str = "") -> str:
    extra = f"\n\n{conf_validation}" if conf_validation.strip() else ""
    return (
        "<b>📷 Ваш ключ WireGuard (QR)</b>\n"
        "WireGuard → «<b>+</b>» → «<b>Сканировать QR-код</b>».\n"
        "<i>Удалите старый туннель. Endpoint <code>:443</code>, без <code>::/0</code>.</i>"
        f"{extra}"
    )


def vpn_beginner_guide_html(settings: Settings) -> str:
    return vpn_checklist_html(settings)


def _esc_alt_connect() -> str:
    return "📱 Happ"


def vpn_main_connect_steps_html() -> str:
    return (
        "<b>📥 Шаг 2 — получить ключ</b> (после оплаты)\n"
        f"{vpn_after_payment_expect_html()}\n"
        "<i>Дальше — «📱 Happ» в меню: установка и пошаговое подключение.</i>"
    )


def vpn_xray_clients_html() -> str:
    return (
        f"<i>Ссылка <code>/sub/…</code> — для <b>{esc(HAPP_APP_NAME)}</b> (iPhone) "
        f"и <b>{esc(HAPP_ANDROID_APP_NAME)}</b> (Android, Google Play). "
        "Кнопки «📱 Happ» / OS → Android.</i>"
    )


vpn_happ_apps_html = vpn_xray_clients_html


def vpn_connect_methods_table_html() -> str:
    return vpn_happ_plus_steps_html()


vpn_wg_vs_backup_table_html = vpn_connect_methods_table_html
vpn_backup_apps_one_method_html = vpn_xray_clients_html


def vpn_connect_choice_short_html() -> str:
    return (
        f"\n\n<b>Подключение:</b> «📱 Happ» + «{COPY_SUB_LINK_BTN}» / «{VPN_QR_CONNECT_BTN}».\n"
        f"{vpn_happ_scam_warning_html()}"
    )


vpn_backup_link_short_html = vpn_connect_choice_short_html


def vpn_xray_ios_steps_html() -> str:
    return vpn_happ_plus_steps_html()


def vpn_xray_android_steps_html() -> str:
    return vpn_happ_android_steps_html()


def vpn_onexray_steps_html() -> str:
    return vpn_happ_plus_steps_html()


vpn_hitwave_steps_html = vpn_onexray_steps_html


def vpn_happ_legacy_steps_html() -> str:
    return vpn_happ_plus_steps_html()


def vpn_appstore_blocked_html() -> str:
    return vpn_happ_appstore_region_guide_html()


def vpn_post_payment_three_steps_html() -> str:
    """После оплаты — коротко."""
    bridge = esc(VPN_PROFILE_BRIDGE)
    return (
        "<b>✅ VPN готов — что дальше</b>\n\n"
        f"<b>1.</b> {esc(HAPP_APP_NAME)} с HWID (см. «📱 Happ» или <b>Помощь</b>).\n"
        "<b>2.</b> Вставьте <b>ссылку выше</b> в Happ → обновите подписку 🔄.\n"
        f"<b>3.</b> Профиль <b>{bridge}</b> → VPN вкл.\n\n"
        f"{vpn_one_profile_stale_note_html()}"
    )


def vpn_happ_auto_update_html() -> str:
    bridge = esc(VPN_PROFILE_BRIDGE)
    return (
        f"<b>💡 Автообновление в {esc(HAPP_APP_NAME)}</b>\n\n"
        "Включите в настройках Happ — сервер сам подтянет новые параметры.\n"
        f"Профиль: <b>{bridge}</b>."
    )


def vpn_xray_next_step_html() -> str:
    return (
        f"<b>Ссылка VPN</b>\n"
        f"{esc(HAPP_APP_NAME)} → «+» → Добавить подписку → вставьте ссылку → Connect."
    )


vpn_happ_next_step_html = vpn_xray_next_step_html

vpn_onexray_auto_update_html = vpn_happ_auto_update_html
vpn_hitwave_auto_update_html = vpn_happ_auto_update_html


def vpn_client_import_matrix_html() -> str:
    return vpn_happ_plus_steps_html()


def _site_link_html(settings: Settings) -> str:
    u = (settings.vpn_instructions_url or "").strip()
    if not u:
        u = (settings.vpn_marketing_landing_url or "").strip()
    if not u:
        return ""
    return f'\n\n<a href="{esc(u)}">🌍 Полная инструкция на сайте</a>.'


def vpn_wireguard_next_step_html() -> str:
    """После выдачи .conf — legacy API, не в UX бота."""
    return (
        "<b>WireGuard — подключение</b>\n"
        f"{vpn_wireguard_import_rules_html()}"
    )


def vpn_wireguard_import_rules_html() -> str:
    """Обязательный чеклист: новый туннель, UI WireGuard, iOS, проверка."""
    return (
        "<b>1.</b> <b>Удалите</b> старый туннель в WireGuard "
        "(редактирование <b>не</b> обновляет Endpoint и Allowed IPs).\n"
        "<b>2.</b> Импортируйте <b>новый</b> файл или QR из этого чата.\n"
        "<b>3.</b> В WireGuard откройте туннель → проверьте:\n"
        "   • <b>Endpoint</b> → <code>185.225.233.150:443</code> "
        "(не <code>:51820</code>)\n"
        "   • <b>Allowed IPs</b> → только <code>0.0.0.0/0</code> "
        "(без <code>::/0</code>)\n"
        "   • <b>DNS</b> → <code>10.8.0.1</code>\n"
        "<b>4.</b> iPhone: <b>Настройки → Apple ID → iCloud → Private Relay — Выкл</b>.\n"
        "<b>5.</b> Wi‑Fi → ваша сеть → <b>Ограничить отслеживание IP — Выкл</b> "
        "(на 4G пункт не нужен).\n"
        "<b>6.</b> Connect → Safari: <code>2ip.ru</code> или <code>http://188.40.167.82</code>.\n"
        "<b>7.</b> В WireGuard <b>Transfer</b> должен вырасти <b>&gt; 100 KB</b>.\n\n"
        "<i>UDP порт <b>443</b> (не TCP). Если не подключается — напишите в поддержку.</i>"
    )


def vpn_sub_url_block_html(subscription_url: str, *, ux_auto: bool = False) -> str:
    """Блок ссылки /sub/… — в начале экрана, удобно копировать."""
    url = (subscription_url or "").strip()
    if not url:
        return ""
    lines = [
        "<b>🔗 Ваша ссылка VPN</b> (Happ → Добавить подписку):",
        f"<code>{esc(url)}</code>",
        f"<i>Один тап: кнопка «{COPY_SUB_LINK_BTN}» ниже — URL целиком.</i>",
        "<i>Или удержите строку выше → «Копировать».</i>",
        "",
        vpn_one_profile_stale_note_html(),
    ]
    return "\n".join(lines)


def vpn_xray_sub_explainer_html(
    *,
    show_url: bool = False,
    subscription_url: str = "",
    mirror_url: str = "",
    ux_auto: bool = False,
) -> str:
    """Legacy: длинная карточка ссылки. UX: кабинет → копировать / QR."""
    _ = mirror_url
    url_block = ""
    if show_url and (subscription_url or "").strip():
        url_block = vpn_sub_url_block_html(subscription_url, ux_auto=ux_auto) + "\n\n"
    return (
        f"<b>🔗 Ссылка VPN</b>\n\n"
        f"{url_block}"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"{vpn_happ_plus_steps_html()}\n\n"
        "<i>Ссылку никому не отправляйте.</i>\n"
        "<i>После окончания срока удалите подписку в Happ.</i>"
    )


vpn_backup_link_explainer_html = vpn_xray_sub_explainer_html


def vpn_extra_menu_html() -> str:
    """Настройки и доп. действия (не засоряют карточку управления)."""
    return (
        "<b>⚙️ Настройки</b>\n\n"
        "Дополнительно: приложение, проверка связи, скорость, локации, помощь и документы.\n"
        "Пошаговое подключение — в «📖 Инструкция» и «🎬 Скачать Happ»."
    )


def vpn_happ_tunnel_report_html() -> str:
    """Как прислать лог из Happ в поддержку."""
    bridge = esc(VPN_PROFILE_BRIDGE)
    return (
        "<b>📋 Как прислать лог из Happ</b>\n\n"
        "Если VPN не работает — напишите в поддержку:\n"
        f"1. <b>Профиль</b> — {bridge}\n"
        "2. <b>Сеть</b> — Wi‑Fi или 4G (оператор)\n"
        "3. <b>Время</b> сбоя\n"
        f"4. <b>HWID</b> включён? ({esc(HAPP_APP_NAME)} → Настройки)\n"
        "5. <b>Логи</b> Happ (tunnel.log) — последние строки\n"
        "6. Скрин: профиль + переключатель VPN\n\n"
        "<b>Симптомы:</b> не подключается / сайты не открываются / только 4G или только Wi‑Fi."
    )


def vpn_openvpn_fallback_html() -> str:
    return (
        "<b>🧱 OpenVPN (запасной)</b>\n\n"
        "Только если Happ не работает. На 4G часто хуже, чем Xray.\n"
        "Запросите файл в поддержке или через админ-выдачу.\n"
        "<i>Основной путь — Happ + ссылка подписки.</i>"
    )


def vpn_friend_link_blurb_html() -> str:
    p = esc(VPN_PRODUCT_NAME)
    return (
        f"\n\n<b>👥 Приглашение в бот ({p})</b>\n"
        "Та же ссылка, что в «Мой профиль» — <b>не</b> для VPN-подключения. "
        "Скидка другу на первую выдачу; если он впервые получит VPN — бонусные дни вам и ему.\n"
        f"<i>Реферальная ссылка — в «Пригласить друга» / «Профиль», не ключ VPN <code>/sub/…</code>.</i>"
    )


def vpn_happ_stub_troubleshoot_html() -> str:
    """Подсказка, если Happ показывает заглушки вместо 🇷🇺 Вход RU."""
    return (
        "<b>⚠️ Если в Happ не тот профиль</b>\n\n"
        "<b>Нормально:</b> профиль <b>🇷🇺 Вход RU</b>, тип <b>Vless-TCP Reality JSON</b>, пинг к серверу.\n\n"
        "<b>Не VPN (заглушка):</b> профили <b>Vless-TCP</b>, <b>none</b>, адрес <code>127.0.0.1</code> — "
        "в названии может быть <b>Лимит-1-устройство</b> или <b>Только-Happ-с-HWID</b>.\n\n"
        "<b>Что делать:</b>\n"
        f"1. Только <b>{esc(HAPP_APP_NAME)}</b> → Подписка → вставить ссылку <code>/sub/…</code>\n"
        "2. HWID в настройках Happ должен быть <b>включён</b>\n"
        "3. Одна ссылка — свой телефон; если телефон уже использовал другую подписку — напишите в поддержку\n"
        "4. Обновите подписку в Happ (потяните вниз / Refresh)\n\n"
        "<i>Заглушка @127.0.0.1 не пингуется — это защита, не сервер VPN.</i>"
    )


def vpn_friend_gift_sub_instructions_html(subscription_url: str) -> str:
    """Текст для друга с подарочной ссылкой /sub/ (beta-слоты)."""
    url = esc((subscription_url or "").strip())
    return (
        "<b>🎁 VPN на год — ссылка для Happ</b>\n\n"
        f"<code>{url}</code>\n\n"
        f"1. Установите <b>{esc(HAPP_APP_NAME)}</b>\n"
        "2. Настройки → <b>HWID</b> — включить\n"
        "3. Подписка → «+» → вставить ссылку целиком\n"
        "4. Должен появиться <b>🇷🇺 Вход RU</b> (Vless-TCP Reality JSON)\n"
        "5. Включите VPN, профиль <b>Мобильный мост</b>\n\n"
        f"{vpn_happ_stub_troubleshoot_html()}"
    )


def vpn_trial_offer_html(settings=None) -> str:
    from bot.services.vpn_trial_copy import vpn_trial_period_phrase, vpn_trial_period_title

    p = esc(VPN_PRODUCT_NAME)
    if settings is None:
        period = "3 дня"
        title = "Пробный период на 3 дня"
    else:
        period = vpn_trial_period_phrase(settings)
        title = vpn_trial_period_title(settings)
    return (
        f"<b>🎁 Бесплатный пробный период — {esc(period)}</b>\n\n"
        f"<b>{esc(title)} — {p}</b>\n\n"
        "1. Нажмите «Активировать».\n"
        "2. Через пару минут придёт ссылка в чат.\n"
        "3. Откройте её в приложении Happ на своём телефоне.\n"
        "4. Включите VPN и пользуйтесь.\n"
        "5. Чтобы не отключилось — до конца срока выберите тариф и оплатите.\n\n"
        "<i>Один раз на аккаунт Telegram. Ссылку другу не отправляйте — "
        "это ваша личная подписка на одном телефоне.</i>"
    )


def vpn_trial_started_html(settings=None) -> str:
    from bot.services.vpn_trial_copy import vpn_trial_period_title
    from bot.services.vpn_subscription_notify_ux import referral_bonus_days

    title = vpn_trial_period_title(settings) if settings else "Пробный период на 3 дня"
    days = referral_bonus_days(settings)
    ref = f"или пригласите друга (+{days} дн.)" if days > 0 else ""
    return (
        f"<b>🎁 {esc(title)} активируется</b>\n\n"
        "1. Запрос принят.\n"
        "2. Ссылка придёт в этот чат через <b>2–5 минут</b>.\n"
        "3. Откройте её в Happ на своём телефоне.\n"
        "4. Включите VPN и пользуйтесь.\n"
        f"5. До конца срока оформите тариф{(' ' + ref) if ref else ''}, чтобы доступ не пропал.\n\n"
        "<i>Напомним за ~1 день и за ~6 часов до окончания пробного периода.</i>"
    )


def vpn_trial_after_delivery_html(settings=None) -> str:
    from bot.services.vpn_trial_copy import vpn_trial_period_phrase, vpn_trial_period_title

    period = vpn_trial_period_phrase(settings) if settings else "3 дня"
    title = vpn_trial_period_title(settings) if settings else "Пробный период на 3 дня"
    return (
        f"<b>🎁 {esc(title)} — {esc(VPN_PRODUCT_NAME)}</b>\n\n"
        f"1. Пробный период — <b>{esc(period)}</b>.\n"
        "2. Ссылка только для вашего телефона — другу не отправляйте.\n"
        "3. В Happ вставьте ссылку и включите VPN.\n"
        "4. Чтобы не отключилось — оплатите тариф до конца пробного периода."
    )


def vpn_trial_device_limit_html() -> str:
    return (
        "<b>Лимит устройств</b>\n\n"
        "Подписка привязана к телефону (HWID). "
        "Пробный период — до <b>2 устройств</b> на время теста; "
        "подарочные ссылки друзьям — тоже до <b>2 телефонов</b> на одну ссылку.\n"
        "Один и тот же телефон нельзя использовать для двух разных ссылок /sub/.\n"
        "Сброс привязки — через поддержку."
    )
