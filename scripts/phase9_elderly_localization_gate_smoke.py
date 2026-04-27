#!/usr/bin/env python3
"""
Phase 9.5 smoke: verify elderly localization lint merge gate wiring.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINT_SCRIPT = ROOT / "scripts/localization_lint.py"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


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


def check_ci_gate() -> None:
    workflow = read(CI_WORKFLOW)
    require(
        "python3 scripts/localization_lint.py --scope elderly60plus" in workflow,
        "CI localization-lint must enforce elderly60plus scope gate",
    )
    print("OK CI gate wiring")


def check_local_scope_lint() -> None:
    out = run(
        ["python3", "scripts/localization_lint.py", "--scope", "elderly60plus"],
        "elderly scoped localization lint",
    )
    require("✅ localization-lint passed" in out, "Scoped localization lint should pass")
    require("- Scope: elderly60plus" in out, "Scoped lint output must include scope")
    print("OK scoped localization lint")


def main() -> int:
    print("PHASE 9.5 ELDERLY LOCALIZATION GATE SMOKE")
    check_ci_gate()
    check_local_scope_lint()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
