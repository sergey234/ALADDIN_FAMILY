# -*- coding: utf-8 -*-
"""P2-05 — Trust decay on inactivity + daily visit streak bonus."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

DECAY_PER_MISSED_DAY = 2
MAX_DECAY_PER_VISIT = 8
STREAK_BONUS_EVERY = 3
STREAK_BONUS_POINTS = 2


def apply_trust_visit(
    store: Any,
    user_id: str,
    character_id: str,
    *,
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Apply decay since last active day, then streak bookkeeping.
    Returns score, streak_days, decay_applied, streak_bonus.
    """
    today = today or date.today()
    today_s = today.isoformat()
    meta = store.get_trust_meta(user_id, character_id)
    last_day = meta.get("last_active_day")
    streak = int(meta.get("streak_days") or 0)
    score = int(store.get_trust(user_id, character_id))

    decay_applied = 0
    if last_day:
        try:
            last = date.fromisoformat(str(last_day)[:10])
            gap = (today - last).days
            if gap > 1:
                decay_applied = min(MAX_DECAY_PER_VISIT, (gap - 1) * DECAY_PER_MISSED_DAY)
                score = max(0, score - decay_applied)
        except ValueError:
            pass

    streak_bonus = 0
    if last_day == today_s:
        pass
    elif last_day:
        try:
            last = date.fromisoformat(str(last_day)[:10])
            if (today - last).days == 1:
                streak += 1
            else:
                streak = 1
        except ValueError:
            streak = 1
    else:
        streak = 1

    if last_day != today_s and streak > 0 and streak % STREAK_BONUS_EVERY == 0:
        streak_bonus = STREAK_BONUS_POINTS
        score = min(100, score + streak_bonus)

    if last_day != today_s:
        store.set_trust(user_id, character_id, score)
        store.set_trust_meta(
            user_id,
            character_id,
            {"last_active_day": today_s, "streak_days": streak, "updated_at": datetime.utcnow().isoformat()},
        )

    return {
        "score": score,
        "streak_days": streak,
        "decay_applied": decay_applied,
        "streak_bonus": streak_bonus,
    }
