#!/usr/bin/env python3
"""GATE-D darkweb smoke — JWT, premium gate, honest source (dw-08)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from smoke_env import smoke_secret

BASE = os.environ.get("DARKWEB_SMOKE_BASE", "http://127.0.0.1:8002")
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
        with urllib.request.urlopen(req, timeout=25) as resp:
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
    for required in ("/api/darkweb/stats", "/api/darkweb/scan/start", "/api/darkweb/check"):
        if required not in paths:
            failures.append(f"openapi missing {required}")

    token = _register_device("darkweb-smoke-free")

    code, body = _request("GET", "/api/darkweb/stats", token=token)
    if code != 403:
        failures.append(f"free user expected 403 got {code}: {body}")

    smoke_key = smoke_secret("DARKWEB_INTERNAL_SMOKE_SECRET")
    smoke_headers = {"X-Aladdin-Smoke": smoke_key} if smoke_key else None
    if not smoke_key:
        failures.append("DARKWEB_INTERNAL_SMOKE_SECRET not set")

    code, stats = _request("GET", "/api/darkweb/stats", token=token, extra_headers=smoke_headers)
    raw = json.dumps(stats, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"forbidden marker {marker} in stats")
    if code != 200:
        failures.append(f"stats expected 200 got {code}")
    elif stats.get("source") in ("sfm_mock", "mock", "sfm_stub"):
        failures.append(f"mock source {stats.get('source')}")
    elif "totalLeaks" not in stats:
        failures.append("stats missing totalLeaks")

    code, scan = _request("POST", "/api/darkweb/scan/start", {}, token, smoke_headers)
    if code != 200:
        failures.append(f"scan/start expected 200 got {code}: {scan}")
    elif scan.get("source") in ("sfm_mock", "mock"):
        failures.append("scan mock source")

    code, check = _request(
        "POST",
        "/api/darkweb/check",
        {"email": "darkweb-smoke@example.com"},
        token,
        smoke_headers,
    )
    if code != 200:
        failures.append(f"check expected 200 got {code}: {check}")
    elif check.get("source") in ("sfm_mock", "mock"):
        failures.append("check mock source")
    elif "results" not in check:
        failures.append("check missing results")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
