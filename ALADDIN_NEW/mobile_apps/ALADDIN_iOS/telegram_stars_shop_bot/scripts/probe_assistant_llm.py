#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from pathlib import Path


def load_env(p: Path) -> dict[str, str]:
    d: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def try_call(base: str, model: str, max_tokens: int, key: str) -> tuple[str, str, str]:
    url = base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Ответь одним словом: ок"}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")
    req.add_header("HTTP-Referer", "https://aimonkey.local")
    req.add_header("X-Title", "AiMonkeyAssistant")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            body = json.loads(r.read().decode())
            txt = ((body.get("choices") or [{}])[0].get("message") or {}).get("content")
            return "OK", str(r.status), (txt or "")[:80].replace("\n", " ")
    except Exception as e:
        msg = str(e)
        if hasattr(e, "read"):
            try:
                msg = e.read().decode()[:240]
            except Exception:
                pass
        return "FAIL", type(e).__name__, msg[:240]


def main() -> None:
    shop = load_env(Path("/opt/aladdin-telegram-shop-bot/shared/.env"))
    key = shop.get("ASSISTANT_LLM_API_KEY", "")
    print("shop_key_len", len(key))
    candidates = [
        ("https://openrouter.ai/api/v1", "deepseek/deepseek-chat", 64),
        ("https://openrouter.ai/api/v1", "meta-llama/llama-3.2-3b-instruct:free", 64),
        ("https://openrouter.ai/api/v1", "google/gemma-2-9b-it:free", 64),
        ("https://openrouter.ai/api/v1", "qwen/qwen3-4b:free", 64),
    ]
    for base, model, mt in candidates:
        st, a, b = try_call(base, model, mt, key)
        print(model, st, a, b)


if __name__ == "__main__":
    main()
