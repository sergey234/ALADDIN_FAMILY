#!/usr/bin/env python3
"""B1-11 / sec-10 — explicit security routers published in OpenAPI (no wildcard-only)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("SECURITY_OPENAPI_SMOKE_BASE", "http://127.0.0.1:8002")

# path, method, required OpenAPI tag (explicit app.routers.*)
EXPLICIT_ROUTES: list[tuple[str, str, str]] = [
    ("POST", "/api/antifake/check/text", "antifake"),
    ("POST", "/api/antifake/check/url", "antifake"),
    ("GET", "/api/darkweb/stats", "darkweb"),
    ("POST", "/api/darkweb/scan/start", "darkweb"),
    ("POST", "/api/darkweb/check", "darkweb"),
    ("POST", "/api/identity-theft/detect", "identity-theft"),
    ("GET", "/api/identity-theft/stats", "identity-theft"),
    ("POST", "/api/identity-theft/check/fraud", "identity-theft"),
    ("GET", "/api/data-cleanup/stats", "data-cleanup"),
    ("POST", "/api/data-cleanup/start", "data-cleanup"),
    ("GET", "/api/data-cleanup/records", "data-cleanup"),
    ("POST", "/api/location-bubble/generate", "location-bubble"),
    ("GET", "/api/location-bubble/stats", "location-bubble"),
    ("GET", "/api/location-bubble/settings", "location-bubble"),
    ("POST", "/api/antivirus/scan", "antivirus"),
    ("POST", "/api/malware/scan", "malware"),
    ("GET", "/api/malware/threats", "malware"),
    ("GET", "/api/components/configuration/{component_id}", "components"),
    ("GET", "/api/components/status/{component_id}", "components"),
    ("GET", "/api/phishing/sensitivity", "phishing"),
    ("GET", "/api/phishing/block_suspicious", "phishing"),
    ("GET", "/api/iot/status/{homeId}", "iot"),
    ("GET", "/api/iot/devices/{homeId}", "iot"),
    ("GET", "/api/iot/threats/{homeId}", "iot"),
    ("POST", "/api/iot/scan/{homeId}", "iot"),
    ("POST", "/api/iot/fix/{threatId}", "iot"),
    ("GET", "/api/mobile/app_lock", "mobile-security"),
    ("GET", "/api/mobile/biometric", "mobile-security"),
    ("GET", "/api/mobile/security/check", "mobile-security"),
    ("POST", "/api/mobile/scan", "mobile-security"),
    ("GET", "/api/parental-control/monitoring/detail", "parental-monitoring"),
    ("POST", "/api/parental-control/monitoring/events", "parental-monitoring"),
]

FORBIDDEN_LEGACY_TAGS = frozenset(
    {
        "Identity Theft Protection",
        "Parental Control",
        "Dark Web Monitoring",
        "Data Cleanup",
    }
)


def _fetch_openapi() -> tuple[int, dict | str]:
    req = urllib.request.Request(f"{BASE}/openapi.json", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw


def main() -> int:
    failures: list[str] = []

    code, openapi = _fetch_openapi()
    if code != 200:
        failures.append(f"openapi.json expected 200 got {code}")
        print(json.dumps({"pass": False, "failures": failures}, indent=2))
        return 1
    if not isinstance(openapi, dict):
        failures.append("openapi.json not a JSON object")
        print(json.dumps({"pass": False, "failures": failures}, indent=2))
        return 1

    paths = openapi.get("paths", {})
    if not paths:
        failures.append("openapi paths empty")

    for method, path, tag in EXPLICIT_ROUTES:
        spec = paths.get(path)
        if not spec:
            failures.append(f"missing path {path}")
            continue
        op = spec.get(method.lower())
        if not op:
            failures.append(f"{path} missing method {method}")
            continue
        tags = op.get("tags") or []
        if tag not in tags:
            failures.append(f"{path} {method} tags={tags} expected explicit tag {tag!r}")
        for legacy in FORBIDDEN_LEGACY_TAGS:
            if legacy in tags and tag not in tags:
                failures.append(f"{path} {method} still has legacy tag {legacy!r}")

    api_paths = [p for p in paths if p.startswith("/api/")]
    if len(api_paths) < 100:
        failures.append(f"openapi suspiciously small: {len(api_paths)} /api paths")

    report = {
        "pass": len(failures) == 0,
        "failures": failures,
        "checked_routes": len(EXPLICIT_ROUTES),
        "api_path_count": len(api_paths),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
