# Build 232 — согласованный план (опросник 2026-06-13)

**SSOT сессии:** этот файл · **Release SSOT:** [`docs/release/BUILD_232_RELEASE_SUMMARY.md`](../docs/release/BUILD_232_RELEASE_SUMMARY.md)  
**Bypass revert (P0-4):** ⏸ перед TestFlight / prod

---

## ✅ Сделано (все «сейчас» + supplemental)

| ID | Задача | Статус |
|----|--------|--------|
| build-232-core | Call Directory M2, M3 history, ux-1-06/07 | ✅ `3cfcf256` |
| P0-2 | ExportOptions — 4-й extension Call Directory | ✅ |
| P0-1 | Fastfile + decode_call_directory_profile_ci.sh | ✅ (в supplemental commit) |
| P0-3a–c | af-8 onboarding + FAQ voices + phone_scam | ✅ |
| P1-5 | af-5-04 deepfakes Premium + server sync | ✅ |
| P1-6 | af-4-05 spoof heuristics (server) | ✅ |
| P1-7 | af-4-01 scope doc звонков | ✅ |
| P1-8 | MARKETING_VERSION extension → 1.0.0 | ✅ |
| P1 | af-4-03 post-call → call tab + banner | ✅ |
| P1-9 | Sync docs / статусы | ✅ |
| **SIM** | xcodebuild Debug sim iPhone 13 Pro Max 18.4 | ✅ BUILD SUCCEEDED 2026-06-13 |

---

## ⏸ Перед TestFlight / prod

| ID | Задача |
|----|--------|
| P0-4 | Revert QA bypass: `bypassPremiumGate=false`, `ANTIFAKE_ALLOW_FREE=0` |
| — | Device QA Call Directory |

---

*Обновлено: 2026-06-13 — supplemental закрыт, sim build PASS.*
