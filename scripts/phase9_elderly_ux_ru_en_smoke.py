#!/usr/bin/env python3
"""
Phase 9.5 smoke: elderly RU/EN localization completeness + UX large text/contrast.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCREEN = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
L10N = ROOT / "Core/Localization/LocalizationManager.swift"
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
DEVICE_ID = "B98F9663-BB22-481C-B4C4-6D7E88F1E017"


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


def check_localization_usage() -> None:
    screen = read(SCREEN)
    l10n = read(L10N)

    keys = sorted(set(re.findall(r'localized\(\s*"([^"]+)"', screen)))
    require(keys, "No localized(\"key\") usage found in elderly screen")

    # Validate that all keys referenced in the elderly screen are present in localization manager maps.
    missing = [key for key in keys if f'"{key}"' not in l10n]
    require(not missing, f"LocalizationManager missing elderly keys: {missing[:25]}")

    # UX contracts for large text / contrast presets.
    require('@AppStorage("elderly_large_read_mode")' in screen, "Missing large read mode storage")
    require('@AppStorage("elderly_contrast_preset")' in screen, "Missing contrast preset storage")
    require(".dynamicTypeSize(elderlyDynamicType)" in screen, "Missing dynamic type application")
    require(".contrast(elderlyContrastValue)" in screen, "Missing contrast application")

    print(f"OK RU/EN key wiring ({len(keys)} localized keys in elderly screen)")


def check_scoped_lint_gate() -> None:
    out = run(
        ["python3", "scripts/localization_lint.py", "--scope", "elderly60plus"],
        "elderly scoped localization lint",
    )
    require("✅ localization-lint passed" in out, "Scoped localization lint must pass")
    require("- Scope: elderly60plus" in out, "Scoped lint should report elderly60plus scope")
    print("OK scoped no-hardcoded localization gate")


def check_build() -> None:
    out = run(
        [
            "xcodebuild",
            "-project",
            PROJECT,
            "-scheme",
            SCHEME,
            "-sdk",
            "iphonesimulator",
            "-destination",
            f"id={DEVICE_ID}",
            "build",
        ],
        "phase9.5 elderly ux build",
    )
    require("** BUILD SUCCEEDED **" in out, "Build must succeed")
    print("OK build")


def main() -> int:
    print("PHASE 9.5 ELDERLY UX RU/EN SMOKE")
    check_localization_usage()
    check_scoped_lint_gate()
    check_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
