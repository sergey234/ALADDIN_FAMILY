#!/usr/bin/env python3
"""CLI bridge: Hermes skill → SFM POST /api/execute (h2-sfm-tools)."""
from __future__ import annotations

import json
import sys
import urllib.request

SFM_URL = "http://127.0.0.1:8003/api/execute"


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: hermes_sfm_execute.py <function> [json_params]"}))
        return 2
    func = sys.argv[1]
    params = {}
    if len(sys.argv) > 2:
        params = json.loads(sys.argv[2])
    body = json.dumps({"function": func, "params": params}).encode()
    req = urllib.request.Request(
        SFM_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(resp.read().decode())
            return 0 if 200 <= resp.status < 300 else 1
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
