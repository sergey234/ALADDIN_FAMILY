from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.config import Settings
from bot.keyboards.shop_kb import admin_order_kb, admin_sell_kb, admin_topup_kb
from bot.services import balance_repo, contest_repo, orders_repo
from bot.services.contest_dates import normalize_contest_date
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
    await message.answer("\n".join(lines) + "\n\n<i>Конкурсы партнёров: команда /contest</i>")


@router.message(Command("contest"))
async def cmd_contest(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not _is_admin(message.from_user.id, settings):
        return
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "<b>Конкурсы партнёров</b>\n\n"
            "<code>/contest list</code> — список\n"
            "<code>/contest new Заголовок | Текст приза | YYYY-MM-DD | YYYY-MM-DD [on]</code>\n"
            "  последний аргумент <code>on</code> — сразу сделать единственным активным\n"
            "<code>/contest activate ID</code>\n"
            "<code>/contest deactivate_all</code>",
        )
        return
    parts = raw.split()
    cmd = parts[0].lower()
    if cmd == "list":
        rows = await contest_repo.list_contests(conn, limit=15)
        if not rows:
            await message.answer("<b>Конкурсы</b>: записей нет.")
            return
        lines = ["<b>Конкурсы</b>\n"]
        for r in rows:
            act = "✅" if int(r["is_active"] or 0) else "○"
            lines.append(
                f"{act} <code>#{r['id']}</code> {esc(r['title'])} · {esc(r['starts_at'])} → {esc(r['ends_at'])}"
            )
        await message.answer("\n".join(lines))
        return
    if cmd == "deactivate_all":
        await contest_repo.deactivate_all(conn)
        await message.answer("<b>Конкурсы</b>: все деактивированы.")
        return
    if cmd == "activate" and len(parts) >= 2:
        try:
            cid = int(parts[1])
        except ValueError:
            await message.answer("Некорректный ID.")
            return
        ok = await contest_repo.set_contest_active(conn, cid, active=True)
        await message.answer("Активирован." if ok else "Не найдено.")
        return
    if cmd == "new":
        body = raw.removeprefix("new").strip()
        if not body:
            await message.answer("Укажите поля через | после <code>new</code>.")
            return
        seg = [x.strip() for x in body.split("|")]
        if len(seg) < 4:
            await message.answer("Нужно 4 поля: Заголовок | Приз | дата начала | дата конца")
            return
        title, prize, ds, de = seg[:4]
        activate = len(seg) >= 5 and seg[4].lower() in ("on", "1", "yes", "true")
        try:
            s_norm = normalize_contest_date(ds, end_of_day=False)
            e_norm = normalize_contest_date(de, end_of_day=True)
        except Exception:
            await message.answer("Ошибка дат. Формат: YYYY-MM-DD")
            return
        oid = await contest_repo.create_contest(
            conn,
            title=title,
            prize_text=prize,
            starts_at=s_norm,
            ends_at=e_norm,
            activate=activate,
        )
        await message.answer(f"<b>Создан конкурс</b> <code>#{oid}</code>." + (" Активен." if activate else ""))
        return
    await message.answer("Неизвестная подкоманда. См. /contest")


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
