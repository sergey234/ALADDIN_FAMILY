# Phase 0 Foundation Execution

## Status

Phase 0 implementation artifacts are defined and approved for execution tracking.
This document is the source of truth for closing Phase 0 tasks in `NEXT_VERSION_IMPLEMENTATION_PLAN.md`.

## 0.1 MVP Scope and Cut Criteria

### MVP vertical slice

- Audience: child 7-12 years.
- Core flow: Child interface -> category selection -> content open -> progress event -> parent dashboard visibility.
- Family flow: parent creates/joins family and sees child activity summary.
- Safety flow: basic parental limits and content filters from parental control hub.

### Feature cut criteria

Use strict prioritization for each phase:
- Must: required for functional release and safety baseline.
- Should: important but can ship in patch release.
- Could: optional enhancements.
- Wont: explicitly postponed to v2+.

### Scope statement for 190 units

`190` content units are roadmap v2+ and not part of MVP completion definition.

### Localization DoD rule

Any UI task is done only if:
- RU and EN keys are delivered in the same PR.
- `localization-lint` passes.
- Accessibility strings are localized.

## 0.2 Kids / App Review Readiness

### Kids review checklist

- Kids category readiness and age-appropriate content mapping.
- Parental gate for sensitive actions.
- Safe external link behavior and no uncontrolled link-outs.
- App Store metadata consistency for age rating and safety declarations.

### Evidence package

For each release candidate include:
- screenshots RU and EN for changed user flows;
- localization lint result;
- privacy and parental control behavior proof;
- regression test notes for child + family + 60+ critical flows.

### Reference docs

- `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
- `docs/LOCALIZATION_PR_CHECKLIST.md`
- `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`

## 0.3 Privacy Governance (COPPA / GDPR frame)

### Data minimization matrix

- Child profile: only necessary data for learning and safety.
- Family roster: role-based access only.
- Analytics: minimal, non-sensitive, policy-limited for child contexts.

### Consent versioning

Track:
- `consent_version`
- `consent_date`
- `consent_source`

Consent changes must be auditable on backend side.

### DSAR workflow

- Parent requests child data export.
- Parent requests child data deletion.
- System logs request and completion status.

### Retention policy

- Define retention periods per data class.
- Add scheduled purge jobs.
- Document fallback and restoration boundaries.

## 0.4 Family Sharing vs Family Controls split

### App-level family model

- `ChildProfile` and family roster are product-level identity and relationship entities.
- Used for UI, permissions, and family-specific app behavior.

### Family Sharing role

- Purchase and family ecosystem context.
- Not treated as universal source of child profile data for all UI.

### Family Controls branch

- Separate device-level parental control pipeline:
  - authorization;
  - managed settings;
  - device activity.
- Entitlements and extension readiness tracked as dedicated implementation stream.

