#!/usr/bin/env python3
"""R-01 static release gate — no xcodebuild, no simulator.

Checks code/UI prerequisites from ANTIFAKE_TESTFLIGHT_CHECKLIST.md before device QA.
Exit 0 = code gate pass; device rows remain manual.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBX = ROOT / "ALADDIN.xcodeproj" / "project.pbxproj"


def ok(msg: str) -> None:
    print(f"OK  {msg}")


def fail(msg: str) -> None:
    print(f"FAIL {msg}")
    failures.append(msg)


failures: list[str] = []


def check_file(rel: str) -> None:
    if (ROOT / rel).is_file():
        ok(f"file {rel}")
    else:
        fail(f"missing file {rel}")


def check_pbx(needle: str, msg: str) -> None:
    text = PBX.read_text(encoding="utf-8", errors="replace")
    if needle in text:
        ok(msg)
    else:
        fail(msg)


def check_privacy_manifest(path: str, data_type: str) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    if data_type in text:
        ok(f"{path} declares {data_type}")
    else:
        fail(f"{path} missing {data_type}")


def _line_allows_mock_reference(line: str) -> bool:
    low = line.lower()
    if "bypasspremiumgate" in low.replace("_", ""):
        return True
    if any(
        k in low
        for k in (
            "forbidden",
            "reject",
            "no mock",
            "mock_source_rejected",
            "detail=",
            "not in",
            "raise ",
        )
    ):
        return True
    return False


def check_no_antifake_mock_bypass_in_prod_paths() -> None:
    bad = []
    for rel in (
        "app/routers/antifake.py",
        "app/services/antifake_service.py",
        "Core/Security/AntifakeAccessPolicy.swift",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"sfm_mock|mock-real-protection|mock_fallback", line, re.I):
                if _line_allows_mock_reference(line):
                    continue
                if re.search(r"in\s*\(|frozenset|forbidden", line, re.I):
                    continue
                bad.append(f"{rel}:{i}")
    if bad:
        fail(f"mock strings in antifake prod paths: {', '.join(bad[:5])}")
    else:
        ok("antifake prod paths reject mock sources (no bypass)")


def main() -> int:
    if not PBX.is_file():
        fail("ALADDIN.xcodeproj/project.pbxproj missing")
        print(json.dumps({"pass": False, "failures": failures}))
        return 1

    # Extensions + privacy manifests (N-01)
    check_pbx("ALADDINCallDirectory.appex in Embed App Extensions", "Call Directory extension embedded")
    check_pbx("ALADDINAntifakeShare.appex in Embed App Extensions", "Antifake Share extension embedded")
    check_pbx("AFPR002F90000200C7D34B /* PrivacyInfo.xcprivacy in Resources */", "main PrivacyInfo in Resources")
    check_pbx("AFNP008F90000200C7D34B /* PrivacyInfo.xcprivacy in Resources */", "Call Directory PrivacyInfo")
    check_pbx("AFNP010F90000200C7D34B /* PrivacyInfo.xcprivacy in Resources */", "Share extension PrivacyInfo")
    check_file("PrivacyInfo.xcprivacy")
    check_file("ALADDINCallDirectory/PrivacyInfo.xcprivacy")
    check_file("ALADDINAntifakeShare/PrivacyInfo.xcprivacy")
    check_privacy_manifest("PrivacyInfo.xcprivacy", "NSPrivacyCollectedDataTypePhoneNumber")
    check_privacy_manifest("PrivacyInfo.xcprivacy", "NSPrivacyCollectedDataTypeOtherUserContent")

    # Hub UI (4 tabs)
    hub = (ROOT / "Screens/AntifakeHubScreen.swift").read_text(encoding="utf-8")
    for tab in ("text", "audio", "video", "call"):
        if f"case .{tab}" in hub or f'.{tab}' in hub:
            ok(f"AntifakeHub tab .{tab}")
        else:
            fail(f"AntifakeHub missing tab .{tab}")

    # Release docs (R-01 / R-02 / A-07)
    check_file("docs/release/ANTIFAKE_TESTFLIGHT_CHECKLIST.md")
    check_file("docs/release/ANTIFAKE_QA_SIGNOFF.md")
    check_file("docs/release/ANTIFAKE_APP_STORE_REVIEW_NOTES.md")
    check_file("docs/release/ANTIFAKE_APP_STORE_PRIVACY_LABELS.md")
    check_file("docs/marketing/ANTIFAKE_LANDING_COPY.md")
    check_file("scripts/verify_antifake_marketing_claims.py")
    check_file("scripts/verify_antifake_q_static.sh")
    check_file("scripts/verify_antifake_no_mock_pre_submit.py")
    check_file("docs/release/ANTIFAKE_TESTFLIGHT_BETA_CRITERIA.md")
    check_file("backend_tests/test_antifake_call_directory_contract.py")
    check_file("Tests/UITests/AntifakeHubTabsUITests.swift")
    check_file("docs/release/qa_signoff/antifake/README.md")

    # Post-call + privacy code paths
    check_file("Core/Security/AntifakePostCallPolicy.swift")
    check_file("Core/Security/AntifakePrivacyWipe.swift")
    check_file("Core/Security/AntifakePhonePrivacy.swift")

    # Deploy / smoke artifacts (B batch)
    check_file("scripts/deploy_antifake_m1.sh")
    check_file("docs/server/test_antifake_prod_smoke.py")
    check_file("scripts/antifake_prod_gate_af11.py")

    check_no_antifake_mock_bypass_in_prod_paths()

    policy_path = ROOT / "Core/Security/AntifakeAccessPolicy.swift"
    if not policy_path.is_file():
        fail("AntifakeAccessPolicy.swift missing")
    else:
        policy = policy_path.read_text(encoding="utf-8")
        if "bypassPremiumGate" in policy:
            compact = policy.replace(" ", "")
            if "bypassPremiumGate:Bool=false" in compact or "bypassPremiumGate=false" in compact:
                ok("bypassPremiumGate=false (G-03 production)")
            elif "bypassPremiumGate:Bool=true" in compact or "bypassPremiumGate=true" in compact:
                fail("bypassPremiumGate still true — run G-03 before App Store")
            else:
                fail("AntifakeAccessPolicy.bypassPremiumGate value unclear")
        else:
            fail("AntifakeAccessPolicy.bypassPremiumGate not found")

    # Open-task code (J-04, D-07/08/10, G-03) — no xcodebuild
    check_file("Core/Security/AntifakeCheckHistoryPDFExporter.swift")
    check_file("Core/Security/AntifakeCallDirectoryLabelPolicy.swift")
    check_file("Tests/UnitTests/AntifakeCallDirectoryStoreTests.swift")
    check_pbx("AntifakeCheckHistoryPDFExporter.swift in Sources", "J-04 PDF exporter wired")
    check_pbx("AntifakeCallDirectoryLabelPolicy.swift in Sources", "D-10 label policy wired")
    check_pbx("AntifakeCallDirectoryStoreTests.swift in Sources", "D-07 store tests wired")
    check_pbx("AntifakeAnalytics.swift in Sources", "M-02 analytics wired")

    result = {"pass": not failures, "failures": failures, "gate": "antifake_r01_static"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
