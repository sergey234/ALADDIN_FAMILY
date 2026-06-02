# -*- coding: utf-8 -*-
"""24h outcome capture (p2-40)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from security.services.ai_platform.wellness_four_pillars import normalize_pillar


@dataclass(frozen=True)
class OutcomeResult:
    id: int
    pillar: str
    helpful: int
    created_at: str


def record_outcome(
    store: Any,
    user_id: str,
    *,
    pillar: str,
    helpful: int,
    note: Optional[str] = None,
    age_band: str = "teen",
) -> OutcomeResult:
    p = normalize_pillar(pillar, age_band) or pillar
    score = max(1, min(5, int(helpful)))
    row = store.save_wellness_outcome(
        user_id,
        pillar=p,
        helpful=score,
        note=(note or "")[:500] or None,
        created_at=datetime.utcnow().isoformat(),
    )
    return OutcomeResult(
        id=int(row["id"]),
        pillar=str(row["pillar"]),
        helpful=int(row["helpful"]),
        created_at=str(row["created_at"]),
    )


def list_recent_outcomes(
    store: Any,
    user_id: str,
    *,
    limit: int = 10,
) -> list[Dict[str, Any]]:
    return store.list_wellness_outcomes(user_id, limit=limit)
