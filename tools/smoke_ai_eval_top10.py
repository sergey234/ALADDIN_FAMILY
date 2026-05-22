#!/usr/bin/env python3
"""ai-eval-top10-run: smoke top-10 intents via POST /api/ai/assistant/chat (needs JWT)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002")
JWT = os.getenv("ALADDIN_TEST_JWT", "")

CASES = [
    ("E01", "Всё ли у меня включено?", "protection_status"),
    ("E02", "Статус защиты ALADDIN", "protection_status"),
    ("E03", "Что заблокировали за неделю?", "general"),
    ("E04", "Сколько угроз сегодня?", "general"),
    ("E05", "Проверь ссылку https://example.com/path", "threat_analysis"),
    ("E06", "Это фишинговое письмо?", "threat_analysis"),
    ("E07", "Кто в моей семье?", "general"),
    ("E08", "Дети под защитой?", "general"),
    ("E09", "Как ограничить YouTube ребёнку?", "general"),
    ("E10", "Почему VPN отключился?", "general"),
]

FORBIDDEN = ("187 функций", "1074 функций", "3 потенциальные угрозы", "Заблокирован IP")


def post_chat(message: str, context: str) -> tuple[int, dict]:
    url = f"{BASE}/api/ai/assistant/chat"
    body = json.dumps({"message": message, "context": context, "stream": False}).encode()
    headers = {"Content-Type": "application/json"}
    if JWT:
        headers["Authorization"] = f"Bearer {JWT}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        payload = {}
        try:
            payload = json.loads(e.read().decode())
        except Exception:
            payload = {"detail": str(e)}
        return e.code, payload


def main() -> int:
    if not JWT:
        print("WARN: set ALADDIN_TEST_JWT for authenticated eval")
    passed = 0
    for case_id, msg, ctx in CASES:
        status, data = post_chat(msg, ctx)
        text = json.dumps(data, ensure_ascii=False)
        bad = any(p in text for p in FORBIDDEN)
        ok = False
        if status == 200:
            ok = bool(data.get("response")) and not bad
            if data.get("grounded") is False and "функций" in text:
                ok = False
        elif status == 503:
            ok = False  # prod eval requires SFM up
        if status == 200 and bad:
            ok = False
        print(
            f"{case_id} HTTP={status} ok={ok} grounded={data.get('grounded')} "
            f"tools={data.get('tools_used')}"
        )
        if ok:
            passed += 1
    print(f"PASS {passed}/{len(CASES)} (need >=9)")
    return 0 if passed >= 9 else 1


if __name__ == "__main__":
    sys.exit(main())
