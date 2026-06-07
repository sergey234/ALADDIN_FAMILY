#!/usr/bin/env python3
"""HERO-3-07 — verify 12 unique emotion PNGs per hero (02b v2 gate before Rive)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_ROOT = REPO / "Resources" / "Companion" / "figma_exports"
EMOTIONS = (
    "idle", "listening", "thinking", "happy", "playful", "sad",
    "comfort", "celebrate", "curious", "nostalgic", "excited", "alert",
)
HEROES = ("unicorn", "aladdin", "genie")
MIN_UNIQUE = 12  # production target; v1.1 often = 1


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not OUT_ROOT.is_dir():
        print(f"ERROR: run companion_07_export_figma_emotions.py first\n  missing: {OUT_ROOT}")
        return 2

    failed = False
    for hero in HEROES:
        hero_dir = OUT_ROOT / hero
        hashes: dict[str, str] = {}
        missing = []
        for emo in EMOTIONS:
            p = hero_dir / f"{emo}.png"
            if not p.is_file():
                missing.append(emo)
                continue
            hashes[emo] = sha256(p)
        unique = len(set(hashes.values()))
        print(f"\n=== {hero} ===")
        print(f"  files: {len(hashes)}/12  unique SHA256: {unique}")
        if missing:
            print(f"  missing: {missing}")
            failed = True
        if unique < MIN_UNIQUE:
            print(f"  FAIL: need {MIN_UNIQUE} unique faces for production Rive (got {unique})")
            print("  → Figma 02b v2: draw 12 different faces per COMPANION_HEROES §2.3")
            print("  → OR Rive Editor: rig brow/eye/mouth layers (approved 07 path)")
            failed = True
        else:
            print("  PASS: ready for Rive 12-state import")
        # show duplicate groups
        by_hash: dict[str, list[str]] = {}
        for emo, h in hashes.items():
            by_hash.setdefault(h, []).append(emo)
        dups = {h: e for h, e in by_hash.items() if len(e) > 1}
        if dups:
            print("  duplicate groups (same image):")
            for emos in dups.values():
                print(f"    {', '.join(emos)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
