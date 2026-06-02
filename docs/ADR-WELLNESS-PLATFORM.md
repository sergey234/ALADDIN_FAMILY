# ADR: ALADDIN Wellness Platform (4 столпа)

**Status:** Accepted (draft for clinical review)  
**Date:** 2026-06-01  
**Plan:** [WELLNESS_PLATFORM_MASTER_PLAN.md](./WELLNESS_PLATFORM_MASTER_PLAN.md) v2.5  
**Server deploy:** [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md)

## Context

Family Companion already provides chat, ethics (L3 crisis), teen playbook, and Hermes LLM. We add **Wellness Loop Engine** — four self-help pillars inside one Hub, not a separate therapy app.

## Decision

1. **Single AI path:** extend `ai_companion_router.py` + `wellness_prompt_builder.py`; no separate Psychology API or fine-tuned models.
2. **Knowledge Pack per pillar:** `security/services/ai_platform/wellness_knowledge/{pillar}/v1/pack.yaml` — clinical review per pack (4 reviews, not 12 hero×pillar prompts).
3. **Determinism before LLM:** `companion_ethics`, `wellness_escalation`, `wellness_assessments` (PHQ scoring in code), `wellness_pillar_guard`.
4. **One pillar per session:** `primary_pillar` + `[WELLNESS v1]` prefix block (see §4.3 master plan).
5. **Feature flags default OFF:** `FEATURE_WELLNESS_*` until gate 0→1 closed.

## Four pillars (UI names only)

| UI | Internal | Backend modules |
|----|----------|-----------------|
| Разобрать мысли | cognitive | `wellness_cognitive_prompt`, `wellness_cbt_exercises`, pack `cognitive/v1` |
| Маленькие шаги | behavioral | `wellness_behavioral_exercises`, `wellness_habit_plans` |
| Принять себя | humanistic | `wellness_humanistic_prompt`, grounding/STOP |
| Понять себя | jung + reflective | `wellness_jung_*`, `wellness_reflective_*` (gated) |

## Knowledge Pack schema (`wellness_knowledge_pack_v1`)

Required keys in `pack.yaml`:

- `pack_version`, `pillar`, `status` (`draft` | `approved`)
- `principles` (ru/en)
- `forbidden_phrases`, `forbidden_concepts`
- `exercises.{id}.steps[]` with `hint`, `llm_rephrase_only`, `instruction`
- `hero_flavor` (unicorn, genie, aladdin) — tone only
- `age_band` overrides (child: no full PHQ/Jung)

Reference implementation: `security/.../wellness_knowledge/cognitive/v1/pack.yaml` (p0-15).

## `[WELLNESS v1]` prefix contract

```
[WELLNESS v1]
primary_pillar=cognitive
escalation=L0
age_band=teen
exercise=thought_record
exercise_step=2/5
allowed_topics=untangle_thoughts,facts_vs_guesses
forbidden=diagnosis,other_pillars,therapy_claims
pack_version=cognitive_v1.0
hero_flavor=mentor_short
instruction=...
```

Built by `build_wellness_prefix()`; appended in `ai_companion_router` after `companion_system_prefix`.

## Escalation (summary)

| Level | Trigger | Action |
|-------|---------|--------|
| L0 | Normal | Pillar session |
| L1 | 3d low mood | PHQ-lite |
| L2 | PHQ≥10, trauma keywords | Referral map |
| L3 | Self-harm (ethics) | 112, block deep modes |

Full spec: [WELLNESS_ESCALATION_LADDER.md](./WELLNESS_ESCALATION_LADDER.md).

## Orchestrator (Phase 3)

`wellness_orchestrator.py` — `run_wellness_loop` + `prepare_wellness_chat_turn` when `FEATURE_WELLNESS_ORCHESTRATOR=1`.
`wellness_pack_registry.py` locks `pack_version` per session; `wellness_agent_hints.py` adds `[WELLNESS AGENTS ACTIVE]` to prefix (one LLM call).
`WELLNESS_AGENTS` also appear in `tools_used`. `GET /api/wellness/session/loop` for Hub.
`COMPANION_USE_ORCHESTRATOR` is unrelated (Hermes multi-agent stub in `orchestrator.py`).

## Consequences

- **Positive:** Family-first, auditable prompts, no model training cost.
- **Negative:** Content drift requires pack versioning + smoke tests (`p1-29`).
- **Risks:** Jung/trauma copy — mitigated by trauma/L3 guards + PO checklist `WELLNESS_CLINICAL_REVIEW.md`; flags `JUNG`/`REFLECTIVE` on prod, revert via `.env` if App Review asks.

## Out of scope

- PPG stress camera, live coaches, separate Psychology app, parent reading teen chat verbatim.

## References

- [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md)
- [WELLNESS_CURSOR_TODO.md](./WELLNESS_CURSOR_TODO.md)
- `companion_ethics.py`, `prod-no-mock-bypass.mdc`
