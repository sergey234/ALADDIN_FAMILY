#!/usr/bin/env python3
"""GATE-D IoT smoke — scan/discover via iot_security_agent (iot-07)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("IOT_SMOKE_BASE", "http://127.0.0.1:8002")
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"source":"mock"')
HOME = os.environ.get("IOT_SMOKE_HOME", "home_default")


def _request(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
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


def main() -> int:
    failures: list[str] = []

    _, openapi = _request("GET", "/openapi.json")
    paths = openapi.get("paths", {})
    for required in (
        f"/api/iot/status/{{homeId}}",
        f"/api/iot/devices/{{homeId}}",
        f"/api/iot/threats/{{homeId}}",
        f"/api/iot/scan/{{homeId}}",
        f"/api/iot/fix/{{threatId}}",
    ):
        if required not in paths:
            failures.append(f"openapi missing {required}")

    code, status = _request("GET", f"/api/iot/status/{HOME}")
    if code != 200:
        failures.append(f"status expected 200 got {code}: {status}")
    elif status.get("totalDevices", 0) < 1:
        failures.append("status expected seeded devices")

    code, devices = _request("GET", f"/api/iot/devices/{HOME}")
    if code != 200:
        failures.append(f"devices expected 200 got {code}")
    elif not devices.get("devices"):
        failures.append("devices list empty")

    code, scan = _request("POST", f"/api/iot/scan/{HOME}", {})
    raw = json.dumps(scan, ensure_ascii=False)
    for marker in FORBIDDEN:
        if marker in raw:
            failures.append(f"scan forbidden marker {marker}")
    if code != 200:
        failures.append(f"scan expected 200 got {code}: {scan}")
    elif not scan.get("scanId"):
        failures.append("scan missing scanId")
    elif scan.get("source") in ("mock", "sfm_mock"):
        failures.append("scan mock source")
    elif int(scan.get("threatsFound", 0)) < 1:
        failures.append(f"scan expected threatsFound>=1 got {scan.get('threatsFound')}")

    code, threats = _request("GET", f"/api/iot/threats/{HOME}")
    if code != 200:
        failures.append(f"threats expected 200 got {code}")
    elif int(threats.get("total", 0)) < 1:
        failures.append("threats empty after scan")

    threat_id = (threats.get("threats") or [{}])[0].get("threatId")
    if threat_id:
        code, fixed = _request("POST", f"/api/iot/fix/{threat_id}", {})
        if code != 200:
            failures.append(f"fix expected 200 got {code}: {fixed}")
        elif not fixed.get("success"):
            failures.append("fix missing success")

    report = {"pass": len(failures) == 0, "failures": failures, "homeId": HOME}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
