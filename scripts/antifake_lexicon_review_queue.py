#!/usr/bin/env python3
"""afhub-p3-01 — ops CLI for lexicon review queue (no auto-lexicon writes).

Examples:
  PYTHONPATH=. python3 scripts/antifake_lexicon_review_queue.py --list
  PYTHONPATH=. python3 scripts/antifake_lexicon_review_queue.py --export
  PYTHONPATH=. python3 scripts/antifake_lexicon_review_queue.py --reject <id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app.services.antifake_lexicon_review_queue import (
        export_review_pack,
        list_pending,
        mark_status,
    )

    parser = argparse.ArgumentParser(description="Lexicon review queue (manual)")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--accept", metavar="ID", help="Mark accepted (still not live lexicon)")
    parser.add_argument("--reject", metavar="ID", help="Mark rejected")
    args = parser.parse_args()

    if args.accept:
        ok = mark_status(args.accept, status="accepted")
        print(json.dumps({"ok": ok, "status": "accepted", "id": args.accept}))
        return 0 if ok else 1
    if args.reject:
        ok = mark_status(args.reject, status="rejected")
        print(json.dumps({"ok": ok, "status": "rejected", "id": args.reject}))
        return 0 if ok else 1
    if args.export:
        path = export_review_pack(limit=args.limit)
        print(json.dumps({"ok": True, "path": str(path)}, ensure_ascii=False, indent=2))
        return 0

    rows = list_pending(limit=args.limit)
    print(json.dumps({"ok": True, "pending": len(rows), "rows": rows}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
