# -*- coding: utf-8 -*-
"""P2-13 — Social bridge after repeated loneliness turns."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

LONELINESS_STREAK_THRESHOLD = 2
SUGGESTIONS = ("family", "friend", "trusted_adult")
_LONELY_MOODS = frozenset({"lonely", "comfort_needed"})
_LONELY_DOMAINS = frozenset({"feelings", "loneliness", "friends", "wellness"})


def apply_social_bridge(
    profile: Dict[str, Any],
    *,
    domain: str,
    mood: str = "neutral",
    social_bridge_hint: bool,
    crisis: bool,
    thread_id: str,
) -> Tuple[Dict[str, Any], bool, List[str]]:
    if crisis:
        return profile, False, []

    bridge = dict(profile.get("social_bridge") or {})
    streak = int(bridge.get("loneliness_streak") or 0)
    last_thread = bridge.get("last_thread")
    mood_key = (mood or "neutral").strip().lower()

    lonely_turn = domain == "loneliness" or (
        mood_key in _LONELY_MOODS and domain in _LONELY_DOMAINS
    ) or (
        social_bridge_hint and domain in ("feelings", "loneliness", "friends")
    )
    if lonely_turn:
        streak = streak + 1 if last_thread == thread_id else 1
        bridge["loneliness_streak"] = streak
        bridge["last_thread"] = thread_id
    elif streak > 0 and mood_key not in _LONELY_MOODS:
        streak = max(0, streak - 1)
        bridge["loneliness_streak"] = streak

    profile = dict(profile)
    profile["social_bridge"] = bridge
    show = streak >= LONELINESS_STREAK_THRESHOLD
    return profile, show, list(SUGGESTIONS) if show else []
