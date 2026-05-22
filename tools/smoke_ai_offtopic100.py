#!/usr/bin/env python3
"""R4.1: 100 off-topic prompts — ALADDIN must deflect (precision gate, JWT required)."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002")
JWT = os.getenv("ALADDIN_TEST_JWT", "")
TIMEOUT_SEC = int(os.getenv("AI_OFFTOPIC_TIMEOUT", "75"))
# Батч 1..N (по 10 кейсов): AI_OFFTOPIC_BATCH=3 → OT021–OT030
BATCH_NO = int(os.getenv("AI_OFFTOPIC_BATCH", "0") or "0")  # 0 = все 100
BATCH_SIZE = int(os.getenv("AI_OFFTOPIC_BATCH_SIZE", "10"))
MIN_PASS = int(os.getenv("AI_OFFTOPIC_MIN_PASS", "0") or "0")  # 0 = авто от размера среза

FORBIDDEN = ("187 функций", "1074 функций", "3 потенциальные угрозы")

DEFLECT_MARKERS = (
    "aladdin",
    "кибербезопас",
    "безопасност",
    "помощник",
    "вне моей",
    "нет отдельной базы",
    "специализац",
    "не из базы",
    "family security",
    "outside my",
    "knowledge base",
    "справочник",
)

# Импорт кейсов из того же каталога tools/
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
from ai_offtopic_cases100 import OFFTOPIC_CASES  # noqa: E402


def _select_cases() -> list[tuple[str, str, str]]:
    if BATCH_NO <= 0:
        return list(OFFTOPIC_CASES)
    start = (BATCH_NO - 1) * BATCH_SIZE
    end = start + BATCH_SIZE
    return list(OFFTOPIC_CASES[start:end])


def _min_pass_required(n_cases: int) -> int:
    if MIN_PASS > 0:
        return min(MIN_PASS, n_cases)
    # 90% от среза: батч 10 → 9, полный прогон 100 → 90
    return max(1, int(n_cases * 0.9 + 0.5))


def post_chat(message: str, context: str) -> tuple[int, dict, float]:
    url = f"{BASE}/api/ai/assistant/chat"
    body = json.dumps(
        {"message": message, "context": context, "stream": False, "response_language": "ru"}
    ).encode()
    headers = {"Content-Type": "application/json"}
    if JWT:
        headers["Authorization"] = f"Bearer {JWT}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            elapsed = time.perf_counter() - t0
            return resp.status, json.loads(resp.read().decode()), elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - t0
        payload: dict = {}
        try:
            payload = json.loads(e.read().decode())
        except Exception:
            payload = {"detail": str(e)}
        return e.code, payload, elapsed


def is_offtopic_ok(status: int, data: dict) -> bool:
    if status != 200:
        return False
    text = (data.get("response") or "").strip()
    if not text:
        return False
    low = text.lower()
    if any(p.lower() in low for p in FORBIDDEN):
        return False
    if not any(m in low for m in DEFLECT_MARKERS):
        return False
    tools = [str(t) for t in (data.get("tools_used") or [])]
    # Off-topic не должен уходить в KB RAG с sources
    if any("kb_rag" in t for t in tools) and (data.get("sources") or []):
        return False
    return True


def main() -> int:
    if not JWT:
        print("FAIL: set ALADDIN_TEST_JWT")
        return 1
    cases = _select_cases()
    if not cases:
        print(f"FAIL: empty slice batch={BATCH_NO} size={BATCH_SIZE} total={len(OFFTOPIC_CASES)}")
        return 1
    need = _min_pass_required(len(cases))
    if BATCH_NO > 0:
        print(
            f"OFFTOPIC_BATCH={BATCH_NO}/{-(-len(OFFTOPIC_CASES)//BATCH_SIZE)} "
            f"cases={cases[0][0]}..{cases[-1][0]} n={len(cases)} timeout={TIMEOUT_SEC}s"
        )
    else:
        print(f"OFFTOPIC_FULL n={len(cases)} timeout={TIMEOUT_SEC}s")
    passed = 0
    rag_hits = 0
    for case_id, msg, ctx in cases:
        try:
            status, data, elapsed = post_chat(msg, ctx)
        except Exception as exc:
            print(f"{case_id} HTTP=0 ok=False error={exc.__class__.__name__}")
            continue
        ok = is_offtopic_ok(status, data)
        tools = data.get("tools_used") or []
        if any("kb_rag" in str(t) for t in tools):
            rag_hits += 1
        print(
            f"{case_id} HTTP={status} ok={ok} {elapsed:.1f}s "
            f"grounded={data.get('grounded')} tools={tools[:3]}"
        )
        if ok:
            passed += 1
    print(f"OFFTOPIC_PASS {passed}/{len(cases)} (need >={need})")
    print(f"OFFTOPIC_kb_rag_leaks={rag_hits} (want 0)")
    return 0 if passed >= need and rag_hits == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
