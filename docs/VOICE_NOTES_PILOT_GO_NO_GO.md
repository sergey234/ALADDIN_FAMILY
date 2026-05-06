# Voice Notes Pilot Go/No-Go

## Pilot Goal

Validate production readiness of Voice Notes with measurable quality thresholds.

## Pilot Window

- Duration: 7-14 days
- Audience: internal team + controlled beta cohort
- Devices: at least 3 iPhone generations

## KPI Targets

- `crash_free_sessions_voice`:
  - Target: `>= 99.5%`
  - No-Go threshold: `< 99.0%`

- `mean_time_to_first_feedback`:
  - Target: `<= 1.5 s`
  - No-Go threshold: `> 2.5 s`

- `empty_result_rate` (transcription):
  - Target: `<= 12%`
  - No-Go threshold: `> 20%`

- `transcription_success_rate`:
  - Target: `>= 80%`
  - No-Go threshold: `< 65%`

- `voice_record_interruption_rate`:
  - Monitor only (contextual by user behavior/device state)
  - No-Go trigger: confirmed data loss during interruption

- UX feedback score (internal survey):
  - Target: `>= 4.2 / 5`
  - No-Go threshold: `< 3.8 / 5`

## Mandatory Functional Gates

- Interruption autosave works on real device.
- No data corruption after app relaunch.
- Search/filter/rename/delete+undo stable.
- AI Assistant mic errors are clear/localized.
- Family Chat feedback path from `+` menu is stable.

## Go/No-Go Decision Template

- Build:
- Pilot dates:
- Sample size:
- KPI summary:
  - crash-free:
  - first-feedback latency:
  - empty-result rate:
  - transcription success:
  - UX score:
- Critical defects open:
- Decision: `GO` / `NO-GO`
- Conditions for re-evaluation:

## Escalation Rules

- Immediate NO-GO if:
  - repeatable crash in core recording flow,
  - note loss after interruption,
  - severe privacy/compliance violation.
