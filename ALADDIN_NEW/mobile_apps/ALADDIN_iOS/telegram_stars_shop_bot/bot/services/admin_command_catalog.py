"""Каталог админ-команд: разделы + расшифровка простым языком."""

from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass(frozen=True)
class AdminCmd:
    """Одна команда для справки."""

    usage: str  # что прописать, напр. /admin_vpn_status 123
    title: str  # коротко «что это»
    how: str  # простым языком «зачем / как»


@dataclass(frozen=True)
class AdminCmdSection:
    key: str
    title: str
    blurb: str
    commands: tuple[AdminCmd, ...]


ADMIN_HELP_SECTIONS: tuple[AdminCmdSection, ...] = (
    AdminCmdSection(
        key="main",
        title="Главное",
        blurb="С чего начать смену.",
        commands=(
            AdminCmd("/admin", "Дашборд", "Выручка, заказы, VPN health, кнопки отчётов."),
            AdminCmd("/admin_help", "Эта справка", "Все команды по разделам — что писать и зачем."),
            AdminCmd("/admqueue", "Очередь внимания", "Заказы, где нужна рука: сбой выдачи или долго «в работе»."),
            AdminCmd("/admdeliveries", "Последние выдачи", "Что уже выдали покупателям."),
        ),
    ),
    AdminCmdSection(
        key="orders",
        title="Заказы",
        blurb="Карточки заказов приходят в личку бота всем админам.",
        commands=(
            AdminCmd(
                "кнопки на алерте",
                "Оплачен / В работе / Выдан",
                "Жмите на карточке заказа в боте — статус меняется у всех одинаково.",
            ),
            AdminCmd(
                "/admin_order 12345",
                "Карточка заказа",
                "Открыть заказ по номеру из меню Продажи → Найти заказ.",
            ),
            AdminCmd(
                "/admin_user 123456789",
                "Карточка пользователя",
                "TG id, @username, #заказ, ник сайта, ref. Меню: Пользователи.",
            ),
            AdminCmd(
                "/admin_find_nick nick",
                "Поиск по нику сайта",
                "Аккаунт web + заказы. Синоним: /find_nick",
            ),
            AdminCmd("/admin_export 30", "CSV заказов", "Выгрузка за N дней. Или: /admin_export all"),
            AdminCmd(
                "/channel_checkout_pin",
                "Текст для канала",
                "Чеклист оплаты по bc — скопировать/закрепить в канале.",
            ),
        ),
    ),
    AdminCmdSection(
        key="vpn",
        title="VPN",
        blurb="Подписки, ссылки, инциденты Happ.",
        commands=(
            AdminCmd("/admin_vpn", "Список VPN-команд", "Краткая шпаргалка прямо в чат."),
            AdminCmd(
                "/vpn_health",
                "VPN путь / скорость",
                "Swap 149, CF Contabo, WG RTT + API. То же: /admin_vpn_health. "
                "В /admin — кнопка «VPN health / путь».",
            ),
            AdminCmd("/admin_vpn_health", "Здоровье VPN (полный)", "Синоним /vpn_health."),
            AdminCmd(
                "/vpn_zombies",
                "Живые + зомби RU-bridge",
                "Оплаченные+trial vs лишние UUID на bridge. "
                "То же: /admin_vpn_zombies. В /admin — «Bridge зомби».",
            ),
            AdminCmd(
                "/admin_vpn_zombies",
                "Зомби bridge (детали)",
                "Синоним /vpn_zombies.",
            ),
            AdminCmd(
                "/admin_vpn_status 123456789",
                "Статус пользователя",
                "Подписка и ссылка /sub/ по telegram_id.",
            ),
            AdminCmd(
                "/admin_vpn_finalize 104",
                "Дожать выдачу",
                "paid→completed + рефка. Или: /admin_vpn_finalize stuck",
            ),
            AdminCmd(
                "/admin_vpn_extend 123 2026-12-31T23:59:59+00:00",
                "Продлить VPN",
                "Новая дата окончания. Можно добавить order_id в конце.",
            ),
            AdminCmd(
                "/admin_vpn_revoke 123 abuse",
                "Отключить VPN",
                "Сразу гасит доступ. Причина опциональна.",
            ),
            AdminCmd(
                "/admin_vpn_devices 123456789",
                "Устройства пользователя",
                "Список устройств (id, имя, статус, ссылка).",
            ),
            AdminCmd(
                "/admin_vpn_device_revoke 123 9",
                "Отвязать устройство",
                "Точечный revoke: telegram_id + device_id. Ссылка /sub умрёт.",
            ),
            AdminCmd(
                "/admin_vpn_device_reset 123",
                "Сброс HWID",
                "Сброс привязки телефона (HWID). Не путать с revoke ссылки.",
            ),
            AdminCmd(
                "/admin_vpn_trial_status 123",
                "Статус trial",
                "Брал ли пробный, привязка устройства.",
            ),
            AdminCmd(
                "/admin_vpn_announce",
                "Статус в Happ",
                "preset 4g / set текст / clear — сообщение пользователям в клиенте.",
            ),
        ),
    ),
    AdminCmdSection(
        key="ref",
        title="Рефералка",
        blurb="Партнёры и выводы бонусов.",
        commands=(
            AdminCmd(
                "/admin_ref_partner 123 25",
                "Партнёрский %",
                "Статус и свой % (15–30). off — вернуть базовые 15%.",
            ),
            AdminCmd(
                "/admin_ref_withdraw list",
                "Заявки на вывод",
                "Список pending. Потом: paid ID или reject ID (перевод руками).",
            ),
        ),
    ),
    AdminCmdSection(
        key="money",
        title="Финансы",
        blurb="Себестоимость и пересчёт прибыли (обычно супер-админ).",
        commands=(
            AdminCmd(
                "/admin_cogs ORDER_ID 120",
                "Себестоимость",
                "Прописать COGS в ₽ и пересчитать прибыль по заказу.",
            ),
            AdminCmd(
                "/admin_recalc_profit 104",
                "Пересчёт прибыли",
                "Один заказ или все VPN: /admin_recalc_profit vpn",
            ),
            AdminCmd(
                "/admin_fin_set fee_sbp 3.4",
                "Комиссии / Fragment",
                "Override в БД для новых заказов. Premium 1м: /admin_fin_set fragment_1m 4.99. Сброс: … clear. Список: /admin_fin_show",
            ),
            AdminCmd(
                "/admin_fin_show",
                "Показать FIN %",
                "Текущие fee/Fragment (env + ✎ overrides).",
            ),
        ),
    ),
    AdminCmdSection(
        key="broadcast",
        title="Рассылки",
        blurb="Ручные акции. VPN trial/expiry — отдельно, не отключаются.",
        commands=(
            AdminCmd(
                "/admin_broadcast",
                "Новая рассылка",
                "Текст → тест себе → админы → когорта 100 / всем с подпиской на акции.",
            ),
            AdminCmd(
                "/admin_broadcast_stats 12",
                "Стата рассылки",
                "sent / fail / skip и сколько отписались от акций.",
            ),
            AdminCmd(
                "/cancel_broadcast",
                "Отмена ввода",
                "Сброс черновика рассылки.",
            ),
        ),
    ),
    AdminCmdSection(
        key="contest",
        title="Конкурсы",
        blurb="Партнёрские конкурсы.",
        commands=(
            AdminCmd("/contest", "Справка конкурсов", "list / activate ID / deactivate_all."),
        ),
    ),
    AdminCmdSection(
        key="promo",
        title="Промокоды",
        blurb="Акции, блогеры, персональные офферы.",
        commands=(
            AdminCmd(
                "/admin_promo",
                "Справка промокодов",
                "list / new CODE|… / on ID / off ID.",
            ),
        ),
    ),
    AdminCmdSection(
        key="user",
        title="Как у пользователя",
        blurb="Чтобы понимать, что видит клиент (админу тоже работают).",
        commands=(
            AdminCmd("/start", "Старт", "Вход и привязка реф-ссылки."),
            AdminCmd("/menu", "Главное меню", "Хаб магазина."),
            AdminCmd("/my", "Профиль", "Баланс, VPN-ссылки."),
            AdminCmd("/orders", "Мои заказы", "История покупок."),
            AdminCmd("/vpn", "Раздел VPN", "Тарифы и настройка."),
            AdminCmd("/vpnlink", "Моя VPN-ссылка", "Быстро открыть /sub/."),
            AdminCmd("/help_ai", "AI-помощник", "Подсказки пользователю."),
            AdminCmd("/cancel", "Отмена", "Сброс текущего шага покупки."),
        ),
    ),
)


def section_by_key(key: str) -> AdminCmdSection | None:
    for s in ADMIN_HELP_SECTIONS:
        if s.key == key:
            return s
    return None


def admin_help_hub_html() -> str:
    return (
        "<b>📚 Справка для админов</b>\n\n"
        "Одинаково у Сергея, Миши и Димы.\n"
        "Выберите раздел — там <b>что прописать</b> и <b>зачем</b>.\n\n"
        "<i>Подсказка: команды в <code>сером</code> можно копировать долгим нажатием.</i>"
    )


def admin_help_section_html(section: AdminCmdSection) -> str:
    lines = [
        f"<b>{section.title}</b>",
        f"<i>{section.blurb}</i>\n",
    ]
    for c in section.commands:
        lines.append(f"<code>{c.usage}</code>")
        lines.append(f"<b>{c.title}</b> — {c.how}\n")
    return "\n".join(lines)


def admin_help_hub_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in ADMIN_HELP_SECTIONS:
        b.row(InlineKeyboardButton(text=s.title, callback_data=f"ahelp:cat:{s.key}"))
    b.row(InlineKeyboardButton(text="⬅️ В /admin", callback_data="ahelp:open_admin"))
    return b.as_markup()


def admin_help_section_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ К разделам", callback_data="ahelp:hub")],
            [InlineKeyboardButton(text="🏠 Дашборд /admin", callback_data="ahelp:open_admin")],
        ]
    )


def admin_dashboard_help_row() -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text="📚 Команды", callback_data="ahelp:hub")]
