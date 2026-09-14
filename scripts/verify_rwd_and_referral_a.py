#!/usr/bin/env python3
"""Offline verify: RWD + Family Referral A (rules, ledger helpers, Swift/API markers)."""

from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def check_swift_rwd() -> list[str]:
    errs: list[str] = []
    policy = (ROOT / "Core/Profile/FamilyAccessPolicy.swift").read_text(encoding="utf-8")
    for needle in (
        "isCaregiverForRewardsUI",
        "syncCurrentUserRoleDefaults",
        "isCaregiver(",
    ):
        if needle not in policy:
            errs.append(f"FamilyAccessPolicy missing {needle}")

    screen = (ROOT / "Screens/ChildRewardsScreen.swift").read_text(encoding="utf-8")
    for needle in (
        "isCurrentUserCaregiver",
        "isEnteredFromChildInterface",
        "FamilyAccessPolicy.isCaregiverForRewardsUI",
        "alignCurrentUserRoleFromPersistedRoster",
    ):
        if needle not in screen:
            errs.append(f"ChildRewardsScreen missing {needle}")
    return errs


def check_referral_a() -> list[str]:
    errs: list[str] = []

    ledger_sql = ROOT / "docs/server/FAMILY_REFERRAL_A_LEDGER.sql"
    if not ledger_sql.exists():
        errs.append("missing docs/server/FAMILY_REFERRAL_A_LEDGER.sql")

    ledger_py = (ROOT / "app/services/family_referral_ledger.py").read_text(encoding="utf-8")
    for needle in (
        "apply_family_referral_a",
        "soft_device_hash",
        "overview_for_referrer",
        "family_referral_ledger",
    ):
        if needle not in ledger_py:
            errs.append(f"family_referral_ledger.py missing {needle}")

    router = (ROOT / "app/routers/referral.py").read_text(encoding="utf-8")
    for needle in (
        '/a/overview',
        '/a/ledger',
        '/a/apply',
        '/a/attach',
        "family_referral_a_overview",
    ):
        if needle not in router:
            errs.append(f"referral.py missing {needle}")

    app_cfg = (ROOT / "Core/Config/AppConfig.swift").read_text(encoding="utf-8")
    for needle in (
        "referralAOverview",
        "referralALedger",
        "referralAApply",
        "referralAAttach",
    ):
        if needle not in app_cfg:
            errs.append(f"AppConfig missing {needle}")

    referral_ui = (ROOT / "Screens/21_ReferralScreen.swift").read_text(encoding="utf-8")
    for needle in (
        "familyInviteTierCard",
        "familyInviteLedgerCard",
        "referralFAQCard",
        "isCaregiverAccess",
        "getFamilyReferralAOverview",
        "FamilyReferralAnalytics",
    ):
        if needle not in referral_ui:
            errs.append(f"ReferralScreen missing {needle}")

    profile = (ROOT / "Screens/11_ProfileScreen.swift").read_text(encoding="utf-8")
    if "FamilyAccessPolicy.isCaregiver()" not in profile:
        errs.append("ProfileScreen missing caregiver gate for referral")

    family = (ROOT / "Screens/02_FamilyScreen.swift").read_text(encoding="utf-8")
    for needle in ("showReferralScreen", "family_invite_cta_title"):
        if needle not in family:
            errs.append(f"FamilyScreen missing {needle}")

    invite = (ROOT / "Core/Referral/FamilyReferralInviteRouter.swift").read_text(encoding="utf-8")
    for needle in ("extractInviteCode", "attachPendingIfNeeded", "notifyGrantIfNeeded"):
        if needle not in invite:
            errs.append(f"FamilyReferralInviteRouter missing {needle}")

    loc = (ROOT / "Core/Localization/LocalizationManager.swift").read_text(encoding="utf-8")
    for needle in (
        "referral_a_faq_q1",
        "referral_a_caregiver_only_title",
        "referral_a_grant_push_body",
        "family_invite_cta_title",
    ):
        if loc.count(f'"{needle}"') < 2:
            errs.append(f"Localization missing RU+EN key {needle}")

    return errs


def main() -> int:
    import importlib.util

    errs = check_swift_rwd() + check_referral_a()

    mods = []
    for name, rel in (
        ("test_family_referral_a", "tests/test_family_referral_a.py"),
        ("test_family_referral_ledger", "tests/test_family_referral_ledger.py"),
    ):
        spec = importlib.util.spec_from_file_location(name, ROOT / rel)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        mods.append(mod)

    suite = unittest.TestSuite()
    for mod in mods:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(mod))
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if errs:
        print("STATIC CHECK FAIL:")
        for e in errs:
            print(" -", e)
    else:
        print("STATIC CHECK OK (RWD + REF-A)")

    if errs or not result.wasSuccessful():
        return 1
    print("VERIFY OK (no Xcode build; deploy only after GO DEPLOY)")
    print("SMOKE after deploy: GET /api/referral/a/overview · GET /api/referral/a/ledger · POST /api/referral/a/attach")
    return 0


if __name__ == "__main__":
    sys.exit(main())
