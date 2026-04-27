# Phase 2 Category Acceptance Checklist Template

Use this template for every child content category (for example: `toys`, `drawing`, `songs`, `stories`, `games`, `study`, `safety`, `cartoons`, `programming`, `social`, `music`, `education`).

---

## 1) Category Header

- Category ID: `________________`
- Audience band: `________________` (for example `kids_1_6`, `school_7_12`, `teen_13_17`, `youngAdult_18_22`)
- Owner (product): `________________`
- Owner (engineering): `________________`
- QA owner: `________________`
- Localization owner: `________________`
- Target release wave: `________________`

---

## 2) Scope And Learning Contract

### 2.1 Learning Outcome Contract (mandatory)

- [ ] `learning_objective` defined
- [ ] `target_age_window` defined
- [ ] `difficulty_level` (L1-L5) defined
- [ ] `success_criteria` defined
- [ ] `assessment_type` defined
- [ ] `estimated_cognitive_load` defined

Notes:
- `________________________________________________________`

### 2.2 Category Volume Target

- Planned target count: `_____`
- Implemented count: `_____`
- [ ] Meets minimum count gate

Evidence:
- manifest/query source: `________________`

---

## 3) Interaction And Feature Completeness

- [ ] Category has dedicated interaction mode (not static card only)
- [ ] Interaction flow supports full loop: discover -> open -> interact -> complete
- [ ] Required module engine delivered (choose one or more):
  - [ ] 3D interaction (if applicable)
  - [ ] Canvas/save (if applicable)
  - [ ] Karaoke/lyrics sync (if applicable)
  - [ ] Scenario/quiz engine (if applicable)
  - [ ] Video active-check flow (if applicable)
- [ ] Error/empty/loading states implemented and reachable
- [ ] Offline behavior verified (fallback/payload/open path)

Evidence:
- code paths: `________________`
- smoke tests: `________________`

---

## 4) Educational Quality And Mastery

- [ ] Assessment exists and matches `learning_objective`
- [ ] Mastery states supported (`introduced/practicing/mastered`)
- [ ] Scoring/feedback is age-appropriate and understandable
- [ ] Retry/hint loop prevents frustration spirals
- [ ] Parent-visible progress reflects skill state, not only opens

Educational QA notes:
- `________________________________________________________`

---

## 5) Telemetry And Analytics

- [ ] Completion rate tracked
- [ ] Mastery gain tracked
- [ ] Drop-off step tracked
- [ ] Retry/error rates tracked
- [ ] Hint dependency tracked (if applicable)
- [ ] Dashboard/report visibility confirmed

Metrics snapshot:
- completion: `_____`
- mastery gain: `_____`
- drop-off hotspot: `_____`

---

## 6) Localization RU/EN Contract

- [ ] RU and EN keys delivered in same change-set
- [ ] No duplicate keys introduced
- [ ] No extra wrapping quotes in user-facing values
- [ ] No noisy nested brackets in user-facing values
- [ ] No mixed RU+EN in one final user-facing string
- [ ] Placeholder parity verified (`%@`, `%d`, order)
- [ ] `localization_lint` pass confirmed

Evidence:
- changed keys file(s): `________________`
- lint command/output ref: `________________`

---

## 7) Accessibility (A11y) Contract

- [ ] `accessibilityLabel` localized
- [ ] `accessibilityHint` localized
- [ ] `accessibilityValue` localized (where needed)
- [ ] VoiceOver smoke pass
- [ ] Dynamic Type readability check pass
- [ ] Reduce Motion behavior acceptable

Evidence:
- screenshots/video refs: `________________`

---

## 8) Child Safety UX Policy

- [ ] Stimulation level appropriate for age band
- [ ] Reward/effect pacing within policy limits
- [ ] Session pacing includes soft pause/rest logic (where applicable)
- [ ] No manipulative dark patterns
- [ ] Parent guardrails respected for sensitive actions

Safety notes:
- `________________________________________________________`

---

## 9) QA And Release Gates

- [ ] Category-specific smoke pass
- [ ] Route coverage pass
- [ ] Interaction feature availability pass
- [ ] Regression pass (child + parent visibility)
- [ ] CI required checks pass

Gate evidence:
- `________________________________________________________`

---

## 10) Final Acceptance Decision

- Status:
  - [ ] READY FOR RELEASE
  - [ ] READY WITH CONDITIONS
  - [ ] NOT READY

- Blocking gaps (if any):
  1. `________________`
  2. `________________`
  3. `________________`

- Product sign-off:
  - Name: `________________`
  - Date: `________________`
  - Decision: `________________`

- Engineering sign-off:
  - Name: `________________`
  - Date: `________________`
  - Decision: `________________`

- QA sign-off:
  - Name: `________________`
  - Date: `________________`
  - Decision: `________________`

