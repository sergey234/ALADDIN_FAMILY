from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.config import Settings
from bot.keyboards.shop_kb import admin_order_kb, admin_sell_kb, admin_topup_kb
from bot.services import balance_repo, orders_repo
from bot.services.order_flow import apply_completed_side_effects
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.sell_repo import get_sell, update_sell_status
from bot.util_html import esc

router = Router(name="admin")


def _is_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.parsed_admin_ids()


@router.message(Command("admin"))
async def cmd_admin(message: Message, settings: Settings, conn) -> None:
    if not _is_admin(message.from_user.id, settings):
        return
    rows = await orders_repo.list_recent_orders(conn, limit=12)
    if not rows:
        await message.answer("<b>Админ</b>: заказов нет.")
        return
    lines = ["<b>Последние заказы</b>\n"]
    for r in rows:
        amt = float(r["rub_after_discounts"])
        lines.append(
            f"#{esc(r['id'])} {esc(r['product_title'])} — <code>{esc(r['status'])}</code> — "
            f"<b>{esc(f'{amt:.2f}')} ₽</b>"
        )
    await message.answer("\n".join(lines))


@router.callback_query(F.data.startswith("adm:"))
async def admin_set_status(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    _, action, oid_s = cb.data.split(":", 2)
    order_id = int(oid_s)
    mapping = {
        "paid": "paid",
        "proc": "processing",
        "done": "completed",
    }
    new_status = mapping.get(action)
    if not new_status:
        await cb.answer()
        return

    order = await orders_repo.get_order(conn, order_id)
    if not order:
        await cb.answer("Заказ не найден", show_alert=True)
        return

    prev_status = str(order["status"])
    await orders_repo.update_status(conn, order_id, new_status)

    if new_status == "completed":
        await apply_completed_side_effects(conn, order_id, settings)

    order2 = await orders_repo.get_order(conn, order_id)
    amt = float(order2["rub_after_discounts"])
    text = (
        f"<b>#{esc(order_id)}</b> → <code>{esc(new_status)}</code>\n\n"
        f"{esc(order2['product_title'])}\n"
        f"user: <code>{esc(order2['user_id'])}</code>\n"
        f"сумма: <b>{esc(f'{amt:.2f}')} ₽</b>"
    )
    await cb.message.edit_text(text, reply_markup=admin_order_kb(order_id))

    try:
        await cb.bot.send_message(
            int(order2["user_id"]),
            f"ℹ️ Заказ <b>#{esc(order_id)}</b>: <code>{esc(new_status)}</code>",
        )
    except Exception:
        pass
    asyncio.create_task(
        emit_order_status_changed(
            db_path=settings.database_path,
            order_id=order_id,
            previous_status=prev_status,
            new_status=new_status,
        )
    )
    await cb.answer("OK")


@router.callback_query(F.data.startswith("top:ok:"))
async def admin_topup_ok(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    tid = int(cb.data.split(":")[-1])
    row = await balance_repo.get_topup(conn, tid)
    if not row:
        await cb.answer("Не найдено", show_alert=True)
        return
    uid = int(row["user_id"])
    ok = await balance_repo.approve_topup(conn, tid)
    if not ok:
        await cb.answer("Уже обработано", show_alert=True)
        return
    await cb.message.edit_text(
        f"<b>Пополнение #{esc(tid)}</b>\nПользователь <code>{esc(uid)}</code>\n<b>✅ Зачислено</b>",
    )
    try:
        await cb.bot.send_message(uid, f"<b>Баланс пополнен</b> по заявке <code>#{esc(tid)}</code>.")
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data.startswith("sel:"))
async def admin_sell_status(cb: CallbackQuery, settings: Settings, conn) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    _, action, sid_s = cb.data.split(":", 2)
    sid = int(sid_s)
    row = await get_sell(conn, sid)
    if not row:
        await cb.answer("Не найдено", show_alert=True)
        return
    uid = int(row["user_id"])
    st_map = {"proc": "processing", "done": "completed", "can": "cancelled"}
    new_st = st_map.get(action)
    if not new_st:
        await cb.answer()
        return
    await update_sell_status(conn, sid, new_st)
    empty = InlineKeyboardMarkup(inline_keyboard=[])
    await cb.message.edit_text(
        f"<b>Выкуп #{esc(sid)}</b> → <code>{esc(new_st)}</code>\n"
        f"user <code>{esc(uid)}</code>",
        reply_markup=admin_sell_kb(sid) if new_st not in ("completed", "cancelled") else empty,
    )
    try:
        await cb.bot.send_message(uid, f"<b>Заявка на выкуп #{esc(sid)}</b>: <code>{esc(new_st)}</code>")
    except Exception:
        pass
    await cb.answer()
