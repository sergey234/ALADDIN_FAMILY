#!/usr/bin/env python3
"""GATE-D identity-theft smoke — verdict contract + premium gate (id-08)."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request

from smoke_env import smoke_secret

BASE = os.environ.get("IDENTITY_SMOKE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"status":"success"')


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
    extra_headers: dict | None = None,
) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def _register_device(device_id: str) -> str:
    _, reg = _request("POST", "/api/auth/register-device", {"deviceId": device_id})
    token = reg.get("token") or reg.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {reg}")
    return token


def main() -> int:
    failures: list[str] = []

    _, openapi = _request("GET", "/openapi.json")
    paths = openapi.get("paths", {})
    for required in ("/api/identity-theft/detect", "/api/identity-theft/stats", "/api/identity-theft/check/fraud"):
        if required not in paths:
            failures.append(f"openapi missing {required}")

    token = _register_device("identity-smoke-free")
    code, _ = _request("POST", "/api/identity-theft/detect", {"snils": "12345678901"}, token)
    if code != 403:
        failures.append(f"free user expected 403 got {code}")

    smoke_key = smoke_secret("IDENTITY_THEFT_INTERNAL_SMOKE_SECRET")
    smoke_headers = {"X-Aladdin-Smoke": smoke_key} if smoke_key else None
    if not smoke_key:
        failures.append("IDENTITY_THEFT_INTERNAL_SMOKE_SECRET not set")

    snils_hash = hashlib.sha256(b"12345678901").hexdigest()
    code, detect = _request(
        "POST",
        "/api/identity-theft/detect",
        {"snils_hash": snils_hash},
        token,
        smoke_headers,
    )
    raw = json.dumps(detect, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"forbidden marker {marker} in detect")
    if code != 200:
        failures.append(f"detect expected 200 got {code}: {detect}")
    elif detect.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
        failures.append(f"invalid verdict {detect.get('verdict')}")
    elif detect.get("source") in ("sfm_mock", "mock"):
        failures.append("detect mock source")

    code, fraud = _request(
        "POST",
        "/api/identity-theft/check/fraud",
        {"snils_hash": snils_hash},
        token,
        smoke_headers,
    )
    if code != 200:
        failures.append(f"check/fraud expected 200 got {code}")
    elif fraud.get("verdict") not in ("likely_fake", "uncertain", "likely_real"):
        failures.append("fraud invalid verdict")

    code, stats = _request("GET", "/api/identity-theft/stats", token=token, extra_headers=smoke_headers)
    if code != 200 or "totalAttempts" not in stats:
        failures.append(f"stats expected 200 with totalAttempts got {code}")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
