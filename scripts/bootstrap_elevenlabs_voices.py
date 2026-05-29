#!/usr/bin/env python3
"""
VOICE-PREM-04: подбор 3 voice id + запись secrets/elevenlabs.local.env

Источники API key (по порядку):
  1) ELEVENLABS_API_KEY в окружении
  2) secrets/elevenlabs.api_key (одна строка, gitignore)
  3) secrets/elevenlabs.local.env

Voice id:
  - GET /v1/voices + эвристики по героям
  - fallback: secrets/elevenlabs.recommended-voices.env

Usage:
  python3 scripts/bootstrap_elevenlabs_voices.py [--write-only]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "secrets"
LOCAL_ENV = SECRETS / "elevenlabs.local.env"
API_KEY_FILE = SECRETS / "elevenlabs.api_key"
RECOMMENDED = SECRETS / "elevenlabs.recommended-voices.env"

HEROES = ("unicorn", "genie", "aladdin")

# Premade ids + name hints for matching account library
CURATED: Dict[str, Dict] = {
    "unicorn": {
        "ids": ["EXAVITQu4vr4xnSDxMaL", "21m00Tcm4TlvDq8ikWAM", "XB0fDUnXU5powFXDhCwa"],
        "names": ["sarah", "rachel", "charlotte", "bella", "elli"],
        "labels": ["soft", "warm", "female", "gentle"],
    },
    "genie": {
        "ids": ["ErXwobaYiN019PkySvjV", "pNInz6obpgDQGcFmaJgB", "VR6AewLTigWG4xSOukaG"],
        "names": ["antoni", "adam", "josh", "sam"],
        "labels": ["energetic", "playful", "dynamic"],
    },
    "aladdin": {
        "ids": ["onwK4e9ZLuTAKqWW03F9", "JBFqnCBsd6RMkjVDRZzb", "pFZP5JQG7iQjIQuC4Bku"],
        "names": ["daniel", "george", "callum", "clyde"],
        "labels": ["calm", "narrative", "mentor", "authoritative"],
    },
}


def load_dotenv(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def resolve_api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    if API_KEY_FILE.exists():
        key = API_KEY_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        if key:
            return key
    key = load_dotenv(LOCAL_ENV).get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    print(
        "Missing ELEVENLABS_API_KEY.\n"
        "  echo 'sk_...' > secrets/elevenlabs.api_key && chmod 600 secrets/elevenlabs.api_key\n"
        "  or export ELEVENLABS_API_KEY=sk_...",
        file=sys.stderr,
    )
    sys.exit(1)


def fetch_voices(api_key: str) -> List[dict]:
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return list(data.get("voices") or [])


def _score_voice(voice: dict, hero: str) -> float:
    cfg = CURATED[hero]
    vid = str(voice.get("voice_id") or "")
    name = str(voice.get("name") or "").lower()
    labels = " ".join(voice.get("labels") or []).lower()
    desc = str(voice.get("description") or "").lower()
    blob = f"{name} {labels} {desc}"
    score = 0.0
    if vid in cfg["ids"]:
        score += 100.0 - float(cfg["ids"].index(vid))
    for i, hint in enumerate(cfg["names"]):
        if hint in blob:
            score += 20.0 - i
    for i, hint in enumerate(cfg["labels"]):
        if hint in blob:
            score += 8.0 - i * 0.5
    return score


def pick_voices(voices: List[dict]) -> Dict[str, str]:
    by_id = {str(v.get("voice_id")): v for v in voices if v.get("voice_id")}
    chosen: Dict[str, str] = {}
    used: set[str] = set()

    for hero in HEROES:
        best_id = ""
        best_score = -1.0
        for cfg_id in CURATED[hero]["ids"]:
            if cfg_id in by_id and cfg_id not in used:
                sc = _score_voice(by_id[cfg_id], hero) + 50.0
                if sc > best_score:
                    best_score = sc
                    best_id = cfg_id
        for voice in voices:
            vid = str(voice.get("voice_id") or "")
            if not vid or vid in used:
                continue
            sc = _score_voice(voice, hero)
            if sc > best_score:
                best_score = sc
                best_id = vid
        if not best_id:
            rec = load_dotenv(RECOMMENDED)
            best_id = rec.get(f"ELEVENLABS_VOICE_{hero.upper()}", "")
        if not best_id:
            raise SystemExit(f"Could not pick voice for {hero}")
        chosen[hero] = best_id
        used.add(best_id)
    return chosen


def probe_tts(api_key: str, voice_id: str, text: str) -> None:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = json.dumps({"text": text, "model_id": "eleven_flash_v2_5"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        audio = resp.read()
    if len(audio) < 32:
        raise RuntimeError("empty audio from ElevenLabs")


def write_local_env(api_key: str, voices: Dict[str, str], model: str) -> None:
    SECRETS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Generated by scripts/bootstrap_elevenlabs_voices.py — VOICE-PREM-04",
        f"ELEVENLABS_API_KEY={api_key}",
        f"ELEVENLABS_MODEL={model}",
        f"ELEVENLABS_VOICE_UNICORN={voices['unicorn']}",
        f"ELEVENLABS_VOICE_GENIE={voices['genie']}",
        f"ELEVENLABS_VOICE_ALADDIN={voices['aladdin']}",
        "",
    ]
    LOCAL_ENV.write_text("\n".join(lines), encoding="utf-8")
    os.chmod(LOCAL_ENV, 0o600)
    print(f"Wrote {LOCAL_ENV}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-only", action="store_true", help="Skip ElevenLabs probe calls")
    args = parser.parse_args()

    api_key = resolve_api_key()
    rec = load_dotenv(RECOMMENDED)
    model = rec.get("ELEVENLABS_MODEL", "eleven_flash_v2_5")

    print("Fetching ElevenLabs voice library…")
    try:
        voices_list = fetch_voices(api_key)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:200]
        raise SystemExit(f"ElevenLabs /voices HTTP {exc.code}: {body}") from exc

    picked = pick_voices(voices_list)
    print("Selected voices:")
    for hero in HEROES:
        print(f"  {hero:8} → {picked[hero]}")

    if not args.write_only:
        probes = {
            "unicorn": "Привет! Я единорог.",
            "genie": "Привет! Я джин.",
            "aladdin": "Привет! Я Алладин.",
        }
        for hero, text in probes.items():
            print(f"Probing TTS {hero}…", end=" ", flush=True)
            probe_tts(api_key, picked[hero], text)
            print("OK")

    write_local_env(api_key, picked, model)
    uniq = len(set(picked.values()))
    if uniq < 3:
        raise SystemExit("ERROR: voice ids must be distinct")
    print("VOICE-PREM-04 bootstrap OK")


if __name__ == "__main__":
    main()
