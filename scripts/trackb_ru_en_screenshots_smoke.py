#!/usr/bin/env python3
"""
Track B smoke: RU/EN screenshots exist for changed UI.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RU_SHOT = ROOT / "docs/screenshots/trackb/elderly_ru.png"
EN_SHOT = ROOT / "docs/screenshots/trackb/elderly_en.png"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def main() -> int:
    print("TRACK B RU/EN SCREENSHOTS SMOKE")
    require(RU_SHOT.exists(), f"Missing RU screenshot: {RU_SHOT.relative_to(ROOT)}")
    require(EN_SHOT.exists(), f"Missing EN screenshot: {EN_SHOT.relative_to(ROOT)}")
    require(RU_SHOT.stat().st_size > 1024, "RU screenshot file is too small")
    require(EN_SHOT.stat().st_size > 1024, "EN screenshot file is too small")
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
