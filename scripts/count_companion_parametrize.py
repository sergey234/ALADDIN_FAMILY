#!/usr/bin/env python3
"""Count pytest parametrized cases in test_companion_*.py (hero-x-60)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = sorted(ROOT.glob("Tests/test_companion_*.py"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=int, default=40)
    args = parser.parse_args()

    parametrize = 0
    test_funcs = 0
    for path in TESTS:
        text = path.read_text(encoding="utf-8")
        parametrize += len(re.findall(r"@pytest\.mark\.parametrize", text))
        test_funcs += len(re.findall(r"^\s+def test_", text, re.M))

    # Each parametrize decor usually expands to multiple cases; also count unittest methods
    estimated = test_funcs + parametrize * 3
    print(f"Companion test files: {len(TESTS)}")
    print(f"test_* functions: {test_funcs}")
    print(f"@parametrize decorators: {parametrize}")
    print(f"Estimated cases (funcs + 3×parametrize): {estimated}")

    if test_funcs < args.min:
        print(f"FAIL: need ≥{args.min} test functions, got {test_funcs}", file=sys.stderr)
        return 1
    print(f"OK: ≥{args.min} companion tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
