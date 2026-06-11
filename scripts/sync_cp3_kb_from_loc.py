#!/usr/bin/env python3
"""Sync CP3 FAQ kb JSON + onboarding kb from LocalizationManager.swift SSOT."""
from __future__ import annotations

import json
import re
from pathlib import Path

IOS = Path(__file__).resolve().parents[1]
LM_PATH = IOS / "Core/Localization/LocalizationManager.swift"
KB_DIR = IOS / "docs/kb/kb_v1/documents"

FAQ_IDS = [
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
    "faq_how_network_protection_works",
    "faq_crash_detection",
    "faq_roadside_assistance",
    "faq_emergency_sos",
    "faq_dark_web_leaks",
    "faq_parental_bypass",
    "faq_geofencing",
    "faq_wellness_support",
]

KEYWORDS: dict[str, list[str]] = {
    "faq_aes256": ["aes", "шифрование", "военное"],
    "faq_malicious_apps": ["вредоносные приложения", "malware app"],
    "faq_sms_scam": ["sms", "смс", "smishing"],
    "faq_location_threats": ["геолокация", "местоположение"],
    "faq_how_network_protection_works": ["защита сети", "vpn", "туннель"],
    "faq_crash_detection": ["авария", "дтп", "crash"],
    "faq_roadside_assistance": ["дорога", "поломка", "roadside"],
    "faq_emergency_sos": ["sos", "экстренно", "60+"],
    "faq_dark_web_leaks": ["темная сеть", "dark web", "утечка"],
    "faq_anonymity": ["анонимность", "приватность"],
    "faq_parental_bypass": ["обход", "bypass", "инкогнито", "tor"],
    "faq_geofencing": ["геозона", "геозоны", "geofence", "местоположение"],
    "faq_wellness_support": ["wellness", "настроение", "эмоциональная поддержка", "самопомощь"],
}


def slice_lang_block(text: str, marker: str, next_marker: str | None) -> str:
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
    return text[start:end]


def parse_loc_blocks(text: str) -> tuple[dict[str, str], dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for marker, nxt in ((".russian", ".english"), (".english", ".chinese")):
        chunk = slice_lang_block(text, marker, nxt)
        d: dict[str, str] = {}
        for km in re.finditer(r'"([^"]+)":\s*"((?:\\.|[^"\\])*)"', chunk):
            d[km.group(1)] = bytes(km.group(2), "utf-8").decode("unicode_escape")
        out[marker] = d
    return out[".russian"], out[".english"]


def faq_json(faq_id: str, locale: str, ru: dict[str, str], en: dict[str, str]) -> dict:
    loc = ru if locale == "ru" else en
    q = loc[f"{faq_id}"]
    a = loc[f"{faq_id}_answer"]
    body = f"{q}\n\n{a}"
    doc_id = f"{faq_id}_{locale}"
    kw = KEYWORDS.get(faq_id, [faq_id.replace("faq_", "").replace("_", " ")])
    return {
        "id": doc_id,
        "locale": locale,
        "topic": "security_faq",
        "title": q,
        "body": body,
        "source": "UnifiedFAQCatalog",
        "keywords": kw,
        "kb_version": "kb_v1",
    }


def sync_onboarding(ru: dict[str, str], en: dict[str, str]) -> None:
    for locale, loc in ("ru", ru), ("en", en):
        lines = []
        for i in range(1, 8):
            for suffix in ("title", "desc"):
                key = f"onboarding_page{i}_{suffix}"
                lines.append(f"### {key}\n{loc[key]}")
        body = "\n\n".join(lines) + "\n"
        path = KB_DIR / f"onboarding_page_onboarding_{locale}.json"
        data = {
            "id": f"onboarding_page_onboarding_{locale}",
            "locale": locale,
            "topic": "onboarding",
            "title": "onboarding_page",
            "body": body,
            "source": "LocalizationManager",
            "keywords": ["onboarding"],
            "kb_version": "kb_v1",
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated {path.name}")


def main() -> None:
    text = LM_PATH.read_text(encoding="utf-8")
    ru, en = parse_loc_blocks(text)
    for faq_id in FAQ_IDS:
        for locale in ("ru", "en"):
            path = KB_DIR / f"{faq_id}_{locale}.json"
            data = faq_json(faq_id, locale, ru, en)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"updated {path.name}")
    sync_onboarding(ru, en)
    print("done")


if __name__ == "__main__":
    main()
