# -*- coding: utf-8 -*-
"""Mood + online safety fusion alert for parent (p2-47)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .wellness_journal import low_mood_streak_days


def evaluate_security_mood_fusion(
    store: Any,
    teen_user_id: str,
    *,
    online_threat: bool = False,
    threat_summary: str = "",
    locale: str = "ru",
) -> Optional[Dict[str, Any]]:
    """
    Fuse low mood streak with optional security signal.
    Returns alert dict for parent dashboard or None.
    """
    settings = store.get_wellness_settings(teen_user_id)
    if int(settings.get("parent_share_aggregate") or 0) != 1:
        return None

    streak = low_mood_streak_days(store, teen_user_id, days=5)
    low_mood = streak >= 2
    if not low_mood and not online_threat:
        return None

    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        if low_mood and online_threat:
            title = "Mood + online safety"
            body = "Low mood several days and a security concern. Check in with care — no chat text shown."
        elif online_threat:
            title = "Online safety signal"
            body = threat_summary or "A security concern was detected. Gentle check-in recommended."
        else:
            title = "Mood needs attention"
            body = f"Low mood about {streak} days. Offer support — summary only, no chat text."
    else:
        if low_mood and online_threat:
            title = "Настроение + безопасность"
            body = "Несколько дней низкое настроение и сигнал безопасности. Поддержите бережно — без текста чата."
        elif online_threat:
            title = "Сигнал безопасности"
            body = threat_summary or "Зафиксирован риск онлайн. Лучше мягко проверить, как дела."
        else:
            title = "Настроению нужно внимание"
            body = f"Низкое настроение около {streak} дней. Сводка без переписки."

    severity = "watch"
    if online_threat and low_mood:
        severity = "alert"

    return {
        "alert_type": "security_mood_fusion",
        "severity": severity,
        "title": title,
        "body": body,
        "action": "open_family_dashboard",
        "low_mood_streak_days": streak,
        "online_threat": bool(online_threat),
    }
