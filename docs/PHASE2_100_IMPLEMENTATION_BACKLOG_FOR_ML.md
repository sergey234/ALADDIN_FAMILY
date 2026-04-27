# Phase 2 → 100% Implementation Backlog For Next ML System

This is an execution-ready backlog to complete child content to full target depth.

## Rules Before Starting

1. Do not mark category done by count alone.
2. Do not mark category done by UI visibility alone.
3. Every category must pass:
   - volume gate
   - interaction-depth gate
   - educational evidence gate
   - localization/a11y gate
4. Any new user-facing text must follow:
   - no duplicate keys
   - no extra wrapping quotes
   - no noisy nested brackets
   - no mixed RU/EN in one final string

---

## Sprint 1 — Contract And Gating Foundation (Required)

### Task P2-001: Learning Outcome Contract in models
- Add fields (or metadata extension strategy):
  - `learningObjective`
  - `targetAgeWindow`
  - `difficultyLevel`
  - `successCriteria`
  - `assessmentType`
  - `cognitiveLoad`
- Target files:
  - `Core/Content/Models/ContentModels.swift`
  - `Core/Content/Validation/ContentValidator.swift`
- DoD:
  - validator rejects missing mandatory learning contract for Phase 2 categories
  - unit tests added

### Task P2-002: Category count gate script
- Add script:
  - `scripts/phase2_category_count_gate.py`
- Validate minimum per category against configured thresholds.
- DoD:
  - PASS/FAIL deterministic output
  - report generated in `docs/`
  - CI step added

### Task P2-003: Category acceptance report scaffold
- Add script:
  - `scripts/phase2_category_acceptance_smoke.py`
- Build status from code + docs + lint + required keys.
- DoD:
  - outputs JSON+MD summary by category

---

## Sprint 2 — 1-6 Deep Modules

### Task P2-101: Toys 3D module
- Build reusable scene host component.
- Add at least 3 toy scenes with interaction events.
- Integrate into route for toys.
- DoD:
  - interaction telemetry
  - child-safe performance profile

### Task P2-102: Drawing canvas + save/load
- Implement PencilKit-based module.
- Save/load works gallery by child profile.
- DoD:
  - no data loss on app restart
  - basic moderation-safe storage policy

### Task P2-103: Karaoke flow
- Implement lyric timeline sync + highlighted playback.
- Add at least 5 tracks.
- DoD:
  - timing tolerance checks
  - completion signal

### Task P2-104: Interactive voiced stories
- Add page/branch model + narration.
- Add at least 5 stories with checkpoints.
- DoD:
  - checkpoint telemetry and completion state

---

## Sprint 3 — 7-12 Learning Depth

### Task P2-201: Games challenge engine
- Math/language challenge flows with scoring and hint model.

### Task P2-202: Study checkpoints
- Lesson + test flow with pass/fail progression.

### Task P2-203: Safety scenarios
- Safe/unsafe scenario engine with explainable feedback.

### Task P2-204: Cartoons active watch
- Add post-view checks (short recall/comprehension tasks).

For all tasks P2-201..P2-204:
- DoD:
  - measurable mastery signal
  - parent-facing visibility of outcomes

---

## Sprint 4 — 13-22 Skill Tracks

### Task P2-301: Programming tasks
- Task-based progression (not passive cards).

### Task P2-302: Social literacy drills
- Privacy/scam/misinformation scenario outcomes.

### Task P2-303: Music drills
- Structured practice with progression metrics.

### Task P2-304: Education pathways
- Finance/career pathway with milestone completion.

For all tasks P2-301..P2-304:
- DoD:
  - skill rubric with mastery transitions
  - telemetry and dashboard hooks

---

## Sprint 5 — Quality Hardening And Release Proof

### Task P2-401: Localization hard gate expansion
- Extend lint/smokes for all new module keys and placeholders.

### Task P2-402: Accessibility pass by category
- VoiceOver + Dynamic Type + Reduce Motion by category.

### Task P2-403: Evidence pack for Phase 2 completion
- Add:
  - per-category acceptance records
  - KPI snapshots
  - RU/EN screenshots
  - final release summary

### Task P2-404: Final Phase 2 sign-off record
- Product + engineering + QA sign-off in one document.

---

## File Touch Map (Primary)

- `Core/Content/Models/ContentModels.swift`
- `Core/Content/Validation/ContentValidator.swift`
- `Core/Content/ContentManager.swift`
- `Core/Content/Experiences/ContentExperienceResolver.swift`
- `Screens/ChildContentScreen.swift`
- `Screens/ChildContentExperienceScreen.swift`
- `Resources/Localization/ru.lproj/Localizable.strings`
- `Resources/Localization/en.lproj/Localizable.strings`
- `.github/workflows/ci.yml`
- `scripts/phase2_category_count_gate.py` (new)
- `scripts/phase2_category_acceptance_smoke.py` (new)

---

## Exit Criteria (Hard)

Phase 2 can be marked 100% only when:
- all 12 categories have accepted status `READY`
- category count gate passes
- category acceptance smoke passes
- localization lint passes full scope
- accessibility checks pass
- final Phase 2 evidence pack and sign-offs are attached
