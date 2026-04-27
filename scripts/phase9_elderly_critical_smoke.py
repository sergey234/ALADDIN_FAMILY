#!/usr/bin/env python3
"""
Phase 9 critical-flow smoke (60+).

Checks:
1) One-tap/quick critical flows exist (call, medication, protection).
2) No language-dependent family role matching in emergency call chooser.
3) Basic localization hygiene for newly touched critical-flow fragments.
4) Build passes on a small-screen simulator.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent
SCREEN = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
SMALL_DEVICE_ID = "AE4850FB-CDAB-4B5B-B765-92CC04F4781B"  # iPhone SE (2nd gen)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


def must_not_contain(text: str, needle: str, context: str) -> None:
    require(needle not in text, f"{context}: forbidden `{needle}` is still present")


def must_match(text: str, pattern: str, context: str) -> None:
    require(re.search(pattern, text, flags=re.MULTILINE) is not None, f"{context}: missing pattern `{pattern}`")


def run(cmd: list[str], context: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{context} failed\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def check_critical_flow_contracts() -> None:
    body = read(SCREEN)
    must_contain(body, "startQuickFamilyCall()", "Quick family call flow")
    must_contain(body, "markFirstPendingMedicationAsTaken()", "Quick medication flow")
    must_contain(body, "runQuickSecurityAction()", "Quick security flow")
    must_contain(body, "criticalActionStatusMessage", "Critical-action feedback")
    print("OK quick critical-flow contracts")


def check_role_safe_contact_filtering() -> None:
    body = read(SCREEN)
    must_contain(body, "private var emergencyContacts", "Emergency contacts role filter")
    must_contain(body, "member.rawRole == .child", "Role-safe child filter")
    must_not_contain(body, '.contains("сын")', "Language-dependent role matching")
    must_not_contain(body, '.contains("дочь")', "Language-dependent role matching")
    print("OK role-safe emergency contact filtering")


def check_localized_fragments() -> None:
    body = read(SCREEN)
    must_not_contain(body, 'Text("Время: ', "Medication hardcoded time label")
    must_not_contain(body, 'Text("Дата: ', "Appointment hardcoded date label")
    must_not_contain(body, 'Button("✏️")', "Hardcoded edit icon button text")
    must_not_contain(body, 'Button("🗑️")', "Hardcoded delete icon button text")
    must_match(body, r'localizationManager\.localized\("elderly_medications_time"\)', "Localized medication time")
    must_match(body, r'localizationManager\.localized\("elderly_appointments_date"\)', "Localized appointment date")
    print("OK localized critical fragments")


def check_small_screen_build() -> None:
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
            f"id={SMALL_DEVICE_ID}",
            "build",
        ],
        "small-screen build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "small-screen build")
    print("OK small-screen build")


def main() -> int:
    print("PHASE 9 ELDERLY CRITICAL SMOKE")
    check_critical_flow_contracts()
    check_role_safe_contact_filtering()
    check_localized_fragments()
    check_small_screen_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
