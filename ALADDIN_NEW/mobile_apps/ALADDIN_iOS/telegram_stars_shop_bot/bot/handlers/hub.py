from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import brand_constants as brand
from bot.config import Settings
from bot.keyboards.shop_kb import (
    hub_menu_kb,
    order_detail_kb,
    orders_cancel_all_confirm_kb,
    products_kb,
    reply_keyboard_remove,
    stars_menu_kb,
)
from bot.services.ui_visibility import gifts_menu_visible
from bot.services import (
    api_clients_repo,
    balance_repo,
    contest_repo,
    onboarding_gate,
    orders_repo,
    users_repo,
    vpn_referral_repo,
)
from bot.services.api_repo import create_api_key_request
from bot.services.catalog import Product, sort_for_display
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member
from bot.services.marketing import (
    faq_comprehensive_html,
    partner_onboarding_html,
    payment_faq_html,
    privacy_screen_html,
    referral_faq_html,
    refund_policy_table_html,
)
from bot.services.pricing import format_rub_usd_html, rub_per_100_stars_display
from bot.services.support_ticket_service import open_inbot_support_ticket
from bot.states.checkout import ApiKeyStates, RefWithdrawStates, TopupStates
from bot.states.support import SupportStates
from bot.support_links import (
    is_telegram_contact,
    support_order_question_url,
    support_prefill_url,
    telegram_support_base,
)
from bot.ui_copy import ONBOARDING_SCREEN_2
from bot.util_telegram import answer_callback_safe
from bot.util_html import esc
from bot.services.topup_payment_service import (
    TopupPayMethod,
    begin_topup_checkout,
    topup_checkout_error_message,
    topup_payment_methods,
)

router = Router(name="hub")

TOPUP_PRESET_RUB = (100, 500, 1000)


def _topup_kop(amount_rub: float) -> int:
    return int(round(float(amount_rub) * 100))


def _topup_rub_from_kop(kop: int) -> float:
    return round(int(kop) / 100.0, 2)


def _topup_amounts_for_ui(settings: Settings) -> tuple[int, ...]:
    lo, hi = settings.topup_min_rub, settings.topup_max_rub
    out: list[int] = []
    for amt in TOPUP_PRESET_RUB:
        if lo - 1e-6 <= amt <= hi + 1e-6:
            out.append(amt)
    return tuple(out)


def _topup_method_label(method: TopupPayMethod) -> str:
    return "💳 LAVA (СБП / карта)" if method == "lava" else "💎 Криптовалюта (USDT)"


def _topup_method_kb(amount_kop: int, settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for method in topup_payment_methods(settings):
        b.row(
            InlineKeyboardButton(
                text=_topup_method_label(method),
                callback_data=f"top:pay:{method}:{amount_kop}",
            )
        )
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:topup"))
    return b.as_markup()


def _topup_pay_kb(topup_id: int, pay_urls: list, settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for item in pay_urls:
        b.row(InlineKeyboardButton(text=item.label, url=item.url))
    b.row(InlineKeyboardButton(text="❌ Отменить", callback_data=f"top:cancel:{topup_id}"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    return b.as_markup()


async def _topup_show_method_picker(cb: CallbackQuery, conn, settings: Settings, amount_rub: float) -> None:
    methods = topup_payment_methods(settings)
    amt = round(float(amount_rub), 2)
    kop = _topup_kop(amt)
    if not methods:
        await answer_callback_safe(cb)
        await cb.message.edit_text(
            "<b>Пополнение баланса</b>\n\n"
            "Сейчас автоматическая оплата недоступна. Попробуйте позже или напишите в поддержку.",
            reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
        )
        return
    if len(methods) == 1:
        await _topup_run_checkout(
            cb=cb,
            conn=conn,
            settings=settings,
            user_id=cb.from_user.id,
            amount_rub=amt,
            method=methods[0],
        )
        return
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        f"<b>Пополнение баланса</b>\n\n"
        f"Сумма: <b>{esc(f'{amt:.2f}')} ₽</b>\n\n"
        "Выберите способ оплаты:",
        reply_markup=_topup_method_kb(kop, settings),
    )


async def _topup_run_checkout(
    *,
    cb: CallbackQuery | None = None,
    message: Message | None = None,
    conn,
    settings: Settings,
    user_id: int,
    amount_rub: float,
    method: TopupPayMethod,
) -> None:
    try:
        result = await begin_topup_checkout(
            conn, settings, user_id=user_id, amount_rub=amount_rub, method=method
        )
    except ValueError as e:
        msg = topup_checkout_error_message(str(e))
        if cb is not None:
            await cb.answer(msg, show_alert=True)
        elif message is not None:
            await message.answer(msg, reply_markup=hub_menu_kb(settings, user_id=user_id))
        return
    if result.error or not result.pay_urls:
        msg = topup_checkout_error_message(result.error)
        if cb is not None:
            await cb.answer(msg, show_alert=True)
        elif message is not None:
            await message.answer(msg, reply_markup=hub_menu_kb(settings, user_id=user_id))
        return
    method_ru = "LAVA (СБП / карта)" if method == "lava" else "криптовалюта (USDT)"
    text = (
        f"<b>Пополнение #{esc(result.topup_id)}</b>\n\n"
        f"Сумма: <b>{esc(f'{result.amount_rub:.2f}')} ₽</b>\n"
        f"Способ: {esc(method_ru)}\n\n"
        "Нажмите кнопку ниже для оплаты. Баланс зачислится автоматически после подтверждения платежа."
    )
    kb = _topup_pay_kb(result.topup_id, result.pay_urls, settings)
    if cb is not None:
        await answer_callback_safe(cb)
        await cb.message.edit_text(text, reply_markup=kb)
    elif message is not None:
        await message.answer(text, reply_markup=kb)

ORDERS_PAGE = 5

FAQ_TEMPLATES = {
    "pay": (
        "<b>Оплата - статус не меняется</b>\n\n"
        "Скопируйте шаблон, подставьте номер заказа и отправьте в поддержку:\n"
        "<code>Заказ #____ - оплатил, статус в боте не обновился</code>"
    ),
    "stars": (
        "<b>Не пришли Stars</b>\n\n"
        "<code>Заказ #____ - не пришли Stars на @username</code>"
    ),
    "user": (
        "<b>Ошибка в @username</b>\n\n"
        "<code>Заказ #____ - ошибся в username получателя, нужно исправить на @____</code>"
    ),
}


def _support_kb(settings: Settings, *, user_id: int | None = None):
    from bot.assistant.access import assistant_menu_visible
    from bot.support_links import external_human_support_url, support_url_is_shop_bot_loop

    b = InlineKeyboardBuilder()
    if assistant_menu_visible(user_id, settings):
        b.row(InlineKeyboardButton(text="🤖 AI Помощник", callback_data="nav:assistant"))
    b.row(InlineKeyboardButton(text="🛡️ Политика магазина", callback_data="sup:privacy"))
    b.row(InlineKeyboardButton(text="↩️ Сроки возврата", callback_data="sup:refund"))
    b.row(InlineKeyboardButton(text="📚 Частые вопросы", callback_data="sup:faq"))
    b.row(InlineKeyboardButton(text="💳 Оплата и зачисление", callback_data="sup:payfaq"))
    # Всегда in-bot: тикет → только ADMIN_IDS / ASSISTANT_ADMIN_CHAT_ID (не видно другим юзерам).
    b.row(InlineKeyboardButton(text="💬 Написать оператору", callback_data="sup:write"))
    b.row(InlineKeyboardButton(text="🧾 Шаблон: оплата / статус", callback_data="sup:tpl:pay"))
    b.row(InlineKeyboardButton(text="⭐ Шаблон: Stars", callback_data="sup:tpl:stars"))
    b.row(InlineKeyboardButton(text="👤 Шаблон: username", callback_data="sup:tpl:user"))
    ext = external_human_support_url(settings)
    if ext and is_telegram_contact(ext) and not support_url_is_shop_bot_loop(settings):
        u1 = support_prefill_url(settings, "Заказ # - оплатил, статус не обновился") or ext
        u2 = support_prefill_url(settings, "Заказ # - не пришли Stars") or ext
        u3 = support_prefill_url(settings, "Заказ # - ошибся в @username") or ext
        b.row(InlineKeyboardButton(text="💳 Оплатил (внешний чат)", url=u1))
        b.row(InlineKeyboardButton(text="⭐ Stars (внешний чат)", url=u2))
        b.row(InlineKeyboardButton(text="@username (внешний чат)", url=u3))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


def _api_kb(settings: Settings):
    b = InlineKeyboardBuilder()
    if (settings.api_key_pepper or "").strip():
        b.row(InlineKeyboardButton(text="🔑 Partner API (X-API-KEY)", callback_data="api:partner_key"))
    b.row(InlineKeyboardButton(text="📩 Запрос ключа у оператора", callback_data="api:req"))
    if settings.api_docs_url:
        b.row(InlineKeyboardButton(text="📄 Документация", url=settings.api_docs_url))
    b.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="nav:hub"))
    return b.as_markup()


async def profile_body_html(bot: Bot, settings: Settings, conn, user_id: int) -> str:
    from bot.services.vpn_subscription_dates import format_datetime_display_msk
    from bot.services.vpn_user_status import vpn_user_status_block_html

    _ = bot  # signature kept for callers
    stats = await users_repo.user_stats(conn, user_id)
    row = await users_repo.get_user(conn, user_id)
    br = float(stats["balance_rub"])
    rr = float(stats["ref_balance_rub"])
    created_raw = ""
    if row is not None:
        try:
            created_raw = str(row["created_at"] or "")
        except (KeyError, IndexError):
            created_raw = ""
    reg_disp = format_datetime_display_msk(created_raw, date_only=True) if created_raw else "—"
    vpn_block = await vpn_user_status_block_html(
        settings, user_id, inactive_variant="profile"
    )
    return (
        f"<b>Личный кабинет</b> · {brand.BRAND_SHORT} · {esc(brand.SHOP_BOT_HANDLE)}\n\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📅 <b>Дата регистрации:</b> {esc(reg_disp)}\n"
        f"💳 <b>Основной баланс:</b> {esc(f'{br:.2f}')} ₽\n"
        f"🎁 <b>Реферальный баланс:</b> {esc(f'{rr:.2f}')} ₽\n"
        f"<i>Можно тратить на VPN, Stars и Premium. Вывод от 1000 ₽ — в реферальном разделе.</i>\n"
        f"🛡️ <b>VPN:</b>\n{vpn_block}"
    )


async def _orders_page_html(conn, user_id: int, page: int) -> tuple[str, bool, bool]:
    from bot.services.order_status_ui import order_list_card_html

    total = await orders_repo.count_user_orders(conn, user_id)
    offset = page * ORDERS_PAGE
    rows = await orders_repo.list_user_orders_page(conn, user_id, limit=ORDERS_PAGE, offset=offset)
    has_prev = page > 0
    has_next = offset + len(rows) < total
    if not rows:
        return "<b>📦 Заказы</b>\n\nПока заказов нет.", has_prev, has_next
    pending_n = await orders_repo.count_user_orders_by_status(conn, user_id, "pending_payment")
    lines = ["<b>📦 Заказы</b>\n"]
    if pending_n > 0:
        lines.append(
            f"<i>Неоплаченных: <b>{pending_n}</b>. Откройте карточку или отмените лишние.</i>\n"
        )
    else:
        lines.append("<i>Откройте заказ кнопкой с номером ниже.</i>\n")
    for r in rows:
        lines.append(
            order_list_card_html(
                order_id=int(r["id"]),
                product_title=str(r["product_title"] or ""),
                rub_amount=float(r["rub_after_discounts"] or 0),
                created_at=str(r["created_at"] or ""),
                status=str(r["status"] or ""),
            )
        )
        lines.append("")  # отступ между карточками
    return "\n".join(lines).rstrip() + "\n", has_prev, has_next


@router.callback_query(F.data == "start:hub")
async def onboarding_continue(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not await users_repo.is_onboarding_completed(conn, cb.from_user.id):
        await cb.answer()
        try:
            await cb.message.delete()
        except Exception:
            pass
        await onboarding_gate.resume_onboarding_pipeline(
            cb.bot, cb.message.chat.id, cb.from_user.id, settings, conn
        )
        return
    if channel_gate_enabled(settings) and not await user_is_channel_member(
        cb.bot, settings, cb.from_user.id
    ):
        await cb.answer(
            "Кажется, подписка на канал ещё не подтверждена. Нажмите «Подписаться», затем «Я подписался - открыть меню».",
            show_alert=True,
        )
        return
    fid2 = (settings.start_photo_file_id_2 or "").strip()
    await answer_callback_safe(cb)
    # Снять залипшие нижние 4 кнопки (если остались у клиента).
    try:
        ghost = await cb.message.answer("\u200b", reply_markup=reply_keyboard_remove())
        try:
            await ghost.delete()
        except Exception:
            pass
    except Exception:
        pass
    if fid2:
        # Keep hub controls on a text message so downstream handlers can safely use edit_text.
        await cb.message.answer_photo(fid2)
        await cb.message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id))
    else:
        await cb.message.edit_text(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id))


@router.callback_query(F.data == "nav:hub")
async def nav_hub(cb: CallbackQuery, settings: Settings) -> None:
    from bot.util_telegram import safe_edit_text

    await answer_callback_safe(cb)
    try:
        ghost = await cb.message.answer("\u200b", reply_markup=reply_keyboard_remove())
        try:
            await ghost.delete()
        except Exception:
            pass
    except Exception:
        pass
    await safe_edit_text(
        cb.message,
        ONBOARDING_SCREEN_2,
        reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
    )


@router.callback_query(F.data == "nav:orders:noop")
async def orders_noop(cb: CallbackQuery) -> None:
    await answer_callback_safe(cb)


@router.callback_query(F.data.startswith("nav:orders:"))
async def nav_orders(cb: CallbackQuery, settings: Settings, conn) -> None:
    from bot.services.lava_payment_reconcile import schedule_lava_reconcile_once

    schedule_lava_reconcile_once(settings)
    suf = cb.data.split(":")[-1]
    try:
        page = int(suf)
    except ValueError:
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await _present_orders_page(cb, settings, conn, page)


async def _present_orders_page(cb: CallbackQuery, settings: Settings, conn, page: int) -> None:
    text, has_prev, has_next = await _orders_page_html(conn, cb.from_user.id, page)
    rows = await orders_repo.list_user_orders_page(
        conn, cb.from_user.id, limit=ORDERS_PAGE, offset=page * ORDERS_PAGE
    )
    b = InlineKeyboardBuilder()
    for r in rows:
        rid = int(r["id"])
        amt = float(r["rub_after_discounts"])
        usd = float(r["usd_base"] or 0.0)
        b.row(
            InlineKeyboardButton(
                text=f"#{rid} · {format_rub_usd_html(amt, usd, rub_decimals=0)}",
                callback_data=f"ord:{rid}",
            )
        )
    row = []
    if has_prev:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav:orders:{page - 1}"))
    row.append(InlineKeyboardButton(text=f"·{page + 1}·", callback_data="nav:orders:noop"))
    if has_next:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"nav:orders:{page + 1}"))
    if row:
        b.row(*row)
    pending_n = await orders_repo.count_user_orders_by_status(conn, cb.from_user.id, "pending_payment")
    if pending_n > 0:
        b.row(
            InlineKeyboardButton(
                text=f"🗑 Отменить все неоплаченные ({pending_n})",
                callback_data="orders:cancel_all_confirm",
            )
        )
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(text, reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("ord:cancel:"))
async def order_user_cancel(cb: CallbackQuery, settings: Settings, conn) -> None:
    oid = int(cb.data.split(":")[-1])
    code = await orders_repo.cancel_user_pending_order(conn, order_id=oid, user_id=cb.from_user.id)
    if code == "not_found":
        await cb.answer("Заказ не найден", show_alert=True)
        return
    if code == "wrong_user":
        await cb.answer("Нет доступа", show_alert=True)
        return
    if code == "wrong_status":
        await cb.answer("Этот заказ уже нельзя отменить (оплачен или закрыт).", show_alert=True)
        return
    await cb.answer(f"Заказ #{oid} отменён.")
    await cb.message.edit_text(
        f"<b>Заказ #{esc(oid)} отменён</b>\n\n"
        "Можно оформить новый заказ в главном меню.",
        reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
    )


@router.callback_query(F.data == "orders:cancel_all_confirm")
async def orders_cancel_all_confirm(cb: CallbackQuery, conn) -> None:
    n = await orders_repo.count_user_orders_by_status(conn, cb.from_user.id, "pending_payment")
    if n <= 0:
        await cb.answer("Нет неоплаченных заказов.", show_alert=True)
        return
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        f"<b>Отменить все неоплаченные заказы?</b>\n\n"
        f"Будет закрыто заказов: <b>{n}</b>.\n"
        "Оплата по старым ссылкам LAVA после этого не пройдёт — "
        "для покупки оформите новый заказ.",
        reply_markup=orders_cancel_all_confirm_kb(),
    )


@router.callback_query(F.data == "orders:cancel_all:yes")
async def orders_cancel_all_yes(cb: CallbackQuery, settings: Settings, conn) -> None:
    cancelled = await orders_repo.cancel_all_user_pending_orders(conn, user_id=cb.from_user.id)
    if not cancelled:
        await cb.answer("Нет неоплаченных заказов.", show_alert=True)
        return
    ids_s = ", ".join(f"#{i}" for i in cancelled)
    await answer_callback_safe(cb, "Готово")
    await cb.message.edit_text(
        f"<b>Отменено заказов: {len(cancelled)}</b>\n"
        f"<code>{esc(ids_s)}</code>\n\n"
        "Теперь можно оформить новый заказ в главном меню.",
        reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
    )


@router.callback_query(F.data.regexp(r"^ord:\d+$"))
async def order_detail(cb: CallbackQuery, settings: Settings, conn) -> None:
    oid = int(cb.data.split(":")[1])
    order = await orders_repo.get_order(conn, oid)
    if not order or int(order["user_id"]) != cb.from_user.id:
        await cb.answer("Заказ не найден", show_alert=True)
        return
    await answer_callback_safe(cb)
    sup = support_order_question_url(settings, oid)
    amt = float(order["rub_after_discounts"])
    usd = float(order["usd_base"] or 0.0)
    bap = float(order["balance_applied_rub"] or 0)
    due = orders_repo.amount_due_external(order)
    st_raw = str(order["status"])
    from bot.services.order_status_ui import format_order_created_display, order_status_ui_label

    when = format_order_created_display(str(order["created_at"] or ""))
    st_ui = order_status_ui_label(st_raw)
    text = (
        f"<b>Заказ #{esc(oid)}</b>\n"
        f"<i>{esc(when)}</i>\n\n"
        f"Товар: {esc(order['product_title'])}\n"
        f"Сумма: <b>{format_rub_usd_html(amt, usd)}</b>\n"
    )
    if bap > 0.005:
        text += f"С баланса: <b>{esc(f'{bap:.2f}')} ₽</b>\n"
    if due > 0.005:
        due_usd = usd * (due / amt) if amt > 0.005 else 0.0
        text += f"К оплате снаружи: <b>{format_rub_usd_html(due, due_usd)}</b>\n"
    text += (
        f"Оплата: <code>{esc(order['payment_method'])}</code>\n"
        f"Статус: <b>{esc(st_ui)}</b>\n"
        f"Получатель: <code>{esc(order['user_note'] or '')}</code>\n\n"
    )
    if st_raw == "pending_payment":
        text += (
            "<i>Оплатите заказ кнопкой ниже. Не уходите из экрана оплаты, "
            "пока не завершите платёж в банке.</i>"
        )
    elif st_raw == "expired":
        text += "<i>Счёт не оплачен в срок. Если оплатили - напишите в поддержку с номером заказа.</i>"
    elif st_raw == "refunded":
        text += "<i>По этому заказу зафиксировано сторно или возврат средств со стороны магазина/поддержки.</i>"
    elif st_raw == "payment_disputed":
        text += "<i>Идёт разбор по оплате; при необходимости поддержка напишет или ответьте в тикет с номером заказа.</i>"
    else:
        text += "<i>После оплаты статус обновит оператор.</i>"
    await cb.message.edit_text(
        text,
        reply_markup=order_detail_kb(oid, sup, pending_payment=(st_raw == "pending_payment")),
    )


@router.callback_query(F.data == "nav:buy_stars")
async def nav_buy_stars(cb: CallbackQuery, products: list[Product], settings: Settings, conn) -> None:
    await answer_callback_safe(cb)
    items = sort_for_display([p for p in products if p.kind == "stars" and not p.hide_from_menu])
    if not items:
        await cb.message.edit_text(
            "<b>Купить Stars</b>\n\n"
            "В каталоге нет позиций <code>kind: stars</code> в <code>products.yaml</code>.\n"
            "Добавьте пакеты Stars и перезапустите бота.",
            reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
        )
        return
    is_first = await orders_repo.count_user_completed_orders(conn, cb.from_user.id) == 0
    r100 = rub_per_100_stars_display(products, settings, is_first_order=is_first)
    sub = ""
    if r100 is not None:
        sub = f"\n\n<i>Ориентир: от {esc(f'{r100:.2f}')} ₽ за 100 ⭐.</i>"
    sub += "\n<i>Stars придут на ваш @username — проверите перед оплатой.</i>"
    await cb.message.edit_text(f"<b>Купить Stars</b>{sub}", reply_markup=stars_menu_kb(items))


@router.callback_query(F.data == "nav:premium")
async def nav_premium(cb: CallbackQuery, products: list[Product], settings: Settings) -> None:
    await answer_callback_safe(cb)
    items = sort_for_display([p for p in products if p.kind == "premium" and not p.hide_from_menu])
    if not items:
        await cb.message.edit_text(
            "<b>Купить Premium</b>\n\n"
            "Нет позиций <code>kind: premium</code> в <code>products.yaml</code>.",
            reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
        )
        return
    await cb.message.edit_text(
        "<b>Купить Premium</b>\n\n"
        "<i>Выберите срок → кому (себе или подарок) → оплату.</i>",
        reply_markup=products_kb(items),
    )


@router.callback_query(F.data == "nav:gifts")
async def nav_gifts(cb: CallbackQuery, products: list[Product], settings: Settings) -> None:
    if not gifts_menu_visible(settings):
        await cb.answer("Раздел временно недоступен.", show_alert=True)
        return
    await answer_callback_safe(cb)
    items = sort_for_display([p for p in products if p.kind == "gift"])
    if not items:
        await cb.message.edit_text(
            "<b>Подарки</b>\n\nДобавьте позиции <code>kind: gift</code> в <code>products.yaml</code>.",
            reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
        )
    else:
        await cb.message.edit_text(
            "<b>Подарки</b>\n\n<i>Оплата → @получателя → выдача оператором.</i>",
            reply_markup=products_kb(items),
        )


@router.callback_query(F.data == "nav:receipts")
async def nav_receipts(cb: CallbackQuery, settings: Settings, conn) -> None:
    """Legacy: «Выданные» → единый раздел «📦 Заказы»."""
    from bot.services.lava_payment_reconcile import schedule_lava_reconcile_once

    schedule_lava_reconcile_once(settings)
    await answer_callback_safe(cb)
    await _present_orders_page(cb, settings, conn, 0)


@router.callback_query(F.data == "nav:api")
async def nav_api(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        "<b>Наш API</b> - для <b>вашего бота, сайта или приложения</b>\n\n"
        "Создание заказов, статусы, пополнения и исходящие вебхуки - по HTTPS, заголовок <code>X-API-KEY</code> "
        "(ключ выпускается ниже). Не встраивайте ключ в публичный фронт - только server-to-server.\n\n"
        "<i>Подробный сценарий «приглашение друзей vs API» — кнопка «Партнёрам» в главном меню.</i>",
        reply_markup=_api_kb(settings),
    )


@router.callback_query(F.data == "api:partner_key")
async def api_partner_key_menu(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not (settings.api_key_pepper or "").strip():
        await cb.answer("Укажите API_KEY_PEPPER в .env на сервере.", show_alert=True)
        return
    await answer_callback_safe(cb)
    prefix = await api_clients_repo.get_active_prefix_for_owner(conn, cb.from_user.id)
    txt = (
        "<b>Partner API</b>\n\n"
        "Ключ передаётся в заголовке <code>X-API-KEY</code>.\n"
        "<b>Не встраивайте</b> ключ в публичный сайт - только server-to-server.\n\n"
    )
    if prefix:
        txt += f"Активный ключ (маска): <code>{esc(prefix)}</code>\n\n"
    txt += (
        "⚠️ <b>Выпуск нового ключа</b> отзывает предыдущий сразу после создания.\n\n"
        "<i>Документация: <code>docs/openapi_v1.yaml</code> в проекте бота.</i>"
    )
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔄 Выпустить / заменить ключ", callback_data="api:partner_key:new"))
    kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:api"))
    await cb.message.edit_text(txt, reply_markup=kb.as_markup())


@router.callback_query(F.data == "api:partner_key:new")
async def api_partner_key_new(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not (settings.api_key_pepper or "").strip():
        await cb.answer("API_KEY_PEPPER не задан.", show_alert=True)
        return
    _, raw = await api_clients_repo.create_api_client(
        conn,
        owner_user_id=cb.from_user.id,
        pepper=settings.api_key_pepper,
        label="telegram",
        revoke_previous=True,
    )
    await cb.message.answer(
        "<b>Partner API - новый ключ</b>\n\n"
        "Сохраните сейчас - показан <b>один раз</b>.\n\n"
        f"<code>{esc(raw)}</code>\n\n"
        "Передавайте в заголовке <code>X-API-KEY</code>.\n"
        "<b>Не передавайте</b> третьим лицам - полный доступ к вашим заказам и пополнениям через API.",
    )
    await cb.answer("Ключ отправлен отдельным сообщением")


@router.callback_query(F.data == "api:req")
async def api_req_start(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ApiKeyStates.waiting_contact)
    await cb.message.edit_text(
        "<b>Запрос ключа API</b>\n\nОтправьте контакт: <b>email</b> или <b>@telegram</b>.",
    )
    await cb.answer()


@router.message(ApiKeyStates.waiting_contact, F.text)
async def api_req_contact(message: Message, state: FSMContext) -> None:
    await state.update_data(api_contact=(message.text or "").strip())
    await state.set_state(ApiKeyStates.waiting_comment)
    await message.answer("<b>Комментарий</b> (зачем API) или <code>-</code>.")


@router.message(ApiKeyStates.waiting_comment, F.text)
async def api_req_done(message: Message, state: FSMContext, conn, bot: Bot, settings: Settings) -> None:
    data = await state.get_data()
    contact = data.get("api_contact", "")
    comment = (message.text or "").strip()
    await state.clear()
    rid = await create_api_key_request(conn, user_id=message.from_user.id, contact=contact, comment=comment)
    await message.answer(
        f"<b>Заявка #{esc(rid)} принята.</b>",
        reply_markup=hub_menu_kb(settings, user_id=message.from_user.id),
    )
    from bot.services.ops_chat import send_ops_chat_html

    await send_ops_chat_html(
        settings,
        f"<b>API #{esc(rid)}</b>\n<code>{message.from_user.id}</code>\n{esc(contact)}\n{esc(comment)}",
    )


@router.callback_query(F.data == "nav:ref")
async def nav_ref(cb: CallbackQuery, settings: Settings, conn, bot: Bot) -> None:
    from bot.services.referral_partner import count_qualified_vpn_referrals, level_for_qualified_count
    from bot.services.referral_ux import referral_home_html, referral_home_kb
    from bot.services.vpn_referral_repo import ensure_my_vpn_referral_code
    from bot.services.vpn_user_links import invite_ref_telegram_url

    await answer_callback_safe(cb)
    me = await bot.get_me()
    bot_user = me.username or "your_bot"
    uid = cb.from_user.id
    ref_link = invite_ref_telegram_url(bot_user, uid)
    web_ref_link = None
    try:
        code = await ensure_my_vpn_referral_code(conn, uid)
        origin = (getattr(settings, "web_checkout_public_origin", None) or "").strip().rstrip("/")
        if not origin:
            origin = "https://aimonkeystars.ru"
        web_ref_link = f"{origin}/r/{code}"
    except Exception:
        web_ref_link = None
    stats = await users_repo.user_stats(conn, uid)
    qn = await count_qualified_vpn_referrals(conn, uid)
    text = referral_home_html(
        ref_link=ref_link,
        web_ref_link=web_ref_link,
        invited=int(stats["referral_invited_count"]),
        buyers=int(stats["referral_buyers_completed_count"]),
        earned_rub=float(stats["referral_commission_earned_rub"]),
        settings=settings,
        qualified_vpn=qn,
        level=level_for_qualified_count(qn),
    )
    await cb.message.edit_text(
        text, reply_markup=referral_home_kb(ref_link, settings, web_ref_url=web_ref_link)
    )


@router.callback_query(F.data == "nav:refstats")
async def nav_refstats(cb: CallbackQuery, settings: Settings, conn) -> None:
    from bot.services.referral_partner import count_qualified_vpn_referrals
    from bot.services.referral_ux import referral_stats_html, referral_stats_kb

    await answer_callback_safe(cb)
    uid = cb.from_user.id
    stats = await users_repo.user_stats(conn, uid)
    qn = await count_qualified_vpn_referrals(conn, uid)
    await cb.message.edit_text(
        referral_stats_html(stats, settings, qualified_vpn=qn),
        reply_markup=referral_stats_kb(),
    )


@router.callback_query(F.data == "nav:refboost")
async def nav_refboost(cb: CallbackQuery, settings: Settings, conn) -> None:
    from bot.services.referral_partner import count_qualified_vpn_referrals
    from bot.services.referral_ux import referral_boost_html, referral_boost_kb

    await answer_callback_safe(cb)
    stats = await users_repo.user_stats(conn, cb.from_user.id)
    qn = await count_qualified_vpn_referrals(conn, cb.from_user.id)
    await cb.message.edit_text(
        referral_boost_html(stats, qualified_vpn=qn),
        reply_markup=referral_boost_kb(settings, can_apply=False),
    )


@router.callback_query(F.data == "nav:refwithdraw")
async def nav_refwithdraw(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    from bot.services import ref_withdraw_repo
    from bot.services.referral_partner import evaluate_withdraw_eligibility
    from bot.services.referral_ux import referral_withdraw_html, referral_withdraw_kb

    await answer_callback_safe(cb)
    await state.clear()
    _ = settings
    uid = cb.from_user.id
    stats = await users_repo.user_stats(conn, uid)
    bal = float(stats.get("ref_balance_rub", 0) or 0)
    pending = await ref_withdraw_repo.has_pending_withdraw(conn, uid)
    el = await evaluate_withdraw_eligibility(
        conn,
        uid,
        balance=bal,
        min_withdraw_rub=ref_withdraw_repo.MIN_WITHDRAW_RUB,
        pending=pending,
    )
    await cb.message.edit_text(
        referral_withdraw_html(balance=bal, pending=pending, eligibility=el),
        reply_markup=referral_withdraw_kb(can_request=el.ok),
    )


async def _create_ref_withdraw_and_alert(
    *,
    settings: Settings,
    conn,
    uid: int,
    bal: float,
    method: str,
    crypto_channel: str | None = None,
    payout_target: str = "",
    details: str = "",
) -> int:
    from bot.services import ref_withdraw_repo
    from bot.services.alerts import send_alert
    from bot.services.referral_partner import evaluate_withdraw_eligibility

    pending = await ref_withdraw_repo.has_pending_withdraw(conn, uid)
    el = await evaluate_withdraw_eligibility(
        conn,
        uid,
        balance=bal,
        min_withdraw_rub=ref_withdraw_repo.MIN_WITHDRAW_RUB,
        pending=pending,
    )
    if not el.ok:
        if not el.balance_ok:
            raise ValueError("below_min")
        if not el.pending_ok:
            raise ValueError("pending_exists")
        if not el.qualified_ok:
            raise ValueError("need_qualified_vpn")
        if not el.own_vpn_ok:
            raise ValueError("need_own_vpn")
        if not el.cooldown_ok:
            raise ValueError("cooldown")
        raise ValueError("withdraw_blocked")

    rid = await ref_withdraw_repo.create_withdraw_request(
        conn,
        user_id=uid,
        amount_rub=bal,
        method=method,
        crypto_channel=crypto_channel,
        payout_target=payout_target,
        details=details,
    )
    label = method if method == "card" else f"crypto/{crypto_channel or '?'}"
    await send_alert(
        settings=settings,
        severity="info",
        title="referral withdraw request",
        body=(
            f"request_id={rid} user_id={uid} amount_rub={bal:.2f} "
            f"method={label} target={payout_target or '-'} "
            f"qualified={el.qualified_n} level={el.level.get('id')}"
        ),
        dedupe_key=f"ref_wd:{rid}",
    )
    return rid


@router.callback_query(F.data == "ref:wd:card")
async def ref_withdraw_card(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    from bot.services import ref_withdraw_repo
    from bot.services.referral_ux import referral_withdraw_html, referral_withdraw_kb

    await state.clear()
    uid = cb.from_user.id
    stats = await users_repo.user_stats(conn, uid)
    bal = float(stats.get("ref_balance_rub", 0) or 0)
    try:
        rid = await _create_ref_withdraw_and_alert(
            settings=settings,
            conn=conn,
            uid=uid,
            bal=bal,
            method=ref_withdraw_repo.METHOD_CARD,
            details="card_payout_request",
        )
    except ValueError as e:
        code = str(e)
        if code == "below_min":
            await cb.answer("Минимум вывода — 1000 ₽.", show_alert=True)
        elif code == "pending_exists":
            await cb.answer("Заявка уже в обработке.", show_alert=True)
        elif code == "need_qualified_vpn":
            await cb.answer("Нужно ≥5 друзей с VPN от 30 дней.", show_alert=True)
        elif code == "need_own_vpn":
            await cb.answer("Нужен свой оплаченный VPN от 30 дней.", show_alert=True)
        elif code == "cooldown":
            await cb.answer("Не чаще 1 заявки в 7 дней.", show_alert=True)
        else:
            await cb.answer("Не удалось создать заявку.", show_alert=True)
        return
    await cb.message.edit_text(
        referral_withdraw_html(balance=bal, pending=True)
        + f"\n\n✅ Заявка на <b>карту</b> <code>#{rid}</code> создана.",
        reply_markup=referral_withdraw_kb(can_request=False),
    )
    await cb.answer("Заявка отправлена")


@router.callback_query(F.data == "ref:wd:crypto")
async def ref_withdraw_crypto_menu(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    from bot.services import ref_withdraw_repo
    from bot.services.referral_partner import evaluate_withdraw_eligibility
    from bot.services.referral_ux import referral_withdraw_crypto_channel_html, referral_withdraw_crypto_kb

    await state.clear()
    uid = cb.from_user.id
    stats = await users_repo.user_stats(conn, uid)
    bal = float(stats.get("ref_balance_rub", 0) or 0)
    pending = await ref_withdraw_repo.has_pending_withdraw(conn, uid)
    el = await evaluate_withdraw_eligibility(
        conn,
        uid,
        balance=bal,
        min_withdraw_rub=ref_withdraw_repo.MIN_WITHDRAW_RUB,
        pending=pending,
    )
    if not el.ok:
        await cb.answer("Вывод сейчас недоступен — смотрите условия на экране.", show_alert=True)
        return
    _ = settings
    await cb.message.edit_text(
        referral_withdraw_crypto_channel_html(),
        reply_markup=referral_withdraw_crypto_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.in_({"ref:wd:crypto:trc20", "ref:wd:crypto:bot"}))
async def ref_withdraw_crypto_channel(cb: CallbackQuery, state: FSMContext) -> None:
    from bot.services.referral_ux import (
        referral_withdraw_cancel_kb,
        referral_withdraw_crypto_prompt_html,
    )
    from bot.states.checkout import RefWithdrawStates

    channel = (
        "usdt_trc20" if cb.data == "ref:wd:crypto:trc20" else "cryptobot"
    )
    await state.set_state(RefWithdrawStates.waiting_crypto_target)
    await state.update_data(ref_wd_crypto_channel=channel)
    await cb.message.edit_text(
        referral_withdraw_crypto_prompt_html(channel=channel),
        reply_markup=referral_withdraw_cancel_kb(),
    )
    await cb.answer()


@router.message(RefWithdrawStates.waiting_crypto_target, F.text)
async def ref_withdraw_crypto_target(message: Message, state: FSMContext, settings: Settings, conn) -> None:
    from bot.services import ref_withdraw_repo
    from bot.services.referral_ux import referral_withdraw_html, referral_withdraw_kb
    from bot.states.checkout import RefWithdrawStates

    _ = RefWithdrawStates
    data = await state.get_data()
    channel = str(data.get("ref_wd_crypto_channel") or "").strip().lower()
    raw = (message.text or "").strip()
    uid = message.from_user.id
    stats = await users_repo.user_stats(conn, uid)
    bal = float(stats.get("ref_balance_rub", 0) or 0)
    try:
        rid = await _create_ref_withdraw_and_alert(
            settings=settings,
            conn=conn,
            uid=uid,
            bal=bal,
            method=ref_withdraw_repo.METHOD_CRYPTO,
            crypto_channel=channel,
            payout_target=raw,
        )
    except ValueError as e:
        code = str(e)
        if code == "below_min":
            await message.answer("Минимум вывода — 1000 ₽.")
        elif code == "pending_exists":
            await message.answer("Заявка уже в обработке.")
        elif code == "need_qualified_vpn":
            await message.answer("Нужно ≥5 друзей с VPN от 30 дней.")
        elif code == "need_own_vpn":
            await message.answer("Нужен свой оплаченный VPN от 30 дней.")
        elif code == "cooldown":
            await message.answer("Не чаще 1 заявки в 7 дней.")
        elif code == "bad_trc20":
            await message.answer(
                "Неверный USDT TRC20 адрес. Нужен адрес Tron на <code>T…</code> (34 символа)."
            )
            return
        elif code == "bad_cryptobot":
            await message.answer("Укажите корректный @username (латиница, 5–32 символа).")
            return
        else:
            await message.answer("Не удалось создать заявку. Проверьте данные и попробуйте снова.")
            return
        await state.clear()
        return
    await state.clear()
    await message.answer(
        referral_withdraw_html(balance=bal, pending=True)
        + f"\n\n✅ Заявка на <b>крипту</b> <code>#{rid}</code> создана.\n"
        f"Реквизиты: <code>{esc(raw)}</code>",
        reply_markup=referral_withdraw_kb(can_request=False),
    )


# backward-compatible alias (old button)
@router.callback_query(F.data == "ref:wd:ask")
async def ref_withdraw_ask_legacy(cb: CallbackQuery, settings: Settings, conn, state: FSMContext) -> None:
    await ref_withdraw_card(cb, settings, conn, state)


@router.callback_query(F.data == "nav:profile")
async def nav_profile(cb: CallbackQuery, settings: Settings, conn, bot: Bot) -> None:
    from bot.keyboards.shop_kb import profile_inline_kb_rows_prefix
    from bot.services.vpn_user_links import append_vpn_copy_link_rows

    await answer_callback_safe(cb)
    text = await profile_body_html(bot, settings, conn, cb.from_user.id)
    b = InlineKeyboardBuilder()
    for row in profile_inline_kb_rows_prefix(settings):
        b.row(*row)
    await append_vpn_copy_link_rows(b, settings=settings, user_id=int(cb.from_user.id))
    b.row(InlineKeyboardButton(text="🔔 Уведомления", callback_data="nav:notify"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(text, reply_markup=b.as_markup())


def _kb_privacy_support(settings: Settings) -> InlineKeyboardMarkup:
    from bot.keyboards.shop_kb import news_channel_url

    b = InlineKeyboardBuilder()
    pu = (settings.privacy_policy_url or "").strip()
    tu = (settings.terms_of_service_url or "").strip()
    ou = (settings.public_offer_url or "").strip()
    ru = (settings.refund_policy_url or "").strip()
    news = news_channel_url(settings)
    if ou:
        b.row(InlineKeyboardButton(text="📜 Публичная оферта", url=ou))
    if ru:
        b.row(InlineKeyboardButton(text="↩️ Политика возвратов", url=ru))
    b.row(InlineKeyboardButton(text="↩️ Сроки возврата", callback_data="sup:refund"))
    if pu:
        b.row(InlineKeyboardButton(text="📄 Политика конфиденциальности", url=pu))
    if tu:
        b.row(InlineKeyboardButton(text="📄 Пользовательское соглашение", url=tu))
    if news:
        b.row(InlineKeyboardButton(text="📢 Новостной канал", url=news))
    b.row(InlineKeyboardButton(text="ℹ️ Частые вопросы", callback_data="sup:faq"))
    b.row(InlineKeyboardButton(text="💳 Оплата и зачисление", callback_data="sup:payfaq"))
    if settings.ui_show_vpn:
        b.row(InlineKeyboardButton(text="🌐 Документы AiMonkeyVPN", callback_data="nav:vpn"))
    b.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    return b.as_markup()


def _kb_faq_support() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛡️ Политика магазина", callback_data="sup:privacy"))
    b.row(InlineKeyboardButton(text="💳 Оплата и зачисление", callback_data="sup:payfaq"))
    b.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    return b.as_markup()


def _kb_payfaq_support() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛡️ Политика магазина", callback_data="sup:privacy"))
    b.row(InlineKeyboardButton(text="ℹ️ Частые вопросы", callback_data="sup:faq"))
    b.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    return b.as_markup()


@router.callback_query(F.data.in_({"sup:privacy", "nav:privacy"}))
async def screen_privacy_support(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        privacy_screen_html(settings),
        reply_markup=_kb_privacy_support(settings),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.in_({"sup:faq", "nav:faq"}))
async def screen_faq_support(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        faq_comprehensive_html(settings),
        reply_markup=_kb_faq_support(),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "nav:reffaq")
async def nav_reffaq(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⬅️ В личный кабинет", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="🏠 В меню", callback_data="nav:hub"))
    await cb.message.edit_text(referral_faq_html(settings), reply_markup=b.as_markup())


@router.callback_query(F.data.in_({"sup:payfaq", "nav:payfaq"}))
async def screen_payfaq_support(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        payment_faq_html(settings),
        reply_markup=_kb_payfaq_support(),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "nav:partners")
async def nav_partners(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="👤 Личный кабинет", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="🔌 Наш API (ключ)", callback_data="nav:api"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(partner_onboarding_html(settings), reply_markup=b.as_markup())


@router.callback_query(F.data == "nav:contest")
async def nav_contest(cb: CallbackQuery, conn) -> None:
    await answer_callback_safe(cb)
    row = await contest_repo.get_active_contest(conn)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    if row is None:
        await cb.message.edit_text(
            "<b>Конкурс партнёров</b>\n\n"
            "Сейчас нет активного конкурса. Следите за объявлениями в канале магазина.\n\n"
            "<i>Метрика: число успешно выданных заказов ваших приглашённых за период конкурса.</i>",
            reply_markup=b.as_markup(),
        )
        return
    title = esc(row["title"])
    prize = esc(row["prize_text"])
    starts = esc(row["starts_at"] or "")
    ends = esc(row["ends_at"] or "")
    board = await contest_repo.leaderboard_for_contest(
        conn, starts_at=str(row["starts_at"]), ends_at=str(row["ends_at"]), limit=12
    )
    lines = [
        f"<b>🏆 {title}</b>\n",
        f"<i>Период:</i> {starts} - {ends}\n",
        f"<b>Призы:</b>\n{prize}\n",
        "<b>Топ партнёров</b> <i>(выданные заказы с рефералом)</i>\n",
    ]
    if not board:
        lines.append("\nПока нет зачётных заказов в этом периоде.")
    else:
        for i, r in enumerate(board, start=1):
            uid = r["referrer_id"]
            vol = float(r["volume_rub"])
            lines.append(f"{i}. <code>{uid}</code> - <b>{r['orders']}</b> зак. · {esc(f'{vol:.0f}')} ₽")
    st = await contest_repo.user_contest_stats(
        conn,
        user_id=cb.from_user.id,
        starts_at=str(row["starts_at"]),
        ends_at=str(row["ends_at"]),
    )
    if st and st["orders"] > 0:
        rk = await contest_repo.rank_for_referrer(
            conn,
            referrer_id=cb.from_user.id,
            starts_at=str(row["starts_at"]),
            ends_at=str(row["ends_at"]),
        )
        rk_s = esc(str(rk)) if rk is not None else " - "
        lines.append(
            f"\n<b>Ваш результат:</b> место <b>{rk_s}</b>, выданных заказов по вашей ссылке: <b>{st['orders']}</b>."
        )
    else:
        lines.append("\n<b>Ваш результат:</b> пока нет выданных заказов по вашим рефералам в этом периоде.")
    await cb.message.edit_text("\n".join(lines), reply_markup=b.as_markup())


@router.callback_query(F.data == "nav:topup")
async def nav_topup(cb: CallbackQuery, conn, settings: Settings) -> None:
    await answer_callback_safe(cb)
    bal = await balance_repo.get_balance(conn, cb.from_user.id)
    b = InlineKeyboardBuilder()
    for amt in _topup_amounts_for_ui(settings):
        kop = _topup_kop(amt)
        b.row(InlineKeyboardButton(text=f"+{amt} ₽", callback_data=f"top:sel:{kop}"))
    b.row(InlineKeyboardButton(text="✍️ Своя сумма", callback_data="top:custom"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    lo, hi = settings.topup_min_rub, settings.topup_max_rub
    await cb.message.edit_text(
        f"<b>Пополнить баланс</b>\n\n"
        f"Текущий баланс: <b>{esc(f'{bal:.2f}')} ₽</b>\n\n"
        "Выберите сумму пополнения или укажите свою.\n"
        f"Диапазон: <b>{lo:g}–{hi:g} ₽</b>. Оплата — LAVA (СБП/карта) или криптовалюта.",
        reply_markup=b.as_markup(),
    )


@router.callback_query(F.data.startswith("top:sel:"))
async def topup_amount_selected(cb: CallbackQuery, conn, settings: Settings) -> None:
    try:
        kop = int(cb.data.split(":")[-1])
    except ValueError:
        await cb.answer("Некорректная сумма", show_alert=True)
        return
    await _topup_show_method_picker(cb, conn, settings, _topup_rub_from_kop(kop))


@router.callback_query(F.data.startswith("top:pay:"))
async def topup_pay_method(cb: CallbackQuery, conn, settings: Settings) -> None:
    parts = cb.data.split(":")
    if len(parts) != 4:
        await cb.answer("Некорректный запрос", show_alert=True)
        return
    method = parts[2]
    if method not in ("lava", "crypto"):
        await cb.answer("Некорректный способ оплаты", show_alert=True)
        return
    try:
        kop = int(parts[3])
    except ValueError:
        await cb.answer("Некорректная сумма", show_alert=True)
        return
    await _topup_run_checkout(
        cb=cb,
        conn=conn,
        settings=settings,
        user_id=cb.from_user.id,
        amount_rub=_topup_rub_from_kop(kop),
        method=method,  # type: ignore[arg-type]
    )


@router.callback_query(F.data.startswith("top:cancel:"))
async def topup_cancel(cb: CallbackQuery, conn, settings: Settings) -> None:
    try:
        tid = int(cb.data.split(":")[-1])
    except ValueError:
        await cb.answer("Некорректная заявка", show_alert=True)
        return
    ok = await balance_repo.cancel_topup(conn, tid, cb.from_user.id)
    if not ok:
        await cb.answer("Заявку нельзя отменить", show_alert=True)
        return
    await answer_callback_safe(cb)
    await cb.message.edit_text(
        f"<b>Заявка #{esc(tid)} отменена</b>",
        reply_markup=hub_menu_kb(settings, user_id=cb.from_user.id),
    )


@router.callback_query(F.data == "top:custom")
async def topup_custom(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await answer_callback_safe(cb)
    await state.set_state(TopupStates.waiting_custom_amount)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:topup"))
    await cb.message.edit_text(
        f"<b>Своя сумма</b>\n\n"
        f"Введите сумму пополнения в ₽ (от {settings.topup_min_rub:g} до {settings.topup_max_rub:g}).",
        reply_markup=b.as_markup(),
    )


@router.message(TopupStates.waiting_custom_amount, F.text)
async def topup_custom_val(message: Message, state: FSMContext, conn, settings: Settings) -> None:
    try:
        amt = float((message.text or "").strip().replace(",", "."))
        lo, hi = settings.topup_min_rub, settings.topup_max_rub
        if amt + 1e-6 < lo or amt - 1e-6 > hi:
            raise ValueError
    except ValueError:
        await message.answer(f"Сумма от {settings.topup_min_rub:g} до {settings.topup_max_rub:g} ₽.")
        return
    await state.clear()
    methods = topup_payment_methods(settings)
    amt = round(amt, 2)
    kop = _topup_kop(amt)
    if not methods:
        await message.answer(
            "Сейчас автоматическая оплата недоступна. Попробуйте позже.",
            reply_markup=hub_menu_kb(settings, user_id=message.from_user.id),
        )
        return
    if len(methods) == 1:
        await _topup_run_checkout(
            message=message,
            conn=conn,
            settings=settings,
            user_id=message.from_user.id,
            amount_rub=amt,
            method=methods[0],
        )
        return
    await message.answer(
        f"<b>Пополнение баланса</b>\n\n"
        f"Сумма: <b>{esc(f'{amt:.2f}')} ₽</b>\n\n"
        "Выберите способ оплаты:",
        reply_markup=_topup_method_kb(kop, settings),
    )


@router.callback_query(F.data == "nav:supp")
async def nav_support(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    await answer_callback_safe(cb)
    await state.clear()
    await cb.message.edit_text(
        "<b>Поддержка</b>\n\n"
        "Здесь: <b>политика и соглашение</b>, <b>сроки возврата</b>, <b>частые вопросы</b>, "
        "раздел про <b>оплату</b> и документы VPN.\n\n"
        "Чтобы связаться с оператором — кнопка <b>«Написать оператору»</b>: сообщение уйдёт "
        "<b>только администрации</b> (другие покупатели его не видят). "
        "Укажите <b>номер заказа</b>, если есть.",
        reply_markup=_support_kb(settings, user_id=cb.from_user.id),
    )


@router.callback_query(F.data == "sup:refund")
async def screen_refund_support(cb: CallbackQuery, settings: Settings) -> None:
    await answer_callback_safe(cb)
    back = InlineKeyboardBuilder()
    ru = (settings.refund_policy_url or "").strip()
    if ru:
        back.row(InlineKeyboardButton(text="📄 Полный текст на сайте", url=ru))
    back.row(InlineKeyboardButton(text="💬 Написать оператору", callback_data="sup:write"))
    back.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    await cb.message.edit_text(
        refund_policy_table_html(settings),
        reply_markup=back.as_markup(),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "sup:write")
async def support_write_start(cb: CallbackQuery, state: FSMContext) -> None:
    await answer_callback_safe(cb)
    await state.set_state(SupportStates.waiting_message)
    back = InlineKeyboardBuilder()
    back.row(InlineKeyboardButton(text="⬅️ Отмена", callback_data="nav:supp"))
    await cb.message.edit_text(
        "<b>Написать оператору</b>\n\n"
        "Одним сообщением опишите проблему. Желательно: <b>номер заказа</b>, "
        "что произошло, способ оплаты.\n\n"
        "Сообщение получит только администрация магазина — не публичный чат.",
        reply_markup=back.as_markup(),
    )


@router.message(SupportStates.waiting_message, F.text)
async def support_write_receive(
    message: Message, state: FSMContext, settings: Settings, conn
) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пустое сообщение. Напишите текст или нажмите «Отмена» в поддержке.")
        return
    if len(text) > 2000:
        await message.answer("Слишком длинно (макс. ~2000 символов). Сократите и отправьте снова.")
        return
    un = message.from_user.username if message.from_user else None
    res = await open_inbot_support_ticket(
        conn,
        settings,
        bot=message.bot,
        telegram_user_id=int(message.from_user.id),
        username=un,
        text=text,
    )
    await state.clear()
    back = InlineKeyboardBuilder()
    back.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    back.row(InlineKeyboardButton(text="🏠 В меню", callback_data="nav:hub"))
    if not res.get("ok"):
        if res.get("error") == "ticket_daily_limit":
            await message.answer(
                "Слишком много обращений за сутки. Попробуйте завтра или укажите номер "
                "заказа в шаблоне и повторите позже.",
                reply_markup=back.as_markup(),
            )
            return
        await message.answer("Не удалось принять обращение. Попробуйте ещё раз.", reply_markup=back.as_markup())
        return
    tid = int(res["ticket_id"])
    await message.answer(
        f"<b>Принято.</b> Тикет <code>#{tid}</code>.\n"
        "Оператор ответит в этом боте. Другие пользователи ваше сообщение не видят.",
        reply_markup=back.as_markup(),
    )


@router.callback_query(F.data.startswith("sup:tpl:"))
async def sup_faq_template(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    key = cb.data.split(":")[-1]
    back = InlineKeyboardBuilder()
    back.row(InlineKeyboardButton(text="💬 Отправить оператору", callback_data="sup:write"))
    back.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:supp"))
    if key == "hint":
        await answer_callback_safe(cb)
        await state.clear()
        await cb.message.edit_text(
            "<b>Как работает поддержка</b>\n\n"
            "Кнопка <b>«Написать оператору»</b> создаёт тикет внутри бота. "
            "Копия уходит только администраторам (<code>ADMIN_IDS</code> / "
            "<code>ASSISTANT_ADMIN_CHAT_ID</code>). "
            "Обычные покупатели чужие обращения не видят.\n\n"
            "Внешний <code>SUPPORT_URL</code> нужен только если это <b>отдельный</b> "
            "чат человека — не ссылка на сам магазинный бот.",
            reply_markup=back.as_markup(),
        )
        return
    body = FAQ_TEMPLATES.get(key)
    if not body:
        await answer_callback_safe(cb)
        return
    await answer_callback_safe(cb)
    await state.clear()
    await cb.message.edit_text(
        body + "\n\n<i>Скопируйте шаблон и нажмите «Написать оператору», затем вставьте текст.</i>",
        reply_markup=back.as_markup(),
    )


async def orders_first_page_html(conn, user_id: int) -> str:
    text, _, _ = await _orders_page_html(conn, user_id, 0)
    return text


