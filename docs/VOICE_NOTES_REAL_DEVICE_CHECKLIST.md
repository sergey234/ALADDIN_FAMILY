# Voice Notes: Real Device Validation Checklist

## Goal

Validate Voice Notes behavior on real iPhone hardware, with priority on interruption and transcription timeout scenarios in local-only mode.

## Scope

- Recording flow: start / pause / resume / stop
- Interruption autosave
- On-device transcription outcomes
- Search and filters
- Rename and delete + undo
- Local-only storage expectations

## Test Environment

- Devices: at least 3 iPhone generations (older, mid, latest)
- iOS: minimum supported + latest stable
- Audio routes: built-in mic, wired headset (if available), Bluetooth (AirPods or similar)
- Build: latest internal build with Voice Notes enabled

## Pre-Check

1. Install clean build (or clear app data if needed).
2. Confirm microphone and speech recognition permissions are requested on first use.
3. Ensure device has enough storage for long recording tests.
4. Confirm network state does not affect core recording flow (Airplane Mode optional sanity check).

## Core Recording Scenarios

### VN-RD-01: Start Recording

- Action: tap `Record` from idle state.
- Expected:
  - Status switches to listening state.
  - Timer starts increasing every second.
  - UI remains responsive (<150ms tap feedback target).

### VN-RD-02: Pause/Resume

- Action: start recording -> pause -> resume.
- Expected:
  - Pause freezes timer and state changes to paused.
  - Resume returns to listening state and timer continues.
  - No duplicate session or crash.

### VN-RD-03: Stop and Save

- Action: start recording -> stop.
- Expected:
  - State goes through processing and returns to saved.
  - New note appears in list with generated title.
  - Transcript initially shows pending status, then updates when ready.

## Interruption Scenarios (Priority)

### VN-RD-10: Phone Call Interruption

- Action: start recording, then trigger incoming call.
- Expected:
  - Recording auto-stops safely.
  - Draft/note is autosaved (not lost).
  - Status reflects autosaved after interruption.
  - App remains stable after returning from call.

### VN-RD-11: Audio Route Change During Recording

- Action: start recording, connect/disconnect Bluetooth headset.
- Expected:
  - No crash or frozen UI.
  - Session either continues safely or autosaves according to service behavior.
  - Note remains accessible in history.

### VN-RD-12: Background/Lock Interruption

- Action: start recording, lock screen or move app to background, then return.
- Expected:
  - No data corruption.
  - If interrupted, recording is autosaved and visible in list.
  - App restores usable state on foreground.

## Transcription Timeout and Error Scenarios (Priority)

### VN-RD-20: Timeout Handling

- Action: run on-device transcription case likely to exceed timeout (long/unclear audio).
- Expected:
  - Timeout does not block UI.
  - Note remains saved.
  - Transcript status shows localized timeout message.

### VN-RD-21: Permission Denied

- Action: disable Speech permission in iOS Settings, then save a new recording.
- Expected:
  - Recording still saves locally.
  - Transcript field shows localized permission-denied status.

### VN-RD-22: Recognizer Unavailable

- Action: run on unsupported or restricted recognizer context.
- Expected:
  - Recording flow unaffected.
  - Transcript status shows localized unavailable message.

## UX Scenarios

### VN-RD-30: Empty States

- Action:
  - open Voice Notes with no notes;
  - run search/filter yielding zero results.
- Expected:
  - Correct empty-state title/subtitle for both cases.

### VN-RD-31: Search and Filters

- Action: create multiple notes with different text/tags/dates, then use search and each filter.
- Expected:
  - Relevant notes appear correctly.
  - No stale results when switching filters.

### VN-RD-32: Rename Note

- Action: rename note via context menu.
- Expected:
  - New title is saved and persists after app restart.
  - Empty/whitespace-only name is not accepted as final title.

### VN-RD-33: Delete and Undo

- Action: delete note, tap undo within 5 seconds; repeat and allow timeout without undo.
- Expected:
  - Undo restores note correctly.
  - Without undo, deletion finalizes and audio file is removed.

## Local-Only Privacy Validation

### VN-RD-40: Local Storage Only

- Action: record, save, restart app.
- Expected:
  - Note and audio persist locally on the same device.
  - No dependency on backend availability for listing/playing metadata.

### VN-RD-41: No Server Requirement for Voice Notes Core

- Action: optional network-off run (Airplane Mode), create and save recording.
- Expected:
  - Recording and local persistence work.
  - Non-critical local transcription status may vary by OS capabilities, but app does not fail.

## Pass/Fail Exit Criteria

- No crashes in all priority scenarios (`VN-RD-10`, `VN-RD-12`, `VN-RD-20`).
- No data loss after interruptions.
- All user-facing error/timeouts are localized and understandable.
- Empty states/search/filter/rename/delete flows are stable.

## Evidence to Capture

- Screen recording for interruption scenarios
- Screenshot of timeout and permission-denied transcript states
- Device model + iOS version for each run
- Repro steps for any failure with exact observed vs expected
