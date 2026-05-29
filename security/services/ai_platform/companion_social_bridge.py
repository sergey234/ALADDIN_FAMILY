# -*- coding: utf-8 -*-
"""P2-13 — Social bridge after repeated loneliness turns."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

LONELINESS_STREAK_THRESHOLD = 2
SUGGESTIONS = ("family", "friend", "trusted_adult")


def apply_social_bridge(
    profile: Dict[str, Any],
    *,
    domain: str,
    social_bridge_hint: bool,
    crisis: bool,
    thread_id: str,
) -> Tuple[Dict[str, Any], bool, List[str]]:
    if crisis:
        return profile, False, []

    bridge = dict(profile.get("social_bridge") or {})
    streak = int(bridge.get("loneliness_streak") or 0)
    last_thread = bridge.get("last_thread")

    lonely_turn = domain == "loneliness" or (
        social_bridge_hint and domain in ("feelings", "loneliness", "friends")
    )
    if lonely_turn:
        streak = streak + 1 if last_thread == thread_id else 1
        bridge["loneliness_streak"] = streak
        bridge["last_thread"] = thread_id
    elif streak > 0:
        streak = max(0, streak - 1)
        bridge["loneliness_streak"] = streak

    profile = dict(profile)
    profile["social_bridge"] = bridge
    show = streak >= LONELINESS_STREAK_THRESHOLD
    return profile, show, list(SUGGESTIONS) if show else []
