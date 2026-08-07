from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from bot.db.database import connect
from bot.services import api_clients_repo, orders_repo
from bot.services.hmac_util import hmac_sha256_hex

logger = logging.getLogger(__name__)
_DEFAULT_MAX_ATTEMPTS = 5


def build_order_status_payload(
    *,
    order_id: int,
    previous_status: str | None,
    new_status: str,
    external_ref: str | None,
) -> dict[str, Any]:
    return {
        "event": "order.status_changed",
        "order_id": order_id,
        "status": new_status,
        "previous_status": previous_status or "",
        "external_ref": external_ref,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


async def emit_order_status_changed(
    *,
    db_path: Path,
    order_id: int,
    previous_status: str | None,
    new_status: str,
) -> None:
    """Fire-and-forget вызывается из админки / вебхука оплат; ошибки только в лог."""
    if new_status == (previous_status or ""):
        return
    conn = await connect(db_path)
    try:
        row = await orders_repo.get_order(conn, order_id)
        if row is None:
            return
        try:
            src = row["source"]
        except (KeyError, IndexError, TypeError):
            return
        if src != "api":
            return
        try:
            cid = row["api_client_id"]
        except (KeyError, IndexError, TypeError):
            cid = None
        if cid is None:
            return
        client = await api_clients_repo.get_by_id(conn, int(cid))
        if client is None:
            return
        url = (client["webhook_url"] or "").strip()
        secret = (client["webhook_secret"] or "").strip()
        if not url or not secret:
            return
        try:
            ext = row["external_ref"]
        except (KeyError, IndexError, TypeError):
            ext = None
        payload = build_order_status_payload(
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            external_ref=str(ext) if ext is not None else None,
        )
        await enqueue_webhook_event(
            conn,
            api_client_id=int(cid),
            order_id=order_id,
            target_url=url,
            payload=payload,
            max_attempts=_DEFAULT_MAX_ATTEMPTS,
        )
        await process_webhook_queue_once(conn, limit=10)
    except Exception:
        logger.warning("partner_webhook_failed order_id=%s", order_id, exc_info=True)
    finally:
        await conn.close()


async def enqueue_webhook_event(
    conn,
    *,
    api_client_id: int,
    order_id: int,
    target_url: str,
    payload: dict[str, Any],
    max_attempts: int,
) -> int:
    cur = await conn.execute(
        """
        INSERT INTO outbound_webhook_events (
            api_client_id, order_id, event_type, target_url, payload_json, max_attempts
        ) VALUES (?, ?, 'order.status_changed', ?, ?, ?)
        """,
        (
            api_client_id,
            order_id,
            target_url,
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            max(1, max_attempts),
        ),
    )
    await conn.commit()
    return int(cur.lastrowid)


async def process_webhook_queue_once(conn, *, limit: int = 20) -> int:
    cur = await conn.execute(
        """
        SELECT * FROM outbound_webhook_events
        WHERE status = 'pending'
          AND attempts < max_attempts
          AND datetime(next_attempt_at) <= datetime('now')
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = await cur.fetchall()
    sent_ok = 0
    for row in rows:
        eid = int(row["id"])
        body = str(row["payload_json"]).encode("utf-8")
        api_client_id = int(row["api_client_id"])
        client = await api_clients_repo.get_by_id(conn, api_client_id)
        if client is None:
            await conn.execute(
                """
                UPDATE outbound_webhook_events
                SET status = 'failed', attempts = attempts + 1, last_error = 'missing_api_client'
                WHERE id = ?
                """,
                (eid,),
            )
            logger.warning("partner_webhook_failed_missing_client event_id=%s", eid)
            continue
        delivery_secret = str(client["webhook_secret"] or "").strip()
        if not delivery_secret:
            await conn.execute(
                """
                UPDATE outbound_webhook_events
                SET status = 'failed', attempts = attempts + 1, last_error = 'missing_webhook_secret'
                WHERE id = ?
                """,
                (eid,),
            )
            logger.warning("partner_webhook_failed_missing_secret event_id=%s client_id=%s", eid, api_client_id)
            continue
        sig = hmac_sha256_hex(delivery_secret, body)
        headers = {"Content-Type": "application/json", "X-Partner-Signature": f"sha256={sig}"}
        ok = False
        err = ""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client_http:
                resp = await client_http.post(str(row["target_url"]), content=body, headers=headers)
            ok = resp.status_code < 400
            if not ok:
                err = f"http_{resp.status_code}"
        except Exception as exc:
            err = exc.__class__.__name__
        if ok:
            await conn.execute(
                """
                UPDATE outbound_webhook_events
                SET status = 'delivered', delivered_at = datetime('now'), attempts = attempts + 1, last_error = NULL
                WHERE id = ?
                """,
                (eid,),
            )
            sent_ok += 1
            continue
        await conn.execute(
            """
            UPDATE outbound_webhook_events
            SET attempts = attempts + 1,
                last_error = ?,
                next_attempt_at = datetime('now', '+' || (
                    CASE
                        WHEN attempts < 1 THEN 1
                        WHEN attempts < 3 THEN 5
                        ELSE 15
                    END
                ) || ' minutes')
            WHERE id = ?
            """,
            (err[:200], eid),
        )
        await conn.execute(
            """
            UPDATE outbound_webhook_events
            SET status = 'failed'
            WHERE id = ? AND attempts >= max_attempts
            """,
            (eid,),
        )
        logger.warning("partner_webhook_retry_scheduled event_id=%s error=%s", eid, err)
    await conn.commit()
    return sent_ok
