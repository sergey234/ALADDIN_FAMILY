# Remediation Backlog - Stage 3.3 (Build 124/125)

## Objective
- Convert Stage 3 findings into executable remediation work with priorities, owners, risks, and acceptance criteria.
- Eliminate hidden mock-success and restore business-ready routes to real `200` responses.

## Priority Model
- **P0**: blocks production readiness.
- **P1**: high impact, can follow P0.
- **P2**: hardening and operational resilience.

---

## P0 Backlog (Must Fix Before Release Gate)

| ID | Area | Problem | Owner | Risk | Action | Acceptance Criteria |
|---|---|---|---|---|---|---|
| P0-1 | Proxy/SFM contract | Proxy function naming (`path -> underscore`) has `0/124` direct matches with runtime SFM functions | Backend | Very High | Introduce explicit route-to-SFM mapping table for critical families (`reports`, `gamification`, `family`, `parental-control`, `v1/parental-control`) | For mapped critical routes: no fallback markers and real typed payloads |
| P0-2 | SFM runtime coverage | Missing callable methods for critical routes force fallback | Backend/SFM | Very High | Implement/alias required SFM methods (or adapter methods) to match mapping table | `missing_count` in gap report for critical families -> `0` |
| P0-3 | Mock policy consistency | Sensitive paths previously leaked `200 + mock` | Backend | High | Keep hard-fail (`503`) for sensitive mock responses until real handlers are in place; enforce for both `main.py` and `api_gateway.py` | No `200` body with `source=sfm_mock` or `result=mock_fallback` on critical routes |
| P0-4 | iOS token hygiene | JWT was historically used as `userId` in URL in some views | iOS | High | Finalize removal of token-as-userId in all gamification callers and managers | `jwt_in_url_count = 0` in full run and access-log regex scan |
| P0-5 | Critical route restore | 37 critical routes currently degraded with `503` | Backend + QA | Very High | Restore real backend handling for business-ready set (`family/members`, `user/profile`, `gamification/*`, core parental routes) | `unauthorized_503_count = 0` for business-ready routes in full run |

---

## P1 Backlog (High Value After P0)

| ID | Area | Problem | Owner | Risk | Action | Acceptance Criteria |
|---|---|---|---|---|---|---|
| P1-1 | Endpoint contract drift | 118 iOS contract drift candidates vs OpenAPI inventory | iOS + Backend | High | Reconcile endpoint definitions, remove dead/legacy paths, align docs/spec | Drift candidates reduced to approved exceptions list |
| P1-2 | Auth coverage in audit | Some routes evaluated only in no-auth safe mode | QA + Backend | Medium | Extend runner with auth profile matrix and route-level auth expectations | Per-route auth expectation pass rate >= target |
| P1-3 | Subscription sync noise | Duplicate event logs and non-implemented sender create noise/risk | iOS | Medium | Implement/guard `flushPendingEvents` and deduplicate dispatch | No duplicate "would send" events in single cycle |
| P1-4 | TTL policy validation | Long-lifetime token behavior not fully policy-verified | Backend + iOS | Medium | Confirm token TTL/exp strategy and clock-skew handling; document policy | Signed TTL policy + tests passing |

---

## P2 Backlog (Stability / Operations)

| ID | Area | Problem | Owner | Risk | Action | Acceptance Criteria |
|---|---|---|---|---|---|---|
| P2-1 | Observability | No guaranteed alerting SLO around mock/503 leakage | DevOps | Medium | Add metrics + alerts (`count_sfm_mock`, `count_mock_fallback`, `count_503_protection_backend_unavailable`) | Alerts firing on synthetic fault tests |
| P2-2 | CI/CD gate | Full regression not enforced in release pipeline | DevOps + QA | Medium | Add nightly full-run and pre-release mandatory gate | Build blocked if gate fails |
| P2-3 | Documentation drift | Architecture doc can diverge from runtime behavior | Tech Lead | Medium | Generate inventory/report artifacts automatically each release | Release checklist includes generated report diff |

---

## Execution Order (Recommended)
1. **P0-1 + P0-2** in one backend sprint branch (mapping + implementations).
2. Keep **P0-3** active as safety net while restoring routes.
3. Apply/verify **P0-4** across all iOS callers.
4. Validate **P0-5** with full-run and critical E2E.
5. Move to P1/P2 hardening.

---

## Release Gate (Final)
- `0` endpoint with `source=sfm_mock` on critical routes.
- `0` endpoint with `result=mock_fallback` on critical routes.
- `0` unauthorized `503` on business-ready routes.
- `0` JWT occurrences in URL/path/query logs.
- Critical E2E suite (2+ children, switch child, DNS on/off, reports/rewards, offline/online) fully green.

