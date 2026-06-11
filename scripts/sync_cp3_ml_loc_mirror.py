#!/usr/bin/env python3
"""Mirror CP3 localization keys from main LocalizationManager to ML_SYSTEM_PACKAGE."""
from __future__ import annotations

import re
from pathlib import Path

IOS = Path(__file__).resolve().parents[1]
SRC = IOS / "Core/Localization/LocalizationManager.swift"
DST = IOS / "ML_SYSTEM_PACKAGE/LocalizationManager.swift"

# Keys touched by COPY-POST-L3 (onboarding, tariffs sample, all CP3 FAQ, privacy servers)
KEY_PREFIXES = (
    "onboarding_page",
    "tariffs_ai_protection",
    "tariffs_recommendation_premium",
    "protection_catalog",
    "protection_scenarios",
    "tariff_protection",
    "faq_what_protects",
    "faq_protect_elderly",
    "faq_data_safe",
    "faq_viruses_trojans",
    "faq_spyware",
    "faq_phone_scam",
    "faq_deepfake",
    "faq_fake_voices",
    "faq_fake_news",
    "faq_mitm_attacks",
    "faq_aes256",
    "faq_anonymity",
    "faq_malicious_apps",
    "faq_sms_scam",
    "faq_location_threats",
    "faq_how_network_protection",
    "faq_crash_detection",
    "faq_roadside_assistance",
    "faq_emergency_sos",
    "faq_dark_web_leaks",
    "privacy_policy_section_responsibility",
    "privacy_policy_section_principles_content_2",
    "privacy_policy_network_protection_encryption_content_",
    "privacy_policy_vpn_encryption_content_",
    "privacy_policy_network_protection_servers",
    "privacy_policy_vpn_servers",
    "terms_section_description_content_2",
)


def slice_lang_block(text: str, marker: str, next_marker: str | None) -> tuple[int, int, dict[str, str]]:
    anchor = text.find("var translations:")
    if anchor < 0:
        raise RuntimeError("var translations not found")
    m = re.search(rf"{re.escape(marker)}:\s*\[", text[anchor:])
    if not m:
        raise RuntimeError(f"marker not found: {marker}")
    start = anchor + m.end()
    if next_marker:
        n = re.search(rf"{re.escape(next_marker)}:\s*\[", text[start:])
        end = start + n.start() if n else len(text)
    else:
        end = len(text)
    chunk = text[start:end]
    entries: dict[str, str] = {}
    for km in re.finditer(r'"([^"]+)":\s*"((?:\\.|[^"\\])*)"', chunk):
        entries[km.group(1)] = km.group(2)
    return start, end, entries


def should_sync(key: str) -> bool:
    return any(key == p or key.startswith(p) for p in KEY_PREFIXES)


def patch_block(text: str, marker: str, next_marker: str | None, src_entries: dict[str, str]) -> tuple[str, int]:
    start, end, dst_entries = slice_lang_block(text, marker, next_marker)
    chunk = text[start:end]
    updated = 0
    for key, src_val in src_entries.items():
        if not should_sync(key):
            continue
        if key not in dst_entries or dst_entries[key] == src_val:
            continue
        old = f'"{key}": "{dst_entries[key]}"'
        new = f'"{key}": "{src_val}"'
        if old in chunk:
            chunk = chunk.replace(old, new, 1)
            updated += 1
    return text[:start] + chunk + text[end:], updated


def main() -> None:
    src_text = SRC.read_text(encoding="utf-8")
    dst_text = DST.read_text(encoding="utf-8")
    _, _, src_ru = slice_lang_block(src_text, ".russian", ".english")
    _, _, src_en = slice_lang_block(src_text, ".english", ".chinese")
    src_all = {**src_ru, **src_en}
    total = 0
    dst_text, n = patch_block(dst_text, ".russian", ".english", src_all)
    total += n
    dst_text, n = patch_block(dst_text, ".english", ".chinese", src_all)
    total += n
    DST.write_text(dst_text, encoding="utf-8")
    print(f"mirrored {total} keys into ML_SYSTEM_PACKAGE/LocalizationManager.swift")


if __name__ == "__main__":
    main()
