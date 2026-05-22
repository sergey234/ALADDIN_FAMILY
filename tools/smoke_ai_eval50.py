#!/usr/bin/env python3
"""ai-eval-50-run: full E01–E50 regression (JWT required)."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002")
JWT = os.getenv("ALADDIN_TEST_JWT", "")

FORBIDDEN = ("187 функций", "1074 функций", "3 потенциальные угрозы", "Заблокирован IP")

CASES = [
    ("E01", "Всё ли у меня включено?", "protection_status"),
    ("E02", "Статус защиты ALADDIN", "protection_status"),
    ("E03", "Что заблокировали за неделю?", "general"),
    ("E04", "Сколько угроз сегодня?", "general"),
    ("E05", "Проверь ссылку https://evil.example/phish", "threat_analysis"),
    ("E06", "Это фишинговое письмо?", "threat_analysis"),
    ("E07", "Кто в моей семье?", "general"),
    ("E08", "Дети под защитой?", "general"),
    ("E09", "Как ограничить YouTube ребёнку?", "general"),
    ("E10", "Почему VPN отключился?", "general"),
    ("E11", "Какие модули защиты активны?", "protection_status"),
    ("E12", "Покажи статистику безопасности", "general"),
    ("E13", "Насколько точна защита?", "general"),
    ("E14", "Есть ли ложные срабатывания?", "general"),
    ("E15", "Система работает?", "protection_status"),
    ("E16", "Что с антифишингом?", "general"),
    ("E17", "Сколько фишинга заблокировали?", "general"),
    ("E18", "Аптайм защиты?", "general"),
    ("E19", "Сколько членов семьи?", "general"),
    ("E20", "Как добавить ребёнка?", "general"),
    ("E21", "Заблокировать игры", "general"),
    ("E22", "Родительский контроль где?", "general"),
    ("E23", "Лимит экранного времени", "general"),
    ("E24", "Ребёнок видит что в интернете?", "general"),
    ("E25", "Семейный турнир что это?", "general"),
    ("E26", "Семейный чат безопасен?", "general"),
    ("E27", "Включи защиту сети", "general"),
    ("E28", "Почему медленный VPN?", "general"),
    ("E29", "Защита Wi-Fi", "general"),
    ("E30", "Мобильная защита что делает?", "general"),
    ("E31", "Фаервол включён?", "protection_status"),
    ("E32", "Сеть дома защищена?", "general"),
    ("E33", "Что даёт Premium?", "general"),
    ("E34", "Чем Free отличается?", "general"),
    ("E35", "Сколько стоит подписка?", "general"),
    ("E36", "Какие функции в тарифе?", "general"),
    ("E37", "Как отменить подписку?", "general"),
    ("E38", "Пробный период есть?", "general"),
    ("E39", "Как включить E2EE в чате?", "general"),
    ("E40", "Сервер видит сообщения семьи?", "general"),
    ("E41", "Что отправляется в AI?", "general"),
    ("E42", "Удалить историю AI", "general"),
    ("E43", "Не отправлять мои данные в AI", "general"),
    ("E44", "В Telegram есть E2EE?", "general"),
    ("E45", "Что улучшить в защите?", "recommendations"),
    ("E46", "Дай совет по безопасности", "general"),
    ("E47", "Сообщить об атаке", "general"),
    ("E48", "Ответ не помог", "feedback"),
    ("E49", "Что ты умеешь?", "general"),
    ("E50", "Привет", "general"),
]


def post_chat(message: str, context: str) -> tuple[int, dict, float]:
    url = f"{BASE}/api/ai/assistant/chat"
    body = json.dumps({"message": message, "context": context}).encode()
    headers = {"Content-Type": "application/json"}
    if JWT:
        headers["Authorization"] = f"Bearer {JWT}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            elapsed = time.perf_counter() - t0
            return resp.status, json.loads(resp.read().decode()), elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - t0
        payload = {}
        try:
            payload = json.loads(e.read().decode())
        except Exception:
            payload = {"detail": str(e)}
        return e.code, payload, elapsed


def is_ok(status: int, data: dict) -> bool:
    if status != 200:
        return False
    text = json.dumps(data, ensure_ascii=False)
    if any(p in text for p in FORBIDDEN):
        return False
    if not (data.get("response") or "").strip():
        return False
    if data.get("grounded") is False and "функций" in text:
        return False
    return True


def main() -> int:
    if not JWT:
        print("FAIL: set ALADDIN_TEST_JWT")
        return 1
    passed = 0
    latencies = []
    for case_id, msg, ctx in CASES:
        try:
            status, data, elapsed = post_chat(msg, ctx)
        except Exception as exc:
            print(f"{case_id} HTTP=0 ok=False error={exc.__class__.__name__}")
            continue
        if status == 200:
            latencies.append(elapsed)
        ok = is_ok(status, data)
        print(
            f"{case_id} HTTP={status} ok={ok} {elapsed:.2f}s "
            f"grounded={data.get('grounded')} tools={data.get('tools_used')}"
        )
        if ok:
            passed += 1
    if latencies:
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95) - 1]
        print(f"latency_p95_chat_sec={p95:.2f} samples={len(latencies)}")
    print(f"PASS {passed}/{len(CASES)} (need >=45)")
    return 0 if passed >= 45 else 1


if __name__ == "__main__":
    sys.exit(main())
