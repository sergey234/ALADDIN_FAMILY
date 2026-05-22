#!/usr/bin/env python3
"""ai-eval-top10-run on prod: mint JWT + run chat eval."""
from __future__ import annotations

import os
import subprocess
import sys

BACKEND = "/opt/aladdin-backend"


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
token = create_access_token(
    {{
        "sub": "eval-smoke-user",
        "user_id": "eval-smoke-user",
        "subscription": {{"level": "premium", "limits": {{}}}},
    }},
    expires_delta=timedelta(hours=2),
)
print(token)
"""
    token = subprocess.check_output(
        [f"{BACKEND}/venv/bin/python3", "-c", mint],
        env=env,
        text=True,
    ).strip()
    env["ALADDIN_TEST_JWT"] = token
    print("JWT minted for eval-smoke-user")
    return subprocess.call(
        [f"{BACKEND}/venv/bin/python3", f"{BACKEND}/tools/smoke_ai_eval_top10.py"],
        env=env,
    )


if __name__ == "__main__":
    sys.exit(main())
