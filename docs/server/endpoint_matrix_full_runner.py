#!/usr/bin/env python3
"""
Endpoint Matrix Full Runner (Build 124/125)

Runs a focused full-regression check for critical endpoints in:
- no-auth mode
- auth mode (if ALADDIN_AUTH_TOKEN is set)

Outputs:
- JSON report with per-request details and fail flags
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")
MOCK_SOURCE_VALUES = {"sfm_mock", "sfm_fallback", "sfm_error", "mock"}


@dataclass
class EndpointCase:
    name: str
    method: str
    path: str
    query: Optional[Dict[str, str]] = None
    critical: bool = True
    business_ready: bool = True


def request_once(base_url: str, case: EndpointCase, auth_token: Optional[str]) -> Dict:
    query = f"?{urlencode(case.query)}" if case.query else ""
    url = f"{base_url}{case.path}{query}"

    headers = {
        "Accept": "application/json",
        "User-Agent": "ALADDIN-Matrix-Runner/1.0",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    req = Request(url=url, method=case.method.upper(), headers=headers)
    started = time.time()

    status_code = None
    response_text = ""
    error_text = None

    try:
        with urlopen(req, timeout=12) as resp:
            status_code = resp.getcode()
            response_text = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        status_code = e.code
        response_text = e.read().decode("utf-8", errors="replace")
        error_text = str(e)
    except URLError as e:
        error_text = f"URLError: {e}"
    except Exception as e:  # noqa: BLE001
        error_text = f"Exception: {e}"

    duration_ms = int((time.time() - started) * 1000)

    body_json = None
    source = None
    result = None
    detail = None
    if response_text:
        try:
            body_json = json.loads(response_text)
            if isinstance(body_json, dict):
                source = body_json.get("source")
                result = body_json.get("result")
                detail = body_json.get("detail")
        except json.JSONDecodeError:
            body_json = None

    has_mock_marker = (
        (isinstance(source, str) and source in MOCK_SOURCE_VALUES)
        or result == "mock_fallback"
        or ("sfm_mock" in response_text)
        or ("mock_fallback" in response_text)
    )

    unauthorized_503 = bool(case.business_ready and status_code == 503 and not has_mock_marker)
    jwt_in_url = bool(JWT_PATTERN.search(url))

    fail_reasons: List[str] = []
    if has_mock_marker:
        fail_reasons.append("mock_marker_detected")
    if unauthorized_503:
        fail_reasons.append("unauthorized_503")
    if jwt_in_url:
        fail_reasons.append("jwt_in_url")
    if status_code is None:
        fail_reasons.append("request_failed_no_status")

    return {
        "name": case.name,
        "method": case.method,
        "url": url,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "source": source,
        "result": result,
        "detail": detail,
        "has_mock_marker": has_mock_marker,
        "unauthorized_503": unauthorized_503,
        "jwt_in_url": jwt_in_url,
        "fail": len(fail_reasons) > 0,
        "fail_reasons": fail_reasons,
        "error_text": error_text,
        "response_preview": response_text[:500],
    }


def build_cases() -> List[EndpointCase]:
    return [
        EndpointCase(
            name="parental_v1_stats",
            method="GET",
            path="/api/v1/parental-control/stats",
            query={"childId": "8E0515FE-33AC-4221-93E0-9912DAE47FBC"},
        ),
        EndpointCase(
            name="parental_time_limits",
            method="GET",
            path="/api/parental-control/time-limits/8E0515FE-33AC-4221-93E0-9912DAE47FBC",
        ),
        EndpointCase(
            name="parental_geofences",
            method="GET",
            path="/api/parental-control/geofences/8E0515FE-33AC-4221-93E0-9912DAE47FBC",
        ),
        EndpointCase(name="family_members", method="GET", path="/api/family/members"),
        EndpointCase(name="user_profile", method="GET", path="/api/user/profile"),
        EndpointCase(
            name="gamification_rewards_shop",
            method="GET",
            path="/api/gamification/rewards/shop",
            query={"userId": "test_user"},
        ),
        EndpointCase(
            name="gamification_balance",
            method="GET",
            path="/api/gamification/balance/test_user",
        ),
        EndpointCase(
            name="metrics_upload_health",
            method="POST",
            path="/api/metrics/upload",
            business_ready=False,
            critical=False,
        ),
    ]


def main() -> int:
    base_url = os.getenv("ALADDIN_BASE_URL", "http://149.154.65.180:8002").rstrip("/")
    auth_token = os.getenv("ALADDIN_AUTH_TOKEN")

    cases = build_cases()
    scenarios = [("no_auth", None)]
    if auth_token:
        scenarios.append(("auth", auth_token))

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "scenarios": {},
        "summary": {},
    }

    all_results: List[Dict] = []
    for scenario_name, token in scenarios:
        scenario_results = []
        for case in cases:
            if case.method == "POST" and case.path == "/api/metrics/upload":
                # Keep this runner non-invasive: skip active metrics upload mutation.
                continue
            result = request_once(base_url, case, token)
            scenario_results.append(result)
            all_results.append(result)
        report["scenarios"][scenario_name] = scenario_results

    report["summary"] = {
        "total_requests": len(all_results),
        "failed_requests": sum(1 for r in all_results if r["fail"]),
        "mock_marker_count": sum(1 for r in all_results if r["has_mock_marker"]),
        "unauthorized_503_count": sum(1 for r in all_results if r["unauthorized_503"]),
        "jwt_in_url_count": sum(1 for r in all_results if r["jwt_in_url"]),
    }

    out_dir = "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/server"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ENDPOINT_MATRIX_BASELINE_REPORT_BUILD_124_125.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Report saved: {out_path}")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

