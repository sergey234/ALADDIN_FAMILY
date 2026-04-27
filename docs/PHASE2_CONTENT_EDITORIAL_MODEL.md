# Phase 2 Content Editorial Model

Status: canonical policy for `P2-006`.

## Purpose

Define one operational standard for:
- `item_quality_rubric`
- `manifest_peer_review`
- `deprecation_policy`

No Phase 2 category can be promoted to `READY` unless this model is applied.

## 1) Item Quality Rubric (mandatory per content item)

Each item is scored 0..2 per dimension (0 = fail, 1 = partial, 2 = pass).
Minimum acceptance score: `>= 14 / 18` and no critical dimension with `0`.

### Rubric dimensions

1. **Learning objective clarity**
   - Item has one clear measurable objective.
2. **Age-band appropriateness**
   - Language, pacing, and challenge match target age window.
3. **Interaction depth**
   - Not static-only; discover -> interact -> completion loop exists.
4. **Assessment integrity**
   - Success criteria and feedback are explicit and fair.
5. **Engagement quality**
   - Child gets meaningful feedback, not only decorative rewards.
6. **Safety and ethics**
   - No manipulative patterns; child-safe UX and parental guardrails.
7. **Localization and accessibility**
   - RU/EN parity + A11y labels/hints/values for new controls.
8. **Technical reliability**
   - Offline/error/empty states and stable route/open behavior.
9. **Telemetry readiness**
   - Item emits required learning and engagement events.

### Critical dimensions (cannot be zero)

- Learning objective clarity
- Age-band appropriateness
- Safety and ethics
- Localization and accessibility
- Technical reliability

## 2) Manifest Peer Review (mandatory before manifest promotion)

Every manifest candidate must pass a 2-person review:
- Product/editor reviewer
- Engineering/QA reviewer

### Peer-review checklist

1. Rubric scores attached for changed/new items.
2. Phase 2 category count gate report attached.
3. Category acceptance smoke report attached.
4. Learning effectiveness and engagement gate reports attached.
5. Localization lint output attached.
6. Breaking change risk assessed (schema/route/metadata compatibility).
7. Rollback path defined (last-known-good manifest id/version).

### Decision outcomes

- `APPROVED` - can enter release candidate.
- `APPROVED_WITH_CONDITIONS` - allowed only with explicit follow-up tasks.
- `REJECTED` - cannot be merged into release candidate manifest.

## 3) Deprecation Policy (weak modules/content retirement)

### Deprecation triggers

Any item/category enters deprecation review if at least one is true:
- Fails critical rubric dimensions.
- Repeated high `boredom_signal`.
- Repeated high drop-off with low mastery gain.
- Security/compliance or localization violations.
- Broken route/asset reliability in production.

### Deprecation lifecycle

1. `DEPRECATION_CANDIDATE` - item flagged, owner assigned.
2. `SOFT_DEPRECATED` - hidden from recommendations/new sessions.
3. `HARD_DEPRECATED` - removed from active manifest.
4. `ARCHIVED` - retained only for audit history.

### Recovery path

Deprecated item can be restored only if:
- rubric re-score passes threshold;
- required gates pass in CI/smoke;
- peer review outcome is `APPROVED`.

## 4) Required Evidence Pack for P2-006 Compliance

For each release wave include:
- rubric score table by changed item/category;
- peer-review decision log;
- deprecation candidates and decisions;
- links to gate reports under `docs/`.

## 5) Enforcement

`P2-006` is considered complete only when:
- this policy file exists and is referenced by team workflow;
- smoke script confirms required sections exist;
- task trackers mark `P2-006` as done.
