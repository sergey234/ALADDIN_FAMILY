#!/usr/bin/env python3
"""GATE-J emergency smoke — crash-detection + roadside-assistance (JWT, no mock envelope)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("EMERGENCY_SMOKE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback")


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
) -> tuple[int, dict | str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def _register_device(device_id: str) -> str:
    _, reg = _request("POST", "/api/auth/register-device", {"deviceId": device_id})
    if not isinstance(reg, dict):
        raise RuntimeError(f"no jwt: {reg}")
    token = reg.get("token") or reg.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {reg}")
    return token


def _body_forbidden(body: object) -> bool:
    text = json.dumps(body) if not isinstance(body, str) else body
    lower = text.lower()
    return any(marker in lower for marker in FORBIDDEN)


def main() -> int:
    failures: list[str] = []

    _, openapi = _request("GET", "/openapi.json")
    if not isinstance(openapi, dict):
        failures.append("openapi.json not JSON")
    else:
        paths = openapi.get("paths", {})
        for required in (
            "/api/crash-detection/start",
            "/api/crash-detection/settings/update",
            "/api/roadside-assistance/call",
            "/api/roadside-assistance/history",
            "/api/elderly/blood-pressure/sync",
        ):
            if required not in paths:
                failures.append(f"openapi missing {required}")

    token = _register_device("emergency-smoke-b7")

    crash_checks = [
        ("POST", "/api/crash-detection/start", {}),
        ("POST", "/api/crash-detection/settings/update", {"userId": "smoke-user", "sensitivity": 3.0, "geofenceRadius": 1000.0}),
        ("GET", "/api/crash-detection/status", None),
    ]
    for method, path, body in crash_checks:
        code, resp = _request(method, path, body, token)
        if code >= 500:
            failures.append(f"crash {method} {path} → {code}: {resp}")
        if _body_forbidden(resp):
            failures.append(f"crash {path} mock envelope")

    roadside_checks = [
        ("POST", "/api/roadside-assistance/call", {
            "userId": "smoke-user",
            "vehicleInfo": "smoke-test",
            "latitude": 55.75,
            "longitude": 37.62,
            "problemType": "breakdown",
        }),
        ("GET", "/api/roadside-assistance/history?userId=smoke-user", None),
    ]
    for method, path, body in roadside_checks:
        code, resp = _request(method, path, body, token)
        if code >= 500:
            failures.append(f"roadside {method} {path} → {code}: {resp}")
        if _body_forbidden(resp):
            failures.append(f"roadside {path} mock envelope")

    code, bp_resp = _request(
        "POST",
        "/api/elderly/blood-pressure/sync",
        {"userId": "smoke-user", "deviceId": "emergency-smoke-b7"},
    )
    if code >= 500:
        failures.append(f"elderly blood-pressure sync → {code}: {bp_resp}")
    if _body_forbidden(bp_resp):
        failures.append("elderly blood-pressure sync mock envelope")

    result = {
        "pass": len(failures) == 0,
        "domain": "emergency",
        "checks": len(crash_checks) + len(roadside_checks) + 1,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
