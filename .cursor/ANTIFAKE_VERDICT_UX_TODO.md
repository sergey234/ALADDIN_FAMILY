# Antifake Verdict UX + SFM Smoke — Cursor tracker

Полный план: `docs/ANTIFAKE_VERDICT_UX_AND_SFM_SMOKE_PLAN.md`

## P0 — Smoke (exit 22)

- [x] **af-smoke-01** — `sfm_prod_smoke.sh`: убрать `curl -f`, проверять `%{http_code}==503`
- [x] **af-smoke-02** — `sfm_truth_check.sh`: то же для probe execute
- [x] **af-smoke-03** — Deploy VPS + `systemctl start aladdin-sfm-prod-smoke.service` → exit 0

## P0 — Server contract

- [x] **af-ux-20** — `insufficient_data` при `too_short` / neutral без hits
- [x] **af-ux-21** — `fake_risk` в `_build_response` (= confidence)

## P0 — iOS presentation

- [x] **af-ux-22** — `AntifakeVerdictPresentation.swift`
- [x] **af-ux-23** — `AntifakeVerdictCard` — «Риск подделки: N% · низкий/средний/высокий»
- [x] **af-ux-24** — Localization RU/EN + reasons + disclaimer
- [x] **af-ux-25** — Unit tests presentation + `insufficient_data`

## P1 — Smoke & ops

- [x] **af-smoke-04** — `test_antifake_prod_smoke.py` golden cases
- [x] **af-smoke-05** — RUNBOOK exit 22
- [x] **af-smoke-06** — Conditional restart sfm-core
- [x] **af-smoke-07** — `verify_prod_smoke_all.sh`

## P2 — Product

- [x] **af-p2-01** — `bypassPremiumGate = false`
- [ ] **af-p2-02** — Device QA Call Directory (manual on device)
