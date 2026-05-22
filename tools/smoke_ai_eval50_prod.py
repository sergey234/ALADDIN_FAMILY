#!/usr/bin/env python3
"""ai-eval-50-run on prod: mint JWT + run smoke_ai_eval50."""
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
print(create_access_token({{"sub":"eval50-smoke","user_id":"eval50-smoke","subscription":{{"level":"premium","limits":{{}}}}}}, expires_delta=timedelta(hours=2)))
"""
    token = subprocess.check_output(
        [f"{BACKEND}/venv/bin/python3", "-c", mint],
        env=env,
        text=True,
    ).strip()
    env["ALADDIN_TEST_JWT"] = token
    print("JWT minted for eval50-smoke-user")
    print(f"AI_RAG_ENABLED={env.get('AI_RAG_ENABLED', '(unset)')}")
    return subprocess.call(
        [f"{BACKEND}/venv/bin/python3", f"{BACKEND}/tools/smoke_ai_eval50.py"],
        env=env,
    )


if __name__ == "__main__":
    sys.exit(main())
