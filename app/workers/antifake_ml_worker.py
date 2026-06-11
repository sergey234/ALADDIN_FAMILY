"""B2-10 — worker entry for heavy antifake ML (cv2 + transformers lazy load)."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict

from app.security.ml_lazy_loader import (
    run_document_check,
    run_text_check,
    warm_worker_deps,
)

logger = logging.getLogger(__name__)


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALADDIN antifake ML worker (lazy deps)")
    parser.add_argument("--warm", action="store_true", help="Warm torch/cv2 and exit")
    parser.add_argument("--job-type", choices=("text", "document"))
    parser.add_argument("--payload-json", default="{}")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    if args.warm:
        status = warm_worker_deps()
        print(json.dumps({"warm": status}))
        return 0

    if not args.job_type:
        parser.error("--job-type is required unless --warm")

    payload = json.loads(args.payload_json)
    result = process_job(args.job_type, payload)
    print(json.dumps({"success": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
