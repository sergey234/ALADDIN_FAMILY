# -*- coding: utf-8 -*-
"""Wellness i18n loader — locale resolution, assessments JSON, crisis copy (p18-04…06)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_I18N_ROOT = Path(__file__).resolve().parent / "wellness_i18n"


def normalize_wellness_locale(locale: Optional[str], *, default: str = "ru") -> str:
    loc = (locale or default or "ru").strip().lower()
    if loc.startswith("en"):
        return "en"
    return "ru"


def _parse_accept_language(header: Optional[str]) -> Optional[str]:
    if not header:
        return None
    for part in header.split(","):
        token = part.strip().split(";")[0].lower()
        if not token:
            continue
        if token.startswith("en"):
            return "en"
        if token.startswith("ru"):
            return "ru"
    return None


def resolve_wellness_locale(
    *,
    query_locale: Optional[str] = None,
    accept_language: Optional[str] = None,
    default: str = "ru",
) -> str:
    """Accept-Language wins over ?locale= (p18-05)."""
    parsed = _parse_accept_language(accept_language)
    if parsed:
        return parsed
    if query_locale:
        return normalize_wellness_locale(query_locale, default=default)
    return normalize_wellness_locale(default, default=default)


@lru_cache(maxsize=32)
def _load_json(relative_path: str) -> Dict[str, Any]:
    path = _I18N_ROOT / relative_path
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_assessment_pack(name: str) -> Dict[str, Any]:
    return _load_json(f"assessments/{name}.json")


def phq_lite_schema_from_i18n(*, locale: str = "ru") -> Optional[Dict[str, Any]]:
    try:
        pack = load_assessment_pack("phq_lite_v1")
    except (OSError, json.JSONDecodeError, KeyError):
        return None
    loc = normalize_wellness_locale(locale)
    questions = [
        {"id": q["id"], "text": q.get(loc) or q.get("ru", "")}
        for q in pack.get("questions", [])
    ]
    opts = []
    for o in pack.get("answer_options", []):
        opts.append(
            {
                "value": o["value"],
                "label_key": o.get("label_key", ""),
                "label": o.get(loc) or o.get("ru", ""),
            }
        )
    disclaimer = pack.get("disclaimer", {})
    return {
        "assessment_type": pack.get("assessment_type", "phq_lite"),
        "version": pack.get("version", "v1"),
        "disclaimer": disclaimer.get(loc) or disclaimer.get("ru", ""),
        "questions": questions,
        "answer_options": opts,
        "max_score": pack.get("max_score", 15),
    }


def wellness_crisis_message(locale: str = "ru") -> str:
    try:
        data = _load_json("crisis_v1.json")
        block = data.get("crisis_message", {})
        loc = normalize_wellness_locale(locale)
        return block.get(loc) or block.get("ru", "")
    except (OSError, json.JSONDecodeError, KeyError):
        return ""


def wellness_crisis_deep_blocked(locale: str = "ru") -> str:
    try:
        data = _load_json("crisis_v1.json")
        block = data.get("crisis_deep_blocked", {})
        loc = normalize_wellness_locale(locale)
        return block.get(loc) or block.get("ru", "")
    except (OSError, json.JSONDecodeError, KeyError):
        return ""


def wellness_action_title(action_id: str, locale: str = "ru") -> str:
    try:
        data = _load_json("crisis_v1.json")
        block = data.get("actions", {}).get(action_id, {})
        loc = normalize_wellness_locale(locale)
        return block.get(loc) or block.get("ru", action_id)
    except (OSError, json.JSONDecodeError, KeyError):
        return action_id


def wellness_suggested_actions_for_level(
    level: str,
    locale: str = "ru",
    *,
    extra_action_ids: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """Build suggested_actions payloads for chat (p18-06)."""
    loc = normalize_wellness_locale(locale)
    ids: List[str] = []
    try:
        data = _load_json("crisis_v1.json")
        ids.extend(data.get("levels", {}).get(level.upper(), []))
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    if extra_action_ids:
        ids.extend(extra_action_ids)
    seen: set[str] = set()
    out: List[Dict[str, str]] = []
    for action_id in ids:
        if action_id in seen:
            continue
        seen.add(action_id)
        out.append({"id": action_id, "title": wellness_action_title(action_id, loc)})
    return out


_ESCALATION_TO_ACTIONS: Dict[str, List[str]] = {
    "call_112": ["wellness_referral_112"],
    "tell_trusted_adult": ["wellness_open_referral"],
    "block_deep_modes": [],
    "referral_specialist": ["wellness_open_referral"],
    "open_referral_sheet": ["wellness_open_referral"],
    "referral_map": ["wellness_open_referral"],
    "suggest_professional": ["wellness_open_referral"],
    "social_bridge": ["wellness_open_referral"],
    "referral_soft": ["wellness_open_referral"],
    "offer_phq_lite": ["wellness_action_open_assessment"],
}


def wellness_suggested_actions_for_escalation(
    level: str,
    locale: str = "ru",
    *,
    escalation_actions: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    extra: List[str] = []
    for code in escalation_actions or []:
        extra.extend(_ESCALATION_TO_ACTIONS.get(code, []))
    return wellness_suggested_actions_for_level(level, locale, extra_action_ids=extra)


def load_exercise_pack(exercise_id: str) -> Optional[Dict[str, Any]]:
    """Load exercise steps from wellness_i18n/exercises/{id}_v1.json (p18-08)."""
    try:
        return _load_json(f"exercises/{exercise_id}_v1.json")
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def exercise_meta_from_i18n(exercise_id: str) -> Optional[Dict[str, Any]]:
    pack = load_exercise_pack(exercise_id)
    if not pack:
        return None
    steps: List[Dict[str, Any]] = []
    for step in pack.get("steps") or []:
        row: Dict[str, Any] = {"step": step.get("step")}
        if "hint" in step:
            row["hint"] = step["hint"]
        if "instruction" in step:
            row["instruction"] = step["instruction"]
        if "llm_rephrase_only" in step:
            row["llm_rephrase_only"] = step["llm_rephrase_only"]
        steps.append(row)
    total = int(pack.get("total_steps") or len(steps) or 1)
    return {
        "exercise_id": pack.get("exercise_id", exercise_id),
        "pillar": pack.get("pillar"),
        "total_steps": total,
        "steps": steps,
        "title": pack.get("title") or {},
    }


def exercise_title_i18n(exercise_id: str, locale: str = "ru") -> str:
    meta = exercise_meta_from_i18n(exercise_id)
    if not meta:
        return exercise_id
    title = meta.get("title") or {}
    loc = normalize_wellness_locale(locale)
    return str(title.get(loc) or title.get("ru") or exercise_id)


def list_i18n_exercise_ids() -> List[str]:
    try:
        manifest = _load_json("exercises/manifest.json")
        return list(manifest.get("exercises") or [])
    except (OSError, json.JSONDecodeError, KeyError):
        return []


def i18n_block_text(block: Optional[Dict[str, Any]], locale: str, *, default: str = "") -> str:
    if not block:
        return default
    loc = normalize_wellness_locale(locale)
    return str(block.get(loc) or block.get("ru") or default)


def list_reflective_modes_from_i18n(*, locale: str = "ru") -> List[Dict[str, Any]]:
    """Reflective sub-modes with label_key + resolved label/hint (p18-09)."""
    try:
        data = _load_json("reflective_modes_v1.json")
    except (OSError, json.JSONDecodeError, KeyError):
        return []
    loc = normalize_wellness_locale(locale)
    out: List[Dict[str, Any]] = []
    for mode in data.get("modes") or []:
        out.append(
            {
                "id": mode.get("id", ""),
                "label_key": mode.get("label_key", ""),
                "hint_key": mode.get("hint_key", ""),
                "label": i18n_block_text(mode.get("label"), loc),
                "hint": i18n_block_text(mode.get("hint"), loc),
                "pillar": mode.get("pillar"),
            }
        )
    return out


def get_referral_payload_from_i18n(*, locale: str = "ru", level: str = "L2") -> Dict[str, Any]:
    try:
        data = _load_json("referral_v1.json")
    except (OSError, json.JSONDecodeError, KeyError):
        return {"level": level, "locale": locale, "disclaimer": "", "lines": []}
    loc = normalize_wellness_locale(locale)
    lines: List[Dict[str, str]] = []
    for row in data.get("lines") or []:
        if loc == "en" and row.get("id") == "mchs":
            continue
        lines.append(
            {
                "id": str(row.get("id") or ""),
                "label_key": str(row.get("label_key") or ""),
                "label": i18n_block_text(row.get("label"), loc),
                "phone": str(row.get("phone") or ""),
            }
        )
    return {
        "level": level,
        "locale": loc,
        "disclaimer": i18n_block_text(data.get("disclaimer"), loc),
        "lines": lines,
    }


def outcome_reminder_from_i18n(*, locale: str = "ru") -> Dict[str, str]:
    try:
        data = _load_json("outcome_v1.json")
        block = data.get("outcome_reminder") or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return {"title": "", "body": ""}
    loc = normalize_wellness_locale(locale)
    return {
        "title": i18n_block_text(block.get("title"), loc),
        "body": i18n_block_text(block.get("body"), loc),
    }


def weekly_meaning_from_i18n(
    *,
    locale: str = "ru",
    observe_text: str = "",
) -> Dict[str, str]:
    try:
        data = _load_json("outcome_v1.json")
        block = data.get("weekly_meaning") or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return {"title": "", "body": "", "prompt": ""}
    loc = normalize_wellness_locale(locale)
    prompt = i18n_block_text(block.get("prompt"), loc)
    if observe_text.strip():
        tpl = i18n_block_text(block.get("prompt_with_observe"), loc, default="%s")
        prompt = tpl.replace("%@", observe_text).replace("%s", observe_text)
    return {
        "title": i18n_block_text(block.get("title"), loc),
        "body": i18n_block_text(block.get("body"), loc),
        "prompt": prompt,
    }


def session_recap_message_from_i18n(
    *,
    locale: str = "ru",
    active_exercise: bool = False,
    low_mood: bool = False,
) -> str:
    try:
        data = _load_json("outcome_v1.json")
        block = data.get("session_recap") or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return ""
    loc = normalize_wellness_locale(locale)
    if active_exercise:
        return i18n_block_text(block.get("active_exercise"), loc)
    if low_mood:
        return i18n_block_text(block.get("low_mood"), loc)
    return i18n_block_text(block.get("default"), loc)


def continuity_prefix_message(*, locale: str = "ru", observe_text: str) -> str:
    try:
        data = _load_json("outcome_v1.json")
        tpl = i18n_block_text(data.get("continuity_prefix"), locale, default="%s")
    except (OSError, json.JSONDecodeError, KeyError):
        tpl = "%s"
    return tpl.replace("%@", observe_text).replace("%s", observe_text)


def together_session_from_i18n(
    *,
    age_band: str = "parent",
    locale: str = "ru",
    duration_sec: int = 180,
) -> Dict[str, Any]:
    try:
        data = _load_json("together_v1.json")
    except (OSError, json.JSONDecodeError, KeyError):
        return {}
    loc = normalize_wellness_locale(locale)
    band = (age_band or "parent").lower()
    is_parent = band in ("parent", "senior", "adult_app")
    intro_key = "wellness_together_parent_intro" if is_parent else "wellness_together_child_intro"
    intro_block = (data.get("intro") or {}).get("parent" if is_parent else "child") or {}
    steps = [
        i18n_block_text(step, loc)
        for step in (data.get("steps") or [])
        if isinstance(step, dict)
    ]
    return {
        "title_key": data.get("title_key", "wellness_together_title"),
        "intro_key": intro_key,
        "title": i18n_block_text({"ru": "Вместе", "en": "Together"}, loc),
        "intro": i18n_block_text(intro_block, loc),
        "duration_sec": max(60, min(600, int(duration_sec))),
        "breath_in_sec": 4,
        "breath_out_sec": 4,
        "steps": steps,
        "exercise_id": "box_breathing",
        "pillar": "humanistic",
    }


def family_theme_label_from_i18n(theme_id: str, *, locale: str = "ru") -> str:
    try:
        data = _load_json("family_v1.json")
        block = (data.get("theme_labels") or {}).get(theme_id) or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return theme_id
    return i18n_block_text(block, locale, default=theme_id)


def family_theme_label_key(theme_id: str) -> str:
    return f"wellness_family_theme_{theme_id}"


def family_dashboard_message_from_i18n(*, locale: str = "ru") -> str:
    try:
        data = _load_json("family_v1.json")
        return i18n_block_text(data.get("dashboard_message"), locale)
    except (OSError, json.JSONDecodeError, KeyError):
        return ""


def family_themes_disclaimer_from_i18n(*, locale: str = "ru") -> str:
    try:
        data = _load_json("family_v1.json")
        return i18n_block_text(data.get("themes_disclaimer"), locale)
    except (OSError, json.JSONDecodeError, KeyError):
        return ""


def family_mood_trend_down_from_i18n(*, locale: str = "ru", days: int) -> str:
    try:
        data = _load_json("family_v1.json")
        tpl = i18n_block_text(data.get("mood_trend_down"), locale, default="%d")
    except (OSError, json.JSONDecodeError, KeyError):
        tpl = "%d"
    return tpl.replace("%d", str(days))


def load_push_message(push_id: str, locale: str = "ru", *, part: str = "body") -> str:
    """Push copy from push_ru.json / push_en.json (p18-11)."""
    loc = normalize_wellness_locale(locale)
    fname = "push_ru.json" if loc == "ru" else "push_en.json"
    try:
        data = _load_json(fname)
    except (OSError, json.JSONDecodeError, KeyError):
        return push_id
    if part == "title" and f"{push_id}_title" in data:
        return str(data[f"{push_id}_title"])
    if part == "body" and f"{push_id}_body" in data:
        return str(data[f"{push_id}_body"])
    return str(data.get(push_id) or push_id)


def load_alert_text(alert_id: str, locale: str = "ru", **fmt: Any) -> str:
    """In-app alert strings from push_v1.json alerts block."""
    try:
        data = _load_json("push_v1.json")
        block = (data.get("alerts") or {}).get(alert_id) or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return alert_id
    text = i18n_block_text(block, locale, default=alert_id)
    if "hour" in fmt:
        try:
            return text % int(fmt["hour"])
        except (TypeError, ValueError):
            return text
    if fmt:
        try:
            return text % tuple(fmt.values())
        except (TypeError, ValueError):
            return text
    return text


def clinician_export_copy_from_i18n(*, locale: str = "ru") -> Dict[str, str]:
    try:
        data = _load_json("export_v1.json")
        block = data.get("clinician") or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return {"title": "", "disclaimer": ""}
    loc = normalize_wellness_locale(locale)
    return {
        "title": i18n_block_text(block.get("title"), loc),
        "disclaimer": i18n_block_text(block.get("disclaimer"), loc),
    }


def weekly_pdf_labels_from_i18n(*, locale: str = "ru") -> Dict[str, str]:
    """Localized PDF section labels for iOS exporter (p18-13 / p3-19)."""
    try:
        data = _load_json("export_v1.json")
        block = data.get("weekly_pdf") or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return {}
    loc = normalize_wellness_locale(locale)
    return {
        "title": i18n_block_text(block.get("title"), loc),
        "title_key": "wellness_pdf_title",
        "disclaimer": i18n_block_text(block.get("disclaimer"), loc),
        "disclaimer_key": "wellness_pdf_disclaimer",
        "section_checkins": i18n_block_text(block.get("section_checkins"), loc),
        "section_checkins_key": "wellness_pdf_section_checkins",
        "section_assessments": i18n_block_text(block.get("section_assessments"), loc),
        "section_assessments_key": "wellness_pdf_section_assessments",
        "section_outcomes": i18n_block_text(block.get("section_outcomes"), loc),
        "section_outcomes_key": "wellness_pdf_section_outcomes",
        "section_insights": i18n_block_text(block.get("section_insights"), loc),
        "section_insights_key": "wellness_pdf_section_insights",
        "generated_label": i18n_block_text(block.get("generated_label"), loc),
        "generated_label_key": "wellness_pdf_generated",
        "share_cta": i18n_block_text(block.get("share_cta"), loc),
        "share_cta_key": "wellness_pdf_share",
    }


def parent_playbook_from_i18n(*, locale: str = "ru") -> Dict[str, Any]:
    try:
        data = _load_json("playbook_v1.json")
    except (OSError, json.JSONDecodeError, KeyError):
        return {"title_key": "", "subtitle_key": "", "phrases": []}
    loc = normalize_wellness_locale(locale)
    phrases: List[Dict[str, str]] = []
    for row in data.get("phrases") or []:
        phrases.append(
            {
                "id": str(row.get("id") or ""),
                "text": i18n_block_text(row.get("text"), loc),
            }
        )
    return {
        "title_key": data.get("title_key", "wellness_parent_playbook_title"),
        "subtitle_key": data.get("subtitle_key", "wellness_parent_playbook_subtitle"),
        "phrases": phrases,
    }


def widget_copy_from_i18n(*, locale: str = "ru") -> Dict[str, str]:
    try:
        data = _load_json("widget_v1.json")
    except (OSError, json.JSONDecodeError, KeyError):
        return {"title": "", "tap": ""}
    loc = normalize_wellness_locale(locale)
    return {
        "title_key": str(data.get("title_key") or "wellness_widget_title"),
        "tap_key": str(data.get("tap_key") or "wellness_widget_tap"),
        "title": i18n_block_text(data.get("title"), loc),
        "tap": i18n_block_text(data.get("tap"), loc),
    }


def load_age_variants_manifest() -> Dict[str, Any]:
    """Keys that support `_child` / `_teen` suffix on iOS (p18-14)."""
    return _load_json("age_variants_v1.json")


def age_copy_from_i18n(
    base_key: str,
    *,
    age_band: str = "parent",
    locale: str = "ru",
) -> str:
    """Resolve age-aware copy for backend payloads (mirrors iOS WellnessAgeL10n)."""
    loc = normalize_wellness_locale(locale)
    band = (age_band or "parent").lower()
    try:
        data = _load_json("age_copy_v1.json")
        block = (data.get("strings") or {}).get(base_key) or {}
    except (OSError, json.JSONDecodeError, KeyError):
        block = {}
    if band == "child" and block.get("child"):
        return i18n_block_text(block["child"], loc)
    if band == "teen" and block.get("teen"):
        return i18n_block_text(block["teen"], loc)
    if block.get("base"):
        return i18n_block_text(block["base"], loc)
    return ""


def wellness_error_from_i18n(code: str, *, locale: str = "ru") -> Dict[str, Any]:
    """Localized wellness API error row (p18-15)."""
    loc = normalize_wellness_locale(locale)
    try:
        data = _load_json("errors_v1.json")
        errors = data.get("errors") or {}
        row = errors.get(code) or {}
    except (OSError, json.JSONDecodeError, KeyError):
        errors = {}
        row = {}
    if not row:
        generic = errors.get("wellness_generic") or {}
        return {
            "code": code,
            "message_key": "wellness_error_generic",
            "message": i18n_block_text(generic.get("message"), loc) if generic else code,
            "http_status": 400,
        }
    return {
        "code": code,
        "message_key": str(row.get("message_key") or "wellness_error_generic"),
        "message": i18n_block_text(row.get("message"), loc),
        "http_status": int(row.get("http_status") or 400),
    }


def wellness_errors_catalog_from_i18n(*, locale: str = "ru") -> List[Dict[str, Any]]:
    loc = normalize_wellness_locale(locale)
    try:
        data = _load_json("errors_v1.json")
        errors = data.get("errors") or {}
    except (OSError, json.JSONDecodeError, KeyError):
        return []
    out: List[Dict[str, Any]] = []
    for code in sorted(errors.keys()):
        row = wellness_error_from_i18n(code, locale=loc)
        out.append(row)
    return out
