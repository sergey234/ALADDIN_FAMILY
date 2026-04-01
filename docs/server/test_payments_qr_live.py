#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Короткий smoke‑тест для живого эндпоинта оплаты QR:

- POST /api/payments/qr/create

Запуск:
  python docs/server/test_payments_qr_live.py

Можно переопределить базовый URL:
  ALADDIN_BASE_URL=https://aladdin-ai.ru python docs/server/test_payments_qr_live.py
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

    payload = {
        "tariffId": "premium",
        "userAlias": "test_user_qr",
        "pin": "1234",
        "paymentMethod": "sbp",
        "periodMonths": 1,
        "amount": 1990,
        "referralCode": None,
    }

    r = session.post(
        f"{BASE_URL}/api/payments/qr/create",
        json=payload,
        timeout=20,
    )
    report["checks"].append(_show("payments_qr_create", r))

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

