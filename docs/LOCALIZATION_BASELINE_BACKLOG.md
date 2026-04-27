# Localization Baseline Backlog

## Goal

Close current localization debt without blocking feature delivery, then switch to strict `Feature mode` where every PR must pass `localization-lint`.

This backlog is based on current `scripts/localization_lint.py` output.

## Delivery Model

## Wave 1: Baseline cleanup

Scope:
- RU/EN parity for missing keys.
- Replace hardcoded user-facing strings with localization keys.
- Keep behavior stable, no feature redesign.

Exit criteria:
- `python3 scripts/localization_lint.py` passes on `main`.
- No missing RU/EN key parity.
- No hardcoded user-facing text in active screens.

## Wave 2: Feature mode

Scope:
- Every new feature PR includes RU and EN keys in same PR.
- PR fails if `localization-lint` fails.
- Namespace map and checklist are mandatory.

Exit criteria:
- Zero bypass merges for localization checks.
- Stable pass rate for `localization-lint` in CI.

---

## Priority Backlog

## P0 (blockers for baseline pass)

### 1) RU/EN key parity gap

Problem:
- Missing EN keys for `network_protection_*` cluster.

Actions:
- Add missing EN entries in `Resources/Localization/en.lproj/Localizable.strings`.
- Validate placeholder parity with RU values.
- Smoke-check affected Network Protection UI.

Target files:
- `Resources/Localization/ru.lproj/Localizable.strings`
- `Resources/Localization/en.lproj/Localizable.strings`

Definition of done:
- No "Keys missing in EN" in lint output.

### 2) High-impact screens with heavy hardcoded text

Problem:
- Multiple production screens contain hardcoded RU or EN strings.

Actions:
- Replace literals with keys from namespace map.
- Add RU and EN values for all new keys in same commit.
- Localize errors, empty states, and action buttons.

Target screens:
- `Screens/07_ParentalControlScreen.swift`
- `Screens/03_NetworkProtectionScreen.swift`
- `Screens/11_ProfileScreen.swift`
- `Screens/MainScreenWithRegistration.swift`
- `Screens/RewardsQuickModal.swift`
- `Screens/RewardsModalView.swift`

Definition of done:
- Zero hardcoded violations in these files.

### 3) Game and reward localization cluster

Problem:
- Many hardcoded strings in game UX and reward UX.

Target screens:
- `Screens/GamesParentalControlScreen.swift`
- `Screens/WheelOfFortuneView.swift`
- `Screens/ChildRewardsScreen.swift`
- `Screens/UnicornUniverseView.swift`

Actions:
- Move all user-facing strings to `games.*`, `rewards.*`, `progress.*` keys.
- Keep emoji/icon characters if product-approved, but text must be localized.

Definition of done:
- Lint clear for game/reward screens.

## P1 (stability and quality hardening)

### 4) Secondary and utility screens

Target screens:
- `Screens/IoTSecurityScreen.swift`
- `Screens/WidgetConfigurationScreen.swift`
- `Screens/CrashLogsView.swift`
- `Screens/26_ActivationCodeScreen.swift`

Actions:
- Localize all visible labels/messages/buttons.
- Ensure accessibility strings are localized too.

### 5) Fallback and diagnostic screens policy

Target screens:
- `Screens/SettingsScreenFallback.swift`
- `Screens/SettingsTestSuiteView.swift`

Actions:
- Keep internal diagnostics in English if needed, but either:
  - move them under debug-only compilation guards, or
  - localize if visible in production builds.

Definition of done:
- No production-visible hardcoded text from fallback/diagnostic screens.

## P2 (cleanup and prevention)

### 6) Legacy/simple screens normalization

Target screens:
- `Screens/SimplePrivacyPolicyScreen.swift`
- `Screens/SimpleTermsOfServiceScreen.swift`
- remaining low-traffic legacy views from lint output.

Actions:
- Normalize to current namespace and remove duplicate wording.
- Archive or deprecate duplicate legacy UI where possible.

### 7) Lint precision tuning

Actions:
- Reduce false positives with controlled allowlist for numeric-only and debug-only patterns.
- Keep rule strict for user-facing literals.

Definition of done:
- Low-noise lint output with clear actionable findings.

---

## Parallel Execution Plan

Recommended parallel lanes:
- Lane A: parity keys (`network_protection_*`) and placeholder fixes.
- Lane B: family/parental/main screens.
- Lane C: games/rewards cluster.
- Lane D: secondary/utility screens.

Suggested cadence:
- Day 1-2: P0 parity + top screens.
- Day 3-4: P0 games/rewards.
- Day 5: P1 cleanup + full lint pass + regression smoke.

---

## Merge Policy During Baseline

- Use small PR batches per screen cluster.
- Each PR must:
  - pass `localization-lint`,
  - include RU/EN keys,
  - include screenshot proof for RU and EN where UI changed.

Temporary rule:
- If baseline branch is used, allow staged merges only into baseline branch, not directly to release branch, until baseline exit criteria are met.

---

## Feature Mode Activation Checklist

- [ ] Baseline branch fully merged.
- [ ] `localization-lint` passes on `main`.
- [ ] Team uses:
  - `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
  - `docs/LOCALIZATION_PR_CHECKLIST.md`
  - `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`
- [ ] PR template includes mandatory localization section.
- [ ] No exception policy for hardcoded user text.

