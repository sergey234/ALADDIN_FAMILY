from __future__ import annotations

import re

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.keyboards.shop_kb import (
    confirm_order_kb,
    hub_menu_kb,
    lava_payment_kb,
    payment_methods_kb,
    premium_dest_kb,
    verify_username_kb,
)
from bot.services import balance_repo, orders_repo, users_repo
from bot.services.catalog import Product, products_by_id
from bot.services.lava_api import create_invoice_payment_url, lava_checkout_configured
from bot.services.payments_stub import crypto_payment_block_html, fiat_placeholder_html
from bot.services.fx_display import fx_payment_hints_html
from bot.services.pricing import quote_product, rub_per_100_stars_display
from bot.states.checkout import CheckoutStates
from bot.util_html import esc

router = Router(name="shop")

_USERNAME_RE = re.compile(r"^@?[a-zA-Z0-9_]{4,32}$")


def _fmt_quote_html(p: Product, q, settings: Settings) -> str:
    lines = [
        f"{p.emoji} <b>{esc(p.title)}</b>",
        "",
        f"База: <b>{esc(f'{q.rub_list:.2f}')} ₽</b>",
    ]
    if q.rub_referral_discount > 0:
        lines.append(f"Реф. скидка: <b>−{esc(f'{q.rub_referral_discount:.2f}')} ₽</b>")
    if q.rub_wholesale_discount > 0:
        lines.append(f"Опт Stars: <b>−{esc(f'{q.rub_wholesale_discount:.2f}')} ₽</b>")
    lines.append(f"К оплате: <b>{esc(f'{q.rub_final:.2f}')} ₽</b> (~{esc(f'{q.usd:.2f}')} USD)")
    body = "\n".join(lines)
    fx = fx_payment_hints_html(settings, rub_final=q.rub_final, usd_base=q.usd)
    return body + fx


async def _is_first_purchase(conn, user_id: int) -> bool:
    """Реф. скидка до первого выданного (completed) заказа — см. pricing.quote_product."""
    return await orders_repo.count_user_completed_orders(conn, user_id) == 0


def _payment_kb(product_id: str, balance: float, rub_final: float):
    show_full = balance + 1e-6 >= rub_final
    show_partial = (not show_full) and balance >= 0.01 and (rub_final - balance) > 0.01
    return payment_methods_kb(
        product_id,
        show_full_balance=show_full,
        show_partial_mix=show_partial,
        balance=balance,
        rub_final=rub_final,
    )


async def _present_fiat_checkout(
    cb: CallbackQuery,
    settings: Settings,
    *,
    order_id: int,
    rub_due: float,
    intro_html: str,
    usd_base: float,
) -> None:
    """
    После создания заказа со статусом «ожидает оплаты»:
    - если в .env настроены LAVA — показываем кнопку на страницу оплаты LAVA;
    - иначе — текстовая инструкция (ручная оплата / донастройка).
    """
    memo = f"ORDER{order_id}"
    pay_url = await create_invoice_payment_url(
        settings,
        order_id=order_id,
        sum_rub=rub_due,
        comment=memo[:255],
    )
    fx = fx_payment_hints_html(settings, rub_final=rub_due, usd_base=usd_base)
    if pay_url:
        tail = (
            fx
            + "\n\n<b>Оплата через LAVA</b> (<a href=\"https://lava.ru\">lava.ru</a>) — СБП, банковские карты "
            "и другие способы по тарифу вашего проекта в LAVA.\n"
            "<b>Нажмите кнопку ниже</b> — откроется страница оплаты. "
            "После успешной оплаты статус заказа в боте обновится автоматически.\n\n"
            "<i>Отдельное сообщение с кнопками «Оплачен / В работе / Выдан» — это панель для операторов магазина, "
            "не нажимайте их как покупатель.</i>"
        )
        await cb.message.edit_text(intro_html + tail, reply_markup=lava_payment_kb(pay_url))
        return
    missing_lava = ""
    if not lava_checkout_configured(settings):
        missing_lava = (
            "\n\n<b>Почему нет кнопки LAVA</b>\n"
            "Для автоматического счёта в LAVA в <code>shared/.env</code> на сервере должны быть заданы одновременно:\n"
            "<code>LAVA_SHOP_ID</code>, <code>LAVA_SECRET_KEY</code> и публичный HTTPS "
            "<code>LAVA_HOOK_URL</code> на ваш Partner API (путь вида <code>…/v1/payments/lava-webhook</code>).\n"
            "Пока они не заполнены или LAVA вернула ошибку — оплата идёт по инструкции ниже или вручную через поддержку."
        )
    else:
        missing_lava = (
            "\n\n<b>Счёт LAVA не создан</b> (ошибка ответа API). Заказ в статусе «ожидает оплаты». "
            "Попробуйте оформить заказ позже или напишите в поддержку с номером заказа."
        )
    instr = fiat_placeholder_html(settings, order_id=order_id, rub=rub_due)
    await cb.message.edit_text(
        intro_html
        + fx
        + missing_lava
        + f"\n\n<b>{esc(instr.title)}</b>\n{instr.body_html}",
        reply_markup=hub_menu_kb(),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("<b>Оформление сброшено.</b>", reply_markup=hub_menu_kb())


@router.callback_query(F.data.startswith("buy:"))
async def open_product(cb: CallbackQuery, products: list[Product], settings: Settings, conn, state: FSMContext) -> None:
    await state.clear()
    pid = cb.data.split(":", 1)[1]
    pmap = products_by_id(products)
    p = pmap.get(pid)
    if not p:
        await cb.answer("Товар не найден", show_alert=True)
        return
    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    if p.kind == "premium":
        text = (
            _fmt_quote_html(p, q, settings)
            + "\n\nКому оформляем <b>Telegram Premium</b>?"
        )
        await cb.message.edit_text(text, reply_markup=premium_dest_kb(p.id))
    else:
        hint = ""
        if p.kind == "stars":
            r100 = rub_per_100_stars_display(products, settings, is_first_order=is_first)
            if r100 is not None:
                hint = f"\n\n<i>Ориентир: от {esc(f'{r100:.2f}')} ₽ за 100 ⭐.</i>"
            hint += "\n<i>Подарок уйдёт на @username, который укажете после выбора оплаты.</i>"
        if p.kind == "gift":
            hint = "\n\n<i>Укажите @username получателя после выбора способа оплаты.</i>"
        bal = await balance_repo.get_balance(conn, cb.from_user.id)
        text = _fmt_quote_html(p, q, settings) + hint + "\n\n<b>Способ оплаты</b>"
        await cb.message.edit_text(
            text,
            reply_markup=_payment_kb(p.id, bal, q.rub_final),
        )
    await cb.answer()


@router.callback_query(F.data.startswith("prem:"))
async def premium_pick_dest(cb: CallbackQuery, products: list[Product], settings: Settings, conn, state: FSMContext) -> None:
    _, who, pid = cb.data.split(":", 2)
    pmap = products_by_id(products)
    p = pmap.get(pid)
    if not p or p.kind != "premium":
        await cb.answer("Товар не найден", show_alert=True)
        return
    await state.update_data(product_id=pid, premium_self=(who == "slf"))
    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    bal = await balance_repo.get_balance(conn, cb.from_user.id)
    text = _fmt_quote_html(p, q, settings) + "\n\n<b>Способ оплаты</b>"
    await cb.message.edit_text(
        text,
        reply_markup=_payment_kb(pid, bal, q.rub_final),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("pay:"))
async def choose_payment(cb: CallbackQuery, state: FSMContext, products: list[Product], settings: Settings, conn) -> None:
    parts = cb.data.split(":", 2)
    if len(parts) < 3:
        await cb.answer()
        return
    _, method, pid = parts
    if method not in ("fiat", "crypto", "bal", "mixfi", "mixcr"):
        await cb.answer()
        return
    pmap = products_by_id(products)
    if pid not in pmap:
        await cb.answer("Товар не найден", show_alert=True)
        return
    p = pmap[pid]
    data = await state.get_data()
    premium_self = bool(data.get("premium_self"))

    if p.kind == "premium" and premium_self:
        un = cb.from_user.username
        if not un:
            await cb.answer("Нужен @username в Telegram или выберите «Подарок другому»", show_alert=True)
            return
        recipient = f"@{un}"
        await state.update_data(product_id=pid, payment=method, recipient=recipient)
        await state.set_state(CheckoutStates.waiting_confirm)
        is_first = await _is_first_purchase(conn, cb.from_user.id)
        q = quote_product(p, settings, is_first_order=is_first)
        await cb.message.edit_text(
            _fmt_quote_html(p, q, settings)
            + f"\n\n<b>Получатель:</b> <code>{esc(recipient)}</code> (ваш аккаунт)",
            reply_markup=confirm_order_kb(),
        )
        await cb.answer()
        return

    await state.update_data(product_id=pid, payment=method)
    await state.set_state(CheckoutStates.waiting_recipient)
    await cb.message.edit_text(
        "✍️ Укажите <b>@username</b> получателя в Telegram.\nПример: <code>@nickname</code>",
    )
    await cb.answer()


@router.message(CheckoutStates.waiting_recipient, F.text)
async def read_recipient(message: Message, state: FSMContext, products: list[Product], settings: Settings, conn) -> None:
    handle = (message.text or "").strip()
    if not _USERNAME_RE.match(handle):
        await message.answer("Похоже, это не username. Пример: <code>@nickname</code>")
        return
    if not handle.startswith("@"):
        handle = "@" + handle

    data = await state.get_data()
    pid = data.get("product_id")
    pmap = products_by_id(products)
    p = pmap.get(pid or "")
    if not p:
        await state.clear()
        await message.answer("Сессия устарела.", reply_markup=hub_menu_kb())
        return

    await state.update_data(recipient=handle)
    await state.set_state(CheckoutStates.waiting_verify_username)
    await message.answer(
        f"<b>Проверьте получателя</b>\n<code>{esc(handle)}</code>\n\n"
        "Если ошиблись — нажмите «Исправить» и введите снова.",
        reply_markup=verify_username_kb(),
    )


@router.callback_query(F.data == "usr:ok", CheckoutStates.waiting_verify_username)
async def verify_username_ok(cb: CallbackQuery, state: FSMContext, products: list[Product], settings: Settings, conn) -> None:
    data = await state.get_data()
    pid = data.get("product_id")
    recipient = data.get("recipient")
    pmap = products_by_id(products)
    p = pmap.get(pid or "")
    if not p or not recipient:
        await state.clear()
        await cb.message.edit_text("Сессия устарела.", reply_markup=hub_menu_kb())
        await cb.answer()
        return
    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    await state.set_state(CheckoutStates.waiting_confirm)
    await cb.message.edit_text(
        _fmt_quote_html(p, q, settings)
        + f"\n\n<b>Получатель:</b> <code>{esc(recipient)}</code>\n"
        "Нажмите «Создать заказ».",
        reply_markup=confirm_order_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "usr:ed", CheckoutStates.waiting_verify_username)
async def verify_username_edit(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CheckoutStates.waiting_recipient)
    await cb.message.edit_text(
        "✍️ Введите <b>@username</b> получателя снова.\nПример: <code>@nickname</code>",
    )
    await cb.answer()


@router.callback_query(F.data == "order:cancel")
async def order_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.edit_text("<b>Оформление отменено.</b>", reply_markup=hub_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "order:submit", CheckoutStates.waiting_confirm)
async def order_submit(
    cb: CallbackQuery,
    state: FSMContext,
    products: list[Product],
    settings: Settings,
    conn,
    bot: Bot,
) -> None:
    data = await state.get_data()
    pid = data.get("product_id")
    payment = data.get("payment")
    recipient = data.get("recipient")
    pmap = products_by_id(products)
    p = pmap.get(pid or "")
    if not p or payment not in ("fiat", "crypto", "bal", "mixfi", "mixcr") or not recipient:
        await cb.answer("Сессия устарела", show_alert=True)
        await state.clear()
        return

    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    row = await users_repo.get_user(conn, cb.from_user.id)
    referrer_id = int(row["referrer_id"]) if row and row["referrer_id"] is not None else None
    rub = q.rub_final

    if payment == "bal":
        try:
            order_id = await orders_repo.create_paid_order_from_balance(
                conn,
                user_id=cb.from_user.id,
                product_id=p.id,
                product_title=f"{p.emoji} {p.title}",
                usd_base=q.usd,
                rub_before=q.rub_list,
                rub_after=rub,
                referral_discount_rub=q.rub_referral_discount,
                wholesale_discount_rub=q.rub_wholesale_discount,
                referrer_id=referrer_id,
                user_note=str(recipient),
            )
        except ValueError:
            await cb.answer("Недостаточно средств на балансе", show_alert=True)
            return
        await state.clear()
        body = (
            f"<b>Заказ оплачен с баланса</b>\n"
            f"ID: <code>{esc(order_id)}</code>\n"
            f"Сумма: <b>{esc(f'{rub:.2f}')} ₽</b>\n"
            f"Получатель: <code>{esc(recipient)}</code>\n\n"
            "Дальше: оператор оформит выдачу на Fragment и обновит статус."
        )
        await cb.message.edit_text(body, reply_markup=hub_menu_kb())
        await cb.answer()
        await _notify_admins(bot, settings, conn, order_id)
        return

    if payment in ("mixfi", "mixcr"):
        bal_now = await balance_repo.get_balance(conn, cb.from_user.id)
        apply = round(min(bal_now, rub), 2)
        if apply <= 0:
            await cb.answer("Недостаточно средств на балансе", show_alert=True)
            return
        pm = "mix_fiat" if payment == "mixfi" else "mix_crypto"
        try:
            order_id = await orders_repo.create_order_with_balance_partial(
                conn,
                user_id=cb.from_user.id,
                product_id=p.id,
                product_title=f"{p.emoji} {p.title}",
                payment_method=pm,
                usd_base=q.usd,
                rub_before=q.rub_list,
                rub_invoice_total=rub,
                referral_discount_rub=q.rub_referral_discount,
                wholesale_discount_rub=q.rub_wholesale_discount,
                referrer_id=referrer_id,
                user_note=str(recipient),
                balance_apply=apply,
            )
        except ValueError:
            await cb.answer("Не удалось списать баланс", show_alert=True)
            return
        await state.clear()
        row = await orders_repo.get_order(conn, order_id)
        due = orders_repo.amount_due_external(row)
        if due <= 0.01:
            body = (
                f"<b>Заказ оплачен</b> (часть с баланса)\n"
                f"ID: <code>{esc(order_id)}</code>\n"
                f"С баланса: <b>{esc(f'{apply:.2f}')} ₽</b>\n"
                f"Всего: <b>{esc(f'{rub:.2f}')} ₽</b>\n"
                f"Получатель: <code>{esc(recipient)}</code>"
            )
            await cb.message.edit_text(body, reply_markup=hub_menu_kb())
        elif payment == "mixfi":
            intro = (
                f"<b>Заказ #{esc(order_id)}</b>\n"
                f"С баланса списано: <b>{esc(f'{apply:.2f}')} ₽</b>\n"
                f"<b>К доплате:</b> <b>{esc(f'{due:.2f}')} ₽</b>\n"
            )
            await _present_fiat_checkout(
                cb, settings, order_id=order_id, rub_due=due, intro_html=intro, usd_base=q.usd
            )
        else:
            usd_part = q.usd * (due / rub) if rub > 1e-6 else q.usd
            pay = crypto_payment_block_html(settings, order_id=order_id, rub=due, usd_for_fx=usd_part)
            await cb.message.edit_text(
                f"<b>Заказ #{esc(order_id)}</b>\n"
                f"С баланса: <b>{esc(f'{apply:.2f}')} ₽</b>\n"
                f"<b>К доплате криптой:</b> <b>{esc(f'{due:.2f}')} ₽</b>\n\n" + pay,
                reply_markup=hub_menu_kb(),
            )
        await cb.answer()
        await _notify_admins(bot, settings, conn, order_id)
        return

    order_id = await orders_repo.create_order(
        conn,
        user_id=cb.from_user.id,
        product_id=p.id,
        product_title=f"{p.emoji} {p.title}",
        payment_method=str(payment),
        usd_base=q.usd,
        rub_before=q.rub_list,
        rub_after=rub,
        referral_discount_rub=q.rub_referral_discount,
        wholesale_discount_rub=q.rub_wholesale_discount,
        referrer_id=referrer_id,
        commission_rub=0.0,
        user_note=str(recipient),
        status="pending_payment",
    )

    await state.clear()

    if payment == "crypto":
        pay = crypto_payment_block_html(settings, order_id=order_id, rub=rub, usd_for_fx=q.usd)
        await cb.message.edit_text(
            f"<b>Заказ создан</b>\nID: <code>{esc(order_id)}</code>\n\n" + pay,
            reply_markup=hub_menu_kb(),
        )
    else:
        intro = (
            f"<b>Заказ создан</b>\nID: <code>{esc(order_id)}</code>\n"
            f"<i>Статус: ожидает оплаты</i> — дальше откроется оплата (LAVA или инструкция).\n"
        )
        await _present_fiat_checkout(cb, settings, order_id=order_id, rub_due=rub, intro_html=intro, usd_base=q.usd)
    await cb.answer()

    await _notify_admins(bot, settings, conn, order_id)


async def _notify_admins(bot: Bot, settings: Settings, conn, order_id: int) -> None:
    order = await orders_repo.get_order(conn, order_id)
    if not order:
        return
    u = await users_repo.get_user(conn, int(order["user_id"]))
    uname = u["username"] if u else None
    user_line = f"@{uname}" if uname else f"id {order['user_id']}"
    amt = float(order["rub_after_discounts"])
    due = orders_repo.amount_due_external(order)
    try:
        bap = float(order["balance_applied_rub"] or 0)
    except (KeyError, TypeError):
        bap = 0.0
    extra = ""
    if bap > 0.01:
        extra = f"\nС баланса: <b>{esc(f'{bap:.2f}')} ₽</b>\nК доплате: <b>{esc(f'{due:.2f}')} ₽</b>"
    text = (
        "<b>Админам магазина</b> <i>(служебное сообщение, не страница оплаты LAVA)</i>\n"
        "Кнопки «Оплачен / В работе / Выдан» — для операторов после проверки оплаты.\n\n"
        "<b>Новый заказ</b>\n\n"
        f"ID: <code>{esc(order['id'])}</code>\n"
        f"Пользователь: {esc(user_line)}\n"
        f"Товар: {esc(order['product_title'])}\n"
        f"Оплата: <code>{esc(order['payment_method'])}</code>\n"
        f"Сумма заказа: <b>{esc(f'{amt:.2f}')} ₽</b>{extra}\n"
        f"Получатель: <code>{esc(order['user_note'] or '')}</code>\n"
        f"Статус: <code>{esc(order['status'])}</code>"
    )
    from bot.keyboards.shop_kb import admin_order_kb

    kb = admin_order_kb(int(order["id"]))
    buyer_id = int(order["user_id"])
    admin_ids = settings.parsed_admin_ids()
    for admin_id in admin_ids:
        if admin_id == buyer_id and len(admin_ids) > 1:
            # Покупатель сам в ADMIN_IDS: не дублировать ему панель оператора, если есть другие админы.
            continue
        try:
            await bot.send_message(admin_id, text, reply_markup=kb)
        except Exception:
            continue
