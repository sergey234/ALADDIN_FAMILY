#!/usr/bin/env python3
"""
Track B smoke: localization core gates (#1/#2/#3 in current pending list).
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "docs/LOCALIZATION_PR_CHECKLIST.md"
LINT = ROOT / "scripts/localization_lint.py"


def require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def run(cmd: list[str], context: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{context} failed\nCMD: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def main() -> int:
    print("TRACK B LOCALIZATION CORE GATES SMOKE")
    require(CHECKLIST.exists(), "Missing localization PR checklist")
    require(LINT.exists(), "Missing localization_lint script")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    require("localization_lint.py" in checklist, "Checklist missing localization-lint requirement")
    require("Placeholders are consistent between RU and EN" in checklist, "Checklist missing placeholder parity requirement")
    require("Reviewer confirmed no hardcoded user-facing strings" in checklist, "Checklist missing hardcoded check gate")

    out = run(["python3", "scripts/localization_lint.py", "--scope", "elderly60plus"], "scoped localization lint")
    require("✅ localization-lint passed" in out, "Scoped localization lint must pass")
    require("- Scope: elderly60plus" in out, "Lint output must include enforced scope")
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
