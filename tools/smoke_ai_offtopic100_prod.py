#!/usr/bin/env python3
"""R4.1 prod runner: mint JWT + smoke_ai_offtopic100."""
from __future__ import annotations

import os
import subprocess
import sys

BACKEND = os.getenv("ALADDIN_BACKEND_ROOT", "/opt/aladdin-backend")


def _load_backend_env(env: dict) -> None:
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


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND
    env.setdefault("ALADDIN_API_BASE", "http://127.0.0.1:8002")
    _load_backend_env(env)
    mint = f"""
import sys
sys.path.insert(0, "{BACKEND}")
from datetime import timedelta
from app.routers.auth_router import create_access_token
print(create_access_token({{"sub":"offtopic-smoke","user_id":"offtopic-smoke","subscription":{{"level":"premium","limits":{{}}}}}}, expires_delta=timedelta(hours=2)))
"""
    token = subprocess.check_output(
        [f"{BACKEND}/venv/bin/python3", "-c", mint],
        env=env,
        text=True,
    ).strip()
    env["ALADDIN_TEST_JWT"] = token
    print("JWT minted for offtopic-smoke-user")
    print(f"AI_RAG_ENABLED={env.get('AI_RAG_ENABLED', '(unset)')}")
    batch = env.get("AI_OFFTOPIC_BATCH", "0")
    if batch and batch != "0":
        print(f"AI_OFFTOPIC_BATCH={batch} (slice of 10)")
    scripts = [
        f"{BACKEND}/tools/smoke_ai_offtopic100.py",
        f"{BACKEND}/tools/ai_offtopic_cases100.py",
    ]
    for path in scripts:
        if not os.path.isfile(path):
            print(f"WARN: missing {path} — sync tools/ to server first")
    return subprocess.call(
        [f"{BACKEND}/venv/bin/python3", f"{BACKEND}/tools/smoke_ai_offtopic100.py"],
        env=env,
    )


if __name__ == "__main__":
    sys.exit(main())
