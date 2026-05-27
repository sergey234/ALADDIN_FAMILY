#!/usr/bin/env python3
# HERO-3-22 — размер `.riv` ×3 (<500 KB каждый, §3.2 COMPANION_HEROES_3_FIGMA_RIVE_PLAN).
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MAX_BYTES = 500 * 1024
RIV_NAMES = ("unicorn.riv", "aladdin.riv", "genie.riv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Companion Rive file size gate (HERO-3-22).")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "Resources" / "Companion",
        help="Directory containing unicorn/aladdin/genie .riv files",
    )
    parser.add_argument("--max-kb", type=int, default=500, help="Max size per file in KB")
    args = parser.parse_args()
    max_bytes = args.max_kb * 1024
    base: Path = args.dir
    failed = False
    for name in RIV_NAMES:
        path = base / name
        if not path.is_file():
            print(f"SKIP missing: {path}")
            failed = True
            continue
        size = path.stat().st_size
        ok = size <= max_bytes
        mark = "OK" if ok else "FAIL"
        print(f"{mark} {name}: {size} bytes (max {max_bytes})")
        if not ok:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
