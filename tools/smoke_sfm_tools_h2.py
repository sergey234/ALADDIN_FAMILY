#!/usr/bin/env python3
"""h2-sfm-tools smoke: all 12 SFM functions via :8003."""
from __future__ import annotations

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8003/api/execute"

TOOLS = [
    ("get_analytics_overview", {"period": "week"}),
    ("get_components_health", {}),
    ("get_phishing_sensitivity", {}),
    ("get_protection_status", {}),
    ("family_members_summary", {}),
    ("ai_assistant_capabilities", {}),
    ("ai_assistant_analyze_threat", {"threat": "https://example.com"}),
    ("ai_assistant_recommendations", {}),
    ("ai_assistant_feedback", {"rating": 5}),
    ("ai_assistant_security_tips", {}),
    ("ai_assistant_report_incident", {"type": "phishing", "description": "test", "severity": "low"}),
    ("ai_assistant_chat", {"message": "статус", "context": "protection_status", "sfm_aggregates": {"protection_status": "ACTIVE"}}),
]


def call(func: str, params: dict) -> bool:
    body = json.dumps({"function": func, "params": params}).encode()
    req = urllib.request.Request(BASE, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            ok = resp.status == 200 and data.get("success")
            print(f"{'OK' if ok else 'FAIL'} {func}")
            return bool(ok)
    except Exception as exc:
        print(f"FAIL {func} {exc}")
        return False


def main() -> int:
    passed = sum(1 for f, p in TOOLS if call(f, p))
    print(f"h2-sfm-tools: {passed}/{len(TOOLS)}")
    return 0 if passed == len(TOOLS) else 1


if __name__ == "__main__":
    sys.exit(main())
