#!/usr/bin/env python3
"""ai-slo: sample health + chat latency, mock ban check."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002")
JWT = os.getenv("ALADDIN_TEST_JWT", "")


def get(path: str) -> tuple[int, float]:
    t0 = time.perf_counter()
    req = urllib.request.Request(f"{BASE}{path}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, time.perf_counter() - t0
    except urllib.error.HTTPError as e:
        return e.code, time.perf_counter() - t0


def post_chat() -> tuple[int, float, dict]:
    body = json.dumps({"message": "Статус защиты", "context": "protection_status"}).encode()
    headers = {"Content-Type": "application/json"}
    if JWT:
        headers["Authorization"] = f"Bearer {JWT}"
    req = urllib.request.Request(f"{BASE}/api/ai/assistant/chat", data=body, headers=headers, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            return resp.status, time.perf_counter() - t0, data
    except urllib.error.HTTPError as e:
        data = {}
        try:
            data = json.loads(e.read().decode())
        except Exception:
            data = {"detail": str(e)}
        return e.code, time.perf_counter() - t0, data


def main() -> int:
    mock_flag = os.getenv("AI_ALLOW_MOCK", "unknown")
    print(f"AI_ALLOW_MOCK={mock_flag}")

    h_status, h_lat = get("/api/health")
    print(f"health HTTP={h_status} latency_sec={h_lat:.3f}")

    if not JWT:
        print("WARN: ALADDIN_TEST_JWT not set — skip chat SLO")
        return 0 if h_status == 200 else 1

    chat_lats = []
    tool_ok = 0
    mock_hits = 0
    http_503 = 0
    for _ in range(5):
        status, lat, data = post_chat()
        chat_lats.append(lat)
        text = json.dumps(data, ensure_ascii=False)
        if "187 функций" in text or "1074 функций" in text:
            mock_hits += 1
        if status == 503:
            http_503 += 1
        if status == 200 and data.get("grounded") and data.get("tools_used"):
            tool_ok += 1
        print(f"chat HTTP={status} latency_sec={lat:.2f} grounded={data.get('grounded')}")

    chat_lats.sort()
    p95 = chat_lats[-1] if chat_lats else 0.0
    print(f"chat_p95_sec={p95:.2f}")
    print(f"tool_grounded_success={tool_ok}/5")
    print(f"mock_marker_count={mock_hits} (target 0)")
    print(f"http_503_count={http_503}/5")

    ok = h_status == 200 and mock_hits == 0 and p95 < 30.0
    print("SLO_SAMPLE_OK" if ok else "SLO_SAMPLE_WARN")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
