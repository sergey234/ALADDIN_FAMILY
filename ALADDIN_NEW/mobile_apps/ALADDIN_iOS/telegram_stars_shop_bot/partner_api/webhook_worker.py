from __future__ import annotations

import argparse
import asyncio
import logging

from bot.config import load_settings
from bot.db.database import connect
from bot.services.partner_outbound import process_webhook_queue_once


async def _run_once(*, limit: int) -> int:
    settings = load_settings()
    conn = await connect(settings.database_path)
    try:
        return await process_webhook_queue_once(conn, limit=limit)
    finally:
        await conn.close()


async def _run_forever(*, limit: int, sleep_sec: int) -> None:
    while True:
        sent = await _run_once(limit=limit)
        logging.info("webhook_worker_cycle sent=%s", sent)
        await asyncio.sleep(max(1, sleep_sec))


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Process outbound webhook queue")
    p.add_argument("--limit", type=int, default=100, help="max events per cycle")
    p.add_argument("--forever", action="store_true", help="run infinite loop mode")
    p.add_argument("--sleep-sec", type=int, default=30, help="sleep in --forever mode")
    return p


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = _parser().parse_args()
    if args.forever:
        asyncio.run(_run_forever(limit=max(1, args.limit), sleep_sec=max(1, args.sleep_sec)))
        return
    sent = asyncio.run(_run_once(limit=max(1, args.limit)))
    logging.info("webhook_worker_once sent=%s", sent)


if __name__ == "__main__":
    main()
