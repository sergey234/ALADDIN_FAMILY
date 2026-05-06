# Voice Notes Smoke and Regression Plan

## Purpose

Provide a fast, repeatable validation pass for Voice Notes and adjacent regressions in AI Assistant and Family Chat.

## When to Run

- Before internal build handoff
- After changes in recording/transcription/localization flows
- After changes in AI Assistant microphone logic
- After changes in Family Chat message composer or voice flow

## Smoke Scope (15-25 minutes)

### A. Voice Notes Core (Manual)

1. Open Voice Notes from Settings.
2. Start recording -> pause -> resume -> stop.
3. Validate note appears in list with expected status transitions.
4. Rename note via context menu and verify persistence after reopen.
5. Delete note and press Undo within 5 seconds.
6. Repeat delete and do not undo (final removal).
7. Use search and each filter tab; verify correct empty states.

Expected:
- No crash.
- No frozen UI.
- No data loss.
- Localized statuses/messages are shown.

### B. Interruption/Timeout (Manual, High Priority)

1. Start recording and trigger interruption (call/lock/background).
2. Return to app and verify autosaved note exists.
3. Validate transcription fallback status for timeout/permission/unavailable case.

Expected:
- Recording safely autosaves on interruption.
- Note stays available.
- User sees clear fallback text.

### C. AI Assistant Regression (Manual)

1. Open AI Assistant.
2. Tap microphone, speak short phrase, stop.
3. Validate recognized text appears or clear localized error shown.
4. Validate feedback star opens feedback sheet and submission is still functional.

Expected:
- Mic flow does not get stuck in inconsistent color-only state.
- Alerts are user-readable and localized.

### D. Family Chat Regression (Manual)

1. Open Family Chat.
2. Open `+` menu and tap `Обратная связь` / `Feedback`.
3. Submit rating via common feedback sheet.
4. Verify composer area remains usable (no star button in input bar).

Expected:
- Feedback entry point works from `+` menu.
- Composer width/UX is preserved.

## Minimal Automated Checks (CLI)

Run a compact existing test subset after smoke changes:

```bash
xcodebuild test \
  -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:Tests/UnitTests/AudioInterruptionTests \
  -only-testing:Tests/UnitTests/FeedbackSystemTests \
  -only-testing:Tests/UnitTests/LocalizationManagerTests
```

If simulator naming differs locally, use available destination from:

```bash
xcodebuild -showdestinations -scheme ALADDIN
```

## Pass/Fail Gate

Release candidate passes smoke only if:

- All manual sections A-D pass without crash/data loss.
- Interruption autosave is confirmed at least once on real device.
- Automated subset exits successfully.

Fail immediately if:

- Voice note disappears after interruption.
- AI Assistant mic fails silently without actionable message.
- Family Chat feedback path is missing or broken.

## Defect Logging Template

- Area: (Voice Notes / AI Assistant / Family Chat)
- Build:
- Device + iOS:
- Repro steps:
- Expected:
- Actual:
- Severity:
- Attachments:

## Execution Order Recommendation

1. Run Voice Notes manual smoke (A + B) on real device.
2. Run AI Assistant + Family Chat regression (C + D).
3. Run automated subset.
4. Record final go/no-go note for the build.
