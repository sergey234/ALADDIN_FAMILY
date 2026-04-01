#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Короткий smoke‑тест для живых Notifications‑эндпоинтов.

Проверяет:
- GET  /api/notifications
- POST /api/notifications/read (негативный сценарий 404, если ID не существует)

Запуск:
  python docs/server/test_notifications_live.py

Можно переопределить базовый URL:
  ALADDIN_BASE_URL=https://aladdin-ai.ru python docs/server/test_notifications_live.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests


BASE_URL = os.environ.get("ALADDIN_BASE_URL", "http://149.154.65.180:8002")


def _show(name: str, resp: requests.Response) -> Dict[str, Any]:
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    entry = {
        "name": name,
        "url": resp.request.url if resp.request else "",
        "method": resp.request.method if resp.request else "",
        "status": resp.status_code,
        "ok": resp.ok,
        "body": body,
    }
    print(json.dumps(entry, ensure_ascii=False))
    return entry


def main() -> None:
    session = requests.Session()
    report = {"base_url": BASE_URL, "checks": []}

    # 1) Список уведомлений (ожидаем 200 и корректную структуру)
    r = session.get(f"{BASE_URL}/api/notifications", timeout=15)
    report["checks"].append(_show("notifications_list", r))

    # 2) Попытка отметить несуществующее уведомление прочитанным (ожидаемый 404)
    r = session.post(
        f"{BASE_URL}/api/notifications/read",
        json={"notificationId": "non_existing_id"},
        timeout=15,
    )
    report["checks"].append(_show("notifications_mark_read_missing", r))

    summary = {
        "base_url": BASE_URL,
        "ok_200": [c["name"] for c in report["checks"] if c["status"] == 200],
        "negatives": [
            {"name": c["name"], "status": c["status"]}
            for c in report["checks"]
            if c["status"] != 200
        ],
    }
    print("SUMMARY:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

