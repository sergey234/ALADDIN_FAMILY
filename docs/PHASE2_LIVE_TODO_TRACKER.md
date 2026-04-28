# Phase 2 Live TODO Tracker (Child Content 100%)

_Last update: 2026-04-29 (synced “Current Baseline” with final category + 275 matrix closure; task checklist below remains the historical execution log)._

## How To Track In Real Time

- Update checkboxes directly in this file after each merged task.
- Keep task IDs (`P2-...`) unchanged for traceability.
- Mark complete tasks with `[x]` and keep done text visible (not deleted).
- Run gates after each wave:
  - `python3 scripts/localization_lint.py`
  - `python3 scripts/phase7_content_qa_matrix_smoke.py`
  - `python3 scripts/phase_w_loc_6_a11y_sync_content_smoke.py`
  - `python3 scripts/ipa_size_gate.py --max-mb 500`

## Current Baseline (Fact)

- **Canonical ML handoff (end-state narrative):** `docs/CHILD_CONTENT_FINAL_SYSTEM_HANDOFF.md`
- Category readiness snapshot (`docs/PHASE2_CATEGORY_ACCEPTANCE_STATUS_ALL.md`):
  - `READY`: **12 / 12**
  - `READY WITH CONDITIONS`: **0**
  - `NOT READY`: **0**
- **275-item matrix:** `DONE 275 / PARTIAL 0 / TODO 0` (canonical: `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`; open rows: `docs/PLAN_ITEM_OPEN_TASKS.md`)
- Gate status at latest run:
  - [x] `localization_lint` PASS
  - [x] `phase7_content_qa_matrix_smoke` PASS
  - [x] `phase_w_loc_6_a11y_sync_content_smoke` PASS
  - [x] `ipa_size_gate --max-mb 500` PASS (`176.91 MB`)

## Master TODO (Execution Order)

### Sprint 1 - Contracts And Gates (Must Start Here)

- [x] `P2-001` Add learning outcome contract fields/strategy in content models and validation.
- [x] `P2-002` Add `scripts/phase2_category_count_gate.py` and wire thresholds per category.
- [x] `P2-003` Add `scripts/phase2_category_acceptance_smoke.py` for acceptance synthesis.
- [x] `P2-004` Add Learning Effectiveness Gates in docs/scripts: `mastery_gain`, `reattempt_success`, `drop_off_step`, `hint_dependency`.
- [x] `P2-005` Add Engagement Health Gates in docs/scripts: `session_depth`, `d1_d7_voluntary_return`, `boredom_signal`.
- [x] `P2-006` Add content editorial model package: `item_quality_rubric`, `manifest_peer_review`, `deprecation_policy`.

### Sprint 2 - Ages 1-6 Deep Modules (Critical Gap)

- [x] `P2-101` Toys: deliver reusable 3D interaction module + at least 3 playable toy scenes.
- [x] `P2-102` Drawing: PencilKit canvas + save/load gallery by child profile.
- [x] `P2-103` Songs: karaoke timeline sync + highlighted lyrics + at least 5 tracks.
- [x] `P2-104` Stories: interactive voiced stories with checkpoints + at least 5 stories.
- [x] `P2-105` Daily Journey v1: personal 3-step journey for child (`discover -> practice -> reflect`).
- [x] `P2-106` Adaptive Loop v1: after 2 consecutive errors trigger hint/simplified step.
- [x] `P2-107` Reward 2.0: reward by skill progress, not only completion.
- [x] `P2-108` Surprise mechanics v1: controlled wow-events every N sessions.
- [x] `P2-109` Creative output v1: mandatory create action in each 1-6 category (draw/build/voice/text).

### Sprint 3 - Ages 7-12 Learning Depth

- [x] `P2-201` Games: challenge engine (math/language), scoring, hints.
- [x] `P2-202` Study: lesson + test progression with pass/fail checkpoints.
- [x] `P2-203` Safety: safe/unsafe scenario engine with explainable feedback.
- [x] `P2-204` Cartoons: active watch + post-view recall/comprehension checks.
- [x] `P2-205` Daily Journey v2 for 7-12 with challenge pacing and corrective feedback.
- [x] `P2-206` Adaptive Loop v2 with frustration prevention (retry, scaffold, confidence-safe messaging).

### Sprint 4 - Ages 13-22 Skill Tracks

- [x] `P2-301` Programming: task-based progression (not passive cards).
- [x] `P2-302` Social: privacy/scam/misinformation drills with measurable outcomes.
- [x] `P2-303` Music: structured practice with progression metrics.
- [x] `P2-304` Education: finance/career pathways with milestone completion.
- [x] `P2-305` Daily Journey v3 for 13-22 with autonomy and reflection prompts.
- [x] `P2-306` Creative output v2: project artifact tracking for teen/young adult tracks.

### Sprint 5 - Hardening, Proof, Final Sign-off

- [x] `P2-401` Extend localization and placeholders hard-gate for all new module keys.
- [x] `P2-402` Accessibility pass by category (VoiceOver, Dynamic Type, Reduce Motion).
- [x] `P2-403` Build full Phase 2 evidence pack (reports, smokes, screenshots, matrix).
- [x] `P2-404` Record final product + engineering + QA sign-offs in one file.
- [x] `P2-405` Content QA matrix at two levels: category and item.
- [x] `P2-406` A/B validation framework for task formats (short/long, text/visual).
- [x] `P2-407` Content freshness SLA for top categories and release cadence.
- [x] `P2-408` Stimulus budget policy for 1-6 (effects/min, rewards/min).

### Sprint 6 - Parent Value Layer (Outcome Visibility)

- [x] `P2-501` Parent panel "what child learned" (skill deltas, not only time spent).
- [x] `P2-502` Auto-digest: `3 achievements + 1 risk zone + 1 parent recommendation`.
- [x] `P2-503` Mastery levels in parent UX: `introduced / practicing / mastered` per topic.
- [x] `P2-504` Educational ROI filter: modules ranked by learning gain efficiency.

### Sprint 7 - Telemetry And Evolution Ops

- [x] `P2-601` Build unified telemetry schema for Learning + Engagement + Freshness.
- [x] `P2-602` Add weekly improvement loop: `build -> measure -> tune` with published report.
- [x] `P2-603` Add content health dashboard and alerting for regressions.
- [x] `P2-604` Add "completion != learning" guard in acceptance rules and reports.

## Category Readiness Checklist (Operational)

### 1-6

- [x] `toys` -> `READY`
- [x] `drawing` -> `READY`
- [x] `songs` -> `READY`
- [x] `stories` -> `READY`

### 7-12

- [x] `games` (`READY WITH CONDITIONS` -> `READY`)
- [x] `study` (`READY WITH CONDITIONS` -> `READY`)
- [x] `safety` (`READY WITH CONDITIONS` -> `READY`)
- [x] `cartoons` (`READY WITH CONDITIONS` -> `READY`)

### 13-22

- [x] `programming` (`READY WITH CONDITIONS` -> `READY`)
- [x] `social` (`READY WITH CONDITIONS` -> `READY`)
- [x] `music` (`READY WITH CONDITIONS` -> `READY`)
- [x] `education` (`READY WITH CONDITIONS` -> `READY`)

## Hard Exit Criteria (Do Not Bypass)

- [x] All 12 categories are `READY`.
- [x] Category count gate passes.
- [x] Category acceptance smoke passes.
- [x] Localization lint passes full scope.
- [x] Accessibility checks pass for all new category flows.
- [x] Final evidence pack + sign-offs attached.
- [x] Learning Effectiveness Gates pass (`mastery_gain`, `reattempt_success`, `drop_off_step`, `hint_dependency`).
- [x] Engagement Health Gates pass (`session_depth`, `d1_d7_voluntary_return`, `boredom_signal`).
- [x] Freshness and governance gates pass (editorial model, QA matrix item-level, SLA cadence).
- [x] Parent outcome layer is live (learned-skills panel, auto-digest, mastery levels, ROI filter).

## Strategic Focus (From Two Analyses)

- [x] `SF-1` Mastery-first: prioritize measurable learning outcomes over raw item counts.
- [x] `SF-2` Scenario-first UX: prioritize live child journeys over static catalog browsing.
- [x] `SF-3` Managed evolution: enforce telemetry, editorial control, and freshness as release gates.
