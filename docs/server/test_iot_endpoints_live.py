#!/usr/bin/env python3
"""
Короткий smoke‑тест для живых IoT‑эндпоинтов.

Проверяет:
- GET  /api/iot/status/{homeId}
- GET  /api/iot/devices/{homeId}
- GET  /api/iot/threats/{homeId}
- POST /api/iot/device/{deviceId}/block
- POST /api/iot/scan/{homeId}
- POST /api/iot/fix/{threatId}    (ожидаемый негативный сценарий 404, если угрозы нет)

Запуск:
  python docs/server/test_iot_endpoints_live.py

Можно переопределить базовый URL:
  ALADDIN_BASE_URL=https://aladdin-ai.ru python docs/server/test_iot_endpoints_live.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests


BASE_URL = os.environ.get("ALADDIN_BASE_URL", "http://149.154.65.180:8002")
HOME_ID = os.environ.get("ALADDIN_IOT_HOME_ID", "home_001")


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
    report = {"base_url": BASE_URL, "home_id": HOME_ID, "checks": []}

    # 1) Статус умного дома
    r = session.get(f"{BASE_URL}/api/iot/status/{HOME_ID}", timeout=15)
    report["checks"].append(_show("iot_status", r))

    # 2) Список устройств
    r = session.get(f"{BASE_URL}/api/iot/devices/{HOME_ID}", timeout=15)
    report["checks"].append(_show("iot_devices", r))

    # 3) Список угроз
    r = session.get(f"{BASE_URL}/api/iot/threats/{HOME_ID}", timeout=15)
    report["checks"].append(_show("iot_threats", r))

    # 4) Блокировка первого устройства (если есть)
    devices = report["checks"][1]["body"]
    first_device_id = None
    if isinstance(devices, dict):
        items = devices.get("devices") or []
        if items:
            first_device_id = items[0].get("deviceId")
    if first_device_id:
        r = session.post(
            f"{BASE_URL}/api/iot/device/{first_device_id}/block",
            timeout=15,
        )
        report["checks"].append(_show("iot_block_device", r))

    # 5) Запуск сканирования
    r = session.post(f"{BASE_URL}/api/iot/scan/{HOME_ID}", timeout=15)
    report["checks"].append(_show("iot_scan", r))

    # 6) Попытка фикса несуществующей угрозы (негативный сценарий)
    r = session.post(f"{BASE_URL}/api/iot/fix/threat_test_missing", timeout=15)
    report["checks"].append(_show("iot_fix_missing_threat", r))

    # Итоговый сводный отчёт одной строкой (для логов/ML‑системы)
    summary = {
        "base_url": BASE_URL,
        "home_id": HOME_ID,
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

