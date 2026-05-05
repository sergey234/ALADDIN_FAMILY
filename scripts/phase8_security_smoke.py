#!/usr/bin/env python3
"""
Phase 8.4 security smoke checks for Parental Control + DSAR.

This script performs deterministic source-contract checks without requiring
ALADDINUnitTests execution (which is intentionally deferred as post-plan item).
"""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


def must_match(text: str, pattern: str, context: str) -> None:
    require(re.search(pattern, text, flags=re.MULTILINE) is not None, f"{context}: missing pattern `{pattern}`")


def check_parent_session_gate() -> None:
    screens = [
        "Screens/02_FamilyScreen.swift",
        "Screens/07_ParentalControlScreen.swift",
        "Screens/ParentDashboardView.swift",
        "Screens/RewardsModalView.swift",
        "Screens/RewardsQuickModal.swift",
        "Screens/GamesParentalControlScreen.swift",
        "Screens/ChildRewardsScreen.swift",
    ]
    for rel_path in screens:
        body = read(rel_path)
        require(
            "ParentSessionGate.confirmSensitiveAction(" not in body,
            f"{rel_path}: ParentSessionGate challenge must be removed from runtime flow",
        )
    print("OK runtime flows are PIN-gate free")


def check_profile_manager_dsar() -> None:
    body = read("Core/Profile/ProfileManager.swift")
    must_contain(body, "struct ChildDataRightsPackage", "ProfileManager DSAR package model")
    must_contain(body, "exportChildDataRightsPackage", "ProfileManager DSAR export")
    must_contain(body, "deleteChildData(serverUserId:", "ProfileManager DSAR delete")
    must_contain(body, "lastDataRightsActionSummary", "ProfileManager DSAR diagnostics")
    print("OK ProfileManager DSAR export/delete")


def check_parent_dashboard_dsar_actions() -> None:
    body = read("Screens/ParentDashboardView.swift")
    has_static_data_rights = "Text(\"Data rights\")" in body
    has_localized_data_rights = "Text(localizationManager.localized(\"parent_dashboard_data_rights\"))" in body
    require(has_static_data_rights or has_localized_data_rights, "ParentDashboard data-rights section is missing")
    must_contain(body, "Button(\"Export child data\")", "ParentDashboard export action")
    must_contain(body, "Button(\"Delete active child data\")", "ParentDashboard delete action")
    must_contain(body, "runSensitiveAction", "ParentDashboard sensitive challenge gate")
    print("OK ParentDashboard sensitive DSAR actions")


def main() -> int:
    print("PHASE 8.4 SECURITY SMOKE")
    check_parent_session_gate()
    check_profile_manager_dsar()
    check_parent_dashboard_dsar_actions()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError) as exc:
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
