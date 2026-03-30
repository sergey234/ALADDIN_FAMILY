#!/usr/bin/env python3
import json
import os
import time
import uuid
from collections import defaultdict
from pathlib import Path

import requests


BASE_URL = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru").rstrip("/")
MATRIX_PATH = Path(
    os.environ.get(
        "ALADDIN_ENDPOINT_MATRIX",
        "docs/release/inventory/endpoint_matrix_enriched.json",
    )
)
OUT_PATH = Path(
    os.environ.get(
        "ALADDIN_IOS_SMOKE_REPORT",
        "docs/release/gates/ios-smoke-42-report.json",
    )
)
TARGET_COMPONENTS = int(os.environ.get("ALADDIN_IOS_SMOKE_COMPONENTS", "42"))
TIMEOUT = int(os.environ.get("ALADDIN_IOS_SMOKE_TIMEOUT", "12"))

FORBIDDEN_MARKERS = [
    "sfm_mock",
    "sfm_fallback",
    "sfm_error",
    "mock_fallback",
    "reports_compat",
]
ACCEPTABLE_STATUSES = {200, 201, 202, 204, 400, 401, 403, 404, 405, 409, 422}


def _token():
    device_id = f"rel13_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    r = requests.post(
        f"{BASE_URL}/api/auth/register-device",
        json={"device_id": device_id},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token") or data.get("token") or data.get("jwt")
    if not token:
        raise RuntimeError(f"No token in response: {data}")
    return token


def _has_markers(text: str):
    s = (text or "").lower()
    return [m for m in FORBIDDEN_MARKERS if m in s]


def _representative_endpoints(rows):
    grouped = defaultdict(list)
    for row in rows:
        comp = row.get("component", "unknown")
        method = (row.get("method") or "GET").upper()
        ep = row.get("endpoint")
        if not ep or not ep.startswith("/api/"):
            continue
        grouped[comp].append((method, ep))

    selected = []
    for comp in sorted(grouped.keys()):
        # Prefer GET for smoke card loading.
        candidates = grouped[comp]
        pick = None
        for m, ep in candidates:
            if m == "GET":
                pick = (m, ep)
                break
        if pick is None:
            pick = candidates[0]
        selected.append({"component": comp, "method": pick[0], "endpoint": pick[1]})
    return selected[:TARGET_COMPONENTS]


def main():
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    rows = matrix.get("rows", [])
    reps = _representative_endpoints(rows)
    token = _token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    checks = []
    for item in reps:
        method = item["method"]
        endpoint = item["endpoint"]
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            else:
                resp = requests.request(method, url, headers=headers, json={}, timeout=TIMEOUT)
            markers = _has_markers(resp.text)
            ok = resp.status_code in ACCEPTABLE_STATUSES and not markers
            checks.append(
                {
                    "component": item["component"],
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": resp.status_code,
                    "markers_found": markers,
                    "pass": ok,
                }
            )
        except Exception as e:
            checks.append(
                {
                    "component": item["component"],
                    "endpoint": endpoint,
                    "method": method,
                    "pass": False,
                    "error": str(e),
                }
            )

    passed = sum(1 for c in checks if c.get("pass"))
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "base_url": BASE_URL,
        "target_components": TARGET_COMPONENTS,
        "checked_components": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "pass": passed == len(checks),
        "checks": checks,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ios-smoke-42: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"checked={len(checks)} passed={passed} failed={len(checks)-passed}")
    print(f"report={OUT_PATH}")
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
