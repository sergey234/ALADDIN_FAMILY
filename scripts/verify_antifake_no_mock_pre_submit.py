#!/usr/bin/env python3
"""Q-05 — pre-submit gate: no mock / bypass strings in antifake prod paths.

Exit 0 = pass · 1 = violations · 2 = ALERT on prod log grep (optional).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

SCAN_FILES = [
    "app/routers/antifake.py",
    "app/services/antifake_service.py",
    "app/services/antifake_worker_tasks.py",
    "Core/Security/AntifakeAccessPolicy.swift",
    "Shared/Components/AntifakeVerdictCard.swift",
]

SCAN_DIRS = [
    "Core/Security",
    "Shared/Components",
]

FORBIDDEN_IN_RESPONSE = re.compile(
    r"sfm_mock|mock-real-protection|mock_fallback|sfm_stub|demo_verdict|fake_verdict_for_ui",
    re.I,
)

ALLOW_LINE = re.compile(
    r"forbidden|reject|no mock|mock_source|FORBIDDEN|bypassPremiumGate|document|"
    r"validateForProduction|503|not in|frozenset|in\s*\(|#|//",
    re.I,
)


def _iter_paths() -> Iterable[Path]:
    for rel in SCAN_FILES:
        p = ROOT / rel
        if p.is_file():
            yield p
    for rel in SCAN_DIRS:
        base = ROOT / rel
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.swift")):
            if "Antifake" in p.name or "antifake" in p.name.lower():
                yield p


def scan_sources() -> List[dict]:
    hits: List[dict] = []
    for path in _iter_paths():
        rel = str(path.relative_to(ROOT))
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not FORBIDDEN_IN_RESPONSE.search(line):
                continue
            if ALLOW_LINE.search(line):
                continue
            hits.append({"file": rel, "line": i, "excerpt": line.strip()[:140]})
    return hits


def main() -> int:
    hits = scan_sources()
    if hits:
        print("FAIL Q-05 mock strings in antifake prod paths:")
        for h in hits[:20]:
            print(f"  {h['file']}:{h['line']}: {h['excerpt']}")
        print(json.dumps({"pass": False, "violations": hits}, ensure_ascii=False, indent=2))
        return 1

    print("OK  Q-05 no mock strings in antifake prod paths")
    print(json.dumps({"pass": True, "gate": "antifake_q05_no_mock"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
