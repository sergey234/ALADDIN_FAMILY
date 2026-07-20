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
# ^ Hermes multi-agent stub (orchestrator.py). NOT wellness — use FEATURE_WELLNESS_ORCHESTRATOR.
VISION_ENABLED = _env_bool("FEATURE_VISION_ENABLED", False)

# Hybrid voice STT fallback (Apple primary → ALADDIN server only on failure; audio not persisted)
COMPANION_SERVER_STT_ENABLED = _env_bool("FEATURE_COMPANION_SERVER_STT", False)

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

# Wellness Platform (Phase 0 — default OFF until gate 0→1)
FEATURE_WELLNESS_ENABLED = _env_bool("FEATURE_WELLNESS_ENABLED", False)
FEATURE_WELLNESS_ORCHESTRATOR = _env_bool("FEATURE_WELLNESS_ORCHESTRATOR", False)
FEATURE_WELLNESS_REFLECTIVE = _env_bool("FEATURE_WELLNESS_REFLECTIVE", False)
FEATURE_WELLNESS_JUNG = _env_bool("FEATURE_WELLNESS_JUNG", False)
/// psych-08 — warm guide role + session modes (A+B). Disable with FEATURE_WELLNESS_GUIDE_MODES=0
FEATURE_WELLNESS_GUIDE_MODES = _env_bool("FEATURE_WELLNESS_GUIDE_MODES", True)
# p1-7b / inf-flags — Due-ping until Done (client also gates; default OFF for fatigue risk)
FEATURE_DUE_PING = _env_bool("FEATURE_DUE_PING", False)
# p2-8 — Focus sessions (default OFF)
FEATURE_FOCUS_SESSION = _env_bool("FEATURE_FOCUS_SESSION", False)
# p2-9h — Family custom challenges (default ON after ship)
FEATURE_FAMILY_CHALLENGES = _env_bool("FEATURE_FAMILY_CHALLENGES", True)
# p3-10 — 0..100 cohort; default 100 = all users (prod parity after full rollout)
# p3-16 — parent playbook LLM personalize (Hermes); default OFF
FEATURE_WELLNESS_PARENT_LLM = _env_bool("FEATURE_WELLNESS_PARENT_LLM", False)

# hero-x-13 — vedic wisdom layer in companion chat (off when 0)
FEATURE_COMPANION_VEDIC_WISDOM = _env_bool("FEATURE_COMPANION_VEDIC_WISDOM", True)
FEATURE_GENIE_HUMOR_AB = _env_bool("FEATURE_GENIE_HUMOR_AB", False)
