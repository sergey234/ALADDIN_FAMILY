from __future__ import annotations

from bot.config import Settings
from bot.services import orders_repo
from bot.util_html import esc


async def operator_bc_manual_checklist_html(
    conn: aiosqlite.Connection,
    settings: Settings,
    order: aiosqlite.Row,
) -> str:
    """
    Короткая памятка для оператора при ручном «Оплачен» после оплаты по универсальной ссылке bc.
    Пустая строка, если в настройках нет bc-URL (при стандартной загрузке Settings подставляется дефолтный магазин).
    """
    univers = (getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip()
    if not univers:
        return ""
    oid = int(order["id"])
    uid = int(order["user_id"])
    due = float(orders_repo.amount_due_external(order))
    total = float(order["rub_after_discounts"] or 0)
    created = str(order["created_at"] or "").strip()
    memo = f"ORDER{oid}"
    ids = await orders_repo.list_user_pending_payment_order_ids(conn, uid, limit=12)
    n = len(ids)
    id_str = ", ".join(str(i) for i in ids[:10])
    bc_min = float(getattr(settings, "ckassa_bc_display_min_rub", 50.0) or 50.0)
    if bc_min < 1.0:
        bc_min = 50.0
    lines = [
        "",
        "<b>Памятка оператору (ручное «Оплачен», оплата по ссылке bc)</b>",
        f"• В ЛК Ckassa сверить сумму: <b>{esc(f'{due:.2f}')} ₽</b> к доплате снаружи (по заказу всего {esc(f'{total:.2f}')} ₽).",
        f"• Время операции в ЛК - не «из воздуха» до создания заказа: в боте заказ создан <code>{esc(created or '—')}</code>.",
        f"• В назначении платежа: <code>{esc(memo)}</code>.",
    ]
    if n > 1:
        lines.append(
            f"• У этого пользователя <b>{n}</b> заказов «ожидает оплаты»: <code>{esc(id_str)}</code> - "
            "сверять строго <b>сумму + ORDER + время</b>, не перепутать заказы."
        )
    else:
        lines.append("• У пользователя один заказ в «ожидает оплаты» - меньше риска перепутать.")
    lines.append(f"• Покупателю в боте показан минимум на странице bc: <b>{esc(f'{bc_min:.0f}')} ₽</b>.")
    return "\n".join(lines)
