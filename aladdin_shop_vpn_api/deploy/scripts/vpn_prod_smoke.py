#!/usr/bin/env python3
"""Prod smoke for aladdin-shop-vpn-api (127.0.0.1:8091)."""
from __future__ import annotations

import hashlib
import hmac as hm
import json
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path("/opt/aladdin-shop-vpn-api/env")
DB_PATH = Path("/opt/aladdin-shop-vpn-api/var/vpn.db")
BASE = "http://127.0.0.1:8091"
TEST_TID = 888777666
TEST_TOKEN = "smoke-drill-opaque-token-2026"


def _read_secret() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("VPN_API_HMAC_SECRET="):
            v = line.split("=", 1)[1].strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            return v
    raise SystemExit("VPN_API_HMAC_SECRET missing")


def _read_env(key: str) -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            v = line.split("=", 1)[1].strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            return v
    return ""


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
    }


def http(secret: str, method: str, path: str, body: bytes = b"", *, nonce: str | None = None) -> tuple[int, str]:
    nonce = nonce or f"smoke-{time.time_ns()}"
    headers = sign(secret, method, path, body, nonce)
    req = urllib.request.Request(
        BASE + path,
        data=body if method != "GET" else None,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read(1200).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(1200).decode("utf-8", errors="replace")


def main() -> int:
    secret = _read_secret()
    rows: list[tuple[str, bool, str]] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        rows.append((name, ok, detail))

    for path in ("/health", "/ready"):
        st, body = http(secret, "GET", path)
        record(f"GET {path}", st == 200, str(st))

    st, _ = http(secret, "GET", "/sub/nonexistent-token-xyz")
    record("GET /sub unknown token", st == 404, str(st))

    st, body = http(secret, "GET", "/v1/legal/vpn-instructions")
    record("GET /v1/legal/vpn-instructions", st == 200 and "VPN" in body, str(st))

    xuuid = _read_env("VPN_XRAY_DEFAULT_CLIENT_UUID") or "bed682e6-1726-419b-b45b-e8e891de7b7b"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id=?", (TEST_TID,))
    conn.execute(
        """
        INSERT INTO vpn_accounts (
            telegram_user_id, status, paid_until, opaque_token, wg_client_tunnel_ip,
            xray_client_uuid, created_at, updated_at
        ) VALUES (?, 'vpn_active', '2099-06-01T00:00:00+00:00', ?, '10.8.0.99', ?, datetime('now'), datetime('now'))
        """,
        (TEST_TID, TEST_TOKEN, xuuid),
    )
    conn.commit()
    conn.close()

    st, body = http(secret, "GET", f"/sub/{TEST_TOKEN}")
    record("GET /sub active account", st == 200 and "vless://" in body, body.split("\n", 1)[0][:80])

    wg_body = json.dumps({"telegram_user_id": TEST_TID}).encode()
    st, body = http(secret, "POST", "/internal/v1/wg/conf", wg_body, nonce=f"smoke-wg-{time.time_ns()}")
    record("POST /internal/v1/wg/conf", st in (200, 503), f"{st}")

    ovpn_body = json.dumps({"telegram_user_id": TEST_TID}).encode()
    st, body = http(secret, "POST", "/internal/v1/ovpn/conf", ovpn_body, nonce=f"smoke-ovpn-{time.time_ns()}")
    record("POST /internal/v1/ovpn/conf", st == 200 and "remote " in body, f"{st}")

    st, body = http(secret, "GET", "/internal/v1/egress/catalog", nonce=f"smoke-egress-{time.time_ns()}")
    record("GET /internal/v1/egress/catalog", st == 200 and "primary" in body, str(st))

    st, body = http(secret, "GET", "/internal/v1/locations/catalog", nonce=f"smoke-loc-{time.time_ns()}")
    record("GET /internal/v1/locations/catalog", st == 200 and '"lines"' in body, str(st))

    try:
        with urllib.request.urlopen(BASE + "/metrics", timeout=5) as resp:
            met = resp.read(3000).decode()
        record("GET /metrics", "http_" in met or "vpn_" in met, "ok")
    except Exception as e:
        record("GET /metrics", False, str(e))

    # cleanup
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM vpn_accounts WHERE telegram_user_id=?", (TEST_TID,))
    conn.commit()
    conn.close()
    prof = Path(f"/opt/aladdin-shop-vpn-api/var/ovpn-profiles/{TEST_TID}.ovpn")
    if prof.is_file():
        prof.unlink()

    print("=== VPN PROD SMOKE ===")
    failed = 0
    for name, ok, detail in rows:
        print(f"{'PASS' if ok else 'FAIL'}\t{name}\t{detail}")
        if not ok:
            failed += 1
    print(f"=== SUMMARY: {len(rows) - failed}/{len(rows)} passed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
