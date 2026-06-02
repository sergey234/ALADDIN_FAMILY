#!/usr/bin/env python3
"""
Smoke: Wellness API on VPS (/opt/aladdin-backend) or prod via nginx.

Usage (on server):
  cd /opt/aladdin-backend && PYTHONPATH=. python3 scripts/vps_smoke_wellness.py
  cd /opt/aladdin-backend && PYTHONPATH=. python3 scripts/vps_smoke_wellness.py --base https://aladdin-ai.ru

Exit 0 = all checks passed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.environ.get("ALADDIN_BACKEND_ROOT", "/opt/aladdin-backend")
if os.path.isdir(ROOT):
    os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

for line in open(".env"):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import jwt  # noqa: E402

from security.services.ai_platform.feature_flags import FEATURE_WELLNESS_ENABLED  # noqa: E402
from security.services.ai_platform.wellness_pillar_guard import assert_single_pillar  # noqa: E402
from security.services.ai_platform.wellness_prompt_builder import load_pillar_pack  # noqa: E402


def mint(*, uid: int = 901701, age_band: str = "teen", level: str = "premium") -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        raise RuntimeError("JWT_SECRET missing in .env")
    now = int(time.time())
    payload = {
        "user_id": uid,
        "sub": str(uid),
        "type": "access",
        "age_band": age_band,
        "subscription_level": level,
        "subscription": {"level": level, "limits": {}},
        "iat": now,
        "exp": now + 3600,
    }
    try:
        from security.services.ai_platform.jwt_claims import enrich_access_token_data

        payload = enrich_access_token_data(payload)
    except Exception:
        pass
    return jwt.encode(payload, secret, algorithm=os.environ.get("JWT_ALGORITHM", "HS256"))


def http(
    base: str,
    method: str,
    path: str,
    token: str | None = None,
    body: dict | None = None,
) -> tuple[int, str]:
    url = base.rstrip("/") + path
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def check(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"PASS {name}" + (f" — {detail}" if detail else ""))
    else:
        print(f"FAIL {name}" + (f" — {detail}" if detail else ""), file=sys.stderr)
        sys.exit(1)


def error_code(body: str) -> str:
    if not body.startswith("{"):
        return body.strip()
    try:
        raw = json.loads(body).get("detail", body)
    except json.JSONDecodeError:
        return body[:120]
    if isinstance(raw, dict):
        return str(raw.get("code") or raw.get("message_key") or raw)
    return str(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        default=os.environ.get("ALADDIN_SMOKE_BASE", "http://127.0.0.1:8002"),
        help="API base (default localhost:8002)",
    )
    args = parser.parse_args()
    base = args.base.rstrip("/")

    print(f"=== Wellness smoke base={base} FEATURE_WELLNESS_ENABLED={FEATURE_WELLNESS_ENABLED}")
    check("feature_flag", FEATURE_WELLNESS_ENABLED, "must be enabled on server")

    # p1-29 local guard + forbidden phrases
    g = assert_single_pillar(session_pillar="cognitive", requested_pillar="jung", age_band="teen")
    check("pillar_guard_mix", not g.ok, g.reason)
    pack = load_pillar_pack("cognitive", "ru", "v1")
    ru_phrases = (pack.get("forbidden_phrases") or {}).get("ru") or []
    check("pack_forbidden_phrases", len(ru_phrases) >= 3, f"count={len(ru_phrases)}")
    pack_h = load_pillar_pack("humanistic", "ru", "v1")
    check("pack_humanistic", pack_h.get("pillar") == "humanistic", str(pack_h.get("pillar")))
    pack_b = load_pillar_pack("behavioral", "ru", "v1")
    check("pack_behavioral", "micro_habit" in (pack_b.get("exercises") or {}), "behavioral pack")

    code, body = http(base, "GET", "/api/health")
    check("health", code == 200 and "ok" in body.lower(), f"{code} {body[:120]}")

    code, body = http(base, "GET", "/api/wellness/pillars")
    check("pillars_no_auth", code in (401, 403), f"{code} {body[:120]}")

    # Unique uid avoids stale session_pillar lock from prior smoke runs (p2-15).
    teen = mint(uid=901701 + int(time.time()) % 40, age_band="teen")
    code, body = http(base, "GET", "/api/wellness/pillars", teen)
    data = json.loads(body)
    pillars = data.get("pillars") or []
    check("pillars_teen_auth", code == 200 and len(pillars) == 4, f"{code} pillars={pillars}")

    child = mint(uid=901702, age_band="child")
    code, body = http(base, "GET", "/api/wellness/pillars", child)
    data = json.loads(body)
    pillars = data.get("pillars") or []
    check(
        "pillars_child_auth",
        code == 200 and set(pillars) == {"humanistic", "behavioral"},
        f"{code} pillars={pillars}",
    )

    code, body = http(base, "POST", "/api/wellness/consent", teen, {"wellness_accepted": True})
    check("consent_teen", code == 200 and json.loads(body).get("has_access") is True, body[:160])

    code, _ = http(base, "POST", "/api/wellness/session/end", teen, {})
    check("session_end_preflight", code == 200, f"{code}")

    parent = mint(uid=901703, age_band="parent")
    code, body = http(
        base,
        "POST",
        "/api/wellness/consent",
        parent,
        {"wellness_accepted": True, "psychological_support_enabled": True},
    )
    check("consent_parent_toggle", code == 200, body[:120])

    code, body = http(
        base,
        "POST",
        "/api/wellness/session/pillar",
        teen,
        {"pillar": "cognitive"},
    )
    data = json.loads(body)
    check("session_pillar_teen", code == 200 and data.get("ok") is True, f"{code}")

    code, body = http(base, "POST", "/api/wellness/consent", child, {"wellness_accepted": True})
    check("consent_child", code == 200 and json.loads(body).get("has_access") is True, body[:120])

    code, body = http(
        base,
        "POST",
        "/api/wellness/session/pillar",
        child,
        {"pillar": "jung"},
    )
    detail = error_code(body)
    check(
        "session_pillar_child_block",
        code == 403 and detail in ("pillar_not_allowed_for_age", "wellness_consent_required"),
        f"{code} {detail}",
    )

    code, body = http(
        base,
        "POST",
        "/api/wellness/checkin",
        teen,
        {"mood": "sad", "sleep_hours": 7, "stress_level": 3},
    )
    data = json.loads(body)
    check("checkin_post", code == 200 and data.get("ok") is True, f"mood={data.get('checkin', {}).get('mood_emoji')}")

    code, body = http(base, "GET", "/api/wellness/journal?days=3", teen)
    data = json.loads(body)
    check("journal", code == 200 and len(data.get("entries") or []) >= 1, f"entries={len(data.get('entries') or [])}")

    code, body = http(base, "GET", "/api/wellness/triggers/status", teen)
    data = json.loads(body)
    check("triggers", code == 200 and "low_mood_streak_days" in data, str(data))

    code, body = http(base, "GET", "/api/wellness/assessments/phq-lite/schema?locale=ru", teen)
    schema = json.loads(body)
    check("phq_schema", code == 200 and len(schema.get("questions") or []) == 5, body[:80])

    code, body = http(
        base,
        "POST",
        "/api/wellness/assessments/phq-lite/submit?locale=ru",
        teen,
        {"answers": [1, 1, 1, 1, 1]},
    )
    phq = json.loads(body)
    check("phq_submit", code == 200 and phq.get("score") == 5, f"score={phq.get('score')}")

    code, body = http(base, "GET", "/api/wellness/assessments/phq-lite/schema", child)
    check("phq_child_block", code == 403, body[:80])

    code, body = http(
        base,
        "GET",
        "/api/wellness/escalation/level?message=sad",
        teen,
    )
    data = json.loads(body)
    check("escalation", code == 200 and "level" in data, f"level={data.get('level')}")

    code, body = http(
        base,
        "GET",
        "/api/wellness/trauma/check?message="
        + urllib.parse.quote("у меня травма и птср"),
        teen,
    )
    trauma = json.loads(body)
    check(
        "trauma_check",
        code == 200 and trauma.get("triggered") is True and trauma.get("show_referral"),
        str(trauma.get("reason")),
    )

    code, body = http(base, "GET", "/api/wellness/alliance", teen)
    alliance = json.loads(body).get("alliance") or {}
    check(
        "alliance",
        code == 200 and "alliance_score" in alliance,
        f"score={alliance.get('alliance_score')}",
    )

    code, body = http(base, "GET", "/api/wellness/hub/copy?locale=ru", teen)
    hub = json.loads(body)
    check("hub_copy", code == 200 and len(hub.get("pillars") or []) >= 2, hub.get("variant"))

    code, body = http(base, "GET", "/api/wellness/weekly-meaning?locale=ru", teen)
    wm = json.loads(body)
    check("weekly_meaning", code == 200 and "show" in wm, str(wm.get("title")))

    code, body = http(base, "GET", "/api/wellness/streaks?locale=ru", teen)
    streaks = json.loads(body).get("streaks") or {}
    check("streaks", code == 200 and "checkin_streak" in streaks, str(streaks.get("checkin_streak")))

    code, body = http(base, "GET", "/api/wellness/together/session?locale=ru", teen)
    together = json.loads(body).get("session") or {}
    check("together_session", code == 200 and together.get("duration_sec") == 180, str(together)[:60])

    code, body = http(base, "GET", "/api/wellness/export/clinician?days=14", teen)
    export = json.loads(body)
    check("clinician_export", code == 200 and export.get("disclaimer"), export.get("title", "")[:40])

    code, body = http(base, "GET", "/api/wellness/referral?locale=ru&level=L2", teen)
    data = json.loads(body)
    lines = data.get("lines") or []
    check("referral", code == 200 and len(lines) >= 1, f"lines={len(lines)}")

    code, body = http(
        base,
        "POST",
        "/api/wellness/outcomes",
        teen,
        {"pillar": "humanistic", "helpful": 5},
    )
    out = json.loads(body)
    check(
        "outcome_post",
        code == 200 and out.get("ok") is True and out.get("outcome", {}).get("helpful") == 5,
        body[:80],
    )

    code, body = http(base, "GET", "/api/wellness/settings", teen)
    settings = json.loads(body).get("settings") or {}
    check(
        "settings_teen",
        code == 200 and settings.get("parent_share_aggregate", 1) == 0,
        f"parent_share={settings.get('parent_share_aggregate')}",
    )

    teen2 = mint(uid=901799, age_band="teen")
    http(base, "POST", "/api/wellness/consent", teen2, {"wellness_accepted": True})
    code, body = http(
        base,
        "POST",
        "/api/wellness/settings/parent-share",
        teen2,
        {"parent_share_aggregate": True},
    )
    data = json.loads(body)
    check(
        "parent_share_on",
        code == 200 and data.get("parent_share_aggregate") is True,
        str(data)[:120],
    )

    code, body = http(
        base,
        "GET",
        "/api/wellness/family/themes?teen_user_id=901799&locale=ru",
        parent,
    )
    ft = json.loads(body)
    check(
        "family_themes",
        code == 200 and ft.get("shared") is True,
        f"themes={len(ft.get('themes') or [])}",
    )

    code, body = http(base, "GET", "/api/wellness/session/suggest-pillar", teen)
    sug = json.loads(body)
    check(
        "suggest_pillar",
        code == 200 and sug.get("suggested_pillar") in (
            "cognitive",
            "behavioral",
            "humanistic",
            "jung",
        ),
        str(sug),
    )

    code, body = http(
        base,
        "GET",
        "/api/wellness/session/suggest-pillar?message="
        + urllib.parse.quote("мне очень тревожно"),
        teen,
    )
    mood_sug = json.loads(body)
    routing = mood_sug.get("mood_routing") or {}
    check(
        "suggest_pillar_mood_fallback",
        code == 200
        and routing.get("mood_source") in ("message_regex", "notes_regex", "checkin"),
        str(routing),
    )

    code, body = http(
        base,
        "GET",
        "/api/wellness/session/loop?locale=ru&message="
        + urllib.parse.quote("устал"),
        teen,
    )
    loop_body = json.loads(body)
    loop = loop_body.get("loop") or {}
    check(
        "session_loop",
        code == 200
        and loop_body.get("orchestrator_enabled") is True
        and loop.get("phase") in ("session", "screening", "idle", "crisis_l3"),
        str(loop)[:160],
    )

    code, body = http(base, "GET", "/api/wellness/session/plan?locale=ru", teen)
    plan_body = json.loads(body)
    check(
        "session_plan",
        code == 200 and (plan_body.get("plan") or {}).get("steps"),
        str(plan_body)[:120],
    )

    code, body = http(base, "GET", "/api/wellness/exercises/catalog?pillar=cognitive", teen)
    cat = json.loads(body)
    exs = cat.get("exercises") or []
    check("exercise_catalog", code == 200 and len(exs) >= 1, f"count={len(exs)}")

    code, body = http(
        base,
        "POST",
        "/api/wellness/exercises/start?locale=ru",
        teen,
        {"pillar": "cognitive", "exercise_id": "thought_record"},
    )
    start = json.loads(body)
    sess = start.get("session") or {}
    ex_id = sess.get("id")
    check("exercise_start", code == 200 and ex_id, f"id={ex_id}")

    code, body = http(
        base,
        "POST",
        f"/api/wellness/exercises/{ex_id}/step?locale=ru",
        teen,
        {"answer": "smoke step"},
    )
    step = json.loads(body).get("session") or {}
    check("exercise_step", code == 200 and step.get("step_index", 0) >= 2, f"step={step.get('step_index')}")

    code, body = http(base, "GET", "/api/wellness/timeline?days=7", teen)
    tl = json.loads(body)
    check("timeline", code == 200 and "checkins" in tl, f"checkins={len(tl.get('checkins') or [])}")

    code, body = http(base, "GET", "/api/wellness/session/recap?locale=ru", teen)
    recap = json.loads(body)
    check("session_recap", code == 200 and recap.get("message"), recap.get("message", "")[:60])
    check(
        "session_recap_fields",
        "continuity_message" in recap and "outcome_due" in recap,
        str(list(recap.keys())[:8]),
    )

    code, body = http(base, "POST", "/api/wellness/session/end", teen, {})
    check("session_end", code == 200 and json.loads(body).get("ok") is True, body[:60])

    code, body = http(
        base,
        "POST",
        "/api/wellness/session/pillar",
        teen,
        {"pillar": "humanistic", "force_switch": True},
    )
    check("session_pillar_force_switch", code == 200, body[:80])

    code, body = http(base, "GET", "/api/wellness/assessments/phq-9/schema?locale=ru", teen)
    phq9 = json.loads(body)
    check("phq9_schema", code == 200 and len(phq9.get("questions") or []) == 9, f"{code}")

    code, body = http(
        base,
        "POST",
        "/api/wellness/assessments/phq-9/submit?locale=ru",
        teen,
        {"answers": [1, 1, 1, 1, 1, 1, 1, 1, 0]},
    )
    p9 = json.loads(body)
    check("phq9_submit", code == 200 and p9.get("score") == 8, f"score={p9.get('score')}")

    code, body = http(base, "GET", "/api/wellness/assessments/gad-7/schema", teen)
    check("gad7_schema", code == 200 and len(json.loads(body).get("questions") or []) == 7, f"{code}")

    code, body = http(base, "GET", "/api/wellness/assessments/phq-9/schema", child)
    check("phq9_child_block", code == 403, body[:80])

    from datetime import date, timedelta

    from security.services.ai_platform.companion_store import CompanionStore

    idle_uid_num = 901950 + (int(time.time()) % 40)
    teen_idle = mint(uid=idle_uid_num, age_band="teen")
    http(base, "POST", "/api/wellness/consent", teen_idle, {"wellness_accepted": True})
    idle_uid = str(idle_uid_num)
    old_day = (date.today() - timedelta(days=4)).isoformat()
    CompanionStore().upsert_wellness_checkin(
        idle_uid,
        day=old_day,
        mood_emoji="ok",
        mood_score=3,
        age_band="teen",
    )
    code, body = http(base, "GET", "/api/wellness/triggers/status?locale=ru", teen_idle)
    trig = json.loads(body)
    check(
        "idle_nudge_shows",
        code == 200 and trig.get("show_idle_nudge") is True,
        str(trig.get("show_idle_nudge")),
    )
    code, body = http(base, "POST", "/api/wellness/nudges/idle/dismiss", teen_idle, {})
    check("idle_nudge_dismiss", code == 200 and json.loads(body).get("ok") is True, body[:80])
    code, body = http(base, "GET", "/api/wellness/triggers/status?locale=ru", teen_idle)
    trig2 = json.loads(body)
    check(
        "idle_nudge_hidden_after_dismiss",
        code == 200 and trig2.get("show_idle_nudge") is False,
        str(trig2.get("show_idle_nudge")),
    )

    # p18-15 / Ф3 endpoints
    code, body = http(base, "GET", "/api/wellness/errors/catalog?locale=ru", teen)
    err_cat = json.loads(body)
    codes = {row.get("code") for row in (err_cat.get("errors") or [])}
    check("errors_catalog", code == 200 and "wellness_consent_required" in codes, f"n={len(codes)}")

    code, body = http(base, "GET", "/api/wellness/premium/eligibility?locale=ru", teen)
    prem = json.loads(body)
    check("premium_eligibility", code == 200 and prem.get("allowed") is True, str(prem.get("reason")))

    code, body = http(base, "GET", "/api/wellness/seasonal/playbooks?locale=ru", teen)
    seasonal = json.loads(body)
    check("seasonal_playbooks", code == 200 and len(seasonal.get("playbooks") or []) >= 1, body[:80])

    code, body = http(base, "GET", "/api/wellness/sleep/stories?locale=ru", teen)
    stories = json.loads(body)
    check("sleep_stories", code == 200 and len(stories.get("stories") or []) >= 5, body[:80])
    sleep0 = (stories.get("stories") or [{}])[0].get("audio_url") or ""
    check(
        "sleep_url_static",
        "aladdin-ai.ru/static/wellness/sleep" in sleep0,
        sleep0[:72],
    )

    code, body = http(base, "GET", "/api/wellness/canary/status", teen)
    canary = json.loads(body)
    check(
        "canary_status",
        code == 200 and canary.get("in_canary") is True,
        f"pct={canary.get('canary_percent')}",
    )

    code, body = http(base, "GET", "/api/wellness/pillar/rive?pillar=humanistic&locale=ru", teen)
    rive = json.loads(body).get("rive") or {}
    check("pillar_rive", code == 200 and rive.get("rive_state"), str(rive.get("emotion")))

    code, body = http(base, "GET", "/api/wellness/export/pdf-labels?locale=ru", teen)
    pdf_labels = json.loads(body)
    check("pdf_labels", code == 200 and pdf_labels.get("title_key") == "wellness_pdf_title", body[:80])

    code, body = http(base, "GET", "/api/wellness/widget/copy?locale=ru", teen)
    widget = json.loads(body)
    check("widget_copy", code == 200 and widget.get("title_key") == "wellness_widget_title", body[:80])

    code, body = http(base, "GET", "/api/wellness/humanistic/values-card?locale=ru", teen)
    values = json.loads(body)
    check("values_card_schema", code == 200 and values.get("schema", {}).get("title_key"), body[:80])

    code, body = http(base, "GET", "/api/wellness/family/talk-prompts?locale=ru&topic=mood", parent)
    talk = json.loads(body)
    check("family_talk_prompts", code == 200 and len(talk.get("prompts") or []) >= 2, body[:80])

    code, body = http(base, "GET", "/api/wellness/crisis/status", teen)
    crisis = json.loads(body)
    check("crisis_status", code == 200 and "crisis" in crisis and "premium" in crisis, body[:80])

    print("=== ALL WELLNESS SMOKE CHECKS PASSED ===")


if __name__ == "__main__":
    main()
