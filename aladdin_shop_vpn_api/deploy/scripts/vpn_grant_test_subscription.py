#!/usr/bin/env python3
"""Выдать тестовую VPN-подписку админам (provision + ожидание job). Запуск на VPS."""
from __future__ import annotations

import hashlib
import hmac as hm
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENV_PATH = Path("/opt/aladdin-shop-vpn-api/env")
DB_PATH = Path("/opt/aladdin-shop-vpn-api/var/vpn.db")
BASE = "http://127.0.0.1:8091"


def _read_secret() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("VPN_API_HMAC_SECRET="):
            v = line.split("=", 1)[1].strip().strip('"')
            return v
    raise SystemExit("VPN_API_HMAC_SECRET missing")


def sign(secret: str, method: str, path: str, body: bytes, nonce: str) -> dict[str, str]:
    ts = str(int(time.time()))
    body_hash = hashlib.sha256(body or b"").hexdigest()
    msg = f"{method.upper()}\n{path}\n{ts}\n{nonce}\n{body_hash}".encode("utf-8")
    sig = hm.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return {
        "X-Signature": sig,
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "Content-Type": "application/json",
        "Idempotency-Key": nonce,
    }


def post_provision(secret: str, telegram_user_id: int, order_id: int) -> tuple[int, str]:
    path = "/internal/v1/provision"
    paid_until = (datetime.now(timezone.utc) + timedelta(days=365)).replace(microsecond=0).isoformat()
    body = json.dumps(
        {"telegram_user_id": telegram_user_id, "order_id": order_id, "paid_until": paid_until}
    ).encode("utf-8")
    nonce = f"test-grant-{telegram_user_id}-{int(time.time())}"
    headers = sign(secret, "POST", path, body, nonce)
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def wait_active(tid: int, timeout_sec: int = 90) -> str:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT status, opaque_token FROM vpn_accounts WHERE telegram_user_id = ?",
            (tid,),
        ).fetchone()
        conn.close()
        if row and row["status"] == "vpn_active":
            return str(row["opaque_token"] or "")[:32]
        time.sleep(2)
    return ""


def main() -> int:
    secret = _read_secret()
    tids = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [493897224, 744254201]
    for i, tid in enumerate(tids):
        st, body = post_provision(secret, tid, order_id=9_000_000 + tid + i)
        print(f"provision tid={tid} status={st} body={body[:200]}")
        tok = wait_active(tid)
        if tok:
            print(f"  -> vpn_active opaque_prefix={tok}…")
        else:
            print("  -> timeout waiting vpn_active (check jobs worker)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
