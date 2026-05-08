# Notifications Security Proof Report Template

## Run Metadata

- Date:
- Build:
- Device model / iOS:
- Tester:
- Environment (staging/prod-test):

## Preflight

- iOS notifications permission: PASS/FAIL
- DND off: PASS/FAIL
- ImportantOnly off: PASS/FAIL
- HighPriorityOnly off: PASS/FAIL
- RateLimit off: PASS/FAIL
- QuietHours off: PASS/FAIL
- Preflight screenshot: `<path-or-link>`

## Scenario Execution

### Scenario ID

- Case: `NS-LC-XX`
- Trigger type: `qa_forced_scenario / real backend source`
- Trigger timestamp:
- Correlation ID:

### Evidence

- Notifications screen screenshot with ID: `<path-or-link>`
- Pipeline health screenshot: `<path-or-link>`
- `/api/notifications` evidence: `<log/screenshot/path>`
- `/api/notifications/read` evidence (if applicable): `<log/screenshot/path>`

### Timing

- Detection timestamp:
- Visible in UI timestamp:
- End-to-end latency (sec):

## Result

- PASS/FAIL:
- If FAIL, primary failure stage:
  - detect / ingest / store / api / ui / reconciliation
- Notes:

## Follow-up Actions

- Bug/Task IDs:
- Owner:
- ETA:
