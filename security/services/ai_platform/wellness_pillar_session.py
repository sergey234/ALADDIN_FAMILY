# -*- coding: utf-8 -*-
"""One pillar per wellness session (p2-15)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .wellness_four_pillars import normalize_pillar


@dataclass(frozen=True)
class PillarSessionResult:
    ok: bool
    settings: Dict[str, Any]
    reason: str = ""


def apply_pillar_selection(
    store: Any,
    user_id: str,
    pillar: str,
    *,
    age_band: str,
    force_switch: bool = False,
    parent_share: Optional[int] = None,
) -> PillarSessionResult:
    """Lock pillar for current session until /session/end."""
    p = normalize_pillar(pillar, age_band)
    if not p:
        return PillarSessionResult(
            ok=False,
            settings=store.get_wellness_settings(user_id),
            reason="pillar_not_allowed_for_age",
        )
    settings = store.get_wellness_settings(user_id)
    locked = settings.get("session_pillar_locked")
    if locked and locked != p and not force_switch:
        return PillarSessionResult(
            ok=False,
            settings=settings,
            reason="pillar_session_locked",
        )
    now = datetime.utcnow().isoformat()
    kwargs: Dict[str, Any] = dict(
        primary_pillar=p,
        session_pillar_locked=p,
        session_started_at=now,
    )
    if parent_share is not None:
        kwargs["parent_share_aggregate"] = parent_share
    updated = store.upsert_wellness_settings(user_id, **kwargs)
    from .wellness_pack_registry import lock_session_pack

    lock_session_pack(store, user_id, p, force=force_switch)
    updated = store.get_wellness_settings(user_id)
    return PillarSessionResult(ok=True, settings=updated)


def end_pillar_session(store: Any, user_id: str) -> Dict[str, Any]:
    return store.upsert_wellness_settings(user_id, clear_session_lock=True)


def get_locked_pillar(settings: Dict[str, Any]) -> Optional[str]:
    locked = settings.get("session_pillar_locked")
    if locked:
        return str(locked)
    return settings.get("primary_pillar")
