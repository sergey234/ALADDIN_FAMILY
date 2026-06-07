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
    parser.add_argument(
        "--min-kb",
        type=int,
        default=0,
        help="Min production size per file in KB (iOS CompanionHeroRiveHost.productionRivMinBytes; 0 = skip)",
    )
    args = parser.parse_args()
    max_bytes = args.max_kb * 1024
    min_bytes = args.min_kb * 1024
    base: Path = args.dir
    failed = False
    for name in RIV_NAMES:
        path = base / name
        if not path.is_file():
            print(f"SKIP missing: {path}")
            failed = True
            continue
        size = path.stat().st_size
        ok_max = size <= max_bytes
        ok_min = min_bytes == 0 or size >= min_bytes
        ok = ok_max and ok_min
        mark = "OK" if ok else "FAIL"
        extra = ""
        if min_bytes and not ok_min:
            extra = f" (min {min_bytes}, placeholder?)"
        elif not ok_max:
            extra = f" (max {max_bytes})"
        print(f"{mark} {name}: {size} bytes{extra}")
        if not ok:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
