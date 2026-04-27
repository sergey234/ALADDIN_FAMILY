# Gamification Plan x Localization Sync Matrix

## Purpose

Synchronize the main implementation plan (142 tasks) with localization execution so feature delivery and RU/EN quality move together.

Related docs:
- `NEXT_VERSION_IMPLEMENTATION_PLAN.md`
- `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
- `docs/LOCALIZATION_PR_CHECKLIST.md`
- `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`
- `docs/LOCALIZATION_BASELINE_BACKLOG.md`

## Core Rule

No UI task is considered done unless:
1) RU and EN keys are delivered in the same PR,
2) no hardcoded user-facing strings remain in changed scope,
3) localization lint passes.

## Phase to Localization Mapping

| Phase | Main task count | Localization requirement |
|---|---:|---|
| Phase 0 | 13 | Define localization DoD, PR gate, and baseline cleanup plan |
| Phase 1 | 16 | Add `content.*` keys and localize content loading, errors, empty states |
| Phase 2 | 12 | Localize all content cards, category names, hints, and child-safe copy |
| Phase 3 | 12 | Localize progress, achievements, streak, and recommendation texts |
| Phase 4 | 12 | Localize audio settings, toggles, labels, and accessibility hints |
| Phase 5 | 12 | Localize animation-related feedback and CTA copy |
| Phase 6 | 8 | Localize reward/feedback texts and fallback behavior copy |
| Phase 7 | 23 | Localize family/profile/parental flows including PIN/security messages |
| Phase 8 | 34 | Validate full localization quality in testing and release checks |

## PR-level Execution Contract

Each PR for plan tasks must include:
- updated RU and EN keys in localization files;
- namespace compliance (`family.*`, `parental.*`, `settings.*`, `profile.*`, `privacy.*`, plus `content.*`, `progress.*`, `rewards.*`);
- localized accessibility fields;
- RU and EN screenshots;
- green `localization-lint`.

## Suggested Parallel Streams

- Stream A: parity keys and common namespaces
- Stream B: family/parental/profile screens
- Stream C: games/rewards/progress screens
- Stream D: settings/privacy/accessibility surfaces

## Weekly Control Metrics

Track weekly:
1) missing key parity count (RU vs EN),
2) hardcoded violation count,
3) localization-lint CI pass rate,
4) number of PRs merged with full RU/EN screenshot proof.

## Definition of 100 Percent Completion

The plan is complete only when:
- all 142 tasks are functionally done,
- localization gate is green for all merged work,
- no open localization baseline debt remains,
- no exceptions are used to bypass localization checks.

