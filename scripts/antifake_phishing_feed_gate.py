#!/usr/bin/env python3
"""afhub-p2-03 / G6 — phishing feed freshness gate + alert (URLHaus/OpenPhish).

Cron (suggested, MAIN …180 — only after owner GO):
  45 3 * * * cd /opt/aladdin-backend && ./venv/bin/python3 scripts/antifake_phishing_feed_gate.py
Exit 1 → alert (stale / missing / both feeds down / too few domains).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app.services.antifake_threat_intel_freshness import check_threat_intel_freshness

    payload = check_threat_intel_freshness()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
