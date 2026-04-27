#!/usr/bin/env python3
"""
Phase 8.3 performance smoke checks.

Validates:
1) Content load/cache optimization contracts.
2) Animation/audio optimization hooks.
3) Old-device build readiness (iPhone 11 simulator).
4) Built app bundle size sanity gate.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = "ALADDIN.xcodeproj"
SCHEME = "ALADDIN"
OLD_DEVICE_ID = "6550064E-C017-4A25-BCC2-5773D7CFBA42"  # iPhone 11 (OS 18.4)
DERIVED = ROOT / "build" / "DerivedDataPhase83"
APP_BUNDLE = DERIVED / "Build" / "Products" / "Debug-iphonesimulator" / "ALADDIN.app"
MAX_APP_SIZE_MB = 500


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def must_contain(text: str, needle: str, context: str) -> None:
    require(needle in text, f"{context}: missing `{needle}`")


def must_match(text: str, pattern: str, context: str) -> None:
    require(re.search(pattern, text, flags=re.MULTILINE) is not None, f"{context}: missing pattern `{pattern}`")


def run(cmd: list[str], context: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{context} failed\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def check_content_cache_contracts() -> None:
    content_manager = read("Core/Content/ContentManager.swift")
    cache_manager = read("Core/Content/Cache/ContentCacheManager.swift")

    must_contain(content_manager, "cacheManager.loadItem", "ContentManager cache hit path")
    must_contain(content_manager, "cacheManager.cacheItem", "ContentManager cache write path")
    must_contain(content_manager, "cacheManager.cacheManifest", "ContentManager manifest cache path")

    must_contain(cache_manager, "defaultTTL", "ContentCacheManager TTL policy")
    must_contain(cache_manager, "maxDiskBudgetMb", "ContentCacheManager budget policy")
    must_contain(cache_manager, "cachePolicyDescription", "ContentCacheManager policy diagnostics")
    print("OK content load/cache optimization contracts")


def check_animation_audio_optimization() -> None:
    particles = read("Core/Animation/ParticleSystem.swift")
    sound_effects = read("Core/Audio/SoundEffectPlayer.swift")
    audio_manager = read("Core/Audio/AudioManager.swift")

    must_contain(particles, "@Environment(\\.accessibilityReduceMotion)", "ParticleSystem reduce motion optimization")
    must_contain(particles, "particleCap", "ParticleSystem bounded particle budget")
    must_match(particles, r"Timer\.publish\(every: 1\.0 / 30\.0", "ParticleSystem bounded frame cadence")

    must_contain(sound_effects, "SoundPriority", "SoundEffectPlayer priority model")
    must_contain(sound_effects, "guard priority.rawValue >= currentPriority.rawValue else { return }", "SoundEffectPlayer priority throttling")
    must_contain(audio_manager, "cachedDataByName", "AudioManager audio data cache")
    must_contain(audio_manager, "cachedPlayerByName", "AudioManager player cache")
    print("OK animation/audio optimization contracts")


def build_old_device() -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    output = run(
        [
            "xcodebuild",
            "-project",
            PROJECT,
            "-scheme",
            SCHEME,
            "-sdk",
            "iphonesimulator",
            "-derivedDataPath",
            str(DERIVED),
            "-destination",
            f"id={OLD_DEVICE_ID}",
            "build",
        ],
        "old-device build",
    )
    must_match(output, r"\*\* BUILD SUCCEEDED \*\*", "iPhone 11 build")
    print("OK old-device build: iPhone 11")


def check_app_size_budget() -> None:
    require(APP_BUNDLE.exists(), f"App bundle not found at {APP_BUNDLE}")
    output = run(["du", "-sm", str(APP_BUNDLE)], "app size check")
    # output example: "123\t/path/to/ALADDIN.app"
    size_mb_str = output.strip().split()[0]
    size_mb = int(size_mb_str)
    require(size_mb < MAX_APP_SIZE_MB, f"App size budget exceeded: {size_mb}MB >= {MAX_APP_SIZE_MB}MB")
    print(f"OK app size budget: {size_mb}MB < {MAX_APP_SIZE_MB}MB")


def main() -> int:
    print("PHASE 8.3 PERFORMANCE SMOKE")
    check_content_cache_contracts()
    check_animation_audio_optimization()
    build_old_device()
    check_app_size_budget()
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE RESULT: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
