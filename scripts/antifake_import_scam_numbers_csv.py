#!/usr/bin/env python3
"""C-05: Import scam numbers CSV into antifake_scam_numbers."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.antifake_call_directory_store import import_csv_rows  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Import antifake scam numbers CSV")
    parser.add_argument("csv_path", type=Path, help="CSV with phone,source,label,block,confidence")
    args = parser.parse_args()

    with args.csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    ok, skipped = import_csv_rows(rows)
    print(f"imported={ok} skipped={skipped}")
    return 0 if skipped == 0 or ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
