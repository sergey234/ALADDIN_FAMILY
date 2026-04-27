#!/usr/bin/env python3
"""
Phase 8.4 compliance smoke for remaining items:
1) Children privacy compliance check (RU primary, COPPA secondary)
2) Personal data storage audit
3) Family Sharing security validation
"""

from __future__ import annotations

import pathlib
import re
import subprocess
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


def check_children_privacy_contracts() -> None:
    dashboard = read("docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md")
    next_plan = read("NEXT_VERSION_IMPLEMENTATION_PLAN.md")

    # Privacy governance baseline commitments present in canonical planning docs.
    require(
        ("Privacy governance (COPPA + GDPR рамка)" in dashboard)
        or ("Privacy governance (РФ 152-ФЗ primary + GDPR/COPPA secondary рамка)" in dashboard),
        "Dashboard privacy governance section: expected COPPA/GDPR legacy or RU-primary wording",
    )
    must_contain(dashboard, "consent_version", "Dashboard consent versioning requirement")
    require(
        ("Privacy governance (COPPA + GDPR рамка)" in next_plan)
        or ("Privacy governance (РФ 152-ФЗ primary + GDPR/COPPA secondary рамка)" in next_plan),
        "Next plan privacy governance section: expected COPPA/GDPR legacy or RU-primary wording",
    )
    must_contain(next_plan, "consent_version", "Next plan consent versioning requirement")
    require(
        ("COPPA readiness" in dashboard)
        or ("COPPA readiness" in next_plan)
        or ("COPPA compliance" in dashboard)
        or ("COPPA compliance" in next_plan),
        "Expected COPPA wording as secondary/global readiness signal",
    )
    print("OK children-privacy governance contracts (RU primary, COPPA secondary)")


def check_personal_data_storage_audit_contracts() -> None:
    parent_gate = read("Core/Profile/ParentSessionGate.swift")
    profile_manager = read("Core/Profile/ProfileManager.swift")
    storage_manager = read("Core/Storage/StorageManager.swift")
    security_manager = read("Core/Security/SecurityManager.swift")

    # Sensitive parental verification data: hashed PIN + rate limiting.
    must_contain(parent_gate, "pinHashSecureKey", "ParentSessionGate secure PIN key")
    must_contain(parent_gate, "SHA256.hash", "ParentSessionGate hashed PIN")
    must_contain(parent_gate, "pinMaxAttempts = 5", "ParentSessionGate brute-force limit")

    # Data rights (DSAR-like) export/delete.
    must_contain(profile_manager, "exportChildDataRightsPackage", "ProfileManager DSAR export")
    must_contain(profile_manager, "deleteChildData(serverUserId:", "ProfileManager DSAR delete")

    # Keychain-backed storage route.
    must_contain(storage_manager, "private let keychain = KeychainManager.shared", "StorageManager keychain route")
    must_contain(security_manager, "storeSecureData", "SecurityManager secure store API")
    print("OK personal-data storage audit contracts")


def check_family_sharing_security_contracts() -> None:
    family_policy = read("Core/Profile/FamilyAccessPolicy.swift")
    family_screen = read("Screens/02_FamilyScreen.swift")

    # Family Sharing separated and parent-only.
    must_contain(family_policy, "case manageFamilySharing", "FamilyAccessPolicy family-sharing permission")
    must_match(family_policy, r"case \.manageFamilySharing:\n\s*return role == \.parent", "FamilyAccessPolicy parent-only sharing")
    must_contain(family_policy, "canManageFamilySharing", "FamilyAccessPolicy sharing accessor")

    # Sensitive roster actions require adult challenge.
    must_contain(family_screen, "ParentSessionGate.confirmSensitiveAction()", "FamilyScreen sensitive-action challenge")
    must_contain(family_screen, "Family Sharing операции", "FamilyScreen sharing-vs-app-profile separation")
    print("OK Family Sharing security contracts")


def run_dependency_smokes() -> None:
    # Ensure previously introduced security and DSAR smoke gates still pass.
    sec = run([sys.executable, "scripts/phase8_security_smoke.py"], "phase8_security_smoke")
    require("SMOKE RESULT: PASS" in sec, "phase8_security_smoke did not pass")

    perf = run([sys.executable, "scripts/phase8_performance_smoke.py"], "phase8_performance_smoke")
    require("SMOKE RESULT: PASS" in perf, "phase8_performance_smoke did not pass")
    print("OK dependency smoke gates")


def main() -> int:
    print("PHASE 8.4 COMPLIANCE SMOKE")
    check_children_privacy_contracts()
    check_personal_data_storage_audit_contracts()
    check_family_sharing_security_contracts()
    run_dependency_smokes()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
