#!/usr/bin/env python3
"""
W5-2: each `AppSoundEffect` case must have `Resources/Audio/<case>.mp3` (app bundle + CI).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOUND_PLAYER = REPO / "Core" / "Audio" / "SoundEffectPlayer.swift"
AUDIO_DIR = REPO / "Resources" / "Audio"


def main() -> int:
    if not SOUND_PLAYER.is_file():
        print(f"ERROR: {SOUND_PLAYER} not found", file=sys.stderr)
        return 1
    text = SOUND_PLAYER.read_text(encoding="utf-8")
    m = re.search(
        r"enum\s+AppSoundEffect:\s*String,?\s*CaseIterable\s*\{([^}]+)\}",
        text,
        re.DOTALL,
    )
    if not m:
        print("ERROR: could not find enum AppSoundEffect in SoundEffectPlayer.swift", file=sys.stderr)
        return 1
    body = m.group(1)
    cases = re.findall(r"case\s+(\w+)", body)
    if not cases:
        print("ERROR: no `case` entries in AppSoundEffect", file=sys.stderr)
        return 1
    missing: list[str] = []
    for c in cases:
        p = AUDIO_DIR / f"{c}.mp3"
        if not p.is_file():
            missing.append(p.relative_to(REPO).as_posix())
    if missing:
        print("ERROR: missing mp3 for AppSoundEffect case(s):", file=sys.stderr)
        for p in missing:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(
        f"OK: {len(cases)} AppSoundEffect case(s) → {AUDIO_DIR.relative_to(REPO)}/<name>.mp3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
