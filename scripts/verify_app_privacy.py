#!/usr/bin/env python3
"""Static App Store privacy consistency gate."""

from pathlib import Path
import plistlib
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PrivacyInfo.xcprivacy"
ANSWERS = ROOT / "docs/AppStore/APP_PRIVACY_ANSWERS_2026-09-09_RU.md"

EXPECTED_TYPES = {
    "NSPrivacyCollectedDataTypeOtherUserContent",
    "NSPrivacyCollectedDataTypePhoneNumber",
    "NSPrivacyCollectedDataTypeAudioData",
    "NSPrivacyCollectedDataTypePhotosorVideos",
    "NSPrivacyCollectedDataTypeName",
    "NSPrivacyCollectedDataTypeEmailAddress",
    "NSPrivacyCollectedDataTypeContacts",
    "NSPrivacyCollectedDataTypePreciseLocation",
    "NSPrivacyCollectedDataTypeUserID",
    "NSPrivacyCollectedDataTypeDeviceID",
    "NSPrivacyCollectedDataTypePurchaseHistory",
    "NSPrivacyCollectedDataTypeProductInteraction",
    "NSPrivacyCollectedDataTypeSensitiveInfo",
    "NSPrivacyCollectedDataTypeOtherDataTypes",
    "NSPrivacyCollectedDataTypePhysicalAddress",
    "NSPrivacyCollectedDataTypeHealth",
    "NSPrivacyCollectedDataTypeFitness",
    "NSPrivacyCollectedDataTypeEmailsorTextMessages",
    "NSPrivacyCollectedDataTypeCustomerSupport",
    "NSPrivacyCollectedDataTypeOtherUsageData",
    "NSPrivacyCollectedDataTypeCrashData",
    "NSPrivacyCollectedDataTypePerformanceData",
    "NSPrivacyCollectedDataTypeOtherDiagnosticData",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


with MANIFEST.open("rb") as stream:
    manifest = plistlib.load(stream)

if manifest.get("NSPrivacyTracking") is not False:
    fail("NSPrivacyTracking must be false")
if manifest.get("NSPrivacyTrackingDomains") != []:
    fail("tracking domains must be empty")

entries = manifest.get("NSPrivacyCollectedDataTypes", [])
by_type = {entry.get("NSPrivacyCollectedDataType"): entry for entry in entries}
missing = EXPECTED_TYPES - set(by_type)
if missing:
    fail(f"missing collected data declarations: {sorted(missing)}")

for data_type in EXPECTED_TYPES:
    entry = by_type[data_type]
    if entry.get("NSPrivacyCollectedDataTypeLinked") is not True:
        fail(f"{data_type} must be disclosed as linked")
    if entry.get("NSPrivacyCollectedDataTypeTracking") is not False:
        fail(f"{data_type} must not be marked for tracking")
    purposes = entry.get("NSPrivacyCollectedDataTypePurposes", [])
    if "NSPrivacyCollectedDataTypePurposeAppFunctionality" not in purposes:
        fail(f"{data_type} must include App Functionality purpose")

accessed = {
    item.get("NSPrivacyAccessedAPIType"): set(item.get("NSPrivacyAccessedAPITypeReasons", []))
    for item in manifest.get("NSPrivacyAccessedAPITypes", [])
}
if "CA92.1" not in accessed.get("NSPrivacyAccessedAPICategoryUserDefaults", set()):
    fail("UserDefaults required reason CA92.1 is missing")
if "1C8F.1" not in accessed.get("NSPrivacyAccessedAPICategoryUserDefaults", set()):
    fail("App Group UserDefaults required reason 1C8F.1 is missing")
if "C617.1" not in accessed.get("NSPrivacyAccessedAPICategoryFileTimestamp", set()):
    fail("FileTimestamp required reason C617.1 is missing")
if "35F9.1" not in accessed.get("NSPrivacyAccessedAPICategorySystemBootTime", set()):
    fail("SystemBootTime required reason 35F9.1 is missing")

for extension_path in (
    "ALADDINCallDirectory/PrivacyInfo.xcprivacy",
    "ALADDINAntifakeShare/PrivacyInfo.xcprivacy",
    "ALADDINContentBlocker/PrivacyInfo.xcprivacy",
):
    with (ROOT / extension_path).open("rb") as stream:
        extension_manifest = plistlib.load(stream)
    extension_accessed = {
        item.get("NSPrivacyAccessedAPIType"): set(item.get("NSPrivacyAccessedAPITypeReasons", []))
        for item in extension_manifest.get("NSPrivacyAccessedAPITypes", [])
    }
    if "1C8F.1" not in extension_accessed.get(
        "NSPrivacyAccessedAPICategoryUserDefaults",
        set(),
    ):
        fail(f"{extension_path} must declare App Group UserDefaults reason 1C8F.1")

answer_text = ANSWERS.read_text(encoding="utf-8")
for required in (
    "Tracking: **No**",
    "Linked to the User: Yes",
    "Precise Location — Yes",
    "Purchase History — Yes",
    "Contacts — Yes",
):
    if required not in answer_text:
        fail(f"App Privacy answer document is missing: {required}")

print("PASS: App Privacy manifest and App Store Connect answers are consistent")
sys.exit(0)
