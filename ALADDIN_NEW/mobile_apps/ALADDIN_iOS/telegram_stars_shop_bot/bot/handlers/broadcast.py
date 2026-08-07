"""Ручная маркетинговая рассылка /admin_broadcast + отписка."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.handlers.admin import _is_admin, _require_admin_message
from bot.services import broadcast_repo
from bot.services.broadcast_send import broadcast_mode_kb, run_broadcast
from bot.states.broadcast import BroadcastStates
from bot.util_html import esc

router = Router(name="broadcast")


@router.message(Command("admin_broadcast"))
async def cmd_admin_broadcast(message: Message, settings: Settings, state: FSMContext) -> None:
    if not await _require_admin_message(message, settings):
        return
    await state.set_state(BroadcastStates.waiting_text)
    await message.answer(
        "<b>📣 Рассылка акций</b>\n\n"
        "Пришлите <b>текст</b> (HTML можно).\n"
        "Дальше выберете: тест себе → админы → когорта / все.\n\n"
        "<i>VPN-напоминания (trial/expiry) этой командой не трогаются.</i>\n"
        "Отмена: /cancel_broadcast"
    )


@router.message(Command("cancel_broadcast"))
async def cmd_cancel_broadcast(message: Message, settings: Settings, state: FSMContext) -> None:
    if not await _require_admin_message(message, settings):
        return
    await state.clear()
    await message.answer("Рассылка отменена.")


@router.message(Command("admin_broadcast_stats"))
async def cmd_admin_broadcast_stats(
    message: Message, command: CommandObject, settings: Settings, conn
) -> None:
    if not await _require_admin_message(message, settings):
        return
    await broadcast_repo.ensure_broadcast_schema(conn)
    parts = (command.args or "").split()
    if not parts or not parts[0].isdigit():
        unsub = await broadcast_repo.count_unsubscribed(conn)
        await message.answer(
            f"Пример: <code>/admin_broadcast_stats 12</code>\n"
            f"Сейчас отписаны от акций: <b>{esc(str(unsub))}</b>"
        )
        return
    row = await broadcast_repo.get_broadcast(conn, int(parts[0]))
    if not row:
        await message.answer("Рассылка не найдена.")
        return
    unsub = await broadcast_repo.count_unsubscribed(conn)
    await message.answer(
        f"<b>Рассылка #{esc(str(row['id']))}</b>\n"
        f"mode: <code>{esc(row['mode'])}</code> · status: <code>{esc(row['status'])}</code>\n"
        f"sent: <b>{esc(str(row['sent_count']))}</b> · "
        f"fail: <b>{esc(str(row['fail_count']))}</b> · "
        f"skip: <b>{esc(str(row['skip_count']))}</b>\n"
        f"Отписаны от акций (всего): <b>{esc(str(unsub))}</b>"
    )


@router.message(BroadcastStates.waiting_text)
async def broadcast_got_text(message: Message, settings: Settings, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id, settings):
        await state.clear()
        return
    text = (message.html_text or message.text or "").strip()
    if not text:
        await message.answer("Пустой текст — пришлите ещё раз или /cancel_broadcast")
        return
    if len(text) > 3900:
        await message.answer("Слишком длинно (макс ~3900). Сократите.")
        return
    await state.update_data(body_html=text)
    await message.answer(
        "<b>Превью:</b>\n\n" + text + "\n\nКуда отправить?",
        reply_markup=broadcast_mode_kb(),
    )


@router.callback_query(F.data == "bc:cancel")
async def bc_cancel(cb: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    await state.clear()
    await cb.message.edit_text("Рассылка отменена.")
    await cb.answer()


@router.callback_query(F.data.startswith("bc:run:"))
async def bc_run(cb: CallbackQuery, settings: Settings, conn, state: FSMContext, bot) -> None:
    if not _is_admin(cb.from_user.id, settings):
        await cb.answer("Нет доступа", show_alert=True)
        return
    data = await state.get_data()
    body = (data.get("body_html") or "").strip()
    if not body:
        await cb.answer("Сначала /admin_broadcast и текст", show_alert=True)
        return
    mode = (cb.data or "").removeprefix("bc:run:")
    await cb.answer("Запускаю…")
    await cb.message.edit_text(f"⏳ Рассылка <code>{esc(mode)}</code>…")
    stats = await run_broadcast(
        bot, settings, conn, admin_user_id=cb.from_user.id, mode=mode, body_html=body
    )
    await state.clear()
    await cb.message.answer(
        f"✅ <b>Готово</b> #{esc(str(stats['broadcast_id']))}\n"
        f"mode: <code>{esc(mode)}</code>\n"
        f"получателей: <b>{esc(str(stats['recipients']))}</b>\n"
        f"sent: <b>{esc(str(stats['sent']))}</b> · "
        f"fail: <b>{esc(str(stats['fail']))}</b> · "
        f"skip: <b>{esc(str(stats['skip']))}</b>\n"
        f"отписаны от акций (всего): <b>{esc(str(stats['unsubscribed_total']))}</b>\n\n"
        f"Стата: <code>/admin_broadcast_stats {stats['broadcast_id']}</code>"
    )


@router.callback_query(F.data == "bc:unsub")
async def bc_unsub(cb: CallbackQuery, conn) -> None:
    await broadcast_repo.ensure_broadcast_schema(conn)
    await broadcast_repo.set_marketing_opt_in(conn, cb.from_user.id, False)
    await cb.answer("Отписались от акций", show_alert=True)
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await cb.message.answer(
        "🔕 Акции больше не приходят.\n"
        "Включить снова: Профиль → 🔔 Уведомления.\n"
        "<i>Сервисные VPN-напоминания по-прежнему могут приходить.</i>"
    )


async def present_notify_settings(cb: CallbackQuery, conn) -> None:
    from bot.util_telegram import answer_callback_safe

    await answer_callback_safe(cb)
    await broadcast_repo.ensure_broadcast_schema(conn)
    on = await broadcast_repo.is_marketing_opt_in(conn, cb.from_user.id)
    status = "включены ✅" if on else "выключены 🔕"
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text="Выключить акции" if on else "Включить акции",
            callback_data="bc:opt:toggle",
        )
    )
    b.row(InlineKeyboardButton(text="⬅️ В личный кабинет", callback_data="nav:profile"))
    await cb.message.edit_text(
        "<b>🔔 Уведомления</b>\n\n"
        f"Акции и новости магазина: <b>{status}</b>\n\n"
        "<i>VPN trial/expiry напоминания — отдельно, их отписка не отключает.</i>",
        reply_markup=b.as_markup(),
    )


@router.callback_query(F.data == "bc:opt:toggle")
async def bc_opt_toggle(cb: CallbackQuery, conn) -> None:
    await broadcast_repo.ensure_broadcast_schema(conn)
    cur = await broadcast_repo.is_marketing_opt_in(conn, cb.from_user.id)
    await broadcast_repo.set_marketing_opt_in(conn, cb.from_user.id, not cur)
    await present_notify_settings(cb, conn)


@router.callback_query(F.data == "nav:notify")
async def nav_notify(cb: CallbackQuery, conn) -> None:
    await present_notify_settings(cb, conn)
