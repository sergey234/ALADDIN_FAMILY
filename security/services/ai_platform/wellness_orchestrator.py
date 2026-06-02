# -*- coding: utf-8 -*-
"""
Wellness orchestrator (p1-18 guard, p3-01 full Wellness Loop).

When FEATURE_WELLNESS_ORCHESTRATOR=1, `prepare_wellness_chat_turn` runs:
  triggers → screening escalation → pillar select → session prefix → agent registry.

Post-LLM: `apply_response_guard` — one pillar per reply.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .wellness_alliance import apply_alliance_for_crisis, apply_alliance_for_trauma_trigger
from .wellness_escalation import EscalationResult, evaluate_escalation
from .wellness_four_pillars import normalize_pillar
from .wellness_journal import low_mood_streak_days
from .wellness_mood_routing import suggest_pillar_with_mood_fallback
from .wellness_pillar_fatigue import evaluate_pillar_fatigue
from .wellness_pillar_guard import PillarGuardResult, assert_single_pillar
from .wellness_prompt_builder import (
    WellnessExerciseContext,
    WellnessPrefixContext,
    build_pillar_prompt_block,
    build_wellness_prefix,
    load_pillar_pack,
)
from .wellness_reflective_modes import resolve_reflective_mode
from .wellness_reflective_prompt import build_reflective_prompt_block
from .wellness_session_recap import build_session_recap
from .wellness_trauma_referral import (
    evaluate_trauma_referral,
    trauma_safety_prompt_block,
)
from .wellness_triggers import evaluate_triggers
from .wellness_agent_hints import build_wellness_agents_block
from .wellness_pack_registry import get_session_pack, session_pack_payload

# Leakage phrases → other pillars (ru + en), per active pillar
_PILLAR_LEAK_PATTERNS: Dict[str, List[str]] = {
    "cognitive": [
        r"маленьк(?:ий|ая)\s+шаг",
        r"привычк",
        r"if-?then",
        r"заземлен",
        r"box\s+breathing",
        r"5-4-3-2-1",
        r"побудь\s+рядом",
        r"сон.*символ",
        r"архетип",
        r"юнг",
        r"jung",
        r"dream\s+symbol",
    ],
    "behavioral": [
        r"мысль-ловуш",
        r"переформулир",
        r"факт.*догадк",
        r"когнитивн",
        r"cbt",
        r"заземлен",
        r"архетип",
        r"сны.*знач",
        r"jung",
    ],
    "humanistic": [
        r"мысль-ловуш",
        r"переформулир",
        r"phq",
        r"привычк",
        r"маленьк(?:ий|ая)\s+шаг",
        r"архетип",
        r"юнг",
    ],
    "jung": [
        r"мысль-ловуш",
        r"переформулир",
        r"phq-?\d",
        r"маленьк(?:ий|ая)\s+шаг",
        r"привычк",
        r"заземлен",
        r"box\s+breathing",
    ],
}

_THERAPY_CLAIM = re.compile(
    r"(психотерап|психолог\w*\s+лечит|я\s+врач|диагноз\s+—|"
    r"psychotherapist|i\s+am\s+your\s+therapist|clinical\s+diagnosis)",
    re.I,
)

# p3-02 — agent registry (Phase 3 target; used in loop metadata / tools_used)
WELLNESS_AGENTS: Dict[str, List[str]] = {
    "cognitive": ["cbt_coach_agent"],
    "behavioral": ["habit_coach_agent"],
    "humanistic": ["presence_coach_agent"],
    "jung": ["symbol_coach_agent", "reflective_agent"],
    "screening": ["clinical_screening_agent"],
    "crisis": ["crisis_agent", "self_harm_detection_agent"],
    "family": ["family_bridge_agent"],
}


class WellnessLoopPhase(str, Enum):
    GUARD_FAIL = "guard_fail"
    CRISIS_L3 = "crisis_l3"
    SCREENING = "screening"
    SESSION = "session"
    IDLE = "idle"


@dataclass(frozen=True)
class OrchestratorGuardResult:
    ok: bool
    text: str
    reason: str = ""


@dataclass
class WellnessLoopResult:
    phase: WellnessLoopPhase
    guard: PillarGuardResult
    escalation: EscalationResult
    primary_pillar: Optional[str] = None
    trauma_block: str = ""
    triggers: Dict[str, Any] = field(default_factory=dict)
    agents_active: List[str] = field(default_factory=list)
    suggest_phq_lite: bool = False
    fatigue_message: Optional[str] = None


@dataclass
class WellnessChatPrep:
    ok: bool
    reason: str = ""
    active_pillar: Optional[str] = None
    wellness_prefix: str = ""
    escalation: Optional[EscalationResult] = None
    agents_active: List[str] = field(default_factory=list)
    loop_phase: str = "legacy"


def orchestrator_instruction_block(primary_pillar: str, locale: str = "ru") -> str:
    """Extra hard rule appended to [WELLNESS v1] block."""
    pack = load_pillar_pack(primary_pillar, locale=locale)
    forbidden = ", ".join(pack.get("forbidden_concepts") or [])
    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        return (
            f"[WELLNESS ORCHESTRATOR] Stay ONLY in pillar={primary_pillar}. "
            f"Never mix other pillars in this reply. Forbidden: {forbidden}."
        )
    return (
        f"[WELLNESS ORCHESTRATOR] Только столп={primary_pillar}. "
        f"Не смешивай другие дорожки в этом ответе. Запрещено: {forbidden}."
    )


def scan_pillar_drift(text: str, primary_pillar: str) -> Optional[str]:
    """Return leak reason if another pillar detected."""
    if not text or not primary_pillar:
        return None
    patterns = _PILLAR_LEAK_PATTERNS.get(primary_pillar) or []
    for pat in patterns:
        if re.search(pat, text, re.I):
            return f"pillar_drift:{pat}"
    pack = load_pillar_pack(primary_pillar)
    phrases = pack.get("forbidden_phrases") or {}
    ru_list = phrases.get("ru") if isinstance(phrases, dict) else []
    if isinstance(ru_list, list):
        for p in ru_list:
            if p and re.search(re.escape(str(p)), text, re.I):
                return f"forbidden_phrase:{p}"
    if _THERAPY_CLAIM.search(text):
        return "therapy_claim"
    return None


def apply_response_guard(
    response_text: str,
    *,
    primary_pillar: str,
    locale: str = "ru",
) -> OrchestratorGuardResult:
    """Post-LLM guard: one pillar per answer."""
    drift = scan_pillar_drift(response_text or "", primary_pillar)
    if not drift:
        return OrchestratorGuardResult(ok=True, text=response_text or "")
    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        safe = (
            "Let's stay with one focus for now — only this path in this message. "
            "What feels most important in that?"
        )
    else:
        safe = (
            "Давай останемся в одной дорожке в этом сообщении — без смешивания тем. "
            "Что сейчас важнее всего для тебя?"
        )
    return OrchestratorGuardResult(ok=False, text=safe, reason=drift)


def teen_default_parent_share(age_band: str, explicit: Optional[int]) -> int:
    """p1-23: teen aggregate OFF unless explicitly enabled."""
    band = (age_band or "").lower()
    if band != "teen":
        return int(explicit) if explicit is not None else 0
    if explicit is None:
        return 0
    return 1 if int(explicit) else 0


def _latest_phq_lite_score(store: Any, user_id: str) -> Optional[int]:
    for row in store.list_wellness_assessments(user_id, limit=10) or []:
        if (row.get("assessment_type") or "") == "phq_lite":
            score = row.get("score")
            if score is not None:
                return int(score)
    return None


def wellness_loop_to_dict(loop: WellnessLoopResult, *, pack: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """JSON-safe Wellness Loop snapshot for Hub / debug API."""
    out = {
        "phase": loop.phase.value,
        "primary_pillar": loop.primary_pillar,
        "escalation_level": loop.escalation.level,
        "escalation_reason": loop.escalation.reason,
        "escalation_actions": list(loop.escalation.actions),
        "agents_active": list(loop.agents_active),
        "suggest_phq_lite": loop.suggest_phq_lite,
        "guard_ok": loop.guard.ok,
        "guard_reason": loop.guard.reason,
        "fatigue_message": loop.fatigue_message,
        "triggers": dict(loop.triggers or {}),
    }
    if pack:
        out["pack_folder"] = pack.get("pack_folder")
        out["pack_version"] = pack.get("pack_version")
    return out


def resolve_agents_for_turn(
    *,
    pillar: Optional[str],
    escalation: EscalationResult,
    suggest_phq_lite: bool,
) -> List[str]:
    """Map pillar + escalation to active agent ids (p3-02)."""
    agents: List[str] = []
    if escalation.level == "L3":
        agents.extend(WELLNESS_AGENTS["crisis"])
        return list(dict.fromkeys(agents))
    if suggest_phq_lite or escalation.level in ("L1", "L2"):
        agents.extend(WELLNESS_AGENTS["screening"])
    if pillar and pillar in WELLNESS_AGENTS:
        agents.extend(WELLNESS_AGENTS[pillar])
    return list(dict.fromkeys(agents))


def run_wellness_loop(
    store: Any,
    user_id: str,
    *,
    message: str,
    age_band: str,
    locale: str,
    requested_pillar: Optional[str],
    jung_enabled: bool,
) -> WellnessLoopResult:
    """
    Full Wellness Loop (p3-01): deterministic pre-LLM chain.

    Hub/check-in → triggers/screening → ONE pillar → session agents.
    """
    loc = (locale or "ru").lower()[:2]
    ws = store.get_wellness_settings(user_id)
    guard = assert_single_pillar(
        session_pillar=ws.get("primary_pillar"),
        requested_pillar=requested_pillar,
        age_band=age_band,
    )
    if not guard.ok:
        return WellnessLoopResult(
            phase=WellnessLoopPhase.GUARD_FAIL,
            guard=guard,
            escalation=evaluate_escalation(message or ""),
        )

    triggers = evaluate_triggers(store, user_id, age_band=age_band, locale=loc)
    streak = int(triggers.get("low_mood_streak_days") or 0)
    phq_score = _latest_phq_lite_score(store, user_id)
    esc = evaluate_escalation(
        message or "",
        phq_lite_score=phq_score,
        days_low_mood=streak,
    )

    if esc.level == "L3":
        from .wellness_crisis_monitor import record_crisis_l3

        record_crisis_l3(store, user_id, source="wellness_loop_l3")
        apply_alliance_for_crisis(store, user_id)
        crisis_agents = resolve_agents_for_turn(
            pillar=None, escalation=esc, suggest_phq_lite=False
        )
        return WellnessLoopResult(
            phase=WellnessLoopPhase.CRISIS_L3,
            guard=guard,
            escalation=esc,
            triggers=triggers,
            agents_active=crisis_agents,
            suggest_phq_lite=bool(triggers.get("suggest_phq_lite")),
        )

    pillar = guard.primary_pillar
    if not pillar:
        mood = suggest_pillar_with_mood_fallback(
            store,
            user_id,
            age_band=age_band,
            escalation_level=esc.level,
            jung_enabled=jung_enabled,
            message=message or "",
        )
        pillar = normalize_pillar(mood.get("suggested_pillar"), age_band)

    fatigue = evaluate_pillar_fatigue(
        store,
        user_id,
        age_band=age_band,
        locale=loc,
        jung_enabled=jung_enabled,
    )
    if fatigue.get("fatigued") and fatigue.get("suggested_pillar"):
        alt = normalize_pillar(fatigue.get("suggested_pillar"), age_band)
        if alt:
            pillar = alt

    if pillar == "jung" and not jung_enabled:
        pillar = normalize_pillar("humanistic", age_band) or pillar

    if esc.reason == "trauma_keywords":
        apply_alliance_for_trauma_trigger(store, user_id)
        tr = evaluate_trauma_referral(
            message or "",
            age_band=age_band,
            locale=loc,
        )
        if tr.redirect_pillar:
            pillar = normalize_pillar(tr.redirect_pillar, age_band) or pillar

    agents = resolve_agents_for_turn(
        pillar=pillar,
        escalation=esc,
        suggest_phq_lite=bool(triggers.get("suggest_phq_lite")),
    )

    phase = WellnessLoopPhase.SESSION if pillar else WellnessLoopPhase.IDLE
    if triggers.get("suggest_phq_lite") and not pillar:
        phase = WellnessLoopPhase.SCREENING

    return WellnessLoopResult(
        phase=phase,
        guard=PillarGuardResult(ok=True, primary_pillar=pillar),
        escalation=esc,
        primary_pillar=pillar,
        triggers=triggers,
        agents_active=agents,
        suggest_phq_lite=bool(triggers.get("suggest_phq_lite")),
        fatigue_message=fatigue.get("message"),
    )


def build_wellness_prefix_for_session(
    store: Any,
    user_id: str,
    *,
    pillar_for_chat: str,
    escalation_level: str,
    age_band: str,
    locale: str,
    character_id: str,
    message: str,
    jung_enabled: bool,
    reflective_enabled: bool,
    ws: Optional[Dict[str, Any]] = None,
    trauma_block: str = "",
    fatigue_message: Optional[str] = None,
    agents_active: Optional[List[str]] = None,
) -> tuple[str, str]:
    """Returns (wellness_prefix, final_pillar)."""
    ws = ws or store.get_wellness_settings(user_id)
    loc = (locale or "ru").lower()[:2]
    pack_folder, pack_version_label = get_session_pack(
        store, user_id, pillar_for_chat, locale=loc
    )
    ex_ctx = None
    if ws.get("exercise_id"):
        ex_ctx = WellnessExerciseContext(
            str(ws.get("exercise_id")),
            int(ws.get("exercise_step") or 1),
            int(ws.get("exercise_step_total") or 0) or 5,
        )

    wp_ctx = WellnessPrefixContext(
        primary_pillar=pillar_for_chat,
        escalation=escalation_level,
        age_band=age_band,
        exercise=ex_ctx,
        character_id=character_id,
        locale=loc,
        pack_folder=pack_folder,
        pack_version=pack_version_label,
    )
    recap = build_session_recap(
        store,
        user_id,
        age_band=age_band,
        locale=loc,
        jung_enabled=jung_enabled,
    )
    continuity = str(recap.get("continuity_message") or "")
    continuity_block = ""
    if continuity:
        continuity_block = f"[WELLNESS CONTINUITY]\n{continuity.strip()}\n"
    fatigue_block = ""
    if fatigue_message:
        fatigue_block = f"[WELLNESS FATIGUE]\n{fatigue_message.strip()}\n"

    reflective_block = ""
    if reflective_enabled and pillar_for_chat == "jung":
        rmode = resolve_reflective_mode(message or "")
        if rmode:
            reflective_block, rguard = build_reflective_prompt_block(
                mode=rmode,
                age_band=age_band,
                locale=loc,
                reflective_enabled=True,
                jung_enabled=jung_enabled,
                escalation_level=escalation_level,
            )
            if rguard.redirect_pillar == "humanistic":
                pillar_for_chat = "humanistic"
                wp_ctx = WellnessPrefixContext(
                    primary_pillar="humanistic",
                    escalation=escalation_level,
                    age_band=age_band,
                    exercise=ex_ctx,
                    character_id=character_id,
                    locale=loc,
                    pack_folder=pack_folder,
                    pack_version=pack_version_label,
                )

    agents_block = build_wellness_agents_block(agents_active or [], locale=loc)
    prefix = (
        trauma_block
        + fatigue_block
        + continuity_block
        + build_wellness_prefix(wp_ctx)
        + build_pillar_prompt_block(wp_ctx, jung_enabled=jung_enabled)
        + reflective_block
        + agents_block
        + orchestrator_instruction_block(pillar_for_chat, loc)
        + "\n"
    )
    return prefix, pillar_for_chat


def prepare_wellness_chat_turn(
    store: Any,
    user_id: str,
    *,
    message: str,
    age_band: str,
    locale: str,
    requested_pillar: Optional[str],
    character_id: str,
    jung_enabled: bool,
    reflective_enabled: bool,
    use_full_loop: bool = False,
) -> WellnessChatPrep:
    """
    Single entry for ai_companion_router wellness block.

    use_full_loop=True when FEATURE_WELLNESS_ORCHESTRATOR=1 (p3-03).
    """
    loc = (locale or "ru").lower()[:2]
    ws = store.get_wellness_settings(user_id)

    if use_full_loop:
        loop = run_wellness_loop(
            store,
            user_id,
            message=message,
            age_band=age_band,
            locale=loc,
            requested_pillar=requested_pillar,
            jung_enabled=jung_enabled,
        )
        if loop.phase == WellnessLoopPhase.GUARD_FAIL:
            return WellnessChatPrep(ok=False, reason=loop.guard.reason, loop_phase="guard_fail")
        if loop.phase == WellnessLoopPhase.CRISIS_L3:
            return WellnessChatPrep(
                ok=True,
                active_pillar=None,
                wellness_prefix="",
                escalation=loop.escalation,
                agents_active=loop.agents_active,
                loop_phase="crisis_l3",
            )
        pillar = loop.primary_pillar
        esc = loop.escalation
        trauma_block = ""
        if esc.reason == "trauma_keywords":
            trauma_block = trauma_safety_prompt_block(
                message,
                age_band=age_band,
                locale=loc,
            )
        if not pillar or esc.level == "L3":
            return WellnessChatPrep(
                ok=True,
                escalation=esc,
                agents_active=loop.agents_active,
                loop_phase=loop.phase.value,
            )
        prefix, pillar = build_wellness_prefix_for_session(
            store,
            user_id,
            pillar_for_chat=pillar,
            escalation_level=esc.level,
            age_band=age_band,
            locale=loc,
            character_id=character_id,
            message=message,
            jung_enabled=jung_enabled,
            reflective_enabled=reflective_enabled,
            ws=ws,
            trauma_block=trauma_block,
            fatigue_message=loop.fatigue_message,
            agents_active=loop.agents_active,
        )
        store.upsert_wellness_settings(
            user_id,
            primary_pillar=pillar,
            escalation_level=esc.level,
        )
        return WellnessChatPrep(
            ok=True,
            active_pillar=pillar,
            wellness_prefix=prefix,
            escalation=esc,
            agents_active=loop.agents_active,
            loop_phase=loop.phase.value,
        )

    # Legacy path (pillar router v1 — only when session/request pillar exists)
    guard = assert_single_pillar(
        session_pillar=ws.get("primary_pillar"),
        requested_pillar=requested_pillar,
        age_band=age_band,
    )
    if not guard.ok:
        return WellnessChatPrep(ok=False, reason=guard.reason, loop_phase="guard_fail")

    if not guard.primary_pillar:
        return WellnessChatPrep(ok=True, loop_phase="idle")

    pillar_for_chat = guard.primary_pillar
    if pillar_for_chat == "jung" and not jung_enabled:
        return WellnessChatPrep(ok=True, loop_phase="idle")

    streak = low_mood_streak_days(store, user_id, days=7)
    phq_score = _latest_phq_lite_score(store, user_id)
    esc = evaluate_escalation(
        message or "",
        phq_lite_score=phq_score,
        days_low_mood=streak,
    )
    trauma_block = ""
    if esc.level == "L3":
        from .wellness_crisis_monitor import record_crisis_l3

        record_crisis_l3(store, user_id, source="wellness_chat_l3")
        apply_alliance_for_crisis(store, user_id)
        return WellnessChatPrep(
            ok=True,
            escalation=esc,
            loop_phase="crisis_l3",
        )
    if esc.reason == "trauma_keywords":
        apply_alliance_for_trauma_trigger(store, user_id)
        tr = evaluate_trauma_referral(message, age_band=age_band, locale=loc)
        if tr.redirect_pillar:
            pillar_for_chat = tr.redirect_pillar or pillar_for_chat
        trauma_block = trauma_safety_prompt_block(
            message, age_band=age_band, locale=loc
        )

    agents = resolve_agents_for_turn(
        pillar=pillar_for_chat,
        escalation=esc,
        suggest_phq_lite=False,
    )
    prefix, pillar_for_chat = build_wellness_prefix_for_session(
        store,
        user_id,
        pillar_for_chat=pillar_for_chat,
        escalation_level=esc.level,
        age_band=age_band,
        locale=loc,
        character_id=character_id,
        message=message,
        jung_enabled=jung_enabled,
        reflective_enabled=reflective_enabled,
        ws=ws,
        trauma_block=trauma_block,
        agents_active=agents,
    )
    store.upsert_wellness_settings(
        user_id,
        primary_pillar=pillar_for_chat,
        escalation_level=esc.level,
    )
    return WellnessChatPrep(
        ok=True,
        active_pillar=pillar_for_chat,
        wellness_prefix=prefix,
        escalation=esc,
        agents_active=agents,
        loop_phase="legacy",
    )
