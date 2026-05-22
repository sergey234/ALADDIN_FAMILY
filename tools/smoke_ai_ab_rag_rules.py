#!/usr/bin/env python3
"""
R4.2: Compare response paths for KB vs factual vs off-topic (read-only metrics).
Does not toggle AI_RAG_ENABLED on prod — reports tools_used / grounded / sources.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

BACKEND = os.getenv("ALADDIN_BACKEND_ROOT", "/opt/aladdin-backend")
BASE = os.getenv("ALADDIN_API_BASE", "http://127.0.0.1:8002")

COMPARE_CASES = [
    ("KB", "Как работает AI-помощник?", "app_help"),
    ("KB", "тариф Premium", "tariff_explain"),
    ("FACT", "Сколько угроз сегодня?", "general"),
    ("FACT", "Статус защиты ALADDIN", "protection_status"),
    ("OFF", "погода в москве", "general"),
]


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


def _mint_jwt(env: dict) -> str:
    mint = f"""
import sys
sys.path.insert(0, "{BACKEND}")
from datetime import timedelta
from app.routers.auth_router import create_access_token
print(create_access_token({{"sub":"ab-smoke","user_id":"ab-smoke","subscription":{{"level":"premium","limits":{{}}}}}}, expires_delta=timedelta(hours=1)))
"""
    return subprocess.check_output(
        [f"{BACKEND}/venv/bin/python3", "-c", mint],
        env=env,
        text=True,
    ).strip()


def post_chat(jwt: str, message: str, context: str) -> dict:
    body = json.dumps({"message": message, "context": context, "stream": False}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/ai/assistant/chat",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jwt}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "detail": e.read().decode()[:200]}


def _path_label(data: dict) -> str:
    tools = [str(t) for t in (data.get("tools_used") or [])]
    if any("kb_rag" in t for t in tools):
        return "kb_rag"
    if any(t.startswith("hermes") for t in tools):
        return "hermes"
    if any(t.startswith("get_") for t in tools):
        return "sfm_aggregates"
    return "sfm_rules"


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND
    _load_env(env)
    rag_flag = env.get("AI_RAG_ENABLED", "(unset)")
    print(f"AI_RAG_ENABLED={rag_flag}")
    jwt = _mint_jwt(env)
    print("case\tpath\tgrounded\tsources\ttools")
    for kind, msg, ctx in COMPARE_CASES:
        data = post_chat(jwt, msg, ctx)
        if data.get("error"):
            print(f"{kind}\tHTTP_{data.get('error')}\t-\t-\t-")
            continue
        print(
            f"{kind}\t{_path_label(data)}\t{data.get('grounded')}\t"
            f"{(data.get('sources') or [])[:2]}\t{(data.get('tools_used') or [])[:4]}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
