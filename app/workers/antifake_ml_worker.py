"""B2-10 / af-3 — worker entry for heavy antifake ML (lazy deps + RQ queue)."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict

from app.security.ml_lazy_loader import (
    run_document_check,
    run_text_check,
    warm_worker_deps,
)

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get(
    "ANTIFAKE_REDIS_URL",
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"),
)
QUEUE_NAME = os.environ.get("ANTIFAKE_QUEUE_NAME", "aladdin-antifake")


def process_job(job_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if job_type == "text":
        text = str(payload.get("text") or "")
        mode = str(payload.get("mode") or "news")
        return run_text_check(text, mode=mode)
    if job_type == "document":
        path = str(payload.get("path") or payload.get("file_path") or "")
        if not path:
            raise ValueError("document job requires path")
        return run_document_check(path)
    raise ValueError(f"unsupported antifake job type: {job_type}")


def run_rq_worker() -> int:
    import redis
    from rq import Worker, Queue

    connection = redis.from_url(REDIS_URL)
    queue = Queue(QUEUE_NAME, connection=connection)
    worker = Worker([queue], connection=connection, name=f"antifake-{os.getpid()}")
    logger.info("Starting RQ worker queue=%s redis=%s", QUEUE_NAME, REDIS_URL)
    worker.work(with_scheduler=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALADDIN antifake ML worker (lazy deps)")
    parser.add_argument("--warm", action="store_true", help="Warm torch/cv2 and exit")
    parser.add_argument("--listen", action="store_true", help="Run RQ worker loop (production)")
    parser.add_argument("--job-type", choices=("text", "document"))
    parser.add_argument("--payload-json", default="{}")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    if args.warm:
        status = warm_worker_deps()
        print(json.dumps({"warm": status}))
        return 0

    if args.listen:
        warm_worker_deps()
        return run_rq_worker()

    if not args.job_type:
        parser.error("--job-type is required unless --warm or --listen")

    payload = json.loads(args.payload_json)
    result = process_job(args.job_type, payload)
    print(json.dumps({"success": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
