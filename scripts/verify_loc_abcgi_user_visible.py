#!/usr/bin/env python3
"""Verify LOC A/B/C/G/I checklist phrases are not hardcoded in user-visible UI.

Source: docs/LOCALIZATION_ZONE_VERIFIED_CHECKLIST_2026-09-15.md
Scope: zones A, B, C, G, I — subsections "Нет перевода" + "Ключ есть".
Excludes: DEBUG/A11Y tags, logger/print-only lines, LocalizationManager / WidgetL10n tables.

Exit 0 = PASS (0 user-visible hardcodes), 1 = FAIL.
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs/LOCALIZATION_ZONE_VERIFIED_CHECKLIST_2026-09-15.md"

ALLOW_FILES = {
    "Core/Localization/LocalizationManager.swift",
    "ALADDINWidgets/WidgetL10n.swift",
    "ML_SYSTEM_PACKAGE/LocalizationManager.swift",
}

LOG_MARKERS = (
    "VisualLogger",
    "MasterLogger",
    "print(",
    "logger.",
    "Logger.",
    "NSLog(",
    "os_log",
    "recordDebugLog",
)

ITEM_RE = re.compile(
    r"^- \[.\] `([^`]+):(\d+)` «([^»]+)» `(NO_KEY|UNUSED_KEY|WIRE[^`]*)`",
    re.M,
)


def parse_checklist() -> dict[str, list[tuple[str, int, str, str]]]:
    text = CHECKLIST.read_text(encoding="utf-8")
    zones: dict[str, list[tuple[str, int, str, str]]] = {z: [] for z in "ABCGI"}
    current = None
    subsection = None
    for line in text.splitlines():
        if line.startswith("## A "):
            current, subsection = "A", None
        elif line.startswith("## B "):
            current, subsection = "B", None
        elif line.startswith("## C "):
            current, subsection = "C", None
        elif line.startswith("## G "):
            current, subsection = "G", None
        elif line.startswith("## I "):
            current, subsection = "I", None
        elif line.startswith("## "):
            current, subsection = None, None
            continue
        if current is None:
            continue
        if line.startswith("### "):
            low = line.lower()
            if "ключ есть" in low or "подключить" in low:
                subsection = "wire"
            elif "нет перевода" in low or "чинить" in low:
                subsection = "fix"
            elif "не экран" in low or "debug" in low or "a11y" in low or "ignore" in low:
                subsection = "ignore"
            continue
        if subsection not in ("fix", "wire"):
            continue
        if "tags=A11Y" in line or "tags=DEBUG" in line or "tags=LOG" in line:
            continue
        m = ITEM_RE.match(line)
        if not m:
            continue
        path, line_no, phrase, kind = m.groups()
        zones[current].append((path, int(line_no), phrase, kind))
    return zones


def is_log_only_line(line: str) -> bool:
    return any(m in line for m in LOG_MARKERS)


def is_dict_entry(line: str, phrase: str) -> bool:
    return bool(re.search(r'"[^"]+"\s*:\s*"' + re.escape(phrase) + r'"', line))


def is_localized_call(line: str) -> bool:
    return bool(
        re.search(
            r"(localizationManager|LocalizationManager\.shared|WidgetL10n)\.localized\(",
            line,
        )
    )


def find_ui_hardcodes(path: Path, phrase: str) -> list[tuple[int, str]]:
    if path.as_posix() in ALLOW_FILES:
        return []
    if not path.exists():
        return [(0, "MISSING_FILE")]
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if phrase not in line:
            continue
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if is_dict_entry(line, phrase):
            continue
        if f'"{phrase}"' not in line and f"'{phrase}'" not in line:
            continue
        if is_log_only_line(line):
            continue
        if is_localized_call(line):
            # Fail only if RU phrase is the localization *key* argument.
            if re.search(r'localized\(\s*"' + re.escape(phrase) + r'"\s*\)', line):
                hits.append((i, line.strip()[:180]))
            continue
        # Comparison against RU sentinel still counts (should use neutral token).
        hits.append((i, line.strip()[:180]))
    return hits


def main() -> int:
    zones = parse_checklist()
    failures: list[tuple[str, str, str, list[tuple[int, str]]]] = []
    skipped_log_only = 0
    seen: set[tuple[str, str, str]] = set()
    by_zone = Counter()

    for zone, items in zones.items():
        for path, _line_no, phrase, _kind in items:
            key = (zone, phrase, path)
            if key in seen:
                continue
            seen.add(key)
            p = ROOT / path
            # If the only remaining occurrences are logs, count as skip not fail.
            if p.exists():
                raw_lines = [
                    ln
                    for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines()
                    if f'"{phrase}"' in ln or f"'{phrase}'" in ln
                ]
                if raw_lines and all(
                    is_log_only_line(ln) or is_dict_entry(ln, phrase) or ln.lstrip().startswith("//")
                    for ln in raw_lines
                ):
                    skipped_log_only += 1
                    continue
            hits = find_ui_hardcodes(p, phrase)
            if hits:
                by_zone[zone] += 1
                failures.append((zone, phrase, path, hits[:3]))

    print("LOC-verify A/B/C/G/I (user-visible)")
    print("items_scanned:", len(seen))
    print("skipped_log_only_phrases:", skipped_log_only)
    print("fail_by_zone:", {z: by_zone[z] for z in "ABCGI"})
    print("fail_total:", len(failures))
    for zone, phrase, path, hits in failures:
        print(f"\n[{zone}] «{phrase}» @ {path}")
        for ln, ht in hits:
            print(f"  L{ln}: {ht}")

    ok = not failures
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
