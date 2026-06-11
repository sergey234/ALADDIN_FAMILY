# COPY-POST-L3 — исполнительный TODO (RU/EN sync)

**SSOT тексты:** `COPY_POST_L3_FULL_AUDIT.md`  
**Batch:** `R-19` · **Порядок:** после SEC-P2 ✅ → **до** B-QA-02 Archive  
**Оценка:** ~87 правок ключей · 14 файловых зон  
**Dashboard:** `COPY_POST_L3_PROGRESS.md` · **Статус:** ✅ **R-19 100% PASS**

---

## CP3-00 — Подготовка

- [x] `CP3-00a` Прочитать `COPY_POST_L3_FULL_AUDIT.md` §согласованные решения
- [x] `CP3-00b` Снять onboarding freeze: `security-l3-report.json` → `onboarding_frozen: false`
- [x] `CP3-00c` Ветка/commit только по запросу PO

---

## CP3-01 — Онбординг (6 keys × 2 lang × 3 файла)

| ID | Файл | Keys |
|----|------|------|
| `CP3-01a` | `Core/Localization/LocalizationManager.swift` | `onboarding_page1_desc`, `page4_desc`, `page6_desc` RU+EN |
| `CP3-01b` | `onboarding_page2_desc` EN only | добавить military-grade (синхрон с RU) |
| `CP3-01c` | `Screens/14_OnboardingScreen.swift` | fallbackTexts + fallbackTextsEnglish (те же 4 desc) |
| `CP3-01d` | `scripts/verify_onboarding_sync_01_03.py` | EXPECTED OB_01,04,06 RU |
| `CP3-01e` | `LocalizedVersions/English/14_OnboardingScreen_Localized.swift` | EN desc |
| `CP3-01f` | `docs/kb/kb_v1/documents/onboarding_page_onboarding_ru.json` | OB_01,04,06 |
| `CP3-01g` | `docs/kb/kb_v1/documents/onboarding_page_onboarding_en.json` | EN mirror |

**Не трогать:** OB_02 RU «Военные технологии шифрования».

---

## CP3-02 — Тарифы и каталог (7 keys × 2 lang)

| ID | Keys |
|----|------|
| `CP3-02a` | `tariffs_ai_protection`, `tariffs_ai_protection_desc` |
| `CP3-02b` | `protection_catalog_title`, `protection_catalog_subtitle` |
| `CP3-02c` | `protection_scenarios_subtitle`, `tariff_protection_title` |
| `CP3-02d` | `tariffs_recommendation_premium_text` |

Файл: `LocalizationManager.swift` только.

---

## CP3-03 — FAQ смягчение (12 answer keys × 2 lang)

| ID | answerKey |
|----|-----------|
| `CP3-03a` | `faq_what_protects_answer` |
| `CP3-03b` | `faq_data_safe_answer` |
| `CP3-03c` | `faq_viruses_trojans_answer`, `faq_spyware_answer` |
| `CP3-03d` | `faq_phone_scam_answer` |
| `CP3-03e` | `faq_deepfake_answer`, `faq_fake_voices_answer`, `faq_fake_news_answer` |
| `CP3-03f` | `faq_mitm_attacks_answer` |
| `CP3-03g` | `faq_aes256_answer`, `faq_anonymity_answer` |
| `CP3-03h` | `faq_protect_elderly_answer` (убрать голос) |
| `CP3-03i` | kb JSON sync для каждого изменённого faq_* |

**SKIP:** `faq_unsafe_wifi_answer` — без изменений (PO).

---

## CP3-04 — FAQ включить в каталог (5 entries)

| ID | faq id | + question/answer EN |
|----|--------|----------------------|
| `CP3-04a` | `faq_aes256` | смягчённый answer из CP3-03g |
| `CP3-04b` | `faq_how_network_protection_works` | существующий loc |
| `CP3-04c` | `faq_malicious_apps` | смягчить «перед установкой» |
| `CP3-04d` | `faq_sms_scam` | смягчить «блокирует» |
| `CP3-04e` | `faq_location_threats` | существующий loc |

Файлы: `13_SupportScreen.swift` (`UnifiedFAQCatalog`), `LocalizationManager.swift`, новые `docs/kb/kb_v1/documents/faq_*_{ru,en}.json` где нет.

---

## CP3-05 — FAQ новые (4 entries × 2 lang)

| ID | faq id |
|----|--------|
| `CP3-05a` | `faq_crash_detection` + `_answer` |
| `CP3-05b` | `faq_roadside_assistance` + `_answer` |
| `CP3-05c` | `faq_emergency_sos` + `_answer` |
| `CP3-05d` | `faq_dark_web_leaks` + `_answer` |

Файлы: `LocalizationManager.swift`, `13_SupportScreen.swift`, kb JSON × 8 файлов.

---

## CP3-06 — Privacy Policy (app)

| ID | Keys / раздел |
|----|---------------|
| `CP3-06a` | `privacy_policy_section_responsibility_content_2` RU+EN |
| `CP3-06b` | `privacy_policy_network_protection_encryption_content_3`, `_content_4` |
| `CP3-06c` | `privacy_policy_vpn_encryption_content_3`, `_content_4` (дубль vpn tab) |
| `CP3-06d` | `privacy_policy_*_servers_subtitle` + `servers_content_1…5` |
| `CP3-06e` | Новые keys: `privacy_policy_section_emergency_*` (crash/roadside/SOS) RU+EN |
| `CP3-06f` | Новые keys: `privacy_policy_section_antifake_async_*` RU+EN |
| `CP3-06g` | `privacy_policy_section_principles_content_2` — уточнить cloud |
| `CP3-06h` | `Screens/18_PrivacyPolicyScreen.swift` — enum cases если новые секции |
| `CP3-06i` | `privacy_policy_version` — единая дата |

**Оставить:** военное шифрование subtitles + AES military level content_1.

---

## CP3-07 — Terms of Service

| ID | Keys |
|----|------|
| `CP3-07a` | `terms_section_description_content_2` RU+EN |
| `CP3-07b` | Новые `terms_section_antifake_*` (title, subtitle, content_1…3) |
| `CP3-07c` | Новые `terms_section_emergency_*` |
| `CP3-07d` | `Screens/19_TermsOfServiceScreen.swift` — TermsSection enum |

**Оставить:** `terms_section_network_protection_content_5`, `liability_content_2`.

---

## CP3-08 — Landing + markdown legal

| ID | Файл |
|----|------|
| `CP3-08a` | `landing/privacy.html` — §13, §16, §17, emergency § |
| `CP3-08b` | `landing/terms.html` |
| `CP3-08c` | `docs/PRIVACY_POLICY_FULL_152FZ.md` |
| `CP3-08d` | `landing/help-faq.html` — выборочно или defer |

---

## CP3-09 — Документация и аудиты

| ID | Файл |
|----|------|
| `CP3-09a` | `docs/release/COPY_01_ONBOARDING_L3_AUDIT.md` — OB_02 keep, OB правки done |
| `CP3-09b` | `docs/release/COPY_02_FAQ_L3_AUDIT.md` — 41 FAQ, gap table |
| `CP3-09c` | `docs/release/COPY_04_APP_STORE_REVIEW_NOTES.md` — async antifake note |
| `CP3-09d` | `.cursor/IMPLEMENTATION_BATCHES_TODO.md` — R-19 ✅ |
| `CP3-09e` | `docs/release/gates/security-l3-report.json` — COPY-POST-L3 block |

---

## CP3-10 — ML package mirror

| ID | Файл |
|----|------|
| `CP3-10a` | `ML_SYSTEM_PACKAGE/LocalizationManager.swift` |
| `CP3-10b` | `ML_SYSTEM_PACKAGE/LocalizedVersions/English/14_OnboardingScreen_Localized.swift` |

---

## CP3-11 — Verification gate

| ID | Команда / критерий |
|----|-------------------|
| `CP3-11a` | `python3 scripts/verify_onboarding_sync_01_03.py` → PASS |
| `CP3-11b` | `rg -i "предсказывает|более 100 видов|НЕВОЗМОЖНО взломать|полная анонимность|никто не узнает" --glob '*.swift' LocalizationManager` → 0 user-facing |
| `CP3-11c` | FAQ count в `UnifiedFAQCatalog` = 41 |
| `CP3-11d` | RU/EN key parity spot-check (все новые keys имеют EN) |
| `CP3-11e` | xcodebuild compile (не Archive) |

---

## CP3-12 — Фаза 2 (не блокер R-19)

- [x] `faq_parental_bypass` — PC-BYPASS 127–129
- [x] `faq_geofencing` — PC-GEO
- [x] `faq_wellness_support` — wellness disclaimer
- [ ] `faq_gamification_rewards` — PC-REW
- [ ] `protection_benefit_fraud` — «Помогает предотвратить»

---

## Сводка по файлам

| # | Путь | Задач |
|---|------|-------|
| 1 | `Core/Localization/LocalizationManager.swift` | ~60 keys |
| 2 | `Screens/14_OnboardingScreen.swift` | 8 strings |
| 3 | `Screens/13_SupportScreen.swift` | +9 catalog entries |
| 4 | `Screens/18_PrivacyPolicyScreen.swift` | sections |
| 5 | `Screens/19_TermsOfServiceScreen.swift` | sections |
| 6 | `scripts/verify_onboarding_sync_01_03.py` | 3 expected |
| 7 | `landing/privacy.html` | major |
| 8 | `landing/terms.html` | minor |
| 9 | `docs/PRIVACY_POLICY_FULL_152FZ.md` | major |
| 10 | `docs/kb/kb_v1/documents/*` | ~40 json |
| 11 | `LocalizedVersions/English/14_OnboardingScreen_Localized.swift` | 4 |
| 12 | `ML_SYSTEM_PACKAGE/*` | mirror |
| 13 | `docs/release/COPY_0*.md` | 3 audits |
| 14 | trackers | 2 |

---

*TODO v1.0 · исполнять строго CP3-01 → CP3-11*
