from __future__ import annotations

from pathlib import Path
from typing import Any

import aiosqlite


async def fetch_vpn_account_user_facing(
    vpn_db_path: Path,
    telegram_user_id: int,
) -> dict[str, str] | None:
    """Краткий снимок VPN-аккаунта для пользовательского UI (без jobs)."""
    if not vpn_db_path.is_file():
        return None
    async with aiosqlite.connect(vpn_db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT status, paid_until, opaque_token
            FROM vpn_accounts WHERE telegram_user_id = ?
            """,
            (telegram_user_id,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        d = dict(row)
        return {
            "status": str(d.get("status") or ""),
            "paid_until": str(d.get("paid_until") or ""),
            "opaque_token": str(d.get("opaque_token") or ""),
        }


async def fetch_vpn_account_admin_snapshot(
    vpn_db_path: Path,
    telegram_user_id: int,
) -> dict[str, Any] | None:
    """
    Чтение vpn.db для админ-команды (только при настроенном VPN_DB_PATH на доступном диске).
    """
    if not vpn_db_path.is_file():
        return None
    async with aiosqlite.connect(vpn_db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT id, telegram_user_id, status, paid_until, opaque_token,
                   wg_client_tunnel_ip,
                   substr(COALESCE(wg_client_public_key,''),1,16) AS wg_pub_prefix,
                   last_error, created_at, updated_at
            FROM vpn_accounts WHERE telegram_user_id = ?
            """,
            (telegram_user_id,),
        )
        acc = await cur.fetchone()
        if acc is None:
            return {"missing_account": True, "telegram_user_id": telegram_user_id}
        row = dict(acc)
        # Jobs: json_extract если есть json1; иначе LIKE по payload.
        jobs: list[dict[str, Any]] = []
        try:
            curj = await db.execute(
                """
                SELECT id, job_type, status, attempts,
                       substr(COALESCE(last_error,''),1,160) AS last_error,
                       created_at, updated_at
                FROM jobs
                WHERE CAST(json_extract(payload_json, '$.telegram_user_id') AS INTEGER) = ?
                ORDER BY id DESC
                LIMIT 12
                """,
                (telegram_user_id,),
            )
            jrows = await curj.fetchall()
            jobs = [dict(r) for r in jrows]
        except (aiosqlite.OperationalError, TypeError, ValueError):
            like_a = f'%"telegram_user_id": {telegram_user_id},%'
            like_b = f'%"telegram_user_id": {telegram_user_id}%'
            like_c = f'%"telegram_user_id":{telegram_user_id},%'
            like_d = f'%"telegram_user_id":{telegram_user_id}%'
            curj = await db.execute(
                """
                SELECT id, job_type, status, attempts,
                       substr(COALESCE(last_error,''),1,160) AS last_error,
                       created_at, updated_at
                FROM jobs
                WHERE payload_json LIKE ? OR payload_json LIKE ?
                   OR payload_json LIKE ? OR payload_json LIKE ?
                ORDER BY id DESC
                LIMIT 12
                """,
                (like_a, like_b, like_c, like_d),
            )
            jrows = await curj.fetchall()
            jobs = [dict(r) for r in jrows]
        row["recent_jobs"] = jobs
        return row


def format_vpn_admin_snapshot_html(d: dict[str, Any]) -> str:
    from bot.util_html import esc

    if d.get("missing_account"):
        tid = int(d["telegram_user_id"])
        return f"<b>VPN аккаунт</b>: для <code>{esc(str(tid))}</code> записи в <code>vpn.db</code> нет."
    lines = [
        "<b>VPN аккаунт</b> (vpn.db)\n",
        f"<code>id</code>: {esc(str(d.get('id')))}",
        f"<code>telegram_user_id</code>: {esc(str(d.get('telegram_user_id')))}",
        f"<code>status</code>: {esc(str(d.get('status') or ''))}",
        f"<code>paid_until</code>: {esc(str(d.get('paid_until') or ''))}",
        f"<code>ссылка_подписки (opaque)</code>: <code>{esc(str(d.get('opaque_token') or '')[:24])}</code>…",
        f"<code>wg_client_tunnel_ip</code>: {esc(str(d.get('wg_client_tunnel_ip') or ''))}",
        f"<code>wg_client_public_key</code> (prefix): {esc(str(d.get('wg_pub_prefix') or ''))}…",
        f"<code>last_error</code>: {esc(str(d.get('last_error') or '')[:400])}",
        f"<code>created_at</code> / <code>updated_at</code>: {esc(str(d.get('created_at')))} / {esc(str(d.get('updated_at')))}",
        "\n<b>Последние jobs</b> (по этому telegram_user_id):",
    ]
    jobs = d.get("recent_jobs") or []
    if not jobs:
        lines.append("<i>нет совпадений в выборке</i>")
    else:
        for j in jobs:
            lines.append(
                f"· <code>#{esc(str(j.get('id')))}</code> {esc(str(j.get('job_type')))} → "
                f"<code>{esc(str(j.get('status')))}</code> att={esc(str(j.get('attempts')))} "
                f"<i>{esc(str(j.get('created_at')))}</i>"
            )
            err = str(j.get("last_error") or "").strip()
            if err:
                lines.append(f"  err: <code>{esc(err)}</code>")
    return "\n".join(lines)
