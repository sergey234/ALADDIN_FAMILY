#!/usr/bin/env python3
"""
Utility script to mark a payment as paid and create a fresh activation code.
Used for manual testing.
"""
import sys
import sqlite3
from datetime import datetime

sys.path.append("/opt/aladdin-backend")

from app.utils import generate_activation_code, code_expiration, now_utc  # type: ignore


def main(payment_id: str):
    conn = sqlite3.connect("/opt/aladdin-backend/payments.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT id, alias, tariff_id FROM payments WHERE id=?",
        (payment_id,),
    )
    row = cur.fetchone()
    if not row:
        raise SystemExit(f"Payment {payment_id} not found")

    now = now_utc().isoformat()
    cur.execute(
        "UPDATE payments SET status=?, updated_at=? WHERE id=?",
        ("paid", now, payment_id),
    )

    cur.execute(
        "DELETE FROM activation_codes WHERE payment_id=?",
        (payment_id,),
    )

    code = generate_activation_code()
    expires_at = code_expiration(30).isoformat()
    cur.execute(
        """
        INSERT INTO activation_codes (code, payment_id, alias, tariff_id, status, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (code, payment_id, row["alias"], row["tariff_id"], "active", expires_at),
    )

    conn.commit()
    print(f"Payment {payment_id} marked as paid.")
    print(f"Activation code: {code}")
    print(f"Expires at: {expires_at}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: manual_mark_paid.py <payment_id>")
    main(sys.argv[1])


