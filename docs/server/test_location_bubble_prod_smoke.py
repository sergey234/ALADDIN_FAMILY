#!/usr/bin/env python3
"""GATE-D location-bubble smoke (loc-06)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from smoke_env import smoke_secret

BASE = os.environ.get("LOCATION_BUBBLE_SMOKE_BASE", "http://127.0.0.1:8002")
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
    for required in ("/api/location-bubble/generate", "/api/location-bubble/stats", "/api/location-bubble/settings"):
        if required not in paths:
            failures.append(f"openapi missing {required}")

    token = _register_device("loc-bubble-smoke-free")
    code, _ = _request(
        "POST",
        "/api/location-bubble/generate",
        {"latitude": 55.75, "longitude": 37.62},
        token,
    )
    if code != 403:
        failures.append(f"free user expected 403 got {code}")

    smoke_key = smoke_secret("LOCATION_BUBBLE_INTERNAL_SMOKE_SECRET")
    smoke_headers = {"X-Aladdin-Smoke": smoke_key} if smoke_key else None
    if not smoke_key:
        failures.append("LOCATION_BUBBLE_INTERNAL_SMOKE_SECRET not set")

    code, gen = _request(
        "POST",
        "/api/location-bubble/generate",
        {"latitude": 55.7558, "longitude": 37.6173, "radius": 500},
        token,
        smoke_headers,
    )
    raw = json.dumps(gen, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"forbidden marker {marker}")
    if code != 200:
        failures.append(f"generate expected 200 got {code}: {gen}")
    elif "approximate_latitude" not in gen:
        failures.append("generate missing approximate_latitude")
    elif gen.get("source") in ("sfm_mock", "mock"):
        failures.append("generate mock source")

    code, stats = _request("GET", "/api/location-bubble/stats", token=token, extra_headers=smoke_headers)
    if code != 200:
        failures.append(f"stats expected 200 got {code}")
    elif stats.get("modifiedRequests", 0) < 1:
        failures.append(f"stats modifiedRequests expected >=1 got {stats}")

    code, settings = _request(
        "POST",
        "/api/location-bubble/settings",
        {"person_id": "child-1", "default_radius_m": 500, "enabled": True},
        token,
        smoke_headers,
    )
    if code != 200:
        failures.append(f"settings expected 200 got {code}")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
