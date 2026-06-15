# TestFlight beta criteria — Antifake (Q-04)

**Related:** `ANTIFAKE_TESTFLIGHT_CHECKLIST.md` (R-01) · device sign-off `ANTIFAKE_QA_SIGNOFF.md` (R-02)

---

## Entry (internal beta)

| # | Criterion | Gate |
|---|-----------|------|
| 1 | R-01 static pass | `python3 scripts/verify_antifake_release_readiness.py` |
| 2 | G-01 marketing honest | `python3 scripts/verify_antifake_marketing_claims.py` |
| 3 | Q-05 no mock in code paths | `python3 scripts/verify_antifake_no_mock_pre_submit.py` |
| 4 | Q batch static | `bash scripts/verify_antifake_q_static.sh` |
| 5 | Prod smoke + af-11 | `ANTIFAKE_SMOKE_POLL_JOB=1` smoke + `antifake_prod_gate_af11.py` |
| 6 | Golden text Q-06 | smoke verdict `real_agent` or honest `local_ml` |
| 7 | Call-directory contract Q-03 | `python3 -m unittest backend_tests.test_antifake_call_directory_contract` |

---

## Exit (external beta / App Store prep)

| # | Criterion | Owner |
|---|-----------|-------|
| 1 | Device: Call Directory label D-04 | QA sign-off R-02 |
| 2 | Device: post-call flow E-06 | `ANTIFAKE_POST_CALL_DEVICE_QA.md` |
| 3 | Privacy manifests N-01 on device | Settings → Privacy report |
| 4 | No `sfm_mock` in prod API 24h | Q-05 prod log grep (ops) |
| 5 | `bypassPremiumGate = false` | G-03 ✅ · `verify_antifake_bypass_off.py` |
| 6 | `ANTIFAKE_ALLOW_FREE=0` on prod | B-10 ✅ |

---

## Blockers (do not promote build)

- Smoke fail or gate af-11 fail
- Q-05 mock strings in user-facing responses
- Marketing gate G-01 fail
- Job failure P-01 alert sustained > 1h
- Fraud DB rollback P-04 incident without sign-off

---

## One-liner (CI / agent)

```bash
bash scripts/verify_antifake_q_static.sh && \
python3 scripts/verify_antifake_no_mock_pre_submit.py && \
python3 -m unittest backend_tests.test_antifake_call_directory_contract -q
```

Device QA rows remain manual until DEVICE phase.
