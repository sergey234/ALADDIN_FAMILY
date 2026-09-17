#!/usr/bin/env python3
"""afhub-p3-03 — monthly red-team regression (RU+EN social engineering SMS).

Runs check_text(mode=sms) on golden_redteam_monthly_* corpus.
Exit 1 if any case returns likely_real / green authentic.

Cron (optional, ops):
  0 4 1 * * cd /opt/aladdin-backend && ./venv/bin/python3 scripts/antifake_redteam_monthly.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run() -> dict:
    from app.services.antifake_service import check_text
    from data.antifake.golden_dataset import (
        golden_redteam_monthly_en,
        golden_redteam_monthly_ru,
    )

    failures = []
    results = []
    for lang, cases in (
        ("ru", golden_redteam_monthly_ru()),
        ("en", golden_redteam_monthly_en()),
    ):
        for text, expected in cases:
            out = check_text(text, mode="sms")
            verdict = str(out.get("verdict") or "")
            ok = verdict == "likely_fake" if expected == "likely_fake" else True
            # Never accept green authentic on red-team scam corpus
            if verdict == "likely_real":
                ok = False
            row = {
                "lang": lang,
                "ok": ok,
                "verdict": verdict,
                "confidence": out.get("confidence"),
                "text": text[:120],
            }
            results.append(row)
            if not ok:
                failures.append(row)
    return {
        "ok": not failures,
        "total": len(results),
        "failed": len(failures),
        "failures": failures,
        "pass_rate": round((len(results) - len(failures)) / max(1, len(results)), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Monthly antifake red-team")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"redteam total={report['total']} failed={report['failed']} "
            f"pass_rate={report['pass_rate']}"
        )
        for row in report["failures"][:20]:
            print(f"  FAIL [{row['lang']}] {row['verdict']}: {row['text']}")
        print("PASS" if report["ok"] else "FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
