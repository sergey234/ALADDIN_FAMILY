#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = os.getenv("ALADDIN_BASE_URL", "http://149.154.65.180:8002").rstrip("/")
AUTH_TOKEN = os.getenv("ALADDIN_AUTH_TOKEN")

ROOT = "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"
APP_CONFIG = f"{ROOT}/Core/Config/AppConfig.swift"
API_SERVICE = f"{ROOT}/Core/Network/APIService.swift"
OUT_JSON = f"{ROOT}/docs/server/FULL_SYSTEM_ENDPOINT_AUDIT_REPORT_BUILD_124_125.json"
OUT_MD = f"{ROOT}/docs/server/FULL_SYSTEM_ENDPOINT_AUDIT_REPORT_BUILD_124_125.md"

JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")
PATH_PARAM_RE = re.compile(r"\{([^}]+)\}")


@dataclass
class EndpointCase:
    method: str
    path: str
    source: str  # openapi | ios
    critical: bool
    runnable: bool
    reason: str = ""


def http_json(url: str, method: str = "GET", body: Optional[Dict] = None, auth: bool = False) -> Tuple[Optional[int], str]:
    headers = {"Accept": "application/json", "User-Agent": "ALADDIN-Full-Audit/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if auth and AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    req = Request(url=url, method=method, headers=headers, data=data)
    try:
        with urlopen(req, timeout=12) as resp:
            return resp.getcode(), resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except URLError as e:
        return None, f"URLError: {e}"
    except Exception as e:  # noqa: BLE001
        return None, f"Exception: {e}"


def fetch_openapi_paths() -> Dict[str, Dict]:
    status, body = http_json(f"{BASE_URL}/openapi.json")
    if status != 200:
        return {}
    try:
        payload = json.loads(body)
        return payload.get("paths", {})
    except Exception:
        return {}


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def collect_ios_endpoints() -> List[str]:
    txt = read_file(APP_CONFIG)
    return sorted(set(re.findall(r'static let \w+\s*=\s*"(/api/[^"]+)"', txt)))


def collect_ios_http_calls() -> List[Tuple[str, str]]:
    txt = read_file(API_SERVICE)
    calls = []
    for m in re.finditer(r"networkManager\.(get|post|put|delete)\(endpoint:\s*([^)]+)\)", txt):
        calls.append((m.group(1).upper(), m.group(2).strip()))
    return calls


def concretize_path(path: str) -> str:
    replacements = {
        "childId": "8E0515FE-33AC-4221-93E0-9912DAE47FBC",
        "familyId": "family_test",
        "userId": "test_user",
        "component_id": "network_protection",
        "componentId": "network_protection",
        "tournamentId": "tour_1",
        "achievementId": "ach_1",
        "gameId": "game_1",
        "geofenceId": "geo_1",
        "dataId": "data_1",
        "messageId": "msg_1",
        "memberId": "member_1",
    }

    def repl(match: re.Match) -> str:
        key = match.group(1)
        return replacements.get(key, "test")

    return PATH_PARAM_RE.sub(repl, path)


def classify_critical(path: str) -> bool:
    critical_prefixes = (
        "/api/v1/parental-control",
        "/api/parental-control",
        "/api/parental/",
        "/api/family/",
        "/api/user/profile",
        "/api/gamification/",
    )
    return path.startswith(critical_prefixes)


def is_safe_to_run(method: str, path: str) -> Tuple[bool, str]:
    if method == "GET":
        return True, ""
    # Safe-mode: avoid mutating production state by default.
    if method == "POST" and path in ("/api/metrics/upload",):
        return True, "safe_post_allowlist"
    return False, "mutation_skipped_safe_mode"


def analyze_response(path: str, status: Optional[int], body: str, runnable: bool) -> Dict:
    source = None
    result = None
    detail = None
    try:
        obj = json.loads(body)
        if isinstance(obj, dict):
            source = obj.get("source")
            result = obj.get("result")
            detail = obj.get("detail")
    except Exception:
        pass

    mock = (
        source in {"sfm_mock", "sfm_fallback", "sfm_error", "mock"}
        or result == "mock_fallback"
        or "sfm_mock" in body
        or "mock_fallback" in body
    )
    unauthorized_503 = bool(classify_critical(path) and status == 503 and not mock)
    jwt_in_url = bool(JWT_RE.search(path))
    fail_reasons = []
    if mock:
        fail_reasons.append("mock_marker_detected")
    if unauthorized_503:
        fail_reasons.append("unauthorized_503")
    if jwt_in_url:
        fail_reasons.append("jwt_in_url")
    if status is None and runnable:
        fail_reasons.append("request_no_status")
    return {
        "source": source,
        "result": result,
        "detail": detail,
        "mock_marker": mock,
        "unauthorized_503": unauthorized_503,
        "jwt_in_url": jwt_in_url,
        "fail_reasons": fail_reasons,
    }


def main() -> int:
    openapi_paths = fetch_openapi_paths()
    ios_endpoints = collect_ios_endpoints()
    ios_calls = collect_ios_http_calls()

    cases: List[EndpointCase] = []

    for path, methods in openapi_paths.items():
        for method in methods.keys():
            m = method.upper()
            runnable, reason = is_safe_to_run(m, path)
            cases.append(
                EndpointCase(
                    method=m,
                    path=path,
                    source="openapi",
                    critical=classify_critical(path),
                    runnable=runnable,
                    reason=reason,
                )
            )

    # Add iOS-only paths not present in openapi (contract drift candidates)
    openapi_path_set = set(openapi_paths.keys())
    for ep in ios_endpoints:
        if ep not in openapi_path_set:
            runnable, reason = is_safe_to_run("GET", ep)
            cases.append(
                EndpointCase(
                    method="GET",
                    path=ep,
                    source="ios",
                    critical=classify_critical(ep),
                    runnable=runnable,
                    reason="ios_path_not_in_openapi",
                )
            )

    seen = set()
    dedup_cases = []
    for c in cases:
        key = (c.method, c.path, c.source)
        if key not in seen:
            seen.add(key)
            dedup_cases.append(c)

    results = []
    for c in dedup_cases:
        concrete_path = concretize_path(c.path)
        url = f"{BASE_URL}{concrete_path}"
        started = time.time()
        if c.runnable:
            status, body = http_json(url, method=c.method, body=None, auth=bool(AUTH_TOKEN))
        else:
            status, body = None, ""
        elapsed_ms = int((time.time() - started) * 1000)
        analysis = analyze_response(concrete_path, status, body, c.runnable)
        results.append(
            {
                "method": c.method,
                "path_template": c.path,
                "path": concrete_path,
                "url": url,
                "source_inventory": c.source,
                "critical": c.critical,
                "runnable": c.runnable,
                "skip_reason": c.reason if not c.runnable else "",
                "status_code": status,
                "duration_ms": elapsed_ms,
                "response_preview": body[:500],
                **analysis,
            }
        )

    summary = {
        "total_cases": len(results),
        "runnable_cases": sum(1 for r in results if r["runnable"]),
        "skipped_cases": sum(1 for r in results if not r["runnable"]),
        "critical_cases": sum(1 for r in results if r["critical"]),
        "critical_runnable": sum(1 for r in results if r["critical"] and r["runnable"]),
        "failed_cases": sum(1 for r in results if len(r["fail_reasons"]) > 0),
        "mock_marker_count": sum(1 for r in results if r["mock_marker"]),
        "unauthorized_503_count": sum(1 for r in results if r["unauthorized_503"]),
        "jwt_in_url_count": sum(1 for r in results if r["jwt_in_url"]),
        "contract_drift_candidates": sum(1 for r in results if r["source_inventory"] == "ios"),
        "ios_http_call_sites": len(ios_calls),
        "ios_endpoint_constants": len(ios_endpoints),
        "openapi_paths": len(openapi_paths),
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "auth_mode": "auth" if AUTH_TOKEN else "no_auth",
        "summary": summary,
        "results": results,
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    fail_top = [r for r in results if r["fail_reasons"]][:40]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Full System Endpoint Audit Report (Build 124/125)\n\n")
        f.write(f"- Generated: `{report['generated_at']}`\n")
        f.write(f"- Base URL: `{BASE_URL}`\n")
        f.write(f"- Auth mode: `{report['auth_mode']}`\n\n")
        f.write("## Summary\n\n")
        for k, v in summary.items():
            f.write(f"- **{k}**: `{v}`\n")
        f.write("\n## Top Fail Cases (first 40)\n\n")
        f.write("| Method | Path | HTTP | Fail Reasons |\n|---|---|---:|---|\n")
        for r in fail_top:
            f.write(f"| {r['method']} | `{r['path']}` | {r['status_code']} | `{','.join(r['fail_reasons'])}` |\n")

    print(f"Saved JSON report: {OUT_JSON}")
    print(f"Saved MD report: {OUT_MD}")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

