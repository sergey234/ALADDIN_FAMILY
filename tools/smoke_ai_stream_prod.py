#!/usr/bin/env python3
"""ai-stream smoke: POST /api/ai/assistant/stream with JWT."""
from __future__ import annotations

import json
import os
import subprocess
import sys

BACKEND = os.getenv("ALADDIN_BACKEND", "/opt/aladdin-backend")


def mint_jwt() -> str:
    code = f"""
import sys
sys.path.insert(0, "{BACKEND}")
from datetime import timedelta
from app.routers.auth_router import create_access_token
print(create_access_token(
    {{"sub": "stream-smoke", "user_id": "stream-smoke", "subscription": {{"level": "premium", "limits": {{}}}}}},
    expires_delta=timedelta(hours=1),
))
"""
    return subprocess.check_output(
        [f"{BACKEND}/venv/bin/python3", "-c", code],
        env={**os.environ, "PYTHONPATH": BACKEND},
        text=True,
    ).strip()


def main() -> int:
    import urllib.request

    token = os.getenv("ALADDIN_TEST_JWT") or mint_jwt()
    url = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002") + "/api/ai/assistant/stream"
    body = json.dumps(
        {"message": "статус защиты", "context": "protection_status", "stream": True, "messageId": "smoke-1"}
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        chunk = resp.read(500).decode()
        print(f"HTTP={resp.status} ct={resp.headers.get('Content-Type')}")
        print(chunk[:300])
        ok = resp.status == 200 and ("data:" in chunk or "token" in chunk)
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
