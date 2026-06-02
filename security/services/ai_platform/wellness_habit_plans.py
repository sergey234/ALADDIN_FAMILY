# -*- coding: utf-8 -*-
"""If-then habit plans — behavioral pillar (p2-05)."""

from __future__ import annotations

from typing import Any, Dict, List


def create_habit_plan(store: Any, user_id: str, *, if_then: str) -> Dict[str, Any]:
    text = (if_then or "").strip()
    if len(text) < 3:
        raise ValueError("if_then_too_short")
    return store.save_wellness_habit_plan(user_id, if_then=text)


def list_habit_plans(store: Any, user_id: str) -> List[Dict[str, Any]]:
    return store.list_wellness_habit_plans(user_id, active_only=True)
