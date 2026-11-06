#!/usr/bin/env python3
"""P-01 / P-02 / T3-07 — antifake ops alerts (job failure, queue depth, uncertain drift).

Cron (see deploy_antifake_m1.sh):
  python3 scripts/antifake_ops_alerts.py --check-all

Exit codes: 0 OK · 2 ALERT · 1 usage/config error
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FAILURE_RATE_THRESHOLD = float(os.environ.get("ANTIFAKE_ALERT_JOB_FAIL_PCT", "5")) / 100.0
FAILURE_WINDOW_MIN = int(os.environ.get("ANTIFAKE_ALERT_JOB_WINDOW_MIN", "60"))
FAILURE_MIN_SAMPLE = int(os.environ.get("ANTIFAKE_ALERT_JOB_MIN_SAMPLE", "20"))
QUEUE_DEPTH_THRESHOLD = int(os.environ.get("ANTIFAKE_ALERT_QUEUE_DEPTH", "50"))


def check_uncertain_drift() -> Tuple[bool, str, Dict[str, Any]]:
    from app.services.antifake_drift import check_uncertain_drift as _check

    return _check()


def check_moderation_sla() -> Tuple[bool, str, Dict[str, Any]]:
    from app.services.antifake_moderation_sla import check_moderation_sla as _check

    return _check()


def _job_failure_stats() -> Dict[str, Any]:
    from sqlalchemy import text

    from app.database.database import engine

    since = datetime.now(timezone.utc) - timedelta(minutes=FAILURE_WINDOW_MIN)
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                    COUNT(*) FILTER (WHERE status = 'completed') AS completed
                FROM antifake_jobs
                WHERE updated_at >= :since
                  AND status IN ('failed', 'completed')
                """
            ),
            {"since": since},
        ).mappings().first()

    failed = int(row["failed"] or 0)
    completed = int(row["completed"] or 0)
    total = failed + completed
    rate = (failed / total) if total else 0.0
    return {
        "failed": failed,
        "completed": completed,
        "total": total,
        "failure_rate": round(rate, 4),
        "window_min": FAILURE_WINDOW_MIN,
        "threshold": FAILURE_RATE_THRESHOLD,
        "min_sample": FAILURE_MIN_SAMPLE,
    }


def check_job_failure_rate() -> Tuple[bool, str, Dict[str, Any]]:
    stats = _job_failure_stats()
    if stats["total"] < FAILURE_MIN_SAMPLE:
        return True, f"OK: sample too small (total={stats['total']})", stats
    if stats["failure_rate"] > FAILURE_RATE_THRESHOLD:
        pct = round(stats["failure_rate"] * 100, 2)
        return (
            False,
            f"ALERT: job failure {pct}% > {FAILURE_RATE_THRESHOLD * 100}% "
            f"(failed={stats['failed']} completed={stats['completed']} window={FAILURE_WINDOW_MIN}m)",
            stats,
        )
    pct = round(stats["failure_rate"] * 100, 2)
    return True, f"OK: job failure {pct}%", stats


def _queue_depth() -> Dict[str, Any]:
    from app.services.antifake_queue import QUEUE_NAME, REDIS_URL, queue_enabled

    if not queue_enabled():
        return {"enabled": False, "depth": 0, "queue": QUEUE_NAME}

    import redis
    from rq import Queue

    connection = redis.from_url(REDIS_URL)
    queue = Queue(QUEUE_NAME, connection=connection)
    depth = int(queue.count)
    return {"enabled": True, "depth": depth, "queue": QUEUE_NAME, "redis": REDIS_URL.split("@")[-1]}


def check_queue_depth() -> Tuple[bool, str, Dict[str, Any]]:
    info = _queue_depth()
    if not info.get("enabled"):
        return True, "OK: async queue disabled (sync fallback)", info
    depth = int(info["depth"])
    if depth > QUEUE_DEPTH_THRESHOLD:
        return (
            False,
            f"ALERT: queue depth {depth} > {QUEUE_DEPTH_THRESHOLD} ({info['queue']})",
            info,
        )
    return True, f"OK: queue depth {depth}", info


def check_phishing_feed_health() -> Tuple[bool, str, Dict[str, Any]]:
    """TI-10 — active_count, last fetch degraded, bank_ru KPI soft warn."""
    from app.services.antifake_phishing_domains_store import (
        MIN_PHISHING_DOMAIN_COUNT,
        active_count,
    )

    active = active_count()
    feed_dir = Path(
        os.environ.get("ANTIFAKE_PHISHING_FEED_DIR", "").strip()
        or str(ROOT / "data" / "antifake" / "feeds")
    )
    fetch_path = feed_dir / "last_fetch_report.json"
    fetch: Dict[str, Any] = {}
    if fetch_path.is_file():
        try:
            fetch = json.loads(fetch_path.read_text(encoding="utf-8"))
        except Exception:
            fetch = {"ok": False, "parse_error": True}

    detail: Dict[str, Any] = {
        "active_count": active,
        "min_required": MIN_PHISHING_DOMAIN_COUNT,
        "last_fetch_ok": fetch.get("ok"),
        "degraded": fetch.get("degraded"),
        "merged_count": fetch.get("merged_count"),
    }

    if active < MIN_PHISHING_DOMAIN_COUNT:
        return (
            False,
            f"ALERT: phishing active_count {active} < {MIN_PHISHING_DOMAIN_COUNT}",
            detail,
        )

    # Two consecutive days of fetch failure → degraded alert if report says not ok
    if fetch and fetch.get("ok") is False and not fetch.get("missing"):
        return (
            False,
            "ALERT: last external feed fetch failed (degraded mode)",
            detail,
        )

    if fetch.get("degraded"):
        return (
            True,
            f"WARN: fetch degraded but active_count={active} OK (snapshot/fallback)",
            detail,
        )

    return True, f"OK: phishing feed active_count={active}", detail


def check_pipeline_health() -> Tuple[bool, str, Dict[str, Any]]:
    """Incident 2026-11-06: worker up, every media job crashed for 21 days."""
    from app.services.antifake_pipeline_health import collect

    result = collect(use_cache=False)
    if result["status"] != "ok":
        return False, f"ALERT: antifake pipeline degraded: {', '.join(result['problems'])}", result
    return True, "OK: antifake pipeline completes media checks", result


def run_checks(which: str) -> int:
    checks: List[Tuple[str, Any]] = []
    if which in ("all", "pipeline"):
        checks.append(("pipeline", check_pipeline_health))
    if which in ("all", "jobs"):
        checks.append(("job_failure", check_job_failure_rate))
    if which in ("all", "queue"):
        checks.append(("queue_depth", check_queue_depth))
    if which in ("all", "drift"):
        checks.append(("uncertain_drift", check_uncertain_drift))
    if which in ("all", "moderation"):
        checks.append(("moderation_sla", check_moderation_sla))
    if which in ("all", "feed"):
        checks.append(("phishing_feed", check_phishing_feed_health))

    results: Dict[str, Any] = {"checks": {}, "pass": True}
    exit_code = 0
    for name, fn in checks:
        try:
            ok, msg, detail = fn()
        except Exception as exc:
            # A crashing check is itself an outage signal, never a silent traceback.
            ok, msg, detail = False, f"ALERT: check {name} crashed: {type(exc).__name__}: {exc}", {}
        results["checks"][name] = {"ok": ok, "message": msg, "detail": detail}
        print(f"{'OK' if ok else 'ALERT'}  {msg}")
        if not ok:
            results["pass"] = False
            exit_code = 2

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Antifake ops alerts (P-01, P-02)")
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Run job failure + queue depth checks",
    )
    parser.add_argument(
        "--check-jobs",
        action="store_true",
        help="P-01: job failure rate only",
    )
    parser.add_argument(
        "--check-queue",
        action="store_true",
        help="P-02: RQ queue depth only",
    )
    parser.add_argument(
        "--check-drift",
        action="store_true",
        help="T3-07: uncertain verdict drift (24h rolling)",
    )
    parser.add_argument(
        "--check-moderation-sla",
        action="store_true",
        help="T5-01: pending reports older than SLA (48h)",
    )
    parser.add_argument(
        "--check-pipeline",
        action="store_true",
        help="Media jobs actually complete (worker registered, no crash loop, smoke fresh)",
    )
    parser.add_argument(
        "--check-feed",
        action="store_true",
        help="TI-10: phishing feed active_count + last fetch health",
    )
    args = parser.parse_args()

    if args.check_jobs:
        which = "jobs"
    elif args.check_queue:
        which = "queue"
    elif args.check_drift:
        which = "drift"
    elif args.check_moderation_sla:
        which = "moderation"
    elif args.check_feed:
        which = "feed"
    elif args.check_pipeline:
        which = "pipeline"
    elif args.check_all:
        which = "all"
    else:
        parser.print_help()
        return 1

    return run_checks(which)


if __name__ == "__main__":
    raise SystemExit(main())
