#!/usr/bin/env python3
"""GATE-D parental monitoring smoke — pc-06."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("PARENTAL_MONITORING_SMOKE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = (
    "sfm_mock",
    "mock-real-protection",
    "mock_fallback",
    '"source":"mock"',
    '"function":',
    "3.0.0-mock-real-protection",
)


def _request(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
) -> tuple[int, dict | str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw


def _register_device(device_id: str) -> str:
    _, reg = _request("POST", "/api/auth/register-device", {"deviceId": device_id})
    if not isinstance(reg, dict):
        raise RuntimeError(f"register-device invalid: {reg}")
    token = reg.get("token") or reg.get("access_token")
    if not token:
        raise RuntimeError(f"no jwt: {reg}")
    return token


def main() -> int:
    failures: list[str] = []

    _, openapi = _request("GET", "/openapi.json")
    if isinstance(openapi, dict):
        paths = openapi.get("paths", {})
        for required in (
            "/api/parental-control/monitoring/detail",
            "/api/parental-control/monitoring/events",
        ):
            if required not in paths:
                failures.append(f"openapi missing {required}")

    code, noauth = _request("GET", "/api/parental-control/monitoring/detail")
    if code not in (401, 403):
        failures.append(f"detail without JWT expected 401/403 got {code}")

    token = _register_device("parental-mon-smoke")
    _, reg_body = _request("POST", "/api/auth/register-device", {"deviceId": "parental-mon-smoke"})
    user_id = None
    if isinstance(reg_body, dict):
        user_id = reg_body.get("user_id") or reg_body.get("id")

    ingest = {
        "events": [
            {
                "kind": "url_visit",
                "payload": {
                    "site": "example-smoke.edu",
                    "visits": 2,
                    "url_sha256": "a" * 64,
                },
            }
        ]
    }
    code, ing = _request("POST", "/api/parental-control/monitoring/events", ingest, token)
    if code != 200:
        failures.append(f"ingest expected 200 got {code}: {ing}")
    elif isinstance(ing, dict) and not ing.get("success"):
        failures.append(f"ingest success false: {ing}")

    child_q = f"?childId={user_id}" if user_id else ""
    code, detail = _request("GET", f"/api/parental-control/monitoring/detail{child_q}", token=token)
    raw = json.dumps(detail, ensure_ascii=False) if isinstance(detail, dict) else str(detail)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"detail forbidden marker {marker}")
    if code != 200:
        failures.append(f"detail expected 200 got {code}: {detail}")
    elif not isinstance(detail, dict):
        failures.append("detail expected JSON object")
    elif "top_sites" not in detail:
        failures.append("detail missing top_sites (mock envelope?)")
    elif "summary" not in detail:
        failures.append("detail missing summary")

    report = {"pass": len(failures) == 0, "failures": failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
