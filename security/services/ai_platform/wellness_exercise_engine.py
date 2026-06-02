# -*- coding: utf-8 -*-
"""Structured wellness exercises from Knowledge Packs (Phase 2, p2-51)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from security.services.ai_platform.wellness_four_pillars import (
    WellnessPillar,
    is_pillar_allowed,
    normalize_pillar,
)
from security.services.ai_platform.wellness_insights import save_insight_from_exercise
from security.services.ai_platform.wellness_prompt_builder import load_pillar_pack


@dataclass(frozen=True)
class ExerciseStepView:
    step_index: int
    step_total: int
    hint: str
    exercise_id: str
    pillar: str


@dataclass(frozen=True)
class ExerciseSessionView:
    id: int
    pillar: str
    exercise_id: str
    step_index: int
    step_total: int
    hint: str
    completed: bool
    state: Dict[str, Any]


def _locale_hint(step: Dict[str, Any], locale: str) -> str:
    hint = step.get("hint") or {}
    if locale == "en":
        return str(hint.get("en") or hint.get("ru") or "")
    return str(hint.get("ru") or hint.get("en") or "")


def exercise_ids_for_pillar(pillar: str) -> List[str]:
    pack = load_pillar_pack(pillar)
    exercises = pack.get("exercises") or {}
    return list(exercises.keys())


def get_exercise_meta(pillar: str, exercise_id: str) -> Dict[str, Any]:
    try:
        from .wellness_i18n_loader import exercise_meta_from_i18n

        loaded = exercise_meta_from_i18n(exercise_id)
        if loaded and loaded.get("steps"):
            return {
                "exercise_id": loaded["exercise_id"],
                "total_steps": loaded["total_steps"],
                "steps": loaded["steps"],
            }
    except Exception:
        pass
    pack = load_pillar_pack(pillar)
    exercises = pack.get("exercises") or {}
    ex = exercises.get(exercise_id)
    if not ex:
        raise KeyError(f"unknown_exercise:{exercise_id}")
    steps = ex.get("steps") or []
    total = int(ex.get("total_steps") or len(steps) or 1)
    return {"exercise_id": exercise_id, "total_steps": total, "steps": steps}


def list_catalog(
    pillar: str,
    *,
    age_band: str,
    locale: str = "ru",
    jung_enabled: bool = False,
) -> List[Dict[str, Any]]:
    p = normalize_pillar(pillar, age_band)
    if not p:
        return []
    if p == WellnessPillar.JUNG.value and not jung_enabled:
        return []
    items: List[Dict[str, Any]] = []
    pack = load_pillar_pack(p)
    ui = pack.get("ui") or {}
    pillar_title = str(ui.get(locale) or ui.get("ru") or p)
    for ex_id in exercise_ids_for_pillar(p):
        meta = get_exercise_meta(p, ex_id)
        first_hint = ""
        steps = meta.get("steps") or []
        if steps:
            first_hint = _locale_hint(steps[0], locale)
        try:
            from .wellness_i18n_loader import exercise_title_i18n

            ex_title = exercise_title_i18n(ex_id, locale)
        except Exception:
            ex_title = pillar_title
        items.append(
            {
                "exercise_id": ex_id,
                "pillar": p,
                "total_steps": meta["total_steps"],
                "title": ex_title,
                "intro_hint": first_hint,
            }
        )
    return items


def _parse_state(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {"answers": []}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {"answers": []}


def _step_view(row: Dict[str, Any], locale: str) -> ExerciseStepView:
    meta = get_exercise_meta(row["pillar"], row["exercise_type"])
    steps = meta["steps"]
    total = int(meta["total_steps"])
    idx = max(1, int(row.get("step_index") or 1))
    step_data = steps[idx - 1] if idx <= len(steps) else {}
    return ExerciseStepView(
        step_index=idx,
        step_total=total,
        hint=_locale_hint(step_data, locale),
        exercise_id=row["exercise_type"],
        pillar=row["pillar"],
    )


def start_exercise(
    store: Any,
    user_id: str,
    *,
    pillar: str,
    exercise_id: str,
    age_band: str,
    locale: str = "ru",
) -> ExerciseSessionView:
    p = normalize_pillar(pillar, age_band)
    if not p:
        raise PermissionError("pillar_not_allowed_for_age")
    meta = get_exercise_meta(p, exercise_id)
    total = int(meta["total_steps"])
    now = datetime.utcnow().isoformat()
    row = store.create_wellness_exercise(
        user_id,
        pillar=p,
        exercise_type=exercise_id,
        step_index=1,
        step_total=total,
        state_json=json.dumps({"answers": []}),
        created_at=now,
    )
    from security.services.ai_platform.wellness_pillar_session import apply_pillar_selection

    apply_pillar_selection(
        store,
        user_id,
        p,
        age_band=age_band,
        force_switch=False,
    )
    store.upsert_wellness_settings(
        user_id,
        exercise_id=exercise_id,
        exercise_step=1,
        exercise_step_total=total,
    )
    view = _step_view(row, locale)
    return ExerciseSessionView(
        id=int(row["id"]),
        pillar=p,
        exercise_id=exercise_id,
        step_index=view.step_index,
        step_total=view.step_total,
        hint=view.hint,
        completed=False,
        state=_parse_state(row.get("state_json")),
    )


def advance_exercise(
    store: Any,
    user_id: str,
    exercise_row_id: int,
    *,
    answer: Optional[str] = None,
    locale: str = "ru",
) -> ExerciseSessionView:
    row = store.get_wellness_exercise(user_id, exercise_row_id)
    if not row:
        raise KeyError("exercise_not_found")
    if int(row.get("completed") or 0):
        view = _step_view(row, locale)
        return ExerciseSessionView(
            id=int(row["id"]),
            pillar=row["pillar"],
            exercise_id=row["exercise_type"],
            step_index=view.step_index,
            step_total=view.step_total,
            hint=view.hint,
            completed=True,
            state=_parse_state(row.get("state_json")),
        )
    state = _parse_state(row.get("state_json"))
    answers = list(state.get("answers") or [])
    if answer is not None:
        answers.append({"step": int(row.get("step_index") or 1), "text": answer[:2000]})
    state["answers"] = answers
    meta = get_exercise_meta(row["pillar"], row["exercise_type"])
    total = int(meta["total_steps"])
    current = int(row.get("step_index") or 1)
    if current >= total:
        completed_row = store.complete_wellness_exercise(
            user_id,
            exercise_row_id,
            state_json=json.dumps(state),
        )
        from security.services.ai_platform.wellness_alliance import (
            apply_alliance_for_exercise_done,
        )

        apply_alliance_for_exercise_done(store, user_id)
        save_insight_from_exercise(
            store,
            user_id,
            pillar=str(completed_row["pillar"]),
            answers=list(state.get("answers") or []),
            locale=locale,
        )
        store.upsert_wellness_settings(
            user_id,
            exercise_id="",
            exercise_step=0,
            exercise_step_total=0,
        )
        view = _step_view(completed_row, locale)
        return ExerciseSessionView(
            id=int(completed_row["id"]),
            pillar=completed_row["pillar"],
            exercise_id=completed_row["exercise_type"],
            step_index=total,
            step_total=total,
            hint=view.hint,
            completed=True,
            state=state,
        )
    next_step = current + 1
    updated = store.update_wellness_exercise(
        user_id,
        exercise_row_id,
        step_index=next_step,
        state_json=json.dumps(state),
    )
    store.upsert_wellness_settings(
        user_id,
        exercise_step=next_step,
        exercise_step_total=total,
    )
    view = _step_view(updated, locale)
    return ExerciseSessionView(
        id=int(updated["id"]),
        pillar=updated["pillar"],
        exercise_id=updated["exercise_type"],
        step_index=view.step_index,
        step_total=view.step_total,
        hint=view.hint,
        completed=False,
        state=state,
    )


def get_active_session(
    store: Any,
    user_id: str,
    *,
    locale: str = "ru",
) -> Optional[ExerciseSessionView]:
    row = store.get_active_wellness_exercise(user_id)
    if not row:
        return None
    view = _step_view(row, locale)
    return ExerciseSessionView(
        id=int(row["id"]),
        pillar=row["pillar"],
        exercise_id=row["exercise_type"],
        step_index=view.step_index,
        step_total=view.step_total,
        hint=view.hint,
        completed=bool(int(row.get("completed") or 0)),
        state=_parse_state(row.get("state_json")),
    )
