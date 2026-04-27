#!/usr/bin/env python3
"""
Track B smoke: UI localization full-coverage contract + RU/EN keys hygiene.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "docs/LOCALIZATION_PR_CHECKLIST.md"
STANDARD = ROOT / "docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md"


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


def check_docs_contract() -> None:
    require(CHECKLIST.exists(), "Missing localization PR checklist")
    require(STANDARD.exists(), "Missing localization implementation standard")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    standard = STANDARD.read_text(encoding="utf-8")
    for needle in [
        "Happy-path labels localized.",
        "Error messages localized.",
        "Empty states localized.",
        "Localized accessibility hints and values are added where needed.",
    ]:
        require(needle in checklist, f"Checklist missing coverage item: {needle}")
    require("Errors and empty states are mandatory" in standard, "Standard missing error/empty-state mandate")
    require("Accessibility localization is required" in standard, "Standard missing accessibility mandate")
    print("OK docs coverage contract")


def check_key_hygiene_gates() -> None:
    lint_out = run(
        ["python3", "scripts/localization_lint.py", "--scope", "elderly60plus"],
        "scoped localization lint",
    )
    require("✅ localization-lint passed" in lint_out, "Scoped localization lint must pass")
    ns_out = run(
        ["python3", "scripts/trackb_namespace_map_smoke.py"],
        "namespace map smoke",
    )
    require("SMOKE RESULT: PASS" in ns_out, "Namespace map smoke must pass")
    print("OK key hygiene gates")


def main() -> int:
    print("TRACK B UI LOCALIZATION COVERAGE+KEYS SMOKE")
    check_docs_contract()
    check_key_hygiene_gates()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
