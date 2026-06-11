#!/usr/bin/env python3
"""GATE-D mobile security smoke — mob-06."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("MOBILE_SECURITY_SMOKE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"source":"mock"')


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
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
    for required in (
        "/api/mobile/app_lock",
        "/api/mobile/biometric",
        "/api/mobile/security/check",
        "/api/mobile/scan",
    ):
        if required not in paths:
            failures.append(f"openapi missing {required}")

    token = _register_device("mob-sec-smoke")

    for path in ("/api/mobile/app_lock", "/api/mobile/biometric"):
        code, body = _request("GET", path, token=token)
        raw = json.dumps(body, ensure_ascii=False)
        for marker in FORBIDDEN:
            if marker in raw:
                failures.append(f"{path} forbidden {marker}")
        if code != 200:
            failures.append(f"{path} expected 200 got {code}")
        elif body.get("source") in ("mock", "sfm_mock"):
            failures.append(f"{path} mock source")

    code, check = _request("GET", "/api/mobile/security/check?deviceId=mob-smoke-1", token=token)
    raw = json.dumps(check, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"security/check forbidden {marker}")
    if code != 200:
        failures.append(f"security/check expected 200 got {code}: {check}")
    elif "security_score" not in check:
        failures.append("security/check missing security_score")
    elif check.get("source") in ("mock", "sfm_mock"):
        failures.append("security/check mock source")

    code, scan = _request("POST", "/api/mobile/scan", {"device_id": "mob-smoke-1"}, token)
    if code != 200:
        failures.append(f"scan expected 200 got {code}: {scan}")
    elif not scan.get("scan_id"):
        failures.append("scan missing scan_id")

    code, cfg = _request("GET", "/api/components/configuration/mobile_security_agent", token=token)
    if code != 200:
        failures.append(f"components config expected 200 got {code}")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
