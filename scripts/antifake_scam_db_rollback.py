#!/usr/bin/env python3
"""P-04 — snapshot / rollback antifake_scam_numbers (mass false positive).

Usage:
  snapshot --tag before_crowd_batch
  deactivate-source --source user_report --since 2026-06-15T00:00:00Z
  restore --file /opt/aladdin-backend/.deploy_backups/scam_snapshot_TAG.json
  stats
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKUP_ROOT = Path(
    __import__("os").environ.get(
        "ANTIFAKE_SCAM_BACKUP_DIR",
        str(ROOT / ".deploy_backups"),
    )
)


def _active_rows() -> List[Dict[str, Any]]:
    from sqlalchemy import text

    from app.database.database import engine
    from app.services.antifake_call_directory_store import ensure_table

    ensure_table()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT phone_e164, label, source, confidence, block, active,
                       expires_at, created_at, updated_at
                FROM antifake_scam_numbers
                WHERE active = TRUE
                  AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY phone_e164
                """
            )
        ).mappings().all()
    out: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        for key in ("expires_at", "created_at", "updated_at"):
            val = item.get(key)
            if val is not None and hasattr(val, "isoformat"):
                item[key] = val.isoformat()
        out.append(item)
    return out


def cmd_snapshot(tag: str) -> int:
    rows = _active_rows()
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_tag = "".join(c if c.isalnum() or c in "-_" else "_" for c in tag)
    path = BACKUP_ROOT / f"scam_snapshot_{safe_tag}_{ts}.json"
    payload = {
        "tag": tag,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "rows": rows,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(path), "row_count": len(rows)}))
    return 0


def cmd_deactivate_source(source: str, since: str) -> int:
    from sqlalchemy import text

    from app.database.database import engine
    from app.services.antifake_call_directory_store import ensure_table

    ensure_table()
    since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE antifake_scam_numbers
                SET active = FALSE, updated_at = :now
                WHERE active = TRUE
                  AND source = :source
                  AND updated_at >= :since
                """
            ),
            {"source": source, "since": since_dt, "now": now},
        )
    count = int(result.rowcount or 0)
    print(json.dumps({"ok": True, "deactivated": count, "source": source, "since": since}))
    return 0


def cmd_restore(path: str) -> int:
    from sqlalchemy import text

    from app.database.database import engine
    from app.services.antifake_call_directory_store import ensure_table

    ensure_table()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("rows") or []
    now = datetime.now(timezone.utc)
    restored = 0
    with engine.begin() as conn:
        for row in rows:
            phone = row.get("phone_e164")
            if not phone:
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO antifake_scam_numbers
                        (phone_e164, label, source, confidence, block, active,
                         expires_at, created_at, updated_at)
                    VALUES
                        (:phone, :label, :source, :confidence, :block, :active,
                         CAST(:expires_at AS TIMESTAMPTZ), :now, :now)
                    ON CONFLICT (phone_e164) DO UPDATE SET
                        label = EXCLUDED.label,
                        source = EXCLUDED.source,
                        confidence = EXCLUDED.confidence,
                        block = EXCLUDED.block,
                        active = EXCLUDED.active,
                        expires_at = EXCLUDED.expires_at,
                        updated_at = EXCLUDED.updated_at
                    """
                ),
                {
                    "phone": phone,
                    "label": row.get("label"),
                    "source": row.get("source") or "restore",
                    "confidence": int(row.get("confidence") or 80),
                    "block": bool(row.get("block")),
                    "active": bool(row.get("active", True)),
                    "expires_at": row.get("expires_at"),
                    "now": now,
                },
            )
            restored += 1
    print(json.dumps({"ok": True, "restored": restored, "from": path}))
    return 0


def cmd_stats() -> int:
    from app.services.antifake_call_directory_store import active_count, ensure_table

    ensure_table()
    print(json.dumps({"active_count": active_count()}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Antifake scam DB rollback (P-04)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="Backup active scam numbers to JSON")
    p_snap.add_argument("--tag", required=True, help="Label for backup file")

    p_deact = sub.add_parser("deactivate-source", help="Deactivate rows by source since timestamp")
    p_deact.add_argument("--source", required=True)
    p_deact.add_argument("--since", required=True, help="ISO8601 UTC")

    p_restore = sub.add_parser("restore", help="Restore from snapshot JSON")
    p_restore.add_argument("--file", required=True)

    sub.add_parser("stats", help="Print active_count")

    args = parser.parse_args()
    if args.cmd == "snapshot":
        return cmd_snapshot(args.tag)
    if args.cmd == "deactivate-source":
        return cmd_deactivate_source(args.source, args.since)
    if args.cmd == "restore":
        return cmd_restore(args.file)
    if args.cmd == "stats":
        return cmd_stats()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
