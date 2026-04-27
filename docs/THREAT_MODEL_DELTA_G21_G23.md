# Threat Model Delta (G21-G23)

## Scope

This delta summarizes security/privacy changes introduced by Wave 0-7 and W-LOC tracks that affect release risk posture.

## Changes Since Previous Baseline

1. Content lifecycle hardening
   - Manifest validation and fail-closed behavior in release-sensitive paths.
   - Rollback handling for last-known-good content snapshot.

2. Family/profile sync controls
   - Conflict-resolution strategies (`serverWins`, `localWins`, `latestUpdatedAt`).
   - Parent-facing conflict resolution controls.

3. Localization governance
   - Full-scope lint visibility and merge-scope localization gates.
   - Reduction of hardcoded user-facing literals in production paths.

4. A11y/security UX alignment
   - Localized retry and critical CTA hints in child content and parent dashboard flows.

## Residual Risks

- Network-dependent integration tests remain environment-sensitive.
- Bundle-size growth risk from media assets requires IPA size gate enforcement.
- Staging drift can produce false negatives in cross-device sync validation.

## Mitigations

- CI gates: localization lint, content QA smoke, device matrix process smoke, IPA size gate.
- Dedicated policy for `SyncBetweenDevicesTests` execution mode.
- Engineering risk register maintained in `docs/ENGINEERING_RISK_REGISTER_META2.md`.

