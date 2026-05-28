from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import brand_constants as brand
from bot.config import Settings
from bot.keyboards.shop_kb import hub_menu_kb, order_detail_kb, products_kb
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
)
from bot.services.pricing import format_rub_usd_html, rub_per_100_stars_display
from bot.services.sell_repo import count_user_sells, create_sell_request, list_user_sells_page
from bot.states.checkout import ApiKeyStates, SellStates, TopupStates
from bot.support_links import (
    is_telegram_contact,
    support_order_question_url,
    support_prefill_url,
    telegram_support_base,
)
from bot.ui_copy import ONBOARDING_SCREEN_2
from bot.util_html import esc

router = Router(name="hub")

ORDERS_PAGE = 5
SELLS_PAGE = 5

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


def _support_kb(settings: Settings):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛡️ Политика Stars / Premium", callback_data="sup:privacy"))
    b.row(InlineKeyboardButton(text="📚 Частые вопросы", callback_data="sup:faq"))
    b.row(InlineKeyboardButton(text="💳 Оплата и зачисление", callback_data="sup:payfaq"))
    base = telegram_support_base(settings)
    if base and is_telegram_contact(base):
        u1 = support_prefill_url(settings, "Заказ # - оплатил, статус не обновился") or base
        u2 = support_prefill_url(settings, "Заказ # - не пришли Stars") or base
        u3 = support_prefill_url(settings, "Заказ # - ошибся в @username") or base
        b.row(InlineKeyboardButton(text="💳 Оплатил - статус не меняется", url=u1))
        b.row(InlineKeyboardButton(text="⭐ Не пришли Stars", url=u2))
        b.row(InlineKeyboardButton(text="@username ошибка", url=u3))
        b.row(InlineKeyboardButton(text="💬 Написать в поддержку", url=base))
    elif base:
        b.row(InlineKeyboardButton(text="🔗 Связаться с поддержкой", url=base))
    else:
        b.row(InlineKeyboardButton(text="🧾 Шаблон: оплата / статус", callback_data="sup:tpl:pay"))
        b.row(InlineKeyboardButton(text="⭐ Шаблон: Stars", callback_data="sup:tpl:stars"))
        b.row(InlineKeyboardButton(text="👤 Шаблон: username", callback_data="sup:tpl:user"))
        b.row(
            InlineKeyboardButton(
                text="🧭 Как указать SUPPORT_URL",
                callback_data="sup:tpl:hint",
            )
        )
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
    from bot.services.vpn_user_links import invite_ref_telegram_url

    me = await bot.get_me()
    bot_user = me.username or "your_bot"
    ref_link = invite_ref_telegram_url(bot_user, user_id)
    stats = await users_repo.user_stats(conn, user_id)
    br = float(stats["balance_rub"])
    rr = float(stats["ref_balance_rub"])
    sp = float(stats["spent_rub"])
    md = esc(settings.marketing_max_discount_percent)
    rb = esc(settings.ref_buyer_discount_percent)
    rc = esc(settings.ref_commission_percent)
    co = esc(stats["completed_orders"])
    r_inv = int(stats["referral_invited_count"])
    r_done = int(stats["referral_buyers_completed_count"])
    r_earn = float(stats["referral_commission_earned_rub"])
    rf = int(settings.vpn_referral_referrer_days)
    ff = int(settings.vpn_referral_friend_days)
    lines = [
        f"<b>Мой профиль</b> · {brand.BRAND_SHORT} · {esc(brand.SHOP_BOT_HANDLE)}\n\n"
        "<b>Пригласить друга в ALADDIN</b>\n"
        f"<code>{esc(ref_link)}</code>\n\n"
        "<b>Как это работает</b>\n"
        "• Друг открывает бота по ссылке и оформляет заказ в магазине.\n"
        f"• Пока у него не было <b>выданной</b> покупки — скидка <b>{rb}%</b> на первый заказ "
        f"(Stars, Premium{', ' + esc(brand.VPN_PRODUCT_NAME) if settings.ui_show_vpn else ''}).\n"
        f"• После первой <b>выданной</b> покупки друга — бонус <b>{rc}%</b> на ваши покупки "
        "в магазине (оплата «С баланса»).\n",
    ]
    if settings.ui_show_vpn and (ff > 0 or rf > 0):
        lines.append(
            f"• Если друг <b>впервые получит</b> {esc(brand.VPN_PRODUCT_NAME)} — дополнительно "
            f"ему <b>+{ff}</b> дн., вам <b>+{rf}</b> дн. (один раз на приглашённого).\n"
        )
    lines += [
        f"• «До {md}%» — в рамках акций и способов оплаты, см. прайс.\n\n"
        "<b>Статистика приглашений</b>\n"
        f"• Перешли по ссылке: <b>{r_inv}</b>\n"
        f"• С выданной покупкой: <b>{r_done}</b>\n"
        f"• Бонусов на покупки (накоплено): <b>{esc(f'{r_earn:.2f}')} ₽</b>\n",
    ]
    if settings.ui_show_vpn:
        vs = await vpn_referral_repo.user_vpn_referral_stats(conn, user_id)
        n_buy = int(vs["vpn_referral_buyers"])
        n_days = int(vs["vpn_referral_days_earned"])
        if n_buy > 0 or n_days > 0:
            lines.append(
                f"• Друзей с первой выдачей VPN: <b>{n_buy}</b> · бонусных дней вам: <b>{n_days}</b>\n"
            )
    lines += [
        "\n"
        f"<b>Счёт в магазине</b> (для оплаты заказов): <b>{esc(f'{br:.2f}')} ₽</b>\n"
        f"<b>Бонус на покупки</b>: <b>{esc(f'{rr:.2f}')} ₽</b>\n"
        f"Заказов выдано: <b>{co}</b>\n"
        f"Сумма покупок: <b>{esc(f'{sp:.2f}')} ₽</b>",
    ]
    return "".join(lines)


async def _orders_page_html(conn, user_id: int, page: int) -> tuple[str, bool, bool]:
    total = await orders_repo.count_user_orders(conn, user_id)
    offset = page * ORDERS_PAGE
    rows = await orders_repo.list_user_orders_page(conn, user_id, limit=ORDERS_PAGE, offset=offset)
    has_prev = page > 0
    has_next = offset + len(rows) < total
    if not rows:
        return "<b>Мои заказы</b>\n\nПока заказов нет.", has_prev, has_next
    lines = ["<b>Мои заказы</b>\n", "<i>Нажмите кнопку с номером заказа.</i>\n"]
    status_ru = {
        "pending_payment": "ожидает оплаты",
        "paid": "оплачен",
        "processing": "в обработке",
        "completed": "выдан",
        "expired": "срок оплаты истёк",
        "refunded": "сторно / возврат",
        "payment_disputed": "спор по оплате",
    }
    for r in rows:
        rid = r["id"]
        created = esc(r["created_at"] or "")
        amt = float(r["rub_after_discounts"])
        usd = float(r["usd_base"] or 0.0)
        st = esc(status_ru.get(r["status"], r["status"]))
        lines.append(
            f"#{esc(rid)} - {esc(r['product_title'])}\n"
            f"  <i>{created}</i> · <b>{format_rub_usd_html(amt, usd)}</b> - {st}\n"
        )
    return "\n".join(lines), has_prev, has_next


async def _sells_page_html(conn, user_id: int, page: int) -> tuple[str, bool, bool]:
    total = await count_user_sells(conn, user_id)
    offset = page * SELLS_PAGE
    rows = await list_user_sells_page(conn, user_id, limit=SELLS_PAGE, offset=offset)
    has_prev = page > 0
    has_next = offset + len(rows) < total
    status_ru = {
        "new": "новая",
        "processing": "в работе",
        "completed": "выполнена",
        "cancelled": "отменена",
    }
    if not rows:
        return "<b>Мои заявки на выкуп</b>\n\nПока нет заявок.", has_prev, has_next
    lines = ["<b>Мои заявки на выкуп</b>\n"]
    for r in rows:
        sid = int(r["id"])
        stars = int(r["stars"])
        rub = float(r["rub_offer"])
        st = esc(status_ru.get(r["status"], r["status"]))
        created = esc(r["created_at"] or "")
        lines.append(
            f"#{esc(sid)} · <b>{stars} ⭐</b> · {esc(f'{rub:.2f}')} ₽ - {st}\n"
            f"<i>{created}</i>\n"
        )
    return "\n".join(lines), has_prev, has_next


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
    if fid2:
        # Keep hub controls on a text message so downstream handlers can safely use edit_text.
        await cb.message.answer_photo(fid2)
        await cb.message.answer(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings))
    else:
        await cb.message.edit_text(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings))
    await cb.answer()


@router.callback_query(F.data == "nav:hub")
async def nav_hub(cb: CallbackQuery, settings: Settings) -> None:
    await cb.message.edit_text(ONBOARDING_SCREEN_2, reply_markup=hub_menu_kb(settings))
    await cb.answer()


@router.callback_query(F.data == "nav:orders:noop")
async def orders_noop(cb: CallbackQuery) -> None:
    await cb.answer()


@router.callback_query(F.data.startswith("nav:orders:"))
async def nav_orders(cb: CallbackQuery, conn) -> None:
    suf = cb.data.split(":")[-1]
    try:
        page = int(suf)
    except ValueError:
        await cb.answer()
        return
    text, has_prev, has_next = await _orders_page_html(conn, cb.from_user.id, page)
    rows = await orders_repo.list_user_orders_page(conn, cb.from_user.id, limit=ORDERS_PAGE, offset=page * ORDERS_PAGE)
    b = InlineKeyboardBuilder()
    for r in rows:
        rid = int(r["id"])
        amt = float(r["rub_after_discounts"])
        usd = float(r["usd_base"] or 0.0)
        b.row(InlineKeyboardButton(text=f"#{rid} · {format_rub_usd_html(amt, usd, rub_decimals=0)}", callback_data=f"ord:{rid}"))
    row = []
    if has_prev:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav:orders:{page - 1}"))
    row.append(InlineKeyboardButton(text=f"·{page + 1}·", callback_data="nav:orders:noop"))
    if has_next:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"nav:orders:{page + 1}"))
    if row:
        b.row(*row)
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("ord:"))
async def order_detail(cb: CallbackQuery, settings: Settings, conn) -> None:
    oid = int(cb.data.split(":")[1])
    order = await orders_repo.get_order(conn, oid)
    if not order or int(order["user_id"]) != cb.from_user.id:
        await cb.answer("Заказ не найден", show_alert=True)
        return
    sup = support_order_question_url(settings, oid)
    amt = float(order["rub_after_discounts"])
    usd = float(order["usd_base"] or 0.0)
    bap = float(order["balance_applied_rub"] or 0)
    due = orders_repo.amount_due_external(order)
    st_raw = str(order["status"])
    st_ru = {
        "pending_payment": "ожидает оплаты",
        "paid": "оплачен",
        "processing": "в обработке",
        "completed": "выдан",
        "expired": "срок оплаты истёк",
        "refunded": "сторно / возврат",
        "payment_disputed": "спор по оплате",
    }.get(st_raw, st_raw)
    text = (
        f"<b>Заказ #{esc(oid)}</b>\n"
        f"<i>{esc(order['created_at'] or '')}</i>\n\n"
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
        f"Статус: <b>{esc(st_ru)}</b>\n"
        f"Получатель: <code>{esc(order['user_note'] or '')}</code>\n\n"
    )
    if st_raw == "expired":
        text += "<i>Счёт не оплачен в срок. Если оплатили - напишите в поддержку с номером заказа.</i>"
    elif st_raw == "refunded":
        text += "<i>По этому заказу зафиксировано сторно или возврат средств со стороны магазина/поддержки.</i>"
    elif st_raw == "payment_disputed":
        text += "<i>Идёт разбор по оплате; при необходимости поддержка напишет или ответьте в тикет с номером заказа.</i>"
    else:
        text += "<i>После оплаты статус обновит оператор.</i>"
    await cb.message.edit_text(text, reply_markup=order_detail_kb(oid, sup))
    await cb.answer()


@router.callback_query(F.data == "nav:buy_stars")
async def nav_buy_stars(cb: CallbackQuery, products: list[Product], settings: Settings, conn) -> None:
    items = sort_for_display([p for p in products if p.kind == "stars"])
    if not items:
        await cb.message.edit_text(
            "<b>Купить Stars</b>\n\n"
            "В каталоге нет позиций <code>kind: stars</code> в <code>products.yaml</code>.\n"
            "Добавьте пакеты Stars и перезапустите бота.",
            reply_markup=hub_menu_kb(),
        )
        await cb.answer()
        return
    is_first = await orders_repo.count_user_completed_orders(conn, cb.from_user.id) == 0
    r100 = rub_per_100_stars_display(products, settings, is_first_order=is_first)
    sub = ""
    if r100 is not None:
        sub = f"\n\n<i>Ориентир: от {esc(f'{r100:.2f}')} ₽ за 100 ⭐.</i>"
    sub += "\n<i>Подарок уйдёт на @username после выбора оплаты.</i>"
    await cb.message.edit_text(f"<b>Купить Stars</b>{sub}", reply_markup=products_kb(items))
    await cb.answer()


@router.callback_query(F.data == "nav:premium")
async def nav_premium(cb: CallbackQuery, products: list[Product]) -> None:
    items = sort_for_display([p for p in products if p.kind == "premium" and not p.hide_from_menu])
    if not items:
        await cb.message.edit_text(
            "<b>Купить Premium</b>\n\n"
            "Нет позиций <code>kind: premium</code> в <code>products.yaml</code>.",
            reply_markup=hub_menu_kb(),
        )
        await cb.answer()
        return
    await cb.message.edit_text(
        "<b>Купить Premium</b>\n\n"
        "<i>Выберите срок → кому (себе или подарок) → оплату.</i>",
        reply_markup=products_kb(items),
    )
    await cb.answer()


@router.callback_query(F.data == "nav:gifts")
async def nav_gifts(cb: CallbackQuery, products: list[Product]) -> None:
    items = sort_for_display([p for p in products if p.kind == "gift"])
    if not items:
        await cb.message.edit_text(
            "<b>Подарки</b>\n\nДобавьте позиции <code>kind: gift</code> в <code>products.yaml</code>.",
            reply_markup=hub_menu_kb(),
        )
    else:
        await cb.message.edit_text(
            "<b>Подарки</b>\n\n<i>Оплата → @получателя → выдача оператором.</i>",
            reply_markup=products_kb(items),
        )
    await cb.answer()


@router.callback_query(F.data == "nav:receipts")
async def nav_receipts(cb: CallbackQuery, conn) -> None:
    cur = await conn.execute(
        """
        SELECT id, created_at, rub_after_discounts, usd_base, product_title FROM orders
        WHERE user_id = ? AND status = 'completed' ORDER BY id DESC LIMIT 12
        """,
        (cb.from_user.id,),
    )
    rows = await cur.fetchall()
    if not rows:
        await cb.message.edit_text(
            "<b>Выданные</b>\n\nЗавершённых заказов пока нет.",
            reply_markup=hub_menu_kb(),
        )
    else:
        b = InlineKeyboardBuilder()
        for r in rows:
            rid = int(r["id"])
            amt = float(r["rub_after_discounts"])
            usd = float(r["usd_base"] or 0.0)
            b.row(InlineKeyboardButton(text=f"#{rid} · {format_rub_usd_html(amt, usd, rub_decimals=0)}", callback_data=f"ord:{rid}"))
        b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
        await cb.message.edit_text(
            "<b>Выданные</b>\n\nВыберите завершённый заказ - откроется карточка. Для PDF уточните в поддержке.",
            reply_markup=b.as_markup(),
        )
    await cb.answer()


@router.callback_query(F.data == "nav:api")
async def nav_api(cb: CallbackQuery, settings: Settings) -> None:
    await cb.message.edit_text(
        "<b>Наш API</b> - для <b>вашего бота, сайта или приложения</b>\n\n"
        "Создание заказов, статусы, пополнения и исходящие вебхуки - по HTTPS, заголовок <code>X-API-KEY</code> "
        "(ключ выпускается ниже). Не встраивайте ключ в публичный фронт - только server-to-server.\n\n"
        "<i>Подробный сценарий «приглашение друзей vs API» — кнопка «Партнёрам» в главном меню.</i>",
        reply_markup=_api_kb(settings),
    )
    await cb.answer()


@router.callback_query(F.data == "api:partner_key")
async def api_partner_key_menu(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not (settings.api_key_pepper or "").strip():
        await cb.answer("Укажите API_KEY_PEPPER в .env на сервере.", show_alert=True)
        return
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
    await cb.answer()


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
        reply_markup=hub_menu_kb(),
    )
    for aid in settings.parsed_admin_ids():
        try:
            await bot.send_message(
                aid,
                f"<b>API #{esc(rid)}</b>\n<code>{message.from_user.id}</code>\n{esc(contact)}\n{esc(comment)}",
            )
        except Exception:
            pass


@router.callback_query(F.data == "nav:ref")
async def nav_ref(cb: CallbackQuery, settings: Settings, conn, bot: Bot) -> None:
    from bot.services.vpn_user_links import invite_ref_telegram_url

    me = await bot.get_me()
    bot_user = me.username or "your_bot"
    uid = cb.from_user.id
    ref_link = invite_ref_telegram_url(bot_user, uid)
    stats = await users_repo.user_stats(conn, uid)
    r_inv = int(stats["referral_invited_count"])
    r_done = int(stats["referral_buyers_completed_count"])
    r_earn = float(stats["referral_commission_earned_rub"])
    rb = esc(settings.ref_buyer_discount_percent)
    rc = esc(settings.ref_commission_percent)
    rf = int(settings.vpn_referral_referrer_days)
    ff = int(settings.vpn_referral_friend_days)
    text = (
        f"<b>Пригласить друга</b> · {brand.BRAND_SHORT} · {esc(brand.SHOP_BOT_HANDLE)}\n\n"
        f"<code>{esc(ref_link)}</code>\n\n"
        f"<b>Условия:</b> −{rb}% другу до первой <b>выданной</b> покупки; "
        f"бонус {rc}% на ваши покупки в магазине после первой выдачи друга."
    )
    if settings.ui_show_vpn and (ff > 0 or rf > 0):
        text += (
            f"\nЕсли друг <b>впервые получит</b> {esc(brand.VPN_PRODUCT_NAME)} — "
            f"дополнительно +{ff} дн. ему, +{rf} дн. вам."
        )
    text += (
        "\n\n<b>Статистика</b>\n"
        f"• Перешли по ссылке: <b>{r_inv}</b>\n"
        f"• С выданной покупкой: <b>{r_done}</b>\n"
        f"• Бонусов на покупки (накоплено): <b>{esc(f'{r_earn:.2f}')} ₽</b>"
    )
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📖 Подробнее", callback_data="nav:reffaq"))
    b.row(InlineKeyboardButton(text="👤 Полный профиль", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data == "nav:profile")
async def nav_profile(cb: CallbackQuery, settings: Settings, conn, bot: Bot) -> None:
    text = await profile_body_html(bot, settings, conn, cb.from_user.id)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📖 Как работает приглашение", callback_data="nav:reffaq"))
    b.row(InlineKeyboardButton(text="📤 Мои заявки на выкуп", callback_data="nav:sells:0"))
    b.row(InlineKeyboardButton(text="💸 Продать Stars", callback_data="nav:sell_stars"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data == "nav:sells:noop")
async def sells_noop(cb: CallbackQuery) -> None:
    await cb.answer()


@router.callback_query(F.data == "nav:sells")
async def nav_sells_legacy(cb: CallbackQuery, conn) -> None:
    await _render_sells_page(cb, conn, 0)


@router.callback_query(F.data.startswith("nav:sells:"))
async def nav_sells_page(cb: CallbackQuery, conn) -> None:
    suf = cb.data.split(":")[-1]
    try:
        page = int(suf)
    except ValueError:
        await cb.answer()
        return
    await _render_sells_page(cb, conn, page)


async def _render_sells_page(cb: CallbackQuery, conn, page: int) -> None:
    text, has_prev, has_next = await _sells_page_html(conn, cb.from_user.id, page)
    rows = await list_user_sells_page(conn, cb.from_user.id, limit=SELLS_PAGE, offset=page * SELLS_PAGE)
    b = InlineKeyboardBuilder()
    row = []
    if has_prev:
        row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav:sells:{page - 1}"))
    row.append(InlineKeyboardButton(text=f"·{page + 1}·", callback_data="nav:sells:noop"))
    if has_next:
        row.append(InlineKeyboardButton(text="▶️", callback_data=f"nav:sells:{page + 1}"))
    if row:
        b.row(*row)
    b.row(InlineKeyboardButton(text="⬅️ В профиль", callback_data="nav:profile"))
    await cb.message.edit_text(text, reply_markup=b.as_markup())
    await cb.answer()


def _kb_privacy_support(settings: Settings) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    pu = (settings.privacy_policy_url or "").strip()
    tu = (settings.terms_of_service_url or "").strip()
    if pu:
        b.row(InlineKeyboardButton(text="📄 Политика конфиденциальности", url=pu))
    if tu:
        b.row(InlineKeyboardButton(text="📄 Пользовательское соглашение", url=tu))
    b.row(InlineKeyboardButton(text="ℹ️ Частые вопросы", callback_data="sup:faq"))
    b.row(InlineKeyboardButton(text="💳 Оплата и зачисление", callback_data="sup:payfaq"))
    if settings.ui_show_vpn:
        b.row(InlineKeyboardButton(text="🌐 Документы AiMonkeyVPN", callback_data="nav:vpn"))
    b.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    return b.as_markup()


def _kb_faq_support() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛡️ Политика Stars / Premium", callback_data="sup:privacy"))
    b.row(InlineKeyboardButton(text="💳 Оплата и зачисление", callback_data="sup:payfaq"))
    b.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    return b.as_markup()


def _kb_payfaq_support() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛡️ Политика Stars / Premium", callback_data="sup:privacy"))
    b.row(InlineKeyboardButton(text="ℹ️ Частые вопросы", callback_data="sup:faq"))
    b.row(InlineKeyboardButton(text="⬅️ В поддержку", callback_data="nav:supp"))
    return b.as_markup()


@router.callback_query(F.data.in_({"sup:privacy", "nav:privacy"}))
async def screen_privacy_support(cb: CallbackQuery, settings: Settings) -> None:
    await cb.message.edit_text(
        privacy_screen_html(settings),
        reply_markup=_kb_privacy_support(settings),
        disable_web_page_preview=True,
    )
    await cb.answer()


@router.callback_query(F.data.in_({"sup:faq", "nav:faq"}))
async def screen_faq_support(cb: CallbackQuery, settings: Settings) -> None:
    await cb.message.edit_text(
        faq_comprehensive_html(settings),
        reply_markup=_kb_faq_support(),
        disable_web_page_preview=True,
    )
    await cb.answer()


@router.callback_query(F.data == "nav:reffaq")
async def nav_reffaq(cb: CallbackQuery, settings: Settings) -> None:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⬅️ В профиль", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="🏠 В меню", callback_data="nav:hub"))
    await cb.message.edit_text(referral_faq_html(settings), reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data.in_({"sup:payfaq", "nav:payfaq"}))
async def screen_payfaq_support(cb: CallbackQuery, settings: Settings) -> None:
    await cb.message.edit_text(
        payment_faq_html(settings),
        reply_markup=_kb_payfaq_support(),
        disable_web_page_preview=True,
    )
    await cb.answer()


@router.callback_query(F.data == "nav:partners")
async def nav_partners(cb: CallbackQuery, settings: Settings) -> None:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👥 Пригласить друга", callback_data="nav:ref"))
    b.row(InlineKeyboardButton(text="👤 Мой профиль", callback_data="nav:profile"))
    b.row(InlineKeyboardButton(text="🔌 Наш API (ключ)", callback_data="nav:api"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(partner_onboarding_html(settings), reply_markup=b.as_markup())
    await cb.answer()


@router.callback_query(F.data == "nav:contest")
async def nav_contest(cb: CallbackQuery, conn) -> None:
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
        await cb.answer()
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
    await cb.answer()


@router.callback_query(F.data == "nav:topup")
async def nav_topup(cb: CallbackQuery, conn, settings: Settings) -> None:
    bal = await balance_repo.get_balance(conn, cb.from_user.id)
    b = InlineKeyboardBuilder()
    lo, hi = settings.topup_min_rub, settings.topup_max_rub
    for amt in (500, 1000, 3000, 5000):
        if lo - 1e-6 <= amt <= hi + 1e-6:
            b.row(InlineKeyboardButton(text=f"+{amt} ₽", callback_data=f"top:amt:{amt}"))
    b.row(InlineKeyboardButton(text="✏️ Своя сумма", callback_data="top:custom"))
    b.row(InlineKeyboardButton(text="⬅️ В меню", callback_data="nav:hub"))
    await cb.message.edit_text(
        f"<b>Пополнить баланс</b>\n\nТекущий: <b>{esc(f'{bal:.2f}')} ₽</b>\n"
        "Выберите сумму - заявка уйдёт админу на зачисление.",
        reply_markup=b.as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("top:amt:"))
async def topup_fixed(cb: CallbackQuery, conn, bot: Bot, settings: Settings) -> None:
    amt = float(cb.data.split(":")[-1])
    try:
        tid = await balance_repo.create_topup_request(
            conn, user_id=cb.from_user.id, amount_rub=amt, settings=settings
        )
    except ValueError as e:
        msg = {
            "topup_amount_invalid": "Сумма вне допустимого диапазона.",
            "topup_pending_cap": "Слишком много заявок на пополнение в ожидании. Дождитесь зачисления или отмены.",
            "topup_rate_limit": "Подождите немного перед следующей заявкой на пополнение.",
        }.get(str(e), "Не удалось создать заявку.")
        await cb.answer(msg, show_alert=True)
        return
    from bot.keyboards.shop_kb import admin_topup_kb

    for aid in settings.parsed_admin_ids():
        try:
            kb = admin_topup_kb(tid, settings=settings, actor_id=aid)
            msg_kw: dict = {
                "chat_id": aid,
                "text": f"<b>Пополнение #{esc(tid)}</b>\n<code>{cb.from_user.id}</code> · <b>{amt:.2f} ₽</b>",
            }
            if kb.inline_keyboard:
                msg_kw["reply_markup"] = kb
            await bot.send_message(**msg_kw)
        except Exception:
            pass
    await cb.message.edit_text(
        f"<b>Заявка #{esc(tid)}</b> на <b>{amt:.2f} ₽</b>.\nПереведите по реквизитам от оператора.",
        reply_markup=hub_menu_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "top:custom")
async def topup_custom(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await state.set_state(TopupStates.waiting_custom_amount)
    await cb.message.edit_text(
        f"<b>Своя сумма</b>\nВведите ₽ от {settings.topup_min_rub:g} до {settings.topup_max_rub:g}."
    )
    await cb.answer()


@router.message(TopupStates.waiting_custom_amount, F.text)
async def topup_custom_val(message: Message, state: FSMContext, conn, bot: Bot, settings: Settings) -> None:
    try:
        amt = float((message.text or "").strip().replace(",", "."))
        lo, hi = settings.topup_min_rub, settings.topup_max_rub
        if amt + 1e-6 < lo or amt - 1e-6 > hi:
            raise ValueError
    except ValueError:
        await message.answer(f"Сумма от {settings.topup_min_rub:g} до {settings.topup_max_rub:g} ₽.")
        return
    await state.clear()
    try:
        tid = await balance_repo.create_topup_request(
            conn, user_id=message.from_user.id, amount_rub=amt, settings=settings
        )
    except ValueError as e:
        msg = {
            "topup_amount_invalid": f"Сумма от {settings.topup_min_rub:g} до {settings.topup_max_rub:g} ₽.",
            "topup_pending_cap": "Слишком много заявок в ожидании.",
            "topup_rate_limit": "Подождите перед следующей заявкой.",
        }.get(str(e), "Не удалось создать заявку.")
        await message.answer(msg, reply_markup=hub_menu_kb())
        return
    from bot.keyboards.shop_kb import admin_topup_kb

    for aid in settings.parsed_admin_ids():
        try:
            kb = admin_topup_kb(tid, settings=settings, actor_id=aid)
            msg_kw: dict = {
                "chat_id": aid,
                "text": f"<b>Пополнение #{esc(tid)}</b>\n<code>{message.from_user.id}</code> · <b>{amt:.2f} ₽</b>",
            }
            if kb.inline_keyboard:
                msg_kw["reply_markup"] = kb
            await bot.send_message(**msg_kw)
        except Exception:
            pass
    await message.answer(f"<b>Заявка #{esc(tid)}</b> создана.", reply_markup=hub_menu_kb())


@router.callback_query(F.data == "nav:sell_stars")
async def nav_sell(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    await state.set_state(SellStates.waiting_stars_amount)
    await cb.message.edit_text(
        f"<b>Продать Stars</b>\n\n"
        f"Ориентир: <b>{settings.sell_offer_rub_per_100_stars:.2f} ₽</b> / 100 ⭐\n"
        f"Лимит: {settings.sell_min_stars}–{settings.sell_max_stars} ⭐\n\n"
        "Введите количество ⭐ одним числом.",
    )
    await cb.answer()


@router.message(SellStates.waiting_stars_amount, F.text)
async def sell_amount(message: Message, state: FSMContext, settings: Settings, conn, bot: Bot) -> None:
    try:
        stars = int((message.text or "").strip().replace(" ", ""))
    except ValueError:
        await message.answer("Введите целое число.")
        return
    if stars < settings.sell_min_stars or stars > settings.sell_max_stars:
        await message.answer("Вне лимита по количеству.")
        return
    await state.clear()
    rub = round(stars / 100.0 * settings.sell_offer_rub_per_100_stars, 2)
    sid = await create_sell_request(conn, user_id=message.from_user.id, stars=stars, rub_offer=rub)
    from bot.keyboards.shop_kb import admin_sell_kb

    for aid in settings.parsed_admin_ids():
        try:
            await bot.send_message(
                aid,
                f"<b>Выкуп #{esc(sid)}</b>\n<code>{message.from_user.id}</code> · {stars} ⭐ · {rub:.2f} ₽",
                reply_markup=admin_sell_kb(sid, settings=settings, actor_id=aid),
            )
        except Exception:
            pass
    await message.answer(
        f"<b>Заявка #{esc(sid)}</b>: {stars} ⭐, ориентир {rub:.2f} ₽.",
        reply_markup=hub_menu_kb(),
    )


@router.callback_query(F.data == "nav:supp")
async def nav_support(cb: CallbackQuery, settings: Settings) -> None:
    await cb.message.edit_text(
        "<b>Поддержка</b>\n\n"
        "Здесь: <b>политика и соглашение</b> (Telegraph), <b>частые вопросы</b>, раздел про <b>оплату</b>, "
        "а ниже - быстрые шаблоны и связь с оператором.\n\n"
        "Опишите проблему и <b>номер заказа</b> (или заявки на пополнение), если обращаетесь в чат.",
        reply_markup=_support_kb(settings),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("sup:tpl:"))
async def sup_faq_template(cb: CallbackQuery, settings: Settings) -> None:
    key = cb.data.split(":")[-1]
    back = InlineKeyboardBuilder()
    back.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:supp"))
    if key == "hint":
        await cb.message.edit_text(
            "<b>Поддержка в .env</b>\n\n"
            "Укажите <code>SUPPORT_URL</code> (любая ссылка) или <code>SUPPORT_USERNAME</code> "
            "(ник без @) - тогда появятся кнопки с переходом в чат и префиллом текста.\n"
            "Если ничего не задано, используйте шаблоны ниже и свой канал связи.",
            reply_markup=back.as_markup(),
        )
        await cb.answer()
        return
    body = FAQ_TEMPLATES.get(key)
    if not body:
        await cb.answer()
        return
    await cb.message.edit_text(body, reply_markup=back.as_markup())
    await cb.answer()


async def orders_first_page_html(conn, user_id: int) -> str:
    text, _, _ = await _orders_page_html(conn, user_id, 0)
    return text


