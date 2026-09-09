#!/usr/bin/env python3
"""Print a secret-safe snapshot of effective AI/STT/TTS production flags."""

from __future__ import annotations

import json
import os
from pathlib import Path


def enabled(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def any_present(*names: str) -> bool:
    return any(bool((os.getenv(name) or "").strip()) for name in names)


def main() -> None:
    stt_mode = (os.getenv("COMPANION_STT_PROVIDER") or "auto").strip().lower()
    yandex_ready = any_present("YANDEX_SPEECHKIT_API_KEY", "YANDEX_CLOUD_API_KEY")
    openai_ready = any_present("COMPANION_STT_OPENAI_API_KEY", "OPENAI_API_KEY")
    if stt_mode == "auto":
        active_stt = "yandex_speechkit" if yandex_ready else "openai_whisper" if openai_ready else "none"
    elif stt_mode in {"yandex", "yandex_speechkit", "speechkit"}:
        active_stt = "yandex_speechkit" if yandex_ready else "none"
    elif stt_mode in {"openai", "openai_whisper", "whisper"}:
        active_stt = "openai_whisper" if openai_ready else "none"
    else:
        active_stt = "none"

    hermes_bin = Path(os.getenv("HERMES_BIN", "/opt/aladdin-backend/venv/bin/hermes"))
    output = {
        "ai": {
            "backend": (os.getenv("AI_BACKEND") or "sfm").strip().lower(),
            "hermesExecutable": hermes_bin.is_file() and os.access(hermes_bin, os.X_OK),
            "openRouterCredentialPresent": any_present(
                "OPENROUTER_API_KEY",
                "HERMES_OPENROUTER_API_KEY",
            ),
            "directFallbackEnabled": enabled("FEATURE_OPENROUTER_DIRECT_FALLBACK", True),
            "directModel": os.getenv(
                "OPENROUTER_DIRECT_MODEL",
                "deepseek/deepseek-v4-flash",
            ),
            "geminiFallbackEnabled": enabled("FEATURE_GEMINI_FALLBACK", False),
            "geminiCredentialPresent": any_present(
                "GEMINI_API_KEY",
                "GOOGLE_AI_API_KEY",
                "GOOGLE_API_KEY",
            ),
            "geminiModel": os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        },
        "stt": {
            "serverFallbackEnabled": enabled("FEATURE_COMPANION_SERVER_STT", False),
            "configuredMode": stt_mode,
            "effectiveProvider": active_stt,
            "yandexCredentialPresent": yandex_ready,
            "openAICredentialPresent": openai_ready,
        },
        "tts": {
            "neuroEnabled": enabled("FEATURE_NEURO_TTS_ENABLED", False),
            "trialEnabled": enabled("FEATURE_NEURO_TTS_TRIAL", True),
            "provider": "elevenlabs",
            "model": os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5"),
            "credentialPresent": any_present("ELEVENLABS_API_KEY"),
            "allCharacterVoicesPresent": all(
                any_present(name)
                for name in (
                    "ELEVENLABS_VOICE_GENIE",
                    "ELEVENLABS_VOICE_UNICORN",
                    "ELEVENLABS_VOICE_ALADDIN",
                )
            ),
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
