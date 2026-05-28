"""
Обработка одной pending-задачи из очереди `jobs` (запуск по cron/systemd timer).

  python3 -m aladdin_shop_vpn_api.worker
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import aiosqlite

from aladdin_shop_vpn_api import hmac_auth
from aladdin_shop_vpn_api.settings import Settings, load_settings
from aladdin_shop_vpn_api.token_rotation import new_opaque_token

logger = logging.getLogger(__name__)


def _is_retryable_job_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    if "unknown job_type" in msg:
        return False
    if "not configured" in msg or "vpn_dev_stub" in msg:
        return False
    return True


def _job_backoff_seconds(attempts_after_fail: int) -> int:
    """attempts уже увеличен при взятии job в processing."""
    return min(300, 30 * (2 ** max(0, attempts_after_fail - 1)))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


async def _expire_stale_active_accounts(
    conn: aiosqlite.Connection,
    *,
    now_dt: datetime,
    now_iso: str,
    settings: Settings,
) -> int:
    """Помечает vpn_expired, если paid_until в прошлом (vpn_active и «застрявший» vpn_provisioning)."""
    cur = await conn.execute(
        """
        SELECT telegram_user_id, paid_until FROM vpn_accounts
        WHERE status IN ('vpn_active', 'vpn_provisioning')
          AND paid_until IS NOT NULL AND TRIM(paid_until) != ''
        """
    )
    rows = await cur.fetchall()
    n = 0
    wg_expire_script = (settings.vpn_wg_post_expire_script or "").strip()
    xray_expire_script = (settings.vpn_xray_post_expire_script or "").strip()
    for r in rows:
        raw = r["paid_until"]
        if not raw:
            continue
        s = str(raw).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if dt < now_dt:
            tid = int(r["telegram_user_id"])
            await conn.execute(
                """
                UPDATE vpn_accounts
                SET status = 'vpn_expired',
                    last_error = 'paid_until_elapsed',
                    opaque_token = ?,
                    updated_at = ?
                WHERE telegram_user_id = ? AND status IN ('vpn_active', 'vpn_provisioning')
                """,
                (new_opaque_token(), now_iso, tid),
            )
            # Скрипт WG открывает отдельное соединение к vpn.db — коммит до subprocess.
            await conn.commit()
            if wg_expire_script:
                try:
                    subprocess.run([wg_expire_script, str(tid)], timeout=120, check=False)
                except Exception:
                    logger.exception("VPN_WG_POST_EXPIRE_SCRIPT failed tid=%s", tid)
            if xray_expire_script:
                try:
                    subprocess.run([xray_expire_script, str(tid)], timeout=120, check=False)
                except Exception:
                    logger.exception("VPN_XRAY_POST_EXPIRE_SCRIPT failed tid=%s", tid)
            n += 1
    return n


async def process_one_job() -> bool:
    settings = load_settings()
    conn = await hmac_auth.open_db(settings.vpn_db_path)
    try:
        now_iso = _utc_now_iso()
        now_dt = datetime.now(timezone.utc).replace(microsecond=0)

        expired_n = await _expire_stale_active_accounts(conn, now_dt=now_dt, now_iso=now_iso, settings=settings)
        if expired_n:
            logger.info("vpn_expired: %s account(s) (paid_until elapsed)", expired_n)

        await conn.execute("BEGIN IMMEDIATE")
        cur = await conn.execute(
            """
            SELECT id, job_type, payload_json, attempts
            FROM jobs
            WHERE status = 'pending'
            ORDER BY next_run_at ASC, id ASC
            LIMIT 1
            """
        )
        row = await cur.fetchone()
        if row is None:
            await conn.rollback()
            return expired_n > 0

        job_id = int(row["id"])
        job_type = str(row["job_type"])
        payload = json.loads(str(row["payload_json"]))
        attempts = int(row["attempts"])

        await conn.execute(
            "UPDATE jobs SET status = 'processing', attempts = ?, updated_at = ? WHERE id = ?",
            (attempts + 1, _utc_now_iso(), job_id),
        )
        await conn.commit()

        now = _utc_now_iso()
        stub = bool(settings.vpn_dev_stub_wg)

        try:
            if job_type == "provision":
                await _handle_provision(conn, payload, stub=stub, now=now, settings=settings)
            elif job_type == "extend":
                await _handle_extend(conn, payload, now=now, settings=settings)
            elif job_type == "revoke":
                await _handle_revoke(conn, payload, now=now, settings=settings)
            else:
                raise RuntimeError(f"unknown job_type {job_type}")
        except Exception as e:  # noqa: BLE001 — воркер логирует и помечает failed / requeue
            err = str(e)[:2000]
            max_attempts = max(1, int(settings.vpn_job_max_attempts))
            current_attempts = attempts + 1
            if _is_retryable_job_error(e) and current_attempts < max_attempts:
                delay = _job_backoff_seconds(current_attempts)
                next_run = (now_dt + timedelta(seconds=delay)).isoformat()
                await conn.execute(
                    """
                    UPDATE jobs
                    SET status = 'pending', last_error = ?, next_run_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (err, next_run, now, job_id),
                )
                await conn.commit()
                logger.warning(
                    "job %s requeued attempt %s/%s in %ss: %s",
                    job_id,
                    current_attempts,
                    max_attempts,
                    delay,
                    err[:200],
                )
                return True

            await conn.execute(
                "UPDATE jobs SET status = 'failed', last_error = ?, updated_at = ? WHERE id = ?",
                (err, now, job_id),
            )
            tid = int(payload.get("telegram_user_id") or 0)
            if tid:
                await conn.execute(
                    """
                    UPDATE vpn_accounts
                    SET status = 'vpn_failed', last_error = ?, updated_at = ?
                    WHERE telegram_user_id = ?
                    """,
                    (err, now, tid),
                )
            await conn.commit()
            logger.exception("job %s failed (final)", job_id)
            return True

        await conn.execute(
            "UPDATE jobs SET status = 'done', last_error = NULL, updated_at = ? WHERE id = ?",
            (now, job_id),
        )
        await conn.commit()
        logger.info("job %s done (%s)", job_id, job_type)
        return True
    finally:
        await conn.close()


async def _ensure_xray_client_uuid(conn, tid: int, settings: Settings) -> None:
    import uuid as _uuid

    cur = await conn.execute(
        "SELECT xray_client_uuid FROM vpn_accounts WHERE telegram_user_id = ?",
        (tid,),
    )
    row = await cur.fetchone()
    if row and str(row["xray_client_uuid"] or "").strip():
        return
    new_uuid = str(_uuid.uuid4())
    await conn.execute(
        "UPDATE vpn_accounts SET xray_client_uuid = ? WHERE telegram_user_id = ?",
        (new_uuid, tid),
    )


async def _handle_provision(conn, payload: dict, *, stub: bool, now: str, settings: Settings) -> None:
    tid = int(payload["telegram_user_id"])
    script = (settings.vpn_wg_post_provision_script or "").strip()
    if not stub and not script:
        raise RuntimeError(
            "WG provision not configured (set VPN_DEV_STUB_WG=1 or VPN_WG_POST_PROVISION_SCRIPT)"
        )
    if script and not stub:
        from pathlib import Path

        sp = Path(script)
        if not sp.is_file():
            raise RuntimeError(f"VPN_WG_POST_PROVISION_SCRIPT not found: {script}")
        proc = subprocess.run(
            [str(sp), str(tid)],
            timeout=120,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()[:500]
            raise RuntimeError(
                f"VPN_WG_POST_PROVISION_SCRIPT exit {proc.returncode}: {detail or 'no output'}"
            )
        cur = await conn.execute(
            "SELECT wg_client_tunnel_ip FROM vpn_accounts WHERE telegram_user_id = ?",
            (tid,),
        )
        row = await cur.fetchone()
        if row is None or not str(row["wg_client_tunnel_ip"] or "").strip():
            raise RuntimeError("wg_client_tunnel_ip missing after VPN_WG_POST_PROVISION_SCRIPT")

    await conn.execute(
        """
        UPDATE vpn_accounts
        SET status = 'vpn_active', last_error = NULL, updated_at = ?
        WHERE telegram_user_id = ?
        """,
        (now, tid),
    )
    await _ensure_xray_client_uuid(conn, tid, settings)
    await conn.commit()
    xray_up = (settings.vpn_xray_post_provision_script or "").strip()
    if xray_up:
        try:
            subprocess.run([xray_up, str(tid)], timeout=120, check=False)
        except Exception:
            logger.exception("VPN_XRAY_POST_PROVISION_SCRIPT tid=%s", tid)


async def _handle_extend(conn, payload: dict, *, now: str, settings: Settings) -> None:
    tid = int(payload["telegram_user_id"])
    paid_until = str(payload["paid_until"])
    await conn.execute(
        """
        UPDATE vpn_accounts
        SET paid_until = ?, status = 'vpn_active', updated_at = ?, last_error = NULL
        WHERE telegram_user_id = ?
        """,
        (paid_until, now, tid),
    )
    await conn.commit()
    await _ensure_xray_client_uuid(conn, tid, settings)
    await conn.commit()
    xray_up = (settings.vpn_xray_post_provision_script or "").strip()
    if xray_up:
        try:
            subprocess.run([xray_up, str(tid)], timeout=120, check=False)
        except Exception:
            logger.exception("VPN_XRAY_POST_PROVISION_SCRIPT after extend tid=%s", tid)


async def _handle_revoke(conn, payload: dict, *, now: str, settings: Settings) -> None:
    tid = int(payload["telegram_user_id"])
    reason = str(payload.get("reason") or "revoke").strip()
    reason_l = reason.lower()
    # Авто-истечение подписки — терминальный vpn_expired; админ/abuse — vpn_manual_override.
    if reason_l in ("paid_until_elapsed", "subscription_expired", "expired"):
        terminal = "vpn_expired"
    else:
        terminal = "vpn_manual_override"
    if terminal == "vpn_expired":
        await conn.execute(
            """
            UPDATE vpn_accounts
            SET status = ?, last_error = ?, opaque_token = ?, updated_at = ?
            WHERE telegram_user_id = ?
            """,
            (terminal, reason, new_opaque_token(), now, tid),
        )
    else:
        await conn.execute(
            """
            UPDATE vpn_accounts
            SET status = ?, last_error = ?, updated_at = ?
            WHERE telegram_user_id = ?
            """,
            (terminal, reason, now, tid),
        )
    await conn.commit()
    wg_expire_script = (settings.vpn_wg_post_expire_script or "").strip()
    xray_expire_script = (settings.vpn_xray_post_expire_script or "").strip()
    if terminal == "vpn_expired":
        if wg_expire_script:
            try:
                subprocess.run([wg_expire_script, str(tid)], timeout=120, check=False)
            except Exception:
                logger.exception("VPN_WG_POST_EXPIRE_SCRIPT after revoke tid=%s", tid)
        if xray_expire_script:
            try:
                subprocess.run([xray_expire_script, str(tid)], timeout=120, check=False)
            except Exception:
                logger.exception("VPN_XRAY_POST_EXPIRE_SCRIPT after revoke tid=%s", tid)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        processed = asyncio.run(process_one_job())
    except Exception:
        logger.exception("worker crash")
        sys.exit(1)
    sys.exit(0 if processed else 0)


if __name__ == "__main__":
    main()
