#!/usr/bin/env python3
"""Read-only triage: paid orders stuck without Stars/Premium fulfill or VPN provision.

Usage (local shop.db or copied DB — never mutate prod from laptop blindly):

  python3 telegram_stars_shop_bot/scripts/triage_stuck_orders.py \\
    --db /path/to/shop.db --hours 2 --json

Exit 0 always (report tool). Prints JSON + short markdown to stdout.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def rows_to_dicts(cur: sqlite3.Cursor) -> list[dict]:
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path to shop SQLite DB (read-only intent)")
    ap.add_argument("--hours", type=float, default=2.0, help="Paid older than N hours")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    db = Path(args.db)
    if not db.exists():
        print(f"ERROR: db not found: {db}", file=sys.stderr)
        return 2

    # URI read-only if possible
    uri = f"file:{db.resolve()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.OperationalError:
        conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row

    hours_mod = f"-{args.hours} hours"
    # Schema note: buyer_username (not username); no paid_at — use updated_at/created_at.
    # Stars/Premium: paid, auto, no provider_ref yet, older than N hours.
    stars_sql = """
    SELECT id, product_id, product_kind, status, buyer_username,
           fulfillment_mode, fulfillment_provider_ref, fulfillment_attempt_count,
           fulfillment_last_error, fulfillment_applied_at,
           created_at, updated_at, completed_at
    FROM orders
    WHERE status = 'paid'
      AND LOWER(TRIM(COALESCE(product_kind, ''))) IN ('stars', 'premium', 'gift')
      AND LOWER(TRIM(COALESCE(fulfillment_mode, 'auto'))) != 'manual_only'
      AND (fulfillment_provider_ref IS NULL OR TRIM(COALESCE(fulfillment_provider_ref, '')) = '')
      AND datetime(COALESCE(updated_at, created_at)) <= datetime('now', ?)
    ORDER BY COALESCE(updated_at, created_at) ASC
    LIMIT ?
    """
    cur = conn.execute(stars_sql, (hours_mod, args.limit))
    stuck_fulfill = rows_to_dicts(cur)

    # VPN still in paid (not completed) older than N hours
    vpn_sql = """
    SELECT id, product_id, product_kind, status, buyer_username,
           fulfillment_provider_ref, fulfillment_last_error, fulfillment_applied_at,
           created_at, updated_at, completed_at
    FROM orders
    WHERE status = 'paid'
      AND LOWER(TRIM(COALESCE(product_kind, ''))) = 'vpn'
      AND datetime(COALESCE(updated_at, created_at)) <= datetime('now', ?)
    ORDER BY COALESCE(updated_at, created_at) ASC
    LIMIT ?
    """
    try:
        cur = conn.execute(vpn_sql, (hours_mod, args.limit))
        stuck_vpn = rows_to_dicts(cur)
    except sqlite3.OperationalError as exc:
        stuck_vpn = [{"error": str(exc)}]

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "db": str(db),
        "hours": args.hours,
        "stuck_stars_premium_gift_count": len(stuck_fulfill),
        "stuck_vpn_paid_count": (
            len(stuck_vpn) if stuck_vpn and not (stuck_vpn and "error" in stuck_vpn[0]) else 0
        ),
        "stuck_stars_premium_gift": stuck_fulfill,
        "stuck_vpn_paid": stuck_vpn,
        "actions_read_only": [
            "Inspect fulfillment_last_error / ApiFragment balance",
            "Check auto_fulfill worker / vpn_payment_hook logs on Contabo",
            "Do NOT auto-refund from this script",
        ],
    }
    conn.close()

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"# Stuck orders triage\n")
        print(f"- Stars/Premium/Gift stuck (paid, no provider_ref): **{report['stuck_stars_premium_gift_count']}**")
        print(f"- VPN still paid (review): **{report['stuck_vpn_paid_count']}**")
        print(f"- Hours threshold: {args.hours}")
        for o in stuck_fulfill[:15]:
            print(
                f"  - order {o.get('id')} kind={o.get('product_kind')} "
                f"attempts={o.get('fulfillment_attempt_count')} err={o.get('fulfillment_last_error')}"
            )
        print("\n_Read-only. No refunds/reprovision._")
    return 0


if __name__ == "__main__":
    sys.exit(main())
