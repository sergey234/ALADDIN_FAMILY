#!/usr/bin/env python3
"""One-off prod smoke: «Ты учишься?» must not return 1074 mock."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import timedelta
from pathlib import Path

BACKEND = Path(os.getenv("ALADDIN_BACKEND", "/opt/aladdin-backend"))
sys.path.insert(0, str(BACKEND))

dotenv = BACKEND / ".env"
if dotenv.is_file():
    for line in dotenv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

from app.routers.auth_router import create_access_token  # noqa: E402

FORBIDDEN = ("1074 функций", "1074 функции", "реальный AI ALADDIN с 1074")


def main() -> int:
    token = create_access_token(
        {
            "sub": "deploy-smoke-learning",
            "user_id": "deploy-smoke-learning",
            "subscription": {"level": "premium", "limits": {}},
        },
        expires_delta=timedelta(hours=1),
    )
    body = json.dumps(
        {"message": "Ты учишься?", "context": "general", "stream": False}
    ).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8002/api/ai/assistant/chat",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read()[:500]!r}")
        return 1

    text = str(data.get("response") or data.get("message") or data)
    print("response:", text[:280])
    for marker in FORBIDDEN:
        if marker.lower() in text.lower():
            print(f"FAIL forbidden marker: {marker!r}")
            return 1
    if "учусь" in text.lower() or "не «учусь»" in text.lower() or "не учусь" in text.lower():
        print("PASS (grounded learning answer, no 1074)")
        return 0
    print("WARN: unexpected wording but no 1074")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
