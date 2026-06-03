#!/usr/bin/env python3
# hero-x-14 — scan vedic YAML for forbidden religion words in user-facing paraphrases.
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEDIC_DIR = ROOT / "security/services/ai_platform/companion_knowledge/vedic/v1"


def main() -> int:
    import yaml

    wisdom = yaml.safe_load((VEDIC_DIR / "wisdom.yaml").read_text(encoding="utf-8")) or {}
    forbidden = [str(w).lower() for w in (wisdom.get("forbidden_user_words") or [])]
    errors: list[str] = []
    for path in sorted(VEDIC_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for snip in data.get("snippets") or []:
            sid = snip.get("id") or "?"
            for field in ("ru_paraphrase", "en_paraphrase"):
                text = (snip.get(field) or "").lower()
                for word in forbidden:
                    if word and re.search(rf"\b{re.escape(word)}\b", text):
                        errors.append(f"{path.name}:{sid}:{field} contains '{word}'")
    if errors:
        print("FAIL vedic secular gate:")
        for e in errors:
            print(" ", e)
        return 1
    count = sum(len((yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("snippets") or []) for p in VEDIC_DIR.glob("*.yaml"))
    print(f"OK vedic secular gate — {count} snippets, {len(forbidden)} forbidden words enforced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
