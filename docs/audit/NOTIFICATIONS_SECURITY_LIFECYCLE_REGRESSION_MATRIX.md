# Notifications Security Lifecycle Regression Matrix

## Preconditions (must pass before matrix run)

- iOS Notifications permission: ON
- In-app filters: DND OFF, ImportantOnly OFF, HighPriorityOnly OFF, RateLimit OFF, QuietHours OFF
- Debug preflight section shows green readiness
- QA smoke injection available

## Matrix

| Case ID | App State | Network State | Trigger | Expected Result | Pass/Fail |
|---|---|---|---|---|---|
| NS-LC-01 | Foreground | Online | QA threat injection | Banner shown, item appears in list, `correlation_id` visible | |
| NS-LC-02 | Background | Online | QA threat injection | Notification delivered, on app open list reconciles from backend | |
| NS-LC-03 | Terminated | Online | QA threat injection | On launch, item present from `/api/notifications` with same `correlation_id` | |
| NS-LC-04 | Foreground | Offline -> Online | QA threat injection offline then reconnect | Local UX signal appears, then backend reconciliation after reconnect | |
| NS-LC-05 | Background | Offline -> Online | QA threat injection and delayed reconnect | No data loss after reconnect, unread count consistent | |
| NS-LC-06 | Foreground | Online | Mark-as-read flow | `/api/notifications/read` success true, unread count never negative | |
| NS-LC-07 | Foreground | Online | Multiple rapid security events | No crash, no duplicate IDs, counters consistent | |
| NS-LC-08 | Foreground | Online | Force contract violation payload (test env) | Client fails fast with explicit contract error | |
| NS-LC-09 | Foreground | Online | Family chat + security notifications mix | No delegate conflict, both behaviors preserved | |
| NS-LC-10 | Relaunch | Online | After prior delivered notifications | `Last sync` updates, health panel shows expected counts | |

## Required Artifacts Per Run

- Preflight screenshot
- Notifications list screenshot with `ID: <correlation_id>`
- Pipeline Health screenshot
- Timestamped note of trigger time and visible time
- API response evidence (`/api/notifications`, `/api/notifications/read`)
