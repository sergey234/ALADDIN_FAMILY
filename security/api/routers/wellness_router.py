# -*- coding: utf-8 -*-
"""
Wellness API (Phase 1 MVP).

Usage in main.py:
    from security.api.routers.wellness_router import router as wellness_router
    app.include_router(wellness_router)
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/wellness", tags=["Wellness"])


async def wellness_locale_dep(
    request: Request,
    locale: str = Query("ru", max_length=8),
) -> str:
    """Resolve locale: Accept-Language header, then ?locale= (p18-05)."""
    from security.services.ai_platform.wellness_i18n_loader import resolve_wellness_locale

    return resolve_wellness_locale(
        query_locale=locale,
        accept_language=request.headers.get("accept-language"),
    )


WellnessLocale = Annotated[str, Depends(wellness_locale_dep)]

try:
    from security.api.routers.ai_assistant_router import get_current_user
    from security.services.ai_platform.feature_flags import FEATURE_WELLNESS_ENABLED
    from security.services.ai_platform.companion_store import get_companion_store
    from security.services.ai_platform.wellness_four_pillars import (
        pillars_for_age_band,
        normalize_pillar,
    )
    from security.services.ai_platform.wellness_escalation import evaluate_escalation
    from security.services.ai_platform.wellness_referral import get_referral_payload
    from security.services.ai_platform.wellness_age_policy import (
        has_wellness_consent,
        normalize_age_band,
        wellness_consent_from_payload,
    )
    from security.services.ai_platform.wellness_journal import (
        record_checkin,
        low_mood_streak_days,
    )
    from security.services.ai_platform.wellness_assessments import (
        phq_lite_schema,
        score_phq_lite,
        assert_phq_allowed,
        phq9_schema,
        gad7_schema,
        score_phq9,
        score_gad7,
        assert_full_assessment_allowed,
        mbi_lite_schema,
        score_mbi_lite,
        assert_mbi_allowed,
    )
    from security.services.ai_platform.wellness_habit_plans import (
        create_habit_plan,
        list_habit_plans,
    )
    from security.services.ai_platform.wellness_pillar_fatigue import evaluate_pillar_fatigue
    from security.services.ai_platform.wellness_mood_routing import suggest_pillar_with_mood_fallback
    from security.services.ai_platform.wellness_plan_agent import build_wellness_plan
    from security.services.ai_platform.wellness_trauma_referral import build_trauma_referral_payload
    from security.services.ai_platform.wellness_alliance import (
        get_alliance_state,
        apply_alliance_for_checkin,
        apply_alliance_for_outcome,
    )
    from security.services.ai_platform.wellness_hub_ab import build_hub_copy
    from security.services.ai_platform.wellness_weekly_meaning import (
        build_weekly_meaning,
        mark_weekly_meaning_shown,
    )
    from security.services.ai_platform.wellness_family_themes import build_family_themes_payload
    from security.services.ai_platform.wellness_security_fusion import evaluate_security_mood_fusion
    from security.services.ai_platform.wellness_streaks import build_streaks_payload
    from security.services.ai_platform.wellness_clinician_export import build_clinician_export
    from security.services.ai_platform.wellness_parent_playbook import build_parent_playbook
    from security.services.ai_platform.wellness_i18n_loader import (
        weekly_pdf_labels_from_i18n,
        widget_copy_from_i18n,
    )
    from security.services.ai_platform.wellness_api_errors import raise_wellness_error
    from security.services.ai_platform.wellness_together_mode import build_together_session
    from security.services.ai_platform.wellness_triggers import evaluate_triggers
    from security.services.ai_platform.wellness_orchestrator import (
        run_wellness_loop,
        teen_default_parent_share,
        wellness_loop_to_dict,
    )
    from security.services.ai_platform.wellness_pack_registry import session_pack_payload
    from security.services.ai_platform.wellness_gdpr import (
        delete_wellness_personal_data,
        export_wellness_personal_data,
    )
    from security.services.ai_platform.wellness_four_pillars import pillars_for_age_band, suggest_pillar
    from security.services.ai_platform.feature_flags import (
        FEATURE_WELLNESS_JUNG,
        FEATURE_WELLNESS_ORCHESTRATOR,
    )
    from security.services.ai_platform.wellness_exercise_engine import (
        list_catalog,
        start_exercise,
        advance_exercise,
        get_active_session,
    )
    from security.services.ai_platform.wellness_session_recap import build_session_recap
    from security.services.ai_platform.wellness_outcomes import record_outcome
    from security.services.ai_platform.wellness_alerts import (
        build_user_alerts,
        build_family_dashboard,
    )
    from security.services.ai_platform.wellness_scheduler import reminders_for_user
    from security.services.ai_platform.wellness_analytics import record_wellness_event
    from security.services.ai_platform.wellness_nudge import dismiss_idle_nudge
    from security.services.ai_platform.wellness_pillar_session import (
        apply_pillar_selection,
        end_pillar_session,
    )
    from security.services.ai_platform.wellness_outcome_followup import (
        apply_outcome_pillar_adjustment,
        dismiss_outcome_prompt,
        build_outcome_reminder,
    )
    from security.services.ai_platform.feature_flags import FEATURE_WELLNESS_REFLECTIVE
    from security.services.ai_platform.wellness_reflective_modes import (
        list_reflective_modes,
        resolve_reflective_mode,
    )
except ImportError:
    from ai_assistant_router import get_current_user  # type: ignore
    from security.services.ai_platform.feature_flags import FEATURE_WELLNESS_ENABLED  # type: ignore
    from security.services.ai_platform.companion_store import get_companion_store  # type: ignore


def _require_wellness(locale: str = "ru", *, user: Optional[dict] = None) -> None:
    if not FEATURE_WELLNESS_ENABLED:
        raise_wellness_error("wellness_disabled", locale=locale)
    if user is not None:
        from security.services.ai_platform.wellness_canary import user_in_wellness_canary

        if not user_in_wellness_canary(_uid(user)):
            raise_wellness_error("wellness_canary_excluded", locale=locale)


def _uid(user: dict) -> str:
    return str(user.get("user_id") or user.get("sub") or "")


def _require_consent(user: dict, *, locale: str = "ru") -> None:
    store = get_companion_store()
    consent = store.get_consent(_uid(user))
    if not has_wellness_consent(consent, age_band=user.get("age_band") or "teen"):
        raise_wellness_error("wellness_consent_required", locale=locale)


def _require_premium_wellness(user: dict, *, locale: str = "ru") -> None:
    """p3-12 — Jung dreams / deep paths only after consent + 48h without L3."""
    from security.services.ai_platform.wellness_crisis_monitor import wellness_premium_eligible

    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    consent = store.get_consent(uid)
    gate = wellness_premium_eligible(
        store, uid, profile=consent, age_band=age_band
    )
    if not gate.get("eligible"):
        raise_wellness_error(
            str(gate.get("reason") or "wellness_premium_blocked"),
            locale=locale,
        )


class PillarSelectRequest(BaseModel):
    pillar: str = Field(..., pattern="^(cognitive|behavioral|humanistic|jung)$")
    force_switch: bool = Field(
        False,
        description="p2-15 — явная смена столпа, сброс session lock",
    )


class CheckinRequest(BaseModel):
    mood: str = Field(..., max_length=32)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)


class ConsentRequest(BaseModel):
    wellness_accepted: bool = True
    psychological_support_enabled: Optional[bool] = None


class PhqLiteSubmitRequest(BaseModel):
    answers: List[int] = Field(..., min_length=5, max_length=5)


class Phq9SubmitRequest(BaseModel):
    answers: List[int] = Field(..., min_length=9, max_length=9)


class Gad7SubmitRequest(BaseModel):
    answers: List[int] = Field(..., min_length=7, max_length=7)


class MbiLiteSubmitRequest(BaseModel):
    answers: List[int] = Field(..., min_length=5, max_length=5)


class HabitPlanRequest(BaseModel):
    if_then: str = Field(..., min_length=3, max_length=500)


class ParentShareRequest(BaseModel):
    parent_share_aggregate: bool = Field(
        ...,
        description="Teen: share mood aggregate with parent (not chat text)",
    )


class ExerciseStartRequest(BaseModel):
    pillar: str = Field(..., pattern="^(cognitive|behavioral|humanistic|jung)$")
    exercise_id: str = Field(..., min_length=1, max_length=64)


class ExerciseStepRequest(BaseModel):
    answer: Optional[str] = Field(None, max_length=2000)


class OutcomeRequest(BaseModel):
    pillar: str = Field(..., pattern="^(cognitive|behavioral|humanistic|jung)$")
    helpful: int = Field(..., ge=1, le=5)
    note: Optional[str] = Field(None, max_length=500)


class DreamNoteRequest(BaseModel):
    dream_text: str = Field(..., min_length=1, max_length=4000)
    mood_tag: Optional[str] = Field(None, max_length=32)


@router.get("/pillars")
async def list_pillars(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    age_band = (user.get("age_band") or "teen").lower()
    return {"pillars": pillars_for_age_band(age_band), "age_band": age_band}


@router.post("/session/pillar")
async def set_session_pillar(
    body: PillarSelectRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = (user.get("age_band") or "teen").lower()
    pillar = normalize_pillar(body.pillar, age_band)
    if not pillar:
        raise_wellness_error("pillar_not_allowed_for_age", 403)
    if pillar == "jung" and not FEATURE_WELLNESS_JUNG:
        raise_wellness_error("jung_disabled", 403)
    store = get_companion_store()
    share = teen_default_parent_share(age_band, None)
    result = apply_pillar_selection(
        store,
        _uid(user),
        pillar,
        age_band=age_band,
        force_switch=body.force_switch,
        parent_share=share,
    )
    if not result.ok:
        raise_wellness_error(getattr(result, "reason", "wellness_generic") or "wellness_generic", 409)
    return {"ok": True, "settings": result.settings}


@router.post("/session/end")
async def end_session(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-15 — завершить wellness-сессию (снять lock столпа)."""
    _require_wellness(user=user)
    _require_consent(user)
    settings = end_pillar_session(get_companion_store(), _uid(user))
    return {"ok": True, "settings": settings}


@router.get("/settings")
async def get_settings(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    store = get_companion_store()
    settings = store.get_wellness_settings(_uid(user))
    age_band = normalize_age_band(user.get("age_band"))
    return {
        "settings": settings,
        "age_band": age_band,
        "can_edit_parent_share": age_band == "teen",
        "alliance": get_alliance_state(store, _uid(user)),
    }


@router.post("/settings/parent-share")
async def set_parent_share(
    body: ParentShareRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p1-25 — teen chooses whether parent sees mood aggregate (not chat)."""
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    if age_band != "teen":
        raise_wellness_error("teen_only", 403)
    store = get_companion_store()
    val = teen_default_parent_share(age_band, 1 if body.parent_share_aggregate else 0)
    settings = store.upsert_wellness_settings(
        _uid(user),
        parent_share_aggregate=val,
    )
    return {"ok": True, "parent_share_aggregate": bool(val), "settings": settings}


@router.get("/consent")
async def get_consent(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    store = get_companion_store()
    raw = store.get_consent(_uid(user))
    age_band = normalize_age_band(user.get("age_band"))
    payload = wellness_consent_from_payload(raw)
    return {
        **payload,
        "age_band": age_band,
        "has_access": has_wellness_consent(raw, age_band=age_band),
        "can_set_parent_toggle": age_band in ("parent", "senior"),
    }


@router.post("/consent")
async def post_consent(
    body: ConsentRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    from datetime import datetime

    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    current = store.get_consent(uid)
    if body.psychological_support_enabled is not None:
        if age_band not in ("parent", "senior"):
            raise_wellness_error("parent_toggle_only", 403)
        current["psychological_support_enabled"] = bool(body.psychological_support_enabled)
        current["psychological_support_agent"] = bool(body.psychological_support_enabled)
    if body.wellness_accepted:
        current["wellness_accepted"] = True
        current["wellness_accepted_at"] = datetime.utcnow().isoformat()
        current["wellness_disclaimer_version"] = "v1"
        if age_band == "child":
            pc = user.get("parent_consent") if isinstance(user.get("parent_consent"), dict) else {}
            if pc.get("child_can_use_companion") or pc.get("companion"):
                current["psychological_support_enabled"] = True
                current["psychological_support_agent"] = True
    else:
        current["wellness_accepted"] = False
    store.set_consent(uid, current)
    payload = wellness_consent_from_payload(current)
    return {
        "ok": True,
        **payload,
        "has_access": has_wellness_consent(current, age_band=age_band),
    }


@router.post("/checkin")
async def post_checkin(
    body: CheckinRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    age_band = user.get("age_band") or "teen"
    row = record_checkin(
        store,
        user_id=_uid(user),
        mood_emoji=body.mood,
        sleep_hours=body.sleep_hours,
        stress_level=body.stress_level,
        energy_level=body.energy_level,
        notes=body.notes,
        age_band=age_band,
    )
    record_wellness_event(
        user_id=_uid(user),
        event="wellness_checkin",
        extra={"age_band": age_band},
    )
    alliance = apply_alliance_for_checkin(store, _uid(user))
    return {"ok": True, "checkin": row, "alliance": alliance}


@router.get("/checkin/today")
async def get_checkin_today(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    store = get_companion_store()
    day = date.today().isoformat()
    row = store.get_wellness_checkin(_uid(user), day)
    return {"day": day, "checkin": row}


@router.get("/journal")
async def get_journal(
    days: int = Query(7, ge=1, le=30),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    rows = store.list_wellness_checkins(_uid(user), days=days)
    return {"days": days, "entries": rows}


@router.get("/triggers/status")
async def triggers_status(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    store = get_companion_store()
    return evaluate_triggers(
        store,
        _uid(user),
        age_band=user.get("age_band") or "teen",
        locale=locale,
    )


@router.post("/nudges/idle/dismiss")
async def dismiss_idle_nudge_endpoint(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-29 — скрыть idle-nudge до завтра."""
    _require_wellness(user=user)
    _require_consent(user)
    return dismiss_idle_nudge(get_companion_store(), _uid(user))


@router.get("/assessments/phq-lite/schema")
async def phq_lite_schema_endpoint(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_phq_allowed(age_band)
    except PermissionError:
        raise_wellness_error("phq_lite_blocked_for_age", 403)
    return phq_lite_schema(locale=locale)


@router.post("/assessments/phq-lite/submit")
async def phq_lite_submit(
    body: PhqLiteSubmitRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_phq_allowed(age_band)
    except PermissionError:
        raise_wellness_error("phq_lite_blocked_for_age", 403)
    try:
        result = score_phq_lite(body.answers, locale=locale)
    except ValueError as e:
        raise_wellness_error("wellness_generic", 400)
    store = get_companion_store()
    saved = store.save_wellness_assessment(
        _uid(user),
        assessment_type="phq_lite",
        answers=body.answers,
        score=result.score,
        severity=result.severity,
        suggest_professional=result.suggest_professional,
    )
    esc = evaluate_escalation("", phq_lite_score=result.score)
    return {
        "ok": True,
        "score": result.score,
        "severity": result.severity,
        "suggest_professional": result.suggest_professional,
        "disclaimer": result.disclaimer,
        "escalation_level": esc.level,
        "assessment": saved,
    }


@router.get("/assessments/phq-9/schema")
async def phq9_schema_endpoint(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(locale, user=user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_full_assessment_allowed(age_band)
    except PermissionError:
        raise_wellness_error("assessment_blocked_for_age", locale=locale)
    store = get_companion_store()
    uid = _uid(user)
    from security.services.ai_platform.wellness_premium_access import require_premium_features

    require_premium_features(
        store, uid, user, profile=store.get_consent(uid), age_band=age_band, locale=locale
    )
    return phq9_schema(locale=locale)


@router.post("/assessments/phq-9/submit")
async def phq9_submit(
    body: Phq9SubmitRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_full_assessment_allowed(age_band)
    except PermissionError:
        raise_wellness_error("assessment_blocked_for_age", 403)
    try:
        result = score_phq9(body.answers, locale=locale)
    except ValueError as e:
        raise_wellness_error("wellness_generic", 400)
    store = get_companion_store()
    saved = store.save_wellness_assessment(
        _uid(user),
        assessment_type="phq9",
        answers=body.answers,
        score=result.score,
        severity=result.severity,
        suggest_professional=result.suggest_professional,
    )
    if result.crisis_flag:
        esc = evaluate_escalation("хочу умереть причинить себе вред")
    else:
        esc = evaluate_escalation("", phq_lite_score=min(result.score, 27))
    return {
        "ok": True,
        "score": result.score,
        "severity": result.severity,
        "suggest_professional": result.suggest_professional,
        "crisis_flag": result.crisis_flag,
        "disclaimer": result.disclaimer,
        "escalation_level": esc.level,
        "assessment": saved,
    }


@router.get("/assessments/gad-7/schema")
async def gad7_schema_endpoint(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(locale, user=user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_full_assessment_allowed(age_band)
    except PermissionError:
        raise_wellness_error("assessment_blocked_for_age", locale=locale)
    store = get_companion_store()
    uid = _uid(user)
    from security.services.ai_platform.wellness_premium_access import require_premium_features

    require_premium_features(
        store, uid, user, profile=store.get_consent(uid), age_band=age_band, locale=locale
    )
    return gad7_schema(locale=locale)


@router.post("/assessments/gad-7/submit")
async def gad7_submit(
    body: Gad7SubmitRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_full_assessment_allowed(age_band)
    except PermissionError:
        raise_wellness_error("assessment_blocked_for_age", 403)
    try:
        result = score_gad7(body.answers, locale=locale)
    except ValueError as e:
        raise_wellness_error("wellness_generic", 400)
    store = get_companion_store()
    saved = store.save_wellness_assessment(
        _uid(user),
        assessment_type="gad7",
        answers=body.answers,
        score=result.score,
        severity=result.severity,
        suggest_professional=result.suggest_professional,
    )
    esc = evaluate_escalation(
        "severe anxiety panic" if result.score >= 15 else "",
    )
    return {
        "ok": True,
        "score": result.score,
        "severity": result.severity,
        "suggest_professional": result.suggest_professional,
        "disclaimer": result.disclaimer,
        "escalation_level": esc.level,
        "assessment": saved,
    }


@router.get("/escalation/level")
async def escalation_level(
    locale: str = Depends(wellness_locale_dep),
    message: str = Query("", max_length=2000),
    phq_lite_score: Optional[int] = Query(None, ge=0, le=27),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    store = get_companion_store()
    streak = low_mood_streak_days(store, _uid(user), days=7)
    result = evaluate_escalation(
        message, phq_lite_score=phq_lite_score, days_low_mood=streak
    )
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    loc = locale
    trauma = build_trauma_referral_payload(
        message, age_band=age_band, locale=loc
    )
    if result.level == "L3":
        from security.services.ai_platform.wellness_alliance import apply_alliance_for_crisis
        from security.services.ai_platform.wellness_crisis_monitor import record_crisis_l3

        record_crisis_l3(store, uid, source="escalation_api_l3")
        apply_alliance_for_crisis(store, uid)
    elif trauma.get("triggered"):
        from security.services.ai_platform.wellness_alliance import apply_alliance_for_trauma_trigger

        apply_alliance_for_trauma_trigger(store, uid)
        store.upsert_wellness_settings(uid, escalation_level="L2")
    return {
        "level": result.level,
        "reason": result.reason,
        "actions": result.actions,
        "trauma": trauma,
        "alliance": get_alliance_state(store, uid),
    }


@router.get("/trauma/check")
async def trauma_check(
    locale: str = Depends(wellness_locale_dep),
    message: str = Query("", max_length=2000),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-34 — trauma keywords → specialist referral (no deep trauma in chat)."""
    _require_wellness(user=user)
    age_band = normalize_age_band(user.get("age_band"))
    payload = build_trauma_referral_payload(
        message, age_band=age_band, locale=locale
    )
    if payload.get("triggered"):
        store = get_companion_store()
        uid = _uid(user)
        from security.services.ai_platform.wellness_alliance import apply_alliance_for_trauma_trigger

        apply_alliance_for_trauma_trigger(store, uid)
        store.upsert_wellness_settings(uid, escalation_level="L2")
        payload["alliance"] = get_alliance_state(store, uid)
    return payload


@router.get("/crisis/status")
async def crisis_status(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-04 — 48h L3 cooldown after self-harm / crisis signals."""
    _require_wellness(user=user)
    from security.services.ai_platform.wellness_crisis_monitor import (
        build_crisis_status_payload,
        wellness_premium_eligible,
    )

    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    consent = store.get_consent(uid)
    return {
        "ok": True,
        "crisis": build_crisis_status_payload(store, uid),
        "premium": wellness_premium_eligible(
            store, uid, profile=consent, age_band=age_band
        ),
    }


@router.get("/premium/eligibility")
async def premium_eligibility(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-12 + p3-06 — ethics + subscription gate for premium wellness."""
    _require_wellness(locale, user=user)
    from security.services.ai_platform.wellness_premium_access import wellness_premium_features_gate

    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    consent = store.get_consent(uid)
    gate = wellness_premium_features_gate(
        store, uid, user, profile=consent, age_band=age_band
    )
    return {"ok": True, **gate}


@router.get("/alliance")
async def wellness_alliance(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-35 — therapeutic alliance score + hero emotion."""
    _require_wellness(user=user)
    return {"ok": True, "alliance": get_alliance_state(get_companion_store(), _uid(user))}


@router.get("/referral")
async def referral(
    locale: WellnessLocale,
    level: str = Query("L2", pattern="^L[0-3]$"),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    return get_referral_payload(locale=locale, level=level)


@router.get("/session/suggest-pillar")
async def session_suggest_pillar(
    message: str = Query("", max_length=500),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-14 / p2-33 — pillar suggestion with mood fallback from notes/chat text."""
    _require_wellness(user=user)
    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    settings = store.get_wellness_settings(uid)
    fatigue = evaluate_pillar_fatigue(
        store,
        uid,
        age_band=age_band,
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )
    mood_routing: Dict[str, Any] = {}
    if fatigue.get("fatigued") and fatigue.get("suggested_pillar"):
        suggested = fatigue["suggested_pillar"]
        reason = "pillar_fatigue"
    else:
        mood_routing = suggest_pillar_with_mood_fallback(
            store,
            uid,
            age_band=age_band,
            escalation_level=str(settings.get("escalation_level") or "L0"),
            jung_enabled=FEATURE_WELLNESS_JUNG,
            message=message,
        )
        suggested = mood_routing["suggested_pillar"]
        src = mood_routing.get("mood_source") or "none"
        reason = "mood_fallback" if src not in ("checkin", "checkin_emoji", "none") else "checkin"
    return {
        "suggested_pillar": suggested,
        "age_band": age_band,
        "reason": reason,
        "pillar_fatigue": fatigue,
        "mood_routing": mood_routing,
    }


@router.get("/session/loop")
async def session_loop(
    locale: str = Depends(wellness_locale_dep),
    message: str = Query("", max_length=2000),
    requested_pillar: Optional[str] = Query(None, max_length=32),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    p3-01 — Wellness Loop Engine snapshot (triggers → escalation → ONE pillar → agents).

    Hub may call before Companion chat; chat uses the same logic when
    FEATURE_WELLNESS_ORCHESTRATOR=1.
    """
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    pillar_req = normalize_pillar(requested_pillar, age_band) if requested_pillar else None
    loop = run_wellness_loop(
        store,
        uid,
        message=message,
        age_band=age_band,
        locale=locale,
        requested_pillar=pillar_req,
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )
    pack: Dict[str, str] = {}
    if loop.primary_pillar:
        pack = session_pack_payload(store, uid, loop.primary_pillar, locale=locale)
    return {
        "ok": True,
        "orchestrator_enabled": FEATURE_WELLNESS_ORCHESTRATOR,
        "loop": wellness_loop_to_dict(loop, pack=pack or None),
        "pack": pack,
    }


@router.get("/session/plan")
async def session_plan(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-18 — lightweight self-help plan from latest assessments."""
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    settings = store.get_wellness_settings(uid)
    phq_score = None
    gad_score = None
    mbi_score = None
    for row in store.list_wellness_assessments(uid, limit=20):
        t = str(row.get("assessment_type") or "")
        score = row.get("score")
        if score is None:
            continue
        if t == "phq_lite" or t == "phq9":
            phq_score = int(score)
        elif t == "gad7":
            gad_score = int(score)
        elif t == "mbi_lite":
            mbi_score = int(score)
    routing = suggest_pillar_with_mood_fallback(
        store,
        uid,
        age_band=age_band,
        escalation_level=str(settings.get("escalation_level") or "L0"),
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )
    plan = build_wellness_plan(
        age_band=age_band,
        phq_score=phq_score,
        gad_score=gad_score,
        mbi_score=mbi_score,
        suggested_pillar=routing["suggested_pillar"],
        locale=locale,
    )
    return {"ok": True, "plan": plan, "mood_routing": routing}


@router.get("/session/recap")
async def session_recap(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    return build_session_recap(
        store,
        _uid(user),
        age_band=normalize_age_band(user.get("age_band")),
        locale=locale,
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )


@router.get("/exercises/catalog")
async def exercises_catalog(
    pillar: str = Query(..., pattern="^(cognitive|behavioral|humanistic|jung)$"),
    locale: str = Depends(wellness_locale_dep),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    age_band = normalize_age_band(user.get("age_band"))
    items = list_catalog(
        pillar,
        age_band=age_band,
        locale=locale,
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )
    return {"pillar": pillar, "exercises": items}


@router.get("/exercises/active")
async def exercises_active(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    session = get_active_session(get_companion_store(), _uid(user), locale=locale)
    if not session:
        return {"active": None}
    return {
        "active": {
            "id": session.id,
            "pillar": session.pillar,
            "exercise_id": session.exercise_id,
            "step_index": session.step_index,
            "step_total": session.step_total,
            "hint": session.hint,
            "completed": session.completed,
        }
    }


@router.post("/exercises/start")
async def exercises_start(
    body: ExerciseStartRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    if body.pillar == "jung" and not FEATURE_WELLNESS_JUNG:
        raise_wellness_error("jung_disabled", 403)
    try:
        session = start_exercise(
            get_companion_store(),
            _uid(user),
            pillar=body.pillar,
            exercise_id=body.exercise_id,
            age_band=age_band,
            locale=locale,
        )
    except PermissionError:
        raise_wellness_error("pillar_not_allowed_for_age", 403)
    except KeyError:
        raise_wellness_error("exercise_not_found", 404)
    return {
        "ok": True,
        "session": {
            "id": session.id,
            "pillar": session.pillar,
            "exercise_id": session.exercise_id,
            "step_index": session.step_index,
            "step_total": session.step_total,
            "hint": session.hint,
            "completed": session.completed,
        },
    }


@router.post("/exercises/{exercise_row_id}/step")
async def exercises_step(
    exercise_row_id: int,
    body: ExerciseStepRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    try:
        session = advance_exercise(
            get_companion_store(),
            _uid(user),
            exercise_row_id,
            answer=body.answer,
            locale=locale,
        )
    except KeyError:
        raise_wellness_error("exercise_not_found", 404)
    return {
        "ok": True,
        "session": {
            "id": session.id,
            "pillar": session.pillar,
            "exercise_id": session.exercise_id,
            "step_index": session.step_index,
            "step_total": session.step_total,
            "hint": session.hint,
            "completed": session.completed,
        },
    }


@router.get("/timeline")
async def wellness_timeline(
    locale: WellnessLocale,
    days: int = Query(14, ge=1, le=60),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-19 — journal + completed exercises summary (p3-06 premium)."""
    _require_wellness(locale, user=user)
    _require_consent(user, locale=locale)
    store = get_companion_store()
    uid = _uid(user)
    from security.services.ai_platform.wellness_premium_access import require_premium_features

    require_premium_features(
        store,
        uid,
        user,
        profile=store.get_consent(uid),
        age_band=normalize_age_band(user.get("age_band")),
        locale=locale,
    )
    return {
        "days": days,
        "checkins": store.list_wellness_checkins(uid, days=days),
        "exercises": store.list_wellness_exercises(uid, limit=days * 2),
        "outcomes": store.list_wellness_outcomes(uid, limit=20),
    }


@router.post("/outcomes")
async def post_outcome(
    body: OutcomeRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    uid = _uid(user)
    age_band = normalize_age_band(user.get("age_band"))
    result = record_outcome(
        store,
        uid,
        pillar=body.pillar,
        helpful=body.helpful,
        note=body.note,
        age_band=age_band,
    )
    adjustment = apply_outcome_pillar_adjustment(
        store,
        uid,
        helpful=body.helpful,
        pillar=result.pillar,
        age_band=age_band,
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )
    return {
        "ok": True,
        "outcome": {
            "id": result.id,
            "pillar": result.pillar,
            "helpful": result.helpful,
            "created_at": result.created_at,
        },
        "adjusted_pillar": adjustment.get("adjusted_pillar"),
        "settings": adjustment.get("settings"),
        "alliance": apply_alliance_for_outcome(store, uid, helpful=body.helpful),
    }


@router.post("/outcomes/dismiss-prompt")
async def dismiss_outcome_prompt_endpoint(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-31 — скрыть outcome push до завтра."""
    _require_wellness(user=user)
    _require_consent(user)
    settings = dismiss_outcome_prompt(get_companion_store(), _uid(user))
    return {"ok": True, "settings": settings}


@router.get("/reflective/modes")
async def reflective_modes(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    if not FEATURE_WELLNESS_REFLECTIVE:
        raise_wellness_error("reflective_disabled", 403)
    return {
        "enabled": True,
        "modes": list_reflective_modes(locale=locale),
    }


@router.get("/pillar/fatigue")
async def pillar_fatigue_status(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-32 — fatigue streak status."""
    _require_wellness(user=user)
    return evaluate_pillar_fatigue(
        get_companion_store(),
        _uid(user),
        age_band=normalize_age_band(user.get("age_band")),
        locale=locale,
        jung_enabled=FEATURE_WELLNESS_JUNG,
    )


@router.post("/habits")
async def create_habit(
    body: HabitPlanRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-05 — if-then habit plan."""
    _require_wellness(user=user)
    _require_consent(user)
    try:
        row = create_habit_plan(get_companion_store(), _uid(user), if_then=body.if_then)
    except ValueError:
        raise_wellness_error("if_then_too_short", 400)
    return {"ok": True, "habit": row}


@router.get("/habits")
async def list_habits(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    rows = list_habit_plans(get_companion_store(), _uid(user))
    return {"habits": rows}


@router.get("/assessments/mbi-lite/schema")
async def mbi_lite_schema_endpoint(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    try:
        assert_mbi_allowed(normalize_age_band(user.get("age_band")))
    except PermissionError:
        raise_wellness_error("mbi_lite_blocked_for_age", 403)
    return mbi_lite_schema(locale=locale)


@router.post("/assessments/mbi-lite/submit")
async def mbi_lite_submit(
    body: MbiLiteSubmitRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    try:
        assert_mbi_allowed(age_band)
    except PermissionError:
        raise_wellness_error("mbi_lite_blocked_for_age", 403)
    try:
        result = score_mbi_lite(body.answers, locale=locale)
    except ValueError as e:
        raise_wellness_error("wellness_generic", 400)
    store = get_companion_store()
    saved = store.save_wellness_assessment(
        _uid(user),
        assessment_type="mbi_lite",
        answers=body.answers,
        score=result.score,
        severity=result.severity,
        suggest_professional=result.suggest_professional,
    )
    return {
        "ok": True,
        "score": result.score,
        "severity": result.severity,
        "suggest_professional": result.suggest_professional,
        "disclaimer": result.disclaimer,
        "assessment": saved,
    }


@router.get("/reflective/resolve")
async def reflective_resolve(
    message: str = Query(..., min_length=1, max_length=500),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    if not FEATURE_WELLNESS_REFLECTIVE:
        raise_wellness_error("reflective_disabled", 403)
    mode = resolve_reflective_mode(message)
    return {"mode": mode}


@router.get("/dreams")
async def list_dreams(
    limit: int = Query(30, ge=1, le=100),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    if age_band == "child":
        raise_wellness_error("dreams_blocked_for_age", 403)
    if not FEATURE_WELLNESS_JUNG:
        raise_wellness_error("jung_disabled", 403)
    _require_premium_wellness(user)
    rows = get_companion_store().list_wellness_dreams(_uid(user), limit=limit)
    return {"dreams": rows}


@router.post("/dreams")
async def post_dream(
    body: DreamNoteRequest,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    _require_premium_wellness(user)
    age_band = normalize_age_band(user.get("age_band"))
    if age_band == "child":
        raise_wellness_error("dreams_blocked_for_age", 403)
    if not FEATURE_WELLNESS_JUNG:
        raise_wellness_error("jung_disabled", 403)
    row = get_companion_store().save_wellness_dream(
        _uid(user),
        dream_text=body.dream_text,
        mood_tag=body.mood_tag,
    )
    return {"ok": True, "dream": row}


@router.get("/alerts")
async def wellness_alerts(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    items = build_user_alerts(
        get_companion_store(),
        _uid(user),
        age_band=age_band,
        locale=locale,
    )
    streak = low_mood_streak_days(get_companion_store(), _uid(user), days=7)
    esc = evaluate_escalation("", days_low_mood=streak)
    if "social_bridge" in (esc.actions or []):
        from security.services.ai_platform.wellness_alerts import WellnessAlert, _t

        items = list(items) + [
            WellnessAlert(
                alert_type="social_bridge",
                severity="watch",
                title=_t(locale, "Поговори с близким", "Talk to someone close"),
                body=_t(
                    locale,
                    "Иногда помогает короткий разговор с тем, кому доверяешь.",
                    "A short talk with someone you trust can help.",
                ),
                action="open_companion",
            )
        ]
    return {
        "alerts": [
            {
                "alert_type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "body": a.body,
                "action": a.action,
            }
            for a in items
        ]
    }


@router.get("/family/dashboard")
async def family_dashboard(
    teen_user_id: str = Query(..., min_length=1, max_length=64),
    locale: str = Depends(wellness_locale_dep),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Родитель: сводка настроения teen (без текста чата), если teen включил share."""
    _require_wellness(user=user)
    age_band = normalize_age_band(user.get("age_band"))
    if age_band not in ("parent", "senior"):
        raise_wellness_error("parent_only", 403)
    return build_family_dashboard(
        get_companion_store(),
        teen_user_id,
        locale=locale,
    )


@router.get("/hub/copy")
async def hub_copy(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-38 — A/B pillar card copy keys."""
    _require_wellness(user=user)
    age_band = normalize_age_band(user.get("age_band"))
    pillars = pillars_for_age_band(age_band)
    return build_hub_copy(_uid(user), pillars=pillars, locale=locale)


@router.get("/weekly-meaning")
async def weekly_meaning(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    uid = _uid(user)
    payload = build_weekly_meaning(
        store, uid, locale=locale, age_band=normalize_age_band(user.get("age_band"))
    )
    return {"ok": True, **payload}


@router.post("/weekly-meaning/dismiss")
async def weekly_meaning_dismiss(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(user=user)
    _require_consent(user)
    settings = mark_weekly_meaning_shown(get_companion_store(), _uid(user))
    return {"ok": True, "settings": settings}


@router.get("/family/themes")
async def family_themes(
    teen_user_id: str = Query(..., min_length=1, max_length=64),
    locale: str = Depends(wellness_locale_dep),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-46 — themes for parent (no chat text)."""
    _require_wellness(user=user)
    if normalize_age_band(user.get("age_band")) not in ("parent", "senior"):
        raise_wellness_error("parent_only", 403)
    return build_family_themes_payload(
        get_companion_store(), teen_user_id, locale=locale
    )


@router.get("/parent/playbook")
async def parent_playbook(
    locale: str = Depends(wellness_locale_dep),
    topic: Optional[str] = Query(None, max_length=32),
    teen_mood: Optional[str] = Query(None, max_length=32),
    use_llm: bool = Query(False),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p18-13 / p3-16 — gentle talk scripts for parents (no chat text)."""
    _require_wellness(user=user)
    if normalize_age_band(user.get("age_band")) not in ("parent", "senior"):
        raise_wellness_error("parent_only", 403)
    return {
        "ok": True,
        **build_parent_playbook(
            locale=locale, topic=topic, teen_mood=teen_mood, use_llm=use_llm
        ),
    }


@router.get("/export/pdf-labels")
async def export_pdf_labels(
    locale: str = Depends(wellness_locale_dep),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p18-13 — localized PDF template labels (iOS weekly export / p3-19)."""
    _require_wellness(user=user)
    _require_consent(user)
    return {"ok": True, **weekly_pdf_labels_from_i18n(locale=locale)}


@router.get("/widget/copy")
async def widget_copy(
    locale: str = Depends(wellness_locale_dep),
) -> Dict[str, Any]:
    """p18-13 — widget strings for Widget Extension (p3-18)."""
    _require_wellness()
    return {"ok": True, **widget_copy_from_i18n(locale=locale)}


@router.get("/security/fusion")
async def security_fusion(
    teen_user_id: str = Query(..., min_length=1, max_length=64),
    online_threat: bool = Query(False),
    threat_summary: str = Query("", max_length=500),
    locale: str = Depends(wellness_locale_dep),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-47 — mood + security fused alert for parent."""
    _require_wellness(user=user)
    if normalize_age_band(user.get("age_band")) not in ("parent", "senior"):
        raise_wellness_error("parent_only", 403)
    alert = evaluate_security_mood_fusion(
        get_companion_store(),
        teen_user_id,
        online_threat=online_threat,
        threat_summary=threat_summary,
        locale=locale,
    )
    return {"ok": True, "alert": alert}


@router.get("/streaks")
async def wellness_streaks(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-48 — check-in streak + badges."""
    _require_wellness(user=user)
    return {
        "ok": True,
        "streaks": build_streaks_payload(
            get_companion_store(), _uid(user), locale=locale
        ),
    }


@router.get("/export/personal")
async def export_personal(
    locale: str = Depends(wellness_locale_dep),
    days: int = Query(90, ge=7, le=365),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-05 — full wellness export for data subject (152-ФЗ / GDPR-style)."""
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    return export_wellness_personal_data(
        get_companion_store(),
        _uid(user),
        days=days,
        locale=locale,
        age_band=age_band,
    )


@router.delete("/data")
async def delete_wellness_data(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-05 — erase all wellness rows for user; resets wellness consent."""
    _require_wellness(user=user)
    _require_consent(user)
    store = get_companion_store()
    uid = _uid(user)
    counts = delete_wellness_personal_data(store, uid)
    consent = store.get_consent(uid)
    consent["wellness_accepted"] = False
    consent.pop("wellness_accepted_at", None)
    store.set_consent(uid, consent)
    return {"ok": True, "deleted": counts}


@router.get("/export/clinician")
async def clinician_export(
    locale: str = Depends(wellness_locale_dep),
    days: int = Query(14, ge=7, le=30),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-37 — teen summary for specialist (JSON; share sheet on iOS)."""
    _require_wellness(user=user)
    _require_consent(user)
    age_band = normalize_age_band(user.get("age_band"))
    if age_band == "child":
        raise_wellness_error("clinician_export_teen_plus", 403)
    return build_clinician_export(
        get_companion_store(),
        _uid(user),
        days=days,
        locale=locale,
        age_band=age_band,
    )


@router.get("/together/session")
async def together_session(
    locale: WellnessLocale,
    duration_sec: int = Query(180, ge=60, le=600),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-44 — Together Mode breathing metadata."""
    _require_wellness(user=user)
    _require_consent(user)
    session = build_together_session(
        age_band=normalize_age_band(user.get("age_band")),
        locale=locale,
        duration_sec=duration_sec,
    )
    return {"ok": True, "session": session}


@router.get("/scheduler/reminders")
async def scheduler_reminders(
    locale: WellnessLocale,
    hour: int = Query(19, ge=0, le=23),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p2-25 — напоминание check-in после hour UTC (push = позже)."""
    _require_wellness(user=user)
    _require_consent(user)
    items = reminders_for_user(
        get_companion_store(),
        _uid(user),
        age_band=normalize_age_band(user.get("age_band")),
        locale=locale,
        target_hour=hour,
    )
    return {"reminders": items, "target_hour": hour}


@router.get("/errors/catalog")
async def wellness_errors_catalog(
    locale: WellnessLocale,
) -> Dict[str, Any]:
    """p18-15 — localized wellness API error codes for iOS."""
    from security.services.ai_platform.wellness_api_errors import build_errors_catalog

    return {"ok": True, "errors": build_errors_catalog(locale=locale)}


class ValuesCardSaveRequest(BaseModel):
    value_ids: List[str] = Field(default_factory=list)
    note: Optional[str] = Field(None, max_length=280)


class ElderlyJournalMergeRequest(BaseModel):
    days: int = Field(14, ge=1, le=60)
    entries: List[Dict[str, Any]] = Field(default_factory=list)


@router.get("/humanistic/values-card")
async def values_card_schema(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-07 — ACT values card schema."""
    _require_wellness(locale, user=user)
    _require_consent(user, locale=locale)
    from security.services.ai_platform.wellness_values_card import (
        build_values_card_schema,
        get_values_card,
    )

    store = get_companion_store()
    return {
        "ok": True,
        "schema": build_values_card_schema(locale=locale),
        **get_values_card(store, _uid(user)),
    }


@router.post("/humanistic/values-card")
async def values_card_save(
    body: ValuesCardSaveRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_wellness(locale, user=user)
    _require_consent(user, locale=locale)
    from security.services.ai_platform.wellness_values_card import save_values_card

    return save_values_card(
        get_companion_store(),
        _uid(user),
        value_ids=body.value_ids,
        note=body.note,
    )


@router.post("/senior/journal/merge")
async def senior_journal_merge(
    body: ElderlyJournalMergeRequest,
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-08 — merge wellness check-ins + elderly health journal."""
    _require_wellness(locale, user=user)
    _require_consent(user, locale=locale)
    if normalize_age_band(user.get("age_band")) != "senior":
        raise_wellness_error("pillar_not_allowed_for_age", locale=locale)
    from security.services.ai_platform.wellness_elderly_journal import merge_senior_journal

    return {
        "ok": True,
        **merge_senior_journal(
            get_companion_store(),
            _uid(user),
            days=body.days,
            elderly_entries=body.entries,
        ),
    }


@router.get("/pillar/rive")
async def pillar_rive(
    locale: WellnessLocale,
    pillar: str = Query("humanistic"),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-09 — Rive + TTS hints per pillar."""
    _require_wellness(locale, user=user)
    from security.services.ai_platform.wellness_pillar_rive import pillar_rive_payload

    return {"ok": True, "rive": pillar_rive_payload(pillar, locale=locale)}


@router.get("/family/talk-prompts")
async def family_talk_prompts(
    locale: WellnessLocale,
    topic: str = Query("mood", max_length=32),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-13 — parent «как поговорить» prompts."""
    _require_wellness(locale, user=user)
    if normalize_age_band(user.get("age_band")) not in ("parent", "senior"):
        raise_wellness_error("parent_only", locale=locale)
    from security.services.ai_platform.wellness_family_prompt import build_family_talk_prompts

    return {
        "ok": True,
        **build_family_talk_prompts(
            locale=locale,
            topic=topic,
            age_band=normalize_age_band(user.get("age_band")),
        ),
    }


@router.get("/seasonal/playbooks")
async def seasonal_playbooks(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-14 — school / exams seasonal tips."""
    _require_wellness(locale, user=user)
    from security.services.ai_platform.wellness_seasonal import list_seasonal_playbooks

    return {"ok": True, "playbooks": list_seasonal_playbooks(locale=locale)}


@router.get("/senior/voice-session")
async def senior_voice_session(
    locale: WellnessLocale,
    pillar: str = Query("humanistic"),
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-15 — voice-first senior session metadata."""
    _require_wellness(locale, user=user)
    _require_consent(user, locale=locale)
    from security.services.ai_platform.wellness_voice_senior import build_senior_voice_session

    return {
        "ok": True,
        "session": build_senior_voice_session(pillar=pillar, locale=locale),
    }


@router.get("/sleep/stories")
async def sleep_stories(
    locale: WellnessLocale,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-17 — wind-down audio catalog."""
    _require_wellness(locale, user=user)
    _require_consent(user, locale=locale)
    from security.services.ai_platform.wellness_sleep_stories import list_sleep_stories

    return {"ok": True, "stories": list_sleep_stories(locale=locale)}


@router.get("/canary/status")
async def wellness_canary_status(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-10 — canary cohort status for current user (ops + client debug)."""
    _require_wellness(user=user)
    from security.services.ai_platform.wellness_canary import build_canary_status

    return {"ok": True, **build_canary_status(user_id=_uid(user))}


@router.get("/store/backend")
async def wellness_store_backend_status(
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """p3-11 — Postgres migration status (ops)."""
    _require_wellness(user=user)
    from security.services.ai_platform.wellness_store_postgres import WellnessPostgresStore
    from security.services.ai_platform.wellness_canary import build_canary_status

    return {
        "ok": True,
        **WellnessPostgresStore().ping(),
        "canary": build_canary_status(user_id=_uid(user)),
    }
