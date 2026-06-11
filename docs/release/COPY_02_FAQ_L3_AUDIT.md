# B-COPY-02 — FAQ L3-Ready Filter (post R-19)

**Дата:** 2026-06-11 · **Источник:** `UnifiedFAQCatalog` in `Screens/13_SupportScreen.swift`  
**Счёт:** **41** visible entries (было 32 + 5 hidden in loc + 4 new)

**Правило:** FAQ описывает только функции с **L3 UI + prod API** или generic education без auto-fix over-promise.

---

## Сводка R-19

| Изменение | Count |
|-----------|-------|
| Смягчено answers (RU+EN) | 12 (`faq_unsafe_wifi` **skip**) |
| Добавлено в каталог (были в loc) | 5 |
| Новые FAQ | 4 |
| kb JSON sync | 40 faq + 2 onboarding |

---

## 41 entries — полный каталог

| # | FAQ ID | L3 Hub / flow | R-19 |
|---|--------|---------------|------|
| 1 | `faq_what_protects` | Overview | soften |
| 2 | `faq_protect_children` | Family GATE-I | — |
| 3 | `faq_protect_elderly` | Elderly + SOS | soften (voice) |
| 4 | `faq_data_safe` | Privacy/E2EE | soften |
| 5 | `faq_aes256` | Premium encryption | **+catalog** soften |
| 6 | `faq_viruses_trojans` | Device malware | soften |
| 7 | `faq_ransomware` | Device malware | — |
| 8 | `faq_spyware` | Device | soften |
| 9 | `faq_phishing_sites` | Device/Identity | — |
| 10 | `faq_fake_apps` | Device mobile | — |
| 11 | `faq_malicious_apps` | Device scan | **+catalog** soften |
| 12 | `faq_malicious_links` | Antifake URL | — |
| 13 | `faq_phone_scam` | Identity | soften |
| 14 | `faq_financial_scam` | Identity | — |
| 15 | `faq_social_engineering` | Identity + Antifake | — |
| 16 | `faq_fake_banks` | Identity | — |
| 17 | `faq_phishing_emails` | Antifake | — |
| 18 | `faq_sms_scam` | SMS links | **+catalog** soften |
| 19 | `faq_inappropriate_content` | Family chd | — |
| 20 | `faq_cyberbullying` | Family chd | — |
| 21 | `faq_dangerous_contacts` | Family | — |
| 22 | `faq_gaming_addiction` | Family limits | — |
| 23 | `faq_accidental_purchases` | Family blocks | — |
| 24 | `faq_password_theft` | Privacy/cleanup | — |
| 25 | `faq_privacy_violation` | Privacy Hub | — |
| 26 | `faq_location_threats` | Location privacy | **+catalog** |
| 27 | `faq_dark_web_leaks` | Privacy Hub darkweb | **NEW** |
| 28 | `faq_deepfake` | Antifake | soften |
| 29 | `faq_fake_voices` | Antifake audio | soften |
| 30 | `faq_fake_news` | Antifake text | soften |
| 31 | `faq_dangerous_sites` | Network Protection | — |
| 32 | `faq_suspicious_downloads` | Malware | — |
| 33 | `faq_unsafe_wifi` | Network Protection | **SKIP** (PO) |
| 34 | `faq_how_network_protection_works` | Network Protection | **+catalog** |
| 35 | `faq_mitm_attacks` | Network Protection | soften |
| 36 | `faq_crash_detection` | B7 Emergency | **NEW** |
| 37 | `faq_roadside_assistance` | B7 Emergency | **NEW** |
| 38 | `faq_emergency_sos` | Elderly SOS | **NEW** |
| 39 | `faq_parental_control_setup` | Family onboarding | — |
| 40 | `faq_cancel_subscription` | Tariffs L1 | — |
| 41 | `faq_ai_how_works` | AI assistant | disclaimer OK |
| 42 | `faq_parental_bypass` | PC-BYPASS 127–129 | **CP3-12** |
| 43 | `faq_geofencing` | PC-GEO | **CP3-12** |
| 44 | `faq_wellness_support` | wellness disclaimer | **CP3-12** |

---

## Gap table — не в UI (фаза 2 / CP3-12)

| FAQ / topic | Причина defer | Batch |
|-------------|---------------|-------|
| `faq_gamification_rewards` | PC-REW | CP3-12 backlog |
| `faq_critical_infrastructure` | нет L3 UI | backlog |
| `faq_domestic_violence` | нет L3 UI | backlog |
| `faq_emotional_problems` | wellness scope | CP3-12 |
| `faq_anonymity` | в loc, не в каталог | optional add |

**138 backend threats** — не дублировать 1:1 в FAQ; обзор через `faq_what_protects` + тариф.

---

## PASS B-COPY-02 + R-19

- [x] 44 FAQ entries classified + in `UnifiedFAQCatalog` (CP3-12 +3)
- [x] Answer soften RU+EN (12 keys, skip unsafe_wifi)
- [x] kb JSON sync (`scripts/sync_cp3_kb_from_loc.py`)
- [x] grep stale phrases — 0 in `LocalizationManager`

*Audit v2.1 · R-19 + CP3-12 (bypass, geofencing, wellness) done · build 227*
