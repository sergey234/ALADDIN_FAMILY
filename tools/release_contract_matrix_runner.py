#!/usr/bin/env python3
import json
import os
import time
import uuid
from collections import Counter
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
        "ALADDIN_ENDPOINT_REPORT",
        "docs/release/gates/endpoint-report.json",
    )
)
TIMEOUT = int(os.environ.get("ALADDIN_CONTRACT_TIMEOUT", "12"))
LIMIT = int(os.environ.get("ALADDIN_CONTRACT_LIMIT", "0"))

FORBIDDEN_MARKERS = [
    "sfm_mock",
    "sfm_fallback",
    "sfm_error",
    "mock_fallback",
    "reports_compat",
    '"source":"mock"',
]
NON_FATAL_STATUSES = {200, 201, 202, 204, 400, 401, 403, 404, 405, 409, 422}


def _register_token() -> str:
    device_id = f"rel08_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    resp = requests.post(
        f"{BASE_URL}/api/auth/register-device",
        json={"device_id": device_id},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    token = (
        payload.get("access_token")
        or payload.get("token")
        or payload.get("jwt")
        or payload.get("accessToken")
    )
    if not token:
        raise RuntimeError(f"no token in auth payload: {payload}")
    return token


def _body_for_method(method: str):
    if method in {"POST", "PUT", "PATCH"}:
        return {}
    return None


def _has_mock_markers(text: str):
    compact = (text or "").replace(" ", "")
    return [m for m in FORBIDDEN_MARKERS if m in compact]


def main():
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    rows = matrix.get("rows", [])
    if LIMIT > 0:
        rows = rows[:LIMIT]

    token = _register_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    status_counter = Counter()
    method_counter = Counter()
    component_counter = Counter()
    failures = []
    results = []

    for row in rows:
        method = (row.get("method") or "GET").upper()
        endpoint = row.get("endpoint")
        component = row.get("component", "unknown")
        function = row.get("function", "unknown")
        if not endpoint:
            continue

        method_counter[method] += 1
        component_counter[component] += 1

        url = f"{BASE_URL}{endpoint}"
        body = _body_for_method(method)
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                timeout=TIMEOUT,
            )
            text = resp.text or ""
            status_counter[str(resp.status_code)] += 1
            markers = _has_mock_markers(text)

            passed = resp.status_code in NON_FATAL_STATUSES and len(markers) == 0
            if not passed:
                failures.append(
                    {
                        "component": component,
                        "function": function,
                        "method": method,
                        "endpoint": endpoint,
                        "status_code": resp.status_code,
                        "markers_found": markers,
                        "response_preview": text[:320],
                    }
                )

            results.append(
                {
                    "component": component,
                    "function": function,
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": resp.status_code,
                    "markers_found": markers,
                    "pass": passed,
                }
            )
        except Exception as exc:
            status_counter["exception"] += 1
            failures.append(
                {
                    "component": component,
                    "function": function,
                    "method": method,
                    "endpoint": endpoint,
                    "error": str(exc),
                }
            )
            results.append(
                {
                    "component": component,
                    "function": function,
                    "method": method,
                    "endpoint": endpoint,
                    "pass": False,
                    "error": str(exc),
                }
            )

    total = len(results)
    passed_count = sum(1 for x in results if x.get("pass"))
    report = {
        "base_url": BASE_URL,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "matrix_path": str(MATRIX_PATH),
        "total_checked": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass": len(failures) == 0,
        "status_distribution": dict(status_counter),
        "method_distribution": dict(method_counter),
        "component_distribution": dict(component_counter),
        "forbidden_markers": FORBIDDEN_MARKERS,
        "failures": failures,
        "results": results,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"contract-matrix: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"checked={total} passed={passed_count} failed={total-passed_count}")
    print(f"report={OUT_PATH}")
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
