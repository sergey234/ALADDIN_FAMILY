# Field UX With Children (G19 / W7-3)

## Goal

Validate real-world usability, comprehension, and safety perception for child-facing ALADDIN flows with parent supervision.

## Scope

- Child flows:
  - onboarding/start interaction
  - opening content and retrying after error/empty state
  - rewards interaction basics
- Parent-supervised safety flows:
  - family controls entry
  - parent confirmation gates for sensitive actions

## Session Format

- Participants:
  - 5-8 families
  - age bands: 6-8, 9-12, 13-15
- Session length: 25-35 minutes per family
- Moderation:
  - one facilitator
  - one observer/note taker
- Environment:
  - quiet room
  - one test device with stable network and one with intermittent network

## Consent And Privacy Requirements

- Parent/guardian written consent is mandatory before session start.
- Child assent (age-appropriate verbal confirmation) is required.
- No production personal data in test sessions.
- Recordings/screenshots only with explicit parent consent.
- Findings must use anonymized participant IDs (for example, `FAM-03`).

## Task Script (Per Session)

1. Open app and reach child content.
2. Find one activity and open it.
3. Recover from simulated loading/error/empty state.
4. Complete one content item and return.
5. Parent opens dashboard and validates recent activity visibility.
6. Parent triggers one sensitive action requiring confirmation.

## Metrics To Capture

- Task completion rate (%)
- Time on task (seconds)
- Number of moderator interventions
- Critical confusion points (count and severity)
- Child verbal confidence score (1-5, facilitator-rated)
- Parent trust/confidence score (1-5)

## Severity And Prioritization

- `P0` - safety/privacy blocker or impossible critical flow
- `P1` - high friction in core child/parent path
- `P2` - moderate UX issue with workaround
- `P3` - cosmetic or low-impact wording/layout issue

Prioritization rule for backlog:
- First: all `P0/P1` from safety-critical and task-completion blockers
- Then: highest-frequency `P2`
- Last: `P3` polish

## Deliverables

- One completed report per test wave:
  - `docs/FIELD_UX_CHILDREN_FINDINGS_G19.md`
- Product sign-off section completed in report:
  - owner name
  - date
  - decision (`GO` / `NO-GO` / `GO with conditions`)

## Product Sign-Off (Required)

- Product owner: `________________`
- Date: `________________`
- Decision: `________________`
- Notes: `________________`

