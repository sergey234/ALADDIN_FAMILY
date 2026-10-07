#!/usr/bin/env python3
"""Wave F / store-lift static verify + RU/EN key parity (no Xcode build).

Plan-fact: checks that code markers for geo/crash/browse/pwd/av/academy/sos/bat/pay exist
and that every newly required localization key exists in both RU and EN dictionaries.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOC = ROOT / "Core" / "Localization" / "LocalizationManager.swift"

REQUIRED_FILES = {
    "geo-04 consent": ROOT / "Core/Family/GeofencePlacesConsentStore.swift",
    "geo-02 noshow": ROOT / "Core/Family/GeofenceNoShowMonitor.swift",
    "geo-01/03 events": ROOT / "Core/Family/GeofenceEventStore.swift",
    "bat-01": ROOT / "Core/Family/FamilyBatteryCriticalMonitor.swift",
    "day strip": ROOT / "Shared/Components/FamilyDayStripView.swift",
    "week digest": ROOT / "Shared/Components/FamilyShieldWeekDigestCard.swift",
    "dark web form": ROOT / "Shared/Components/Modals/DarkWebDataInputView.swift",
    "crash settings": ROOT / "Shared/Components/Modals/CrashDetectionSettingsModal.swift",
    "young defender": ROOT / "Screens/YoungDefenderView.swift",
}

CODE_MARKERS = [
    ("geo-04", "Screens/02_FamilyScreen.swift", "GeofencePlacesConsentStore"),
    ("geo-02", "Screens/02_FamilyScreen.swift", "GeofenceNoShowMonitor"),
    ("geo-03", "Core/Family/GeofenceEventStore.swift", "retentionDays = 7"),
    ("geo-01", "Core/Family/GeofenceEventStore.swift", "geofence_home_push"),
    ("crash-02", "Shared/Components/Modals/CrashDetectionAlertModal.swift", "crash_alert_im_ok"),
    ("consent-01", "Shared/Components/Modals/CrashDetectionSettingsModal.swift", "crashConsentAccepted"),
    ("browse-01", "Screens/AntifakeHubScreen.swift", "share_onboard_path_share"),
    ("browse-02", "Screens/02_FamilyScreen.swift", "browse_safari_how_to_enable"),
    ("darkweb-01", "Shared/Components/Modals/DarkWebDataInputView.swift", "passport: nil"),
    ("foot-02", "Screens/PrivacyHubScreen.swift", "dark_web_flow_title"),
    ("pwd-01", "Shared/Components/Modals/PasswordGeneratorModal.swift", "password_honest_scope"),
    ("av-01", "Screens/03_NetworkProtectionScreen.swift", "antivirus_file_hub_cta"),
    ("call-01", "Screens/09_ElderlyInterfaceScreen.swift", "elderly_scam_call_step1"),
    ("ux-01", "Shared/Components/FamilyDayStripView.swift", "day_strip_on_view_badge"),
    ("pay-01", "Screens/10_TariffsScreen.swift", "pay_tiers_plain_title"),
    ("priv-01", "Screens/YoungDefenderView.swift", "young_defender_lesson_8_title"),
    ("gai-08", "Screens/YoungDefenderView.swift", "young_defender_lesson_9_title"),
    ("id-01", "Screens/YoungDefenderView.swift", "young_defender_lesson_10_title"),
    ("sos-01", "Screens/09_ElderlyInterfaceScreen.swift", "sos_alarm_family_cta"),
    ("bat-01", "Core/Family/FamilyBatteryCriticalMonitor.swift", "battery_critical_push_title"),
    ("bat hook", "ALADDINApp.swift", "FamilyBatteryCriticalMonitor.checkAndNotifyIfNeeded"),
]

REQUIRED_KEYS = [
    "geofence_home_push_title",
    "geofence_consent_title",
    "geofence_noshow_section_title",
    "location_events_7d",
    "dark_web_flow_title",
    "dark_web_flow_steps",
    "crash_alert_im_ok",
    "crash_consent_title",
    "crash_consent_required",
    "elderly_scam_call_step1",
    "elderly_scam_call_step2",
    "elderly_scam_call_step3",
    "share_onboard_path_share",
    "share_onboard_path_widget",
    "share_onboard_path_siri",
    "browse_safari_how_to_enable",
    "password_honest_scope_title",
    "password_honest_scope_body",
    "antivirus_file_result_clean",
    "antivirus_file_result_threats_fmt",
    "antivirus_file_hub_hint",
    "antivirus_file_hub_cta",
    "sos_alarm_family_cta",
    "sos_alarm_push_title",
    "battery_critical_push_title",
    "battery_critical_push_body",
    "pay_tiers_plain_title",
    "pay_tiers_plain_body",
    "day_strip_on_view_badge",
    "young_defender_lesson_8_title",
    "young_defender_lesson_9_title",
    "young_defender_lesson_10_title",
]

# User-visible string literals must not advertise abbreviations (plain language canon).
# Comments/MARK are OK; we only flag `"…"` / Text("…") style occurrences of these tokens.
FORBIDDEN_UI_LITERALS = ["HIBP", "SHA-1", "Pwned"]


def split_ru_en(text: str) -> tuple[str, str]:
    # Heuristic: EN block starts at first English lesson-7 title.
    marker = '"young_defender_lesson_7_title": "A face'
    idx = text.find(marker)
    if idx < 0:
        # fallback: second big dict after english comment
        idx = text.find("\n        .english:")
        if idx < 0:
            idx = text.find("Language.english")
    if idx < 0:
        return text, ""
    return text[:idx], text[idx:]


def keys_in(block: str) -> set[str]:
    return set(re.findall(r'"([a-zA-Z0-9_.]+)"\s*:', block))


def main() -> int:
    errors: list[str] = []
    ok: list[str] = []

    for label, path in REQUIRED_FILES.items():
        if path.is_file():
            ok.append(f"file {label}")
        else:
            errors.append(f"MISSING FILE {label}: {path}")

    for tid, rel, needle in CODE_MARKERS:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"{tid}: missing {rel}")
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        if needle in body:
            ok.append(f"marker {tid}")
        else:
            errors.append(f"{tid}: missing `{needle}` in {rel}")

    # darkweb-01: no passport/snils fields in form UI
    dark = (ROOT / "Shared/Components/Modals/DarkWebDataInputView.swift").read_text(
        encoding="utf-8", errors="replace"
    )
    if "dark_web_scan_data_passport" in dark or "$passport" in dark or "$snils" in dark:
        errors.append("darkweb-01: passport/SNILS still in DarkWebDataInputView UI")
    else:
        ok.append("darkweb-01 no PII fields")

    loc = LOC.read_text(encoding="utf-8")
    ru, en = split_ru_en(loc)
    ru_keys, en_keys = keys_in(ru), keys_in(en)
    for key in REQUIRED_KEYS:
        in_ru = key in ru_keys
        in_en = key in en_keys
        if in_ru and in_en:
            ok.append(f"i18n {key}")
        else:
            errors.append(f"i18n {key}: RU={in_ru} EN={in_en}")

    hub = (ROOT / "Screens/PrivacyHubScreen.swift").read_text(encoding="utf-8", errors="replace")
    for snippet in FORBIDDEN_UI_LITERALS:
        # strip // comments then look for quoted snippets
        stripped = "\n".join(
            line.split("//", 1)[0] for line in hub.splitlines()
        )
        if f'"{snippet}' in stripped or f"'{snippet}" in stripped or snippet in re.findall(
            r'Text\("[^"]*"\)', stripped
        ):
            # simpler: any quoted string containing the token
            if any(snippet in s for s in re.findall(r'"([^"]*)"', stripped)):
                errors.append(f"forbidden UI literal `{snippet}` in PrivacyHubScreen.swift")

    print("=== verify_lift_wave_f ===")
    print(f"OK: {len(ok)}  FAIL: {len(errors)}")
    for e in errors:
        print("FAIL:", e)
    if errors:
        return 1
    print("PASS — Wave F code markers + RU/EN keys")
    return 0


if __name__ == "__main__":
    sys.exit(main())
