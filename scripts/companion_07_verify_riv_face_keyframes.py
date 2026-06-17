#!/usr/bin/env python3
"""HERO-3-04 — verify idle/speaking timeline keyframes exist in editor .rev source."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "Resources" / "Companion"

# Latin-1 decode is enough to spot animation names / keyframe markers in .rev/.riv.
MARKERS = (
    b"idle_anim",
    b"speaking_anim",
    b"eye_left_pupil",
    b"mouth_shape",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "rev",
        nargs="?",
        default="unicorn_golden_amp.rev",
        help="Editor .rev file (default: unicorn_golden_amp.rev)",
    )
    args = parser.parse_args()
    path = COMPANION / args.rev
    if not path.is_file():
        print(f"FAIL: missing {path}")
        return 1
    data = path.read_bytes()
    missing = [m.decode() for m in MARKERS if m not in data]
    if missing:
        print(f"FAIL: missing markers in {path.name}: {missing}")
        return 1
    print(f"PASS: {path.name} has idle/speaking face markers")
    print("Next: open in Rive Editor → Export Runtime → unicorn.riv → re-patch aladdin/genie")
    return 0


if __name__ == "__main__":
    sys.exit(main())
