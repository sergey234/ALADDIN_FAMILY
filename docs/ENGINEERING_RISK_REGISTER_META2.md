# Engineering Risk Register (META-2)

| ID | Risk | Impact | Likelihood | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Canonical JSON drift for signature checks | Release-blocking false fails or unsafe accepts | Medium | Keep canonical serializer policy + contract tests | iOS + Backend |
| R2 | Key rotation mismatch across environments | Auth/signature outages | Medium | Rotation runbook + staged rollout checks | Security |
| R3 | Flaky network integration tests | CI instability and noisy regressions | High | Enforce explicit staging opt-in and skip policy (META-3) | QA/Infra |
| R4 | IPA size growth from media/assets | App Store rejection risk (>500MB target) | Medium | Automated size gate (G20) + top-assets report | iOS |
| R5 | Backend dependency instability | User-facing feature regressions despite app changes | Medium | health/smoke gates + graceful degradation paths | Backend |
| R6 | Localization regressions in new UI | UX trust decline / support load increase | Medium | W-LOC policy + lint in CI + checklist | iOS |
| R7 | Incomplete DSAR evidence chain | Compliance review delays | Medium | Structured evidence pack generation (G21-G23) | Product/Security |
| R8 | Device/OS coverage gaps | Release-only crashes on untested variants | Medium | Device matrix process (G18) + pre-release manual ring | QA |

## Review Cadence

- Weekly during active release waves.
- Mandatory review before TestFlight RC and production release.

