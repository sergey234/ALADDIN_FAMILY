#!/usr/bin/env python3
import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests


BASE_URL = os.environ.get("ALADDIN_API_BASE", "https://aladdin-ai.ru").rstrip("/")
OUT_PATH = Path(
    os.environ.get(
        "ALADDIN_ANTI_MOCK_REPORT",
        "docs/release/gates/anti-mock-report.json",
    )
)

FORBIDDEN_MARKERS = [
    "sfm_mock",
    "sfm_fallback",
    "sfm_error",
    "mock_fallback",
    "reports_compat",
    '"source":"mock"',
]


def _register_token() -> str:
    device_id = f"anti_mock_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    resp = requests.post(
        f"{BASE_URL}/api/auth/register-device",
        json={"device_id": device_id},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = (
        data.get("access_token")
        or data.get("token")
        or data.get("jwt")
        or data.get("accessToken")
    )
    if not token:
        raise RuntimeError(f"No token in auth response: {data}")
    return token


def _contains_forbidden_markers(payload_text: str):
    found = []
    normalized = payload_text.replace(" ", "")
    for marker in FORBIDDEN_MARKERS:
        if marker in normalized:
            found.append(marker)
    return found


def main():
    token = _register_token()
    headers = {"Authorization": f"Bearer {token}"}

    checks = [
        {"name": "darkweb_stats", "method": "GET", "path": "/api/reports/dark-web/stats", "expect_status": [200]},
        {"name": "identity_stats", "method": "GET", "path": "/api/reports/identity-theft/stats", "expect_status": [200]},
        {"name": "tracker_stats", "method": "GET", "path": "/api/reports/privacy/tracker/stats", "expect_status": [200]},
        {"name": "location_stats", "method": "GET", "path": "/api/reports/privacy/location/stats", "expect_status": [200]},
        {"name": "cleanup_stats", "method": "GET", "path": "/api/reports/privacy/cleanup/stats", "expect_status": [200]},
        {"name": "driving_stats", "method": "GET", "path": "/api/reports/driving/stats", "expect_status": [200]},
        {"name": "ai_categories_stats", "method": "GET", "path": "/api/reports/ai-categories/stats", "expect_status": [200]},
        {
            "name": "reports_wildcard_unknown_blocked",
            "method": "GET",
            "path": "/api/reports/unknown-path-for-wildcard-check",
            "expect_status": [404],
        },
    ]

    report = {
        "base_url": BASE_URL,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "forbidden_markers": FORBIDDEN_MARKERS,
        "results": [],
        "pass": True,
    }

    for check in checks:
        url = f"{BASE_URL}{check['path']}"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            payload_text = resp.text or ""
            markers = _contains_forbidden_markers(payload_text)
            status_ok = resp.status_code in check["expect_status"]
            check_pass = status_ok and len(markers) == 0
            report["results"].append(
                {
                    "name": check["name"],
                    "path": check["path"],
                    "status_code": resp.status_code,
                    "expected_status": check["expect_status"],
                    "markers_found": markers,
                    "pass": check_pass,
                    "response_preview": payload_text[:400],
                }
            )
            if not check_pass:
                report["pass"] = False
        except Exception as exc:
            report["results"].append(
                {
                    "name": check["name"],
                    "path": check["path"],
                    "pass": False,
                    "error": str(exc),
                }
            )
            report["pass"] = False

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"anti-mock gate: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"report: {OUT_PATH}")
    if not report["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
