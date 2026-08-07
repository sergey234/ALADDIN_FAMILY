#!/usr/bin/env python3
"""Live smoke: LLM failover chain on Contabo."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path


def _load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


async def main() -> None:
    _load_env(Path("/opt/aladdin-telegram-shop-bot/shared/.env"))
    from bot.config import load_settings
    from bot.assistant.llm_client import assistant_llm_model_chain, chat_complete

    s = load_settings()
    chain = assistant_llm_model_chain(s)
    print("chain", chain)
    r = await chat_complete(
        s,
        [
            {"role": "system", "content": "Ответь одним словом по-русски."},
            {"role": "user", "content": "Скажи: ок"},
        ],
    )
    print(
        "ok",
        r.ok,
        "model",
        r.model_used,
        "err",
        r.error,
        "text",
        (r.text or "")[:80].replace("\n", " "),
    )
    assert r.ok, r.error
    print("FAILOVER_SMOKE_OK")


if __name__ == "__main__":
    asyncio.run(main())
