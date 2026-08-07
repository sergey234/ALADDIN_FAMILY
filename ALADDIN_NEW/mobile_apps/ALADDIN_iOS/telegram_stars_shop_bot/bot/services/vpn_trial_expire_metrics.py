"""Метрики trial/expire для /vpn_health и ops (зеркало vpn_trial_expire_reconcile.py)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _parse_paid_until(raw: str | None) -> datetime | None:
    if not raw:
        return None
    s = str(raw).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def collect_trial_expire_metrics(
    vpn_db_path: Path | str | None,
    xray_config: Path | str | None = None,
) -> dict[str, Any]:
    if vpn_db_path is None:
        return {
            "ok": False,
            "error": "no_vpn_db",
            "trial_active": 0,
            "trial_expired": 0,
            "trial_used_at": 0,
            "paid_after_trial_active": 0,
            "overdue_active": 0,
            "expired_with_uuid": 0,
            "xray_orphan_clients": 0,
        }
    path = Path(vpn_db_path)
    now_u = datetime.now(timezone.utc).replace(microsecond=0)
    db = sqlite3.connect(str(path))
    try:
        trial_active = int(
            db.execute(
                "SELECT COUNT(*) FROM vpn_accounts WHERE account_kind='trial' AND status='vpn_active'"
            ).fetchone()[0]
        )
        trial_expired = int(
            db.execute(
                "SELECT COUNT(*) FROM vpn_accounts "
                "WHERE account_kind='trial' AND status='vpn_expired'"
            ).fetchone()[0]
        )
        trial_used = int(
            db.execute(
                "SELECT COUNT(*) FROM vpn_accounts "
                "WHERE trial_used_at IS NOT NULL AND TRIM(trial_used_at)!=''"
            ).fetchone()[0]
        )
        paid_after = int(
            db.execute(
                """
                SELECT COUNT(*) FROM vpn_accounts
                WHERE account_kind='paid' AND status='vpn_active'
                  AND trial_used_at IS NOT NULL AND TRIM(trial_used_at)!=''
                """
            ).fetchone()[0]
        )
        overdue = 0
        for row in db.execute(
            """
            SELECT paid_until FROM vpn_accounts
            WHERE status IN ('vpn_active', 'vpn_provisioning')
              AND paid_until IS NOT NULL AND TRIM(paid_until) != ''
            """
        ):
            dt = _parse_paid_until(row[0])
            if dt is not None and dt < now_u:
                overdue += 1
        expired_uuid = int(
            db.execute(
                """
                SELECT COUNT(*) FROM vpn_accounts
                WHERE status='vpn_expired'
                  AND xray_client_uuid IS NOT NULL AND TRIM(xray_client_uuid)!=''
                """
            ).fetchone()[0]
        )
        active_uuids: set[str] = set()
        for row in db.execute(
            """
            SELECT lower(COALESCE(xray_client_uuid,'')) FROM vpn_accounts
            WHERE status IN ('vpn_active', 'vpn_provisioning')
              AND xray_client_uuid IS NOT NULL AND TRIM(xray_client_uuid)!=''
            """
        ):
            if row[0]:
                active_uuids.add(row[0])
    finally:
        db.close()

    orphan = 0
    xcfg = Path(xray_config or "/opt/xray/config.json")
    if xcfg.is_file():
        try:
            cfg = json.loads(xcfg.read_text(encoding="utf-8"))
            seen: set[str] = set()
            for ib in cfg.get("inbounds", []) or []:
                if ib.get("protocol") != "vless":
                    continue
                for c in (ib.get("settings") or {}).get("clients") or []:
                    uid = str(c.get("id") or "").strip().lower()
                    email = str(c.get("email") or "")
                    if not uid or uid in seen:
                        continue
                    seen.add(uid)
                    if email.lower().startswith("bridge"):
                        continue
                    if uid not in active_uuids:
                        orphan += 1
        except Exception:
            orphan = -1

    return {
        "ok": overdue == 0 and expired_uuid == 0 and orphan == 0,
        "trial_active": trial_active,
        "trial_expired": trial_expired,
        "trial_used_at": trial_used,
        "paid_after_trial_active": paid_after,
        "overdue_active": overdue,
        "expired_with_uuid": expired_uuid,
        "xray_orphan_clients": orphan,
        "utc_now": now_u.isoformat(),
    }
