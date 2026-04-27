#!/usr/bin/env python3
"""
Phase 9.2 smoke: elderly data integrity + parent desync report.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent
ELDERLY_SCREEN = ROOT / "Screens/09_ElderlyInterfaceScreen.swift"
PARENTAL_SCREEN = ROOT / "Screens/07_ParentalControlScreen.swift"
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
DEVICE_ID = "B98F9663-BB22-481C-B4C4-6D7E88F1E017"  # iPhone 16


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


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


def check_elderly_integrity_contract() -> None:
    body = read(ELDERLY_SCREEN)
    must_contain(body, "enum ElderlyHealthSyncAudit", "Elderly sync audit type")
    must_contain(body, "struct ElderlyHealthSyncReport", "Elderly sync report model")
    must_contain(body, "struct ElderlyHealthSyncEnvelope", "Elderly sync envelope model")
    must_contain(body, "static func perform(", "Elderly sync perform")
    must_contain(body, "static func synchronizeAcrossDevices(", "No-loss cross-device synchronization entrypoint")
    must_contain(body, "mergeWithoutLoss(", "No-loss merge strategy")
    must_contain(body, "snapshotEnvelopeKey", "Versioned sync snapshot key")
    must_contain(body, "persistSnapshot(", "Snapshot persistence")
    must_contain(body, "persistLatestReport", "Elderly sync report persistence")
    must_contain(body, "latestReport(", "Elderly sync report retrieval")
    require('phone: "+7 (999) 000-00-00", // TODO: Добавить телефон в FamilyMemberData' not in body, "Legacy placeholder contact phone TODO must be removed")
    must_match(body, r"\.onAppear \{\n[\s\S]*runDataIntegrityAudit\(\)", "Elderly screen runs audit on appear")
    print("OK elderly integrity contracts")


def check_parent_desync_integration() -> None:
    body = read(PARENTAL_SCREEN)
    must_contain(body, "@State private var elderlySyncReportBanner", "Parental state for elderly desync report")
    must_contain(body, "elderlySyncAuditBanner", "Parental banner component")
    must_contain(body, "refreshElderlySyncReport()", "Parental refresh function")
    must_contain(body, "ElderlyHealthSyncAudit.latestReport()", "Parental reads latest elderly report")
    print("OK parent desync report integration")


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
        "phase9.2 build",
    )
    must_match(out, r"\*\* BUILD SUCCEEDED \*\*", "phase9.2 build result")
    print("OK build for phase 9.2 changes")


def main() -> int:
    print("PHASE 9.2 DATA INTEGRITY SMOKE")
    check_elderly_integrity_contract()
    check_parent_desync_integration()
    check_build()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
