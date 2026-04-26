from __future__ import annotations

import argparse
import asyncio
import logging

from bot.config import load_settings
from bot.services.auto_fulfill_runner import process_auto_fulfill_once
from bot.services.catalog import load_products


async def _run_once(*, limit: int) -> dict[str, int]:
    settings = load_settings()
    products = load_products(settings.products_path)
    return await process_auto_fulfill_once(settings, products, limit=limit)


async def _run_forever(*, limit: int, sleep_sec: int) -> None:
    while True:
        stats = await _run_once(limit=limit)
        logging.info("auto_fulfill_worker_cycle stats=%s", stats)
        await asyncio.sleep(max(1, sleep_sec))


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Process auto-fulfillment queue (iStar partner API)")
    p.add_argument("--limit", type=int, default=10, help="max orders considered per cycle")
    p.add_argument("--forever", action="store_true", help="run infinite loop mode")
    p.add_argument(
        "--sleep-sec",
        type=int,
        default=0,
        help="sleep in --forever mode (0 = use AUTO_FULFILL_POLL_INTERVAL_SECONDS from settings)",
    )
    return p


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = _parser().parse_args()
    settings = load_settings()
    sleep_sec = int(args.sleep_sec) if args.sleep_sec > 0 else max(1, int(settings.auto_fulfill_poll_interval_seconds or 60))
    if args.forever:
        asyncio.run(_run_forever(limit=max(1, args.limit), sleep_sec=sleep_sec))
        return
    stats = asyncio.run(_run_once(limit=max(1, args.limit)))
    logging.info("auto_fulfill_worker_once stats=%s", stats)


if __name__ == "__main__":
    main()
