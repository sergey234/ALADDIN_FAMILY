#!/usr/bin/env python3
"""HERO-3-07 — verify production .riv contract (HeroSM + 13 triggers + PNG)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMPANION = Path(__file__).resolve().parents[1] / "Resources" / "Companion"
MIN_BYTES = 25_000
TRIGGERS = (
    "idle", "listening", "thinking", "speaking", "happy", "playful", "sad",
    "comfort", "celebrate", "curious", "nostalgic", "excited", "alert",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("hero", nargs="?", default="unicorn", choices=("unicorn", "aladdin", "genie"))
    args = parser.parse_args()
    riv_path = COMPANION / f"{args.hero}.riv"
    if not riv_path.is_file():
        print(f"FAIL: missing {riv_path}")
        return 1
    data = riv_path.read_bytes()
    size = len(data)
    print(f"{riv_path.name}: {size} bytes")
    if size < MIN_BYTES:
        print(f"FAIL: size < {MIN_BYTES} (placeholder)")
        return 1
    missing = [t for t in TRIGGERS if t.encode() not in data]
    if b"mouth_open" not in data:
        missing.append("mouth_open")
    if b"HeroSM" not in data:
        missing.append("HeroSM")
    if missing:
        print(f"FAIL: missing in file: {missing}")
        return 1
    if b"\x89PNG\r\n\x1a\n" not in data:
        print("FAIL: no embedded PNG")
        return 1
    print(f"PASS: production {args.hero} .riv OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
