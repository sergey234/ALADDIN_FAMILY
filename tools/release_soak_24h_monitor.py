#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path

import requests


PROM = os.environ.get("ALADDIN_PROM_URL", "http://149.154.65.180:9090").rstrip("/")
OUT_DIR = Path(
    os.environ.get("ALADDIN_SOAK_DIR", "docs/release/soak")
)
DURATION_SEC = int(os.environ.get("ALADDIN_SOAK_DURATION_SEC", str(24 * 3600)))
INTERVAL_SEC = int(os.environ.get("ALADDIN_SOAK_INTERVAL_SEC", "300"))


def prom_query(expr: str):
    r = requests.get(f"{PROM}/api/v1/query", params={"query": expr}, timeout=15)
    r.raise_for_status()
    payload = r.json()
    return payload.get("data", {}).get("result", [])


def _float_or_none(result):
    if not result:
        return None
    try:
        return float(result[0]["value"][1])
    except Exception:
        return None


def collect_once():
    p95 = _float_or_none(
        prom_query('histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="gateway"}[5m])) by (le))')
    )
    five_xx = _float_or_none(
        prom_query('sum(rate(http_requests_total{job="gateway",code=~"5.."}[5m])) / clamp_min(sum(rate(http_requests_total{job="gateway"}[5m])), 1)')
    )
    alerts = prom_query("ALERTS{alertstate='firing'}")
    freshness_raw = prom_query("aladdin_analytics_freshness_seconds")
    freshness = {}
    for row in freshness_raw:
        domain = row.get("metric", {}).get("domain", "unknown")
        try:
            freshness[domain] = float(row["value"][1])
        except Exception:
            freshness[domain] = None

    return {
        "ts": int(time.time()),
        "p95_seconds": p95,
        "five_xx_share": five_xx if five_xx is not None else 0.0,
        "firing_alerts_count": len(alerts),
        "firing_alerts": [a.get("metric", {}).get("alertname", "unknown") for a in alerts],
        "freshness_seconds": freshness,
    }


def summarize(samples):
    def vals(key):
        return [s[key] for s in samples if s.get(key) is not None]

    p95_vals = vals("p95_seconds")
    e5_vals = vals("five_xx_share")
    max_alerts = max([s.get("firing_alerts_count", 0) for s in samples], default=0)
    latest_freshness = samples[-1].get("freshness_seconds", {}) if samples else {}

    thresholds = {
        "darkweb": 72 * 3600,
        "identity": 24 * 3600,
        "tracker": 12 * 3600,
        "location": 6 * 3600,
        "cleanup": 168 * 3600,
    }
    freshness_ok = all(
        latest_freshness.get(k, 10**12) is not None and latest_freshness.get(k, 10**12) <= v
        for k, v in thresholds.items()
    )

    return {
        "samples_count": len(samples),
        "p95_max": max(p95_vals) if p95_vals else None,
        "p95_avg": (sum(p95_vals) / len(p95_vals)) if p95_vals else None,
        "five_xx_max": max(e5_vals) if e5_vals else None,
        "max_firing_alerts": max_alerts,
        "latest_freshness_seconds": latest_freshness,
        "slo_checks": {
            "p95_max_lt_0_5s": (max(p95_vals) < 0.5) if p95_vals else False,
            "five_xx_max_lt_1pct": (max(e5_vals) < 0.01) if e5_vals else False,
            "no_firing_alerts": max_alerts == 0,
            "freshness_within_thresholds": freshness_ok,
        },
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d_%H%M%S")
    samples_path = OUT_DIR / f"soak-{run_id}.samples.jsonl"
    summary_path = OUT_DIR / f"soak-{run_id}.summary.json"

    start = int(time.time())
    end = start + DURATION_SEC
    samples = []

    while int(time.time()) < end:
        sample = collect_once()
        samples.append(sample)
        with samples_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
        time.sleep(INTERVAL_SEC)

    summary = {
        "run_id": run_id,
        "prometheus_url": PROM,
        "started_at": start,
        "ended_at": int(time.time()),
        "duration_sec": DURATION_SEC,
        "interval_sec": INTERVAL_SEC,
        "samples_file": str(samples_path),
        "summary": summarize(samples),
    }
    summary["pass"] = all(summary["summary"]["slo_checks"].values())
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"soak-finished: {'PASS' if summary['pass'] else 'FAIL'}")
    print(f"summary={summary_path}")


if __name__ == "__main__":
    main()
