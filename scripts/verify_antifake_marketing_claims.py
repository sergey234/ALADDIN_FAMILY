#!/usr/bin/env python3
"""G-01 — static gate: no dishonest antifake marketing claims.

Scans app strings, landing, and marketing docs for banned phrases
(real-time all calls, background listening, etc.).
Exit 0 = pass · 1 = violations found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

SCAN_PATHS = [
    "Core/Localization/LocalizationManager.swift",
    "landing/index.html",
    "landing/help-faq.html",
    "docs/marketing",
]

SKIP_SUBSTRINGS = (
    "verify_antifake_marketing_claims.py",
    "ANTIFAKE_APPLE_LIMITS_AND_CLAIMS",
    "ANTIFAKE_CALLS_PRODUCT_SCOPE",
    "ANTIFAKE_VS_TRUECALLER",
    "не перехватывает",
    "does not intercept",
    "не слушает",
    "does not listen",
    "NOT collect contacts",
    "не собираем контакты",
    "no contact harvest",
)

BANNED: List[Tuple[str, re.Pattern[str]]] = [
    ("ai_fake_calls_ru", re.compile(r"AI\s+распознаёт\s+фейковые\s+звонки", re.I)),
    ("ai_fake_calls_en", re.compile(r"AI\s+(recognizes|detects)\s+fake\s+calls", re.I)),
    ("listens_all_calls_ru", re.compile(r"слушает\s+(все|ваши)\s+.*звонк", re.I)),
    ("listens_all_calls_en", re.compile(r"listens\s+to\s+(all|your)\s+.*calls", re.I)),
    ("realtime_fake_calls", re.compile(r"real[- ]?time.*fake.*call", re.I)),
    ("realtime_calls_ru", re.compile(r"в\s+реальном\s+времени.*фейков.*звонк", re.I)),
    ("protect_all_calls_en", re.compile(r"protect(ion)?\s+from\s+all\s+(phone\s+)?calls", re.I)),
    ("protect_all_calls_ru", re.compile(r"защита\s+от\s+всех\s+звонков", re.I)),
    ("intercepts_incoming", re.compile(r"intercepts?\s+incoming\s+calls", re.I)),
    ("intercepts_incoming_ru", re.compile(r"перехватывает\s+входящие\s+звонки", re.I)),
]


def _iter_files() -> Iterable[Path]:
    for rel in SCAN_PATHS:
        path = ROOT / rel
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix in {".md", ".html", ".swift", ".json"}:
                    yield child


def _line_allowed(line: str) -> bool:
    return any(s in line for s in SKIP_SUBSTRINGS)


def scan() -> List[dict]:
    hits: List[dict] = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(ROOT))
        for i, line in enumerate(text.splitlines(), 1):
            if _line_allowed(line):
                continue
            for rule_id, pattern in BANNED:
                if pattern.search(line):
                    hits.append(
                        {
                            "rule": rule_id,
                            "file": rel,
                            "line": i,
                            "excerpt": line.strip()[:160],
                        }
                    )
    return hits


def main() -> int:
    hits = scan()
    if hits:
        print("FAIL banned marketing claims:")
        for h in hits:
            print(f"  [{h['rule']}] {h['file']}:{h['line']}: {h['excerpt']}")
        print(json.dumps({"pass": False, "violations": hits}, ensure_ascii=False, indent=2))
        return 1
    print("OK  no banned antifake marketing claims (G-01)")
    print(json.dumps({"pass": True, "gate": "antifake_g01_marketing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
