# QA TestFlight Checklist (Final)

Use this matrix for final verification on real devices/TestFlight.

## A. Voice messages (Family Chat)

- [ ] Send voice message in family chat.
- [ ] Play immediately after send.
- [ ] Verify sound is audible.
- [ ] Re-open chat and replay (cache path check).
- [ ] Verify error state appears if URL is broken/offline.

## B. Onboarding legal gate

- [ ] Final onboarding step shows both links:
  - Privacy Policy
  - Terms of Service
- [ ] Start is disabled until both checkboxes are enabled.
- [ ] Skip on final step is disabled until both checkboxes are enabled.
- [ ] Accepted flags are persisted after app restart.

## C. Add Member UX

- [ ] Screen scrolls on small display.
- [ ] `Cancel` is always visible in bottom safe area.
- [ ] `Cancel` is tappable with dynamic text sizes.
- [ ] Back and option buttons still work correctly.

## D. Security/Lessons readability (Light/Dark)

- [ ] Open Security Education in light mode and verify text contrast.
- [ ] Switch to dark mode and verify all text remains readable.
- [ ] Validate lesson cards and tip rows for both themes.

## E. Sync status localization

- [ ] Russian locale: sync badges show Russian terms (no `Idle`/`Syncing` in English).
- [ ] English locale: sync badges show English terms.
- [ ] Validate on screens:
  - Family
  - Settings
  - Network Protection
  - Threat category detail screens

## F. Tariff limits SSOT

- [ ] Tariffs screen shows family-member limits aligned with SSOT.
- [ ] Personal limit displayed as `2` family members.
- [ ] Family/Premium values match `SubscriptionManager` table.

## G. Trial anti-abuse (privacy-safe)

- [ ] First trial activation succeeds on clean install/device state.
- [ ] Rapid repeated trial attempts hit local cooldown and are blocked.
- [ ] Request payload includes `anti_abuse` signals (inspect proxy/logs).
- [ ] Backend fallback to free works when anti-abuse gate denies trial.

## H. Safari content blocker reliability

- [ ] App shows correct state: enabled / needs activation / extension missing.
- [ ] Opening iOS settings and returning refreshes state.
- [ ] If extension enabled in iOS Safari settings, app reflects enabled state.
- [ ] If disabled in settings, app reflects needs activation state.

## I. Build and release smoke

- [ ] Debug build on simulator succeeds.
- [ ] TestFlight build installs and launches.
- [ ] No startup crashes with extension embedded.
- [ ] Basic navigation across modified screens is stable.

## Exit criteria

- [ ] All critical checks (A, B, C, H) passed.
- [ ] No blocker severity bugs remain.
- [ ] Product + QA sign-off recorded.

