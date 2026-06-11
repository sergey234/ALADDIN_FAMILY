#!/usr/bin/env python3
"""Functional 138 runner — fail on mock/404 wildcard (B-OPS-11)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8002"
FORBIDDEN = ("sfm_mock", "mock-real-protection", "mock_fallback", '"status":"success"')


def probe(path: str, method: str = "GET") -> tuple[int, str]:
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    checks = [
        ("GET", "/api/darkweb/stats", {401, 403}),  # explicit router exists
        ("POST", "/api/deepfake/analyze-video", {404, 405}),
        ("GET", "/api/protection/settings", {401, 403}),
    ]
    failures: list[str] = []
    for method, path, allowed in checks:
        code, body = probe(path, method)
        if code not in allowed and code == 200:
            for marker in FORBIDDEN:
                if marker in body:
                    failures.append(f"{path}: mock marker {marker}")
        if code == 200 and "status" in body and "success" in body and "verdict" not in body:
            if "mock" in body.lower() or "sfm_mock" in body:
                failures.append(f"{path}: wildcard mock envelope")

    report = {
        "runner": "functional_138_l3",
        "failures": failures,
        "pass": len(failures) == 0,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
