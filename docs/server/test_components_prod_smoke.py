#!/usr/bin/env python3
"""GATE-D components smoke — phishing_protection + explicit /api/components/* (B1-07)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("COMPONENTS_SMOKE_BASE", "http://127.0.0.1:8002")
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
    for required in (
        "/api/components/configuration/{component_id}",
        "/api/components/status/{component_id}",
        "/api/phishing/sensitivity",
        "/api/phishing/block_suspicious",
    ):
        if required not in paths:
            failures.append(f"openapi missing {required}")

    token = _register_device("components-smoke")

    for component_id in ("phishing_protection_agent", "phishing_protection"):
        code, cfg = _request("GET", f"/api/components/configuration/{component_id}", token=token)
        raw = json.dumps(cfg, ensure_ascii=False)
        for marker in FORBIDDEN:
            if marker in raw:
                failures.append(f"{component_id} forbidden marker {marker}")
        if code != 200:
            failures.append(f"configuration/{component_id} expected 200 got {code}: {cfg}")
        elif "configuration" not in cfg:
            failures.append(f"configuration/{component_id} missing envelope")

    code, sens = _request("GET", "/api/phishing/sensitivity")
    raw = json.dumps(sens, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"phishing/sensitivity forbidden {marker}")
    if code != 200:
        failures.append(f"phishing/sensitivity expected 200 got {code}")
    elif sens.get("source") in ("mock", "sfm_mock"):
        failures.append("phishing/sensitivity mock source")
    elif not sens.get("sensitivity_level"):
        failures.append("phishing/sensitivity missing sensitivity_level")

    code, block = _request("GET", "/api/phishing/block_suspicious")
    if code != 200:
        failures.append(f"phishing/block_suspicious expected 200 got {code}")
    elif block.get("source") in ("mock", "sfm_mock"):
        failures.append("phishing/block_suspicious mock source")

    code, saved = _request(
        "POST",
        "/api/components/configuration/phishing_protection_agent",
        {"settings": {"sensitivityLevel": "high", "blockSuspiciousLinks": True}},
        token,
    )
    if code not in (200, 201):
        failures.append(f"configuration POST expected 200 got {code}: {saved}")

    code, reread = _request("GET", "/api/components/configuration/phishing_protection_agent", token=token)
    settings = (reread.get("configuration") or {}).get("settings") or {}
    if code != 200:
        failures.append(f"configuration re-read expected 200 got {code}")
    elif settings.get("sensitivityLevel") != "high":
        failures.append(f"configuration persist failed: {settings}")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
