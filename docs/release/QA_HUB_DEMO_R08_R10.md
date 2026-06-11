# R-08…R-10 — Hub demo для App Store / TestFlight reviewer

**Дата:** 2026-06-11 · **Build:** 227 · **Backend evidence:** `gates/hub-demo-smoke-report.json`  
**Review notes:** `COPY_04_APP_STORE_REVIEW_NOTES.md` · **Archive:** `QA_02_TESTFLIGHT_CHECKLIST.md`

---

## Preconditions

| Item | Requirement |
|------|-------------|
| Account | **Premium** test family (JWT device registered) |
| API | `https://aladdin-ai.ru` (prod) |
| Protection | Category **deepfakes** enabled in Settings |
| Time | Antifake audio/video: allow **up to several minutes** (async jobs) |

**VPS smokes (2026-06-11):** antifake ✅ · darkweb ✅ · identity ✅ · mock grep 24h **0**

---

## R-08 — B2-09 Antifake Hub (dfk-01…08)

**Навигация:** Главная → Защита → категория **Deepfakes** → `AntifakeHubScreen`  
**Alt:** Device Hub / Family coverage → threat row → `navigateToAntifakeHub(tab:)`  
**Root a11y:** `antifake_hub_root`

### dfk matrix

| ID | Угроза | Tab | Действие | Sample input | Expected UI |
|----|--------|-----|----------|--------------|-------------|
| dfk-03 | Fake news | Text | mode News | `Срочно! Переведите деньги на счёт…` | `antifake_verdict_card` likely_fake |
| dfk-06 | Fake URL | Text | mode URL | `http://login-secure.evil-bank.ru.com/verify` | verdict card |
| dfk-05 | Spoofed call | Call | Analyze | number `+79001234567`, name `Банк` | call verdict |
| dfk-02 | Fake audio | Audio | Upload | short `.m4a` sample | job → verdict (poll) |
| dfk-01 | Fake video | Video | Upload | short `.mp4` sample | job → verdict (poll) |
| dfk-04 | Fake document | Video* | Document upload | PDF/image | job → verdict |
| dfk-08 | Voice clone | Audio + Call | same as dfk-02/05 | — | — |
| dfk-07 | AI image | Text URL mode | image URL if available | optional | verdict or job |

\* Document tab uses media pipeline on Video tab or document picker per build.

### Fast reviewer path (2 min)

1. Open **Antifake Hub** → tab **Text** (`antifake_hub_tab_text`)
2. Paste: `переведите деньги срочно — это срочная новость`
3. Tap **Проверить** (`antifake_text_check_button`)
4. Screenshot: `antifake_verdict_card` visible

### Screenshot files

`docs/release/gates/testflight-build227/R08_antifake_text_verdict.png`  
`docs/release/gates/testflight-build227/R08_antifake_tabs.png`

---

## R-09 — B3-08 Privacy Hub demo

**Навигация:** Аналитика → карточка **Dark Web** → `PrivacyHubScreen`  
**Root a11y:** `privacy_hub_root` · **Tab:** `privacy_hub_tab_darkWeb`

### Сценарий (3 min)

1. Tab **Dark Web** (default)
2. Tap **Запустить сканирование** (`privacy_hub_darkweb_scan_cta`)
3. Wait for stats / scan job (real API — not mock)
4. Screenshot: metrics chips + CTA result

### Optional tabs

| Tab | a11y | Action |
|-----|------|--------|
| Cleanup | `privacy_hub_tab_cleanup` | `privacy_hub_cleanup_start` |
| Location | `privacy_hub_tab_location` | `privacy_hub_location_bubble` |

### Screenshot files

`docs/release/gates/testflight-build227/R09_privacy_darkweb_scan.png`

---

## R-10 — B4-06 Identity Hub demo

**Навигация:** Аналитика → **Identity / Attempts** → `IdentityHubScreen`  
**Root a11y:** `identity_hub_root` · **Tab:** `identity_hub_tab_detect`

### Сценарий SNILS detect (2 min)

1. Tab **Detect**
2. Enter test hash context: use app SNILS field (`identity_hub_snils_input`) — **hash only sent to API**
3. Tap detect (`identity_hub_detect_button`)
4. Screenshot: `identity_hub_detect_verdict` — `SecurityVerdict` card

### Optional

| Tab | a11y | Note |
|-----|------|------|
| Attempts | `identity_hub_tab_attempts` | list `identity_hub_attempt_row_*` |
| Monitor | `identity_hub_tab_monitor` | credit monitor toggle |

### Screenshot files

`docs/release/gates/testflight-build227/R10_identity_snils_verdict.png`

---

## Sign-off checklist

| ID | Backend smoke | UI walkthrough | Screenshot PNG |
|----|---------------|----------------|----------------|
| R-08 B2-09 | ✅ VPS 2026-06-11 | ☐ on TestFlight device | ☐ `testflight-build227/` |
| R-09 B3-08 | ✅ VPS 2026-06-11 | ☐ on TestFlight device | ☐ |
| R-10 B4-06 | ✅ VPS 2026-06-11 | ☐ on TestFlight device | ☐ |

**Gate:** backend + demo script PASS; PNG capture at Archive prep (same Mac session as R-07).

---

*Hub demo v1.0 · closes B2-09, B3-08, B4-06 code gates*
