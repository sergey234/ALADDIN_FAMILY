# -*- coding: utf-8 -*-
"""Feature flags for modular companion platform (env-driven)."""

from __future__ import annotations

import os


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# Core (P0 defaults: chat + voice + companion on)
CHAT_CORE_ENABLED = _env_bool("FEATURE_CHAT_CORE", True)
VOICE_ENABLED = _env_bool("FEATURE_VOICE_ENABLED", True)
COMPANION_ENABLED = _env_bool("FEATURE_COMPANION_ENABLED", True)
TRUST_ENABLED = _env_bool("FEATURE_TRUST_ENABLED", True)

# P1+
MEMORY_ENABLED = _env_bool("FEATURE_MEMORY_ENABLED", False)
STREAM_RESUME_ENABLED = _env_bool("FEATURE_STREAM_RESUME_ENABLED", True)

# P2+
WEB_SEARCH_ENABLED = _env_bool("FEATURE_WEB_SEARCH_ENABLED", False)
MULTI_AGENT_ENABLED = _env_bool("FEATURE_MULTI_AGENT_ENABLED", False)
COMPANION_USE_ORCHESTRATOR = _env_bool("COMPANION_USE_ORCHESTRATOR", False)
VISION_ENABLED = _env_bool("FEATURE_VISION_ENABLED", False)

# Premium neuro-TTS (ElevenLabs Flash) — server + capability gate
NEURO_TTS_ENABLED = _env_bool("FEATURE_NEURO_TTS_ENABLED", False)
# Testing window: trial → same neuro-TTS path as premium (disable with FEATURE_NEURO_TTS_TRIAL=0)
NEURO_TTS_TRIAL_ENABLED = _env_bool("FEATURE_NEURO_TTS_TRIAL", True)

# P3+
IMAGE_GEN_ENABLED = _env_bool("FEATURE_IMAGE_GEN_ENABLED", False)
VIDEO_GEN_ENABLED = _env_bool("FEATURE_VIDEO_GEN_ENABLED", False)
WORKSPACES_ENABLED = _env_bool("FEATURE_WORKSPACES_ENABLED", False)

# Adult infra (backend only; UI in separate app)
ADULT_APP_ENABLED = _env_bool("FEATURE_ADULT_APP_ENABLED", True)
