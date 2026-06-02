#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wellness l10n gate (p18-12).

Checks:
  - wellness_* keys parity ru/en in LocalizationManager.swift
  - wellness_i18n JSON files have non-empty ru+en where bilingual blocks exist
  - forbidden UI terms (§19 glossary) not in wellness iOS strings
  - age_variants_v1.json keys have matching _child/_teen iOS suffixes (p18-14)

Usage:
  python3 scripts/check_wellness_l10n.py
  python3 scripts/check_wellness_l10n.py --strict   # fail on glossary hits
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SWIFT = ROOT / "Core/Localization/LocalizationManager.swift"
I18N_ROOT = ROOT / "security/services/ai_platform/wellness_i18n"

FORBIDDEN_IN_WELLNESS_UI = (
    "psychotherapist",
    "психотерап",
    "диагноз",
    " diagnose",
    " cure ",
    " лечит",
    "emdr",
)

BILINGUAL_KEY_MARKERS = frozenset({"ru", "en"})


def _extract_wellness_keys(section: str) -> set[str]:
    return set(re.findall(r'"(wellness_[^"]+)":', section))


def _split_ru_en_sections(text: str) -> tuple[str, str]:
    ru_start = text.find("        .russian: [")
    en_start = text.find("        .english: [")
    if ru_start < 0 or en_start < 0 or en_start <= ru_start:
        raise RuntimeError("Could not locate .russian / .english blocks in LocalizationManager.swift")
    return text[ru_start:en_start], text[en_start:]


def _extract_key_values(section: str, keys: set[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in keys:
        pattern = rf'"{re.escape(key)}":\s*"((?:\\.|[^"\\])*)"'
        m = re.search(pattern, section)
        if m:
            out[key] = m.group(1)
    return out


def check_ios_parity() -> list[str]:
    errors: list[str] = []
    text = SWIFT.read_text(encoding="utf-8")
    ru_sec, en_sec = _split_ru_en_sections(text)
    ru_keys = _extract_wellness_keys(ru_sec)
    en_keys = _extract_wellness_keys(en_sec)

    missing_en = sorted(ru_keys - en_keys)
    missing_ru = sorted(en_keys - ru_keys)
    if missing_en:
        errors.append(f"iOS: {len(missing_en)} wellness keys missing in EN: {', '.join(missing_en[:8])}"
                      + (" …" if len(missing_en) > 8 else ""))
    if missing_ru:
        errors.append(f"iOS: {len(missing_ru)} wellness keys missing in RU: {', '.join(missing_ru[:8])}"
                      + (" …" if len(missing_ru) > 8 else ""))

    ru_vals = _extract_key_values(ru_sec, ru_keys & en_keys)
    for key, val in ru_vals.items():
        if not val.strip():
            errors.append(f"iOS: empty RU value for {key}")
    en_vals = _extract_key_values(en_sec, ru_keys & en_keys)
    for key, val in en_vals.items():
        if not val.strip():
            errors.append(f"iOS: empty EN value for {key}")
    return errors


def _is_bilingual_leaf(obj: dict) -> bool:
    return BILINGUAL_KEY_MARKERS.issubset(obj.keys())


def check_json_bilingual(obj: object, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(obj, dict):
        if _is_bilingual_leaf(obj):
            for loc in ("ru", "en"):
                if not str(obj.get(loc) or "").strip():
                    errors.append(f"JSON {path or '<root>'}: empty '{loc}'")
        else:
            for key, val in obj.items():
                child = f"{path}.{key}" if path else str(key)
                errors.extend(check_json_bilingual(val, child))
    elif isinstance(obj, list):
        for idx, val in enumerate(obj):
            errors.extend(check_json_bilingual(val, f"{path}[{idx}]"))
    return errors


def check_backend_json() -> list[str]:
    errors: list[str] = []
    if not I18N_ROOT.is_dir():
        return [f"Missing wellness_i18n dir: {I18N_ROOT}"]
    for path in sorted(I18N_ROOT.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")
            continue
        rel = str(path.relative_to(ROOT))
        errors.extend(f"{rel}: {msg}" for msg in check_json_bilingual(data))
    return errors


def check_age_variants() -> list[str]:
    """p18-14 — base keys + _child/_teen suffix parity vs age_variants_v1.json."""
    errors: list[str] = []
    manifest_path = I18N_ROOT / "age_variants_v1.json"
    if not manifest_path.is_file():
        return [f"Missing {manifest_path.relative_to(ROOT)}"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_keys = manifest.get("keys_with_variants") or []
    text = SWIFT.read_text(encoding="utf-8")
    ru_sec, en_sec = _split_ru_en_sections(text)
    ru_keys = _extract_wellness_keys(ru_sec)
    en_keys = _extract_wellness_keys(en_sec)

    for base in base_keys:
        if base not in ru_keys or base not in en_keys:
            errors.append(f"age variants: missing base key {base} in iOS ru/en")
        for suffix in ("_child", "_teen"):
            variant = f"{base}{suffix}"
            in_ru = variant in ru_keys
            in_en = variant in en_keys
            if in_ru != in_en:
                errors.append(f"age variants: {variant} ru/en mismatch (ru={in_ru}, en={in_en})")
            if in_ru and in_en:
                ru_val = _extract_key_values(ru_sec, {variant}).get(variant, "")
                en_val = _extract_key_values(en_sec, {variant}).get(variant, "")
                if not ru_val.strip() or not en_val.strip():
                    errors.append(f"age variants: empty value for {variant}")
    return errors


def check_glossary(*, strict: bool) -> list[str]:
    if not strict:
        return []
    errors: list[str] = []
    text = SWIFT.read_text(encoding="utf-8")
    ru_sec, en_sec = _split_ru_en_sections(text)
    for section_name, section in (("RU", ru_sec), ("EN", en_sec)):
        for key in _extract_wellness_keys(section):
            m = re.search(rf'"{re.escape(key)}":\s*"((?:\\.|[^"\\])*)"', section)
            if not m:
                continue
            val = m.group(1).lower()
            for bad in FORBIDDEN_IN_WELLNESS_UI:
                if bad.strip() in val:
                    errors.append(f"glossary: {section_name} {key} contains forbidden '{bad.strip()}'")
                    break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Wellness ru/en l10n gate")
    parser.add_argument("--strict", action="store_true", help="Fail on glossary forbidden terms")
    args = parser.parse_args()

    errors: list[str] = []
    errors.extend(check_ios_parity())
    errors.extend(check_backend_json())
    errors.extend(check_age_variants())
    errors.extend(check_glossary(strict=args.strict))

    if errors:
        print("WELLNESS L10N CHECK FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1

    ru_sec, en_sec = _split_ru_en_sections(SWIFT.read_text(encoding="utf-8"))
    ru_n = len(_extract_wellness_keys(ru_sec))
    json_n = len(list(I18N_ROOT.rglob("*.json")))
    print(f"OK: wellness i18n — {ru_n} iOS keys (ru/en parity), {json_n} backend JSON files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
