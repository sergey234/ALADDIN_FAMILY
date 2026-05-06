# Voice Notes QA Matrix

## Objective

Standardize validation coverage for Voice Notes across devices, audio routes, and high-risk runtime conditions.

## Device Matrix

| Tier | Example Device | iOS Version | Priority |
|---|---|---|---|
| Legacy | iPhone 11 / SE (2nd gen) | Minimum supported iOS | P0 |
| Mid | iPhone 13 | Current - 1 | P0 |
| Latest | iPhone 15/16 series | Latest stable iOS | P0 |

## Audio Route Matrix

| Route | Setup | Priority |
|---|---|---|
| Built-in microphone | No external accessories | P0 |
| Bluetooth headset | AirPods / BT headset connected | P0 |
| Wired headset (if available) | Lightning/USB-C audio adapter | P1 |

## Scenario Matrix

| ID | Scenario | Legacy | Mid | Latest | Built-in | Bluetooth | Wired | Priority |
|---|---|---:|---:|---:|---:|---:|---:|---|
| VM-01 | Start recording from idle | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P0 |
| VM-02 | Pause -> Resume -> Stop | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P0 |
| VM-03 | Save note + pending transcript -> final status | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P0 |
| VM-04 | Incoming call interruption autosave | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | P0 |
| VM-05 | Lock screen / background interruption handling | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | P0 |
| VM-06 | BT route switch during active recording | ○ | ✓ | ✓ | ○ | ✓ | ○ | P0 |
| VM-07 | Timeout transcription status (long/unclear audio) | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | P0 |
| VM-08 | Speech permission denied fallback | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | P0 |
| VM-09 | Recognizer unavailable fallback | ○ | ✓ | ✓ | ✓ | ✓ | ○ | P1 |
| VM-10 | Search + filters + empty states | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P0 |
| VM-11 | Rename note persistence after relaunch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P0 |
| VM-12 | Delete + Undo (within 5s / after timeout) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P0 |
| VM-13 | Long recording 30+ minutes stability | ○ | ✓ | ✓ | ✓ | ✓ | ○ | P0 |
| VM-14 | Local-only behavior in Airplane Mode | ✓ | ✓ | ✓ | ✓ | ✓ | ○ | P1 |
| VM-15 | No crash on repeated quick taps Record/Stop | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | P1 |

Legend: `✓` mandatory, `○` optional/stretch.

## Execution Order (Recommended)

1. Run all P0 scenarios on Mid + Latest with built-in mic.
2. Run interruption and long-record P0 scenarios on Legacy.
3. Repeat critical P0 scenarios with Bluetooth route.
4. Run P1 scenarios based on time budget.

## Pass Criteria

- 0 crashes in all P0 scenarios.
- 0 data loss after interruption.
- Correct localized status for timeout / permission denied / unavailable.
- Search/filter/empty states and rename/delete flows are stable.
- Local-only behavior works regardless of network state.

## Defect Logging Template

- Scenario ID:
- Device + iOS:
- Audio route:
- Build number:
- Steps to reproduce:
- Expected result:
- Actual result:
- Frequency:
- Attachments (video/screenshot/log):

## Exit Recommendation

Feature is candidate for pilot only when all P0 scenarios pass on all three device tiers and at least one Bluetooth route run completes without blockers.
