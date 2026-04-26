from __future__ import annotations

import asyncio
import json

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.config import Settings
from bot.keyboards.shop_kb import admin_order_kb, admin_sell_kb, admin_topup_kb
from bot.services import admin_audit_repo, balance_repo, contest_repo, marketing, orders_repo
from bot.services.admin_crypto_paid_gate import crypto_manual_paid_gate_applies
from bot.services.admin_order_ff import ff_context_from_order_row, format_fulfillment_admin_block
from bot.services.alerts import send_alert
from bot.services.contest_dates import normalize_contest_date
from bot.services.buyer_order_notify import buyer_message_admin_status_change
from bot.services.order_flow import apply_completed_side_effects
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.sell_repo import get_sell, update_sell_status
from bot.util_html import esc

router = Router(name="admin")


def _is_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.parsed_admin_ids()


async def _audit_admin(conn, admin_id: int, action: str, **parts: object) -> None:
    payload = json.dumps(parts, ensure_ascii=False) if parts else None
    await admin_audit_repo.append_admin_action(
        conn, admin_user_id=admin_id, action=action, payload_json=payload
    )


def _admin_order_message_text(order_row, order_id: int, *, status_for_header: str | None = None) -> str:
    lbl = status_for_header or str(order_row["status"])
    amt = float(order_row["rub_after_discounts"])
    return (
        f"<b>#{esc(order_id)}</b> → <code>{esc(lbl)}</code>\n\n"
        f"{esc(order_row['product_title'])}\n"
        f"user: <code>{esc(order_row['user_id'])}</code>\n"
        f"сумма: <b>{esc(f'{amt:.2f}')} ₽</b>"
        f"{format_fulfillment_admin_block(order_row)}"
    )


@router.callback_query(F.data.startswith("adm:ff"))
async def admin_fulfill_controls(cb: CallbackQuery, settings: Settings, conn) -> None:
    """Ручной override автовыдачи и сброс полей (план 37-6). Должен быть до обработчика `adm:paid` и т.д."""
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    parts = cb.data.split(":")
    if len(parts) != 3 or parts[0] != "adm":
        await cb.answer()
        return
    action, oid_s = parts[1], parts[2]
    if action not in ("ffman", "ffauto", "ffrst") or not oid_s.isdigit():
        await cb.answer()
        return
    order_id = int(oid_s)

    order = await orders_repo.get_order(conn, order_id)
    if not order:
        await cb.answer("Заказ не найден", show_alert=True)
        return

    st = str(order["status"] or "").strip().lower()
    if st in ("completed", "expired", "refunded", "payment_disputed"):
        await cb.answer("Заказ уже завершён или в споре.", show_alert=True)
        return
    if st not in ("paid", "processing"):
        await cb.answer("Действие только для оплаченных / в работе.", show_alert=True)
        return

    if action == "ffman":
        ok = await orders_repo.set_order_fulfillment_mode(conn, order_id, mode="manual_only")
        if not ok:
            await cb.answer("Не удалось обновить режим.", show_alert=True)
            return
        await _audit_admin(conn, cb.from_user.id, "adm:ffman", order_id=order_id)
    elif action == "ffauto":
        if not settings.is_super_admin(cb.from_user.id):
            await cb.answer("Только супер-админ включает авто снова.", show_alert=True)
            return
        ok = await orders_repo.set_order_fulfillment_mode(conn, order_id, mode="auto")
        if not ok:
            await cb.answer("Не удалось обновить режим.", show_alert=True)
            return
        await _audit_admin(conn, cb.from_user.id, "adm:ffauto", order_id=order_id)
    elif action == "ffrst":
        if not settings.is_super_admin(cb.from_user.id):
            await cb.answer("Только супер-админ сбрасывает поля авто-выдачи.", show_alert=True)
            return
        if st != "paid":
            await cb.answer("Сброс только для заказа в статусе «Оплачен».", show_alert=True)
            return
        ok = await orders_repo.super_reset_paid_auto_fulfill_fields(conn, order_id)
        if not ok:
            await cb.answer("Сброс не применён (проверьте статус заказа).", show_alert=True)
            return
        await _audit_admin(conn, cb.from_user.id, "adm:ffrst", order_id=order_id)
    else:
        await cb.answer()
        return

    order2 = await orders_repo.get_order(conn, order_id)
    await cb.message.edit_text(
        _admin_order_message_text(order2, order_id),
        reply_markup=admin_order_kb(
            order_id,
            settings=settings,
            actor_id=cb.from_user.id,
            order_ff=ff_context_from_order_row(order2),
        ),
    )
    await cb.answer("OK")


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
            f"#{esc(r['id'])} {esc(r['product_title'])} - <code>{esc(r['status'])}</code> - "
            f"<b>{esc(f'{amt:.2f}')} ₽</b>"
        )
    foot = "\n\n<i>Конкурсы партнёров: команда /contest</i>"
    foot += "\n<i>Текст для закрепа канала (оплата по ссылке bc): /channel_checkout_pin</i>"
    if settings.admin_roles_restricted():
        foot += "\n<i>Роли: зачисление топапа / «Оплачен» / «Выдан» и правки конкурсов - только у SUPER_ADMIN_IDS.</i>"
    await message.answer("\n".join(lines) + foot)


@router.message(Command("channel_checkout_pin"))
async def cmd_channel_checkout_pin(message: Message, settings: Settings) -> None:
    """HTML для закрепля в канале: чеклист оплаты по ссылке bc (копировать / переслать в канал)."""
    if not _is_admin(message.from_user.id, settings):
        return
    await message.answer(marketing.channel_pin_bc_checkout_html(settings), disable_web_page_preview=True)


@router.message(Command("admqueue"))
async def cmd_admqueue(message: Message, settings: Settings, conn) -> None:
    """Список заказов для ручного внимания: paid с ошибкой выдачи или долго processing (гибрид G+)."""
    if not _is_admin(message.from_user.id, settings):
        return
    idle = max(1, int(settings.operator_queue_processing_idle_minutes))
    rows = await orders_repo.list_orders_operator_attention_queue(
        conn, processing_idle_minutes=idle, limit=25
    )
    if not rows:
        await message.answer(
            "<b>Очередь внимания</b>\n\n"
            "Нет заказов в статусе «оплачен с ошибкой выдачи» или «в работе» дольше "
            f"<code>{idle}</code> мин. без обновления."
        )
        return
    lines = [
        "<b>Очередь внимания</b> (до 25 заказов)\n",
        f"<i>processing без движения: &gt; {esc(str(idle))} мин.</i>\n",
    ]
    for r in rows:
        oid = int(r["id"])
        st = esc(str(r["status"] or ""))
        title = esc(str(r["product_title"] or ""))[:60]
        err_raw = str(r["fulfillment_last_error"] or "").strip()
        err = esc(err_raw[:120]) if err_raw else " - "
        note = esc(str(r["user_note"] or "")[:40])
        lines.append(
            f"#{esc(str(oid))} <code>{st}</code> {title}\n"
            f"  получ.: <code>{note}</code>\n"
            f"  err: <code>{err}</code>\n"
        )
    lines.append(
        "\n<i>Откройте карточку из уведомления о заказе или найдите номер в админ-чате; "
        "кнопки статусов - там же.</i>"
    )
    await message.answer("\n".join(lines))


@router.message(Command("contest"))
async def cmd_contest(message: Message, command: CommandObject, settings: Settings, conn) -> None:
    if not _is_admin(message.from_user.id, settings):
        return
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "<b>Конкурсы партнёров</b>\n\n"
            "<code>/contest list</code> - список\n"
            "<code>/contest new Заголовок | Текст приза | YYYY-MM-DD | YYYY-MM-DD [on]</code>\n"
            "  последний аргумент <code>on</code> - сразу сделать единственным активным\n"
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
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может деактивировать все конкурсы.")
            return
        await contest_repo.deactivate_all(conn)
        await _audit_admin(conn, message.from_user.id, "contest:deactivate_all")
        await message.answer("<b>Конкурсы</b>: все деактивированы.")
        return
    if cmd == "activate" and len(parts) >= 2:
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может активировать конкурс.")
            return
        try:
            cid = int(parts[1])
        except ValueError:
            await message.answer("Некорректный ID.")
            return
        ok = await contest_repo.set_contest_active(conn, cid, active=True)
        if ok:
            await _audit_admin(conn, message.from_user.id, "contest:activate", contest_id=cid)
        await message.answer("Активирован." if ok else "Не найдено.")
        return
    if cmd == "new":
        if not settings.is_super_admin(message.from_user.id):
            await message.answer("Только супер-админ может создавать конкурс.")
            return
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
        await _audit_admin(
            conn,
            message.from_user.id,
            "contest:new",
            contest_id=oid,
            title=title,
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
        "paidbg": "paid",
        "proc": "processing",
        "done": "completed",
        "refund": "refunded",
        "disp": "payment_disputed",
        "dispok": "paid",
    }
    new_status = mapping.get(action)
    if not new_status:
        await cb.answer()
        return

    if new_status in ("refunded", "payment_disputed") and not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ: сторно / спор по заказу.", show_alert=True)
        return

    if new_status in ("paid", "completed") and not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ отмечает «Оплачен» или «Выдан».", show_alert=True)
        return

    order = await orders_repo.get_order(conn, order_id)
    if not order:
        await cb.answer("Заказ не найден", show_alert=True)
        return

    prev_status = str(order["status"])
    if action == "dispok" and prev_status != "payment_disputed":
        await cb.answer("«Снять спор» только из статуса спора.", show_alert=True)
        return
    if new_status == "paid" and prev_status == "pending_payment":
        applies = crypto_manual_paid_gate_applies(order, settings)
        if action == "paid" and applies:
            await cb.answer(
                "Заказ в ожидании оплаты через Crypto Pay / xRocket: дождитесь вебхука. "
                "Ручное «Оплачен» здесь отключено. Если вебхук невозможен - кнопка break-glass в карточке заказа.",
                show_alert=True,
            )
            return
        if action == "paidbg":
            if not applies:
                await cb.answer(
                    "Break-glass только для заказов в ожидании оплаты с крипто-счётом "
                    "(включён Crypto Pay или xRocket). Иначе используйте «Оплачен».",
                    show_alert=True,
                )
                return
    break_glass_payload: dict[str, object] | None = None
    if action == "paidbg":
        amount = float(order["rub_after_discounts"] or 0.0)
        super_admin_count = len(
            [x for x in settings.parsed_admin_ids() if settings.is_super_admin(x)]
        )
        two_eyes_threshold = float(settings.break_glass_two_eyes_threshold_rub or 0.0)
        two_eyes_required = bool(two_eyes_threshold > 0 and amount >= two_eyes_threshold and super_admin_count >= 2)
        break_glass_payload = {
            "reason_code": "webhook_unavailable_manual_paid",
            "provider": str(order["invoice_last_provider"] or order["payment_method"] or "unknown"),
            "external_invoice_id": str(order["invoice_last_external_id"] or ""),
            "evidence_ref": f"order:{order_id}",
            "two_eyes_required": two_eyes_required,
            "two_eyes_threshold_rub": two_eyes_threshold,
            "order_amount_rub": amount,
        }

    try:
        await orders_repo.update_status(conn, order_id, new_status)
    except ValueError as exc:
        if "invalid_order_transition" in str(exc) or "order_not_found" in str(exc):
            await cb.answer("Недопустимый переход статуса для этого заказа.", show_alert=True)
            return
        raise

    if new_status == "completed" and prev_status != "completed":
        await apply_completed_side_effects(conn, order_id, settings)

    audit_action = "adm:paid_break_glass" if action == "paidbg" else f"adm:{action}"
    await _audit_admin(
        conn,
        cb.from_user.id,
        audit_action,
        order_id=order_id,
        from_status=prev_status,
        to_status=new_status,
        **(break_glass_payload or {}),
    )
    if action == "paidbg" and break_glass_payload is not None:
        amount = float(break_glass_payload["order_amount_rub"])
        await send_alert(
            settings=settings,
            severity="warning",
            title="break-glass paid applied",
            body=(
                f"order_id={order_id} admin_id={cb.from_user.id} amount_rub={amount:.2f} "
                f"provider={break_glass_payload['provider']} "
                f"external_invoice_id={break_glass_payload['external_invoice_id']} "
                f"evidence_ref={break_glass_payload['evidence_ref']} "
                f"two_eyes_required={break_glass_payload['two_eyes_required']}"
            ),
            dedupe_key=f"break_glass_paid:{order_id}",
        )

    order2 = await orders_repo.get_order(conn, order_id)
    text = _admin_order_message_text(order2, order_id, status_for_header=new_status)
    await cb.message.edit_text(
        text,
        reply_markup=admin_order_kb(
            order_id,
            settings=settings,
            actor_id=cb.from_user.id,
            order_ff=ff_context_from_order_row(order2),
        ),
    )

    buyer_text = buyer_message_admin_status_change(order_id=order_id, new_status=new_status)
    if buyer_text:
        try:
            await cb.bot.send_message(int(order2["user_id"]), buyer_text)
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
    if not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ может зачислить топап.", show_alert=True)
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
    await _audit_admin(conn, cb.from_user.id, "top:ok", topup_id=tid, user_id=uid)
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
    if new_st in ("completed", "cancelled") and not settings.is_super_admin(cb.from_user.id):
        await cb.answer("Только супер-админ завершает или отменяет выкуп.", show_alert=True)
        return
    await update_sell_status(conn, sid, new_st)
    await _audit_admin(conn, cb.from_user.id, f"sel:{action}", sell_id=sid, to_status=new_st)
    empty = InlineKeyboardMarkup(inline_keyboard=[])
    await cb.message.edit_text(
        f"<b>Выкуп #{esc(sid)}</b> → <code>{esc(new_st)}</code>\n"
        f"user <code>{esc(uid)}</code>",
        reply_markup=admin_sell_kb(sid, settings=settings, actor_id=cb.from_user.id)
        if new_st not in ("completed", "cancelled")
        else empty,
    )
    try:
        await cb.bot.send_message(uid, f"<b>Заявка на выкуп #{esc(sid)}</b>: <code>{esc(new_st)}</code>")
    except Exception:
        pass
    await cb.answer()
