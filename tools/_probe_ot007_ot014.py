#!/usr/bin/env python3
"""One-off probe for OT007/OT014 HTTP codes."""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

BACKEND = os.getenv("ALADDIN_BACKEND_ROOT", "/opt/aladdin-backend")
BASE = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002")


def _load_env(env: dict) -> None:
    dotenv = os.path.join(BACKEND, ".env")
    if not os.path.isfile(dotenv):
        return
    with open(dotenv, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            env.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def mint() -> str:
    env = {**os.environ, "PYTHONPATH": BACKEND}
    _load_env(env)
    code = f"""
import sys
sys.path.insert(0, {BACKEND!r})
from datetime import timedelta
from app.routers.auth_router import create_access_token
print(create_access_token({{"sub":"probe","user_id":"probe","subscription":{{"level":"premium","limits":{{}}}}}}, expires_delta=timedelta(hours=1)))
"""
    return subprocess.check_output(
        [f"{BACKEND}/venv/bin/python3", "-c", code],
        env=env,
        text=True,
    ).strip()


def chat(token: str, msg: str) -> None:
    body = json.dumps({"message": msg, "context": "general", "stream": False}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/ai/assistant/chat",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
            print(f"OK {r.status} len={len(d.get('response') or '')} preview={(d.get('response') or '')[:100]}")
    except urllib.error.HTTPError as e:
        print(f"ERR {e.code} body={e.read().decode()[:400]}")


def main() -> int:
    tok = mint()
    for label, msg in [
        ("OT007", "какое лекарство от головной боли"),
        ("OT014", "лучший ноутбук для игр 2026"),
        ("ctrl", "погода в москве завтра"),
    ]:
        print(label, msg[:50])
        chat(tok, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
