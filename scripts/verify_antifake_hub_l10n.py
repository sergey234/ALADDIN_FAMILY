#!/usr/bin/env python3
"""afhub-p3-02 — Antifake Hub RU/EN l10n audit.

Checks:
  1) Every antifake_* key in RU exists in EN (and vice versa)
  2) EN antifake_* values contain no Cyrillic
  3) localized("…") keys used by Antifake Swift surfaces exist in both dicts
     (accessibilityIdentifier strings are ignored)

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
LM_PATH = ROOT / "Core" / "Localization" / "LocalizationManager.swift"
CYR = re.compile(r"[А-Яа-яЁё]")
KEY_PAIR = re.compile(r'"([a-z0-9_]+)"\s*:\s*"((?:\\.|[^"\\])*)"')
LOCALIZED_CALL = re.compile(r'localized\(\s*"([a-z0-9_]+)"')
A11Y_ID = re.compile(r'accessibilityIdentifier\(\s*"([a-z0-9_]+)"')


def _load_lang_dicts(text: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    ru_m = re.search(r"\n        \.russian:\s*\[", text)
    en_m = re.search(r"\n        \.english:\s*\[", text)
    if not ru_m or not en_m:
        raise RuntimeError("Cannot find .russian / .english translation blocks")
    ru = dict(KEY_PAIR.findall(text[ru_m.end() : en_m.start()]))
    rest = text[en_m.end() :]
    close = re.search(r"\n        \]\s*\n    \]", rest)
    if not close:
        close = re.search(r"\n        \]", rest)
    if not close:
        raise RuntimeError("Cannot find end of .english block")
    en = dict(KEY_PAIR.findall(text[en_m.end() : en_m.end() + close.start()]))
    return ru, en


def _antifake_swift_files() -> List[Path]:
    files: List[Path] = []
    for base in (
        ROOT / "Screens",
        ROOT / "Shared" / "Components",
        ROOT / "ViewModels",
        ROOT / "Core" / "Models",
        ROOT / "Core" / "Security",
        ROOT / "Core" / "Family",
        ROOT / "Shared" / "AntifakeCallDirectory",
        ROOT / "Shared" / "AntifakeShare",
    ):
        if not base.exists():
            continue
        if base.is_file():
            files.append(base)
            continue
        files.extend(base.rglob("Antifake*.swift"))
    hub = ROOT / "Screens" / "AntifakeHubScreen.swift"
    if hub.is_file() and hub not in files:
        files.append(hub)
    return sorted({p.resolve() for p in files})


def _used_localized_keys(files: List[Path]) -> Set[str]:
    used: Set[str] = set()
    for path in files:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        used.update(LOCALIZED_CALL.findall(raw))
    return used


def audit() -> Dict[str, object]:
    text = LM_PATH.read_text(encoding="utf-8")
    ru, en = _load_lang_dicts(text)
    ru_af = {k: v for k, v in ru.items() if k.startswith("antifake_")}
    en_af = {k: v for k, v in en.items() if k.startswith("antifake_")}

    missing_en = sorted(set(ru_af) - set(en_af))
    missing_ru = sorted(set(en_af) - set(ru_af))
    en_cyr = sorted(k for k, v in en_af.items() if CYR.search(v))

    files = _antifake_swift_files()
    used = _used_localized_keys(files)
    # Hub-related extras
    related = {
        "protection_upgrade_tariff",
        "support_ask_assistant",
        "support_ask_assistant_antifake_subtitle",
        "companion_conversation_done",
        "common_cancel",
    }
    check_used = {k for k in used if k.startswith("antifake_") or k in related}
    used_missing_en = sorted(k for k in check_used if k not in en)
    used_missing_ru = sorted(k for k in check_used if k not in ru)

    hard_ru: List[str] = []
    for path in files:
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if 'Text("' not in line:
                continue
            if CYR.search(line) and not line.strip().startswith("//"):
                hard_ru.append(f"{path.relative_to(ROOT)}:{i}")

    ok = not (
        missing_en
        or missing_ru
        or en_cyr
        or used_missing_en
        or used_missing_ru
        or hard_ru
    )
    return {
        "ok": ok,
        "ru_antifake_keys": len(ru_af),
        "en_antifake_keys": len(en_af),
        "missing_en": missing_en,
        "missing_ru": missing_ru,
        "en_with_cyrillic": en_cyr,
        "used_keys_checked": len(check_used),
        "used_missing_en": used_missing_en,
        "used_missing_ru": used_missing_ru,
        "hardcoded_text_cyrillic": hard_ru,
        "swift_files": len(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Antifake Hub RU/EN l10n audit")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        import json

        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"antifake keys RU={report['ru_antifake_keys']} EN={report['en_antifake_keys']} "
            f"swift_files={report['swift_files']} used={report['used_keys_checked']}"
        )
        for label in (
            "missing_en",
            "missing_ru",
            "en_with_cyrillic",
            "used_missing_en",
            "used_missing_ru",
            "hardcoded_text_cyrillic",
        ):
            rows = report[label]
            if rows:
                print(f"FAIL {label}: {len(rows)}")
                for row in rows[:40]:
                    print(f"  - {row}")
        print("PASS" if report["ok"] else "FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
