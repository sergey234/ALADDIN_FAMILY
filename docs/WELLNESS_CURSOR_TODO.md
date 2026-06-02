# Wellness Platform — Cursor TODO (131 задача)

> **Единственный рабочий чеклист** для реализации. Архитектура — [WELLNESS_PLATFORM_MASTER_PLAN.md](./WELLNESS_PLATFORM_MASTER_PLAN.md) **§4.3 Knowledge Pack**.  
> **Handoff для другой ML:** [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md) · **Статус реализации:** [WELLNESS_IMPLEMENTATION_STATUS.md](./WELLNESS_IMPLEMENTATION_STATUS.md)  
> **HealthKit (Apple Developer):** [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md)  
> **Обновлено:** 2026-06-01 · **Версия плана:** v2.5  
> **Панель Cursor:** все `p0-*` … `p18-*` — статус дублируется в TodoWrite (не удалять).

**Рабочая папка (обязательно):**
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

**Правило ID:** каждая задача = `p{фаза}-{номер}` или `p18-{номер}`. Закрывать только с ссылкой на PR/файлы.

---

## Фаза 0 — подготовка (16)

- [x] **p0-01** — `docs/ADR-WELLNESS-PLATFORM.md` (4 столпа, orchestrator, ethics, § Knowledge Pack)
- [x] **p0-02** — Позиционирование: «цифровой друг», не психотерапевт (согласовать с PO)
- [x] **p0-03** — Флаги: `FEATURE_WELLNESS_ENABLED`, `WELLNESS_ORCHESTRATOR`, `WELLNESS_REFLECTIVE`, `WELLNESS_JUNG`
- [x] **p0-04** — Disclaimer ru/en: самопомощь, не диагноз, не врач
- [x] **p0-05** — Disclaimer «Понять себя» / сны: метафоры, не предсказания
- [x] **p0-06** — Чеклист App Store 1.4.1 (без мед. обещаний в metadata)
- [x] **p0-07** — Копирайт 4 кнопок Hub (RU/EN черновик)
- [x] **p0-08** — `docs/WELLNESS_CLINICAL_REVIEW.md` — PO self-review + prod flags (без внешнего психолога)
- [x] **p0-09** — Referral map РФ: 112, 8-800-2000-122, 051
- [x] **p0-10** — Escalation ladder spec L0–L3 (кратко в ADR)
- [x] **p0-11** — `docs/WELLNESS_ESCALATION_LADDER.md` — полная спецификация
- [x] **p0-12** — Синхрон с p0-08: Jung/trauma/copy review
- [x] **p0-13** — Региональные линии РФ + EN export текстов referral
- [x] **p0-14** — ADR § Knowledge Pack format + контракт `[WELLNESS v1]` prefix
- [x] **p0-15** — Scaffold `wellness_knowledge/cognitive/v1/pack.yaml` (principles, step_hints, forbidden_phrases, hero_flavor)
- [x] **p0-16** — i18n `wellness_hero_intro_{pillar}_{age}` — micro-intro перед упражнением (не LLM)

---

## Фаза 1 — MVP (29)

- [x] **p1-01** — БД `companion_store`: wellness_checkins, assessments, exercises, insights, dreams, habits, settings, alerts
- [x] **p1-02** — `wellness_journal.py` — mood + автозапись из чата
- [x] **p1-03** — `wellness_router.py` — `/api/wellness/*` + регистрация
- [x] **p1-04** — API consent + `age_policy` gating
- [x] **p1-05** — Toggle `psychological_support_agent` (родитель)
- [x] **p1-06** — `wellness_assessments.py` — PHQ-lite (5) + «не диагноз»
- [x] **p1-07** — `wellness_four_pillars.py` v1 — enum + ручной выбор
- [x] **p1-08** — Domain wellness + chip «Настроение» в intent router
- [x] **p1-09** — `wellness_triggers.py` — 3 дня грустно → PHQ-lite
- [x] **p1-10** — iOS `WellnessConsentScreen`
- [x] **p1-11** — iOS `WellnessAPIService` + AppConfig endpoints
- [x] **p1-12** — iOS `WellnessHubScreen` — 4 карточки
- [x] **p1-13** — iOS `WellnessCheckinScreen` — emoji + sleep/stress
- [x] **p1-14** — `LocalizationManager` — базовые `wellness_*` ru/en
- [x] **p1-15** — Companion chat: блок wellness (mood + pillar banner; `wellness_pillar` в chat/stream)
- [x] **p1-16** — VPS smoke `vps_smoke_wellness.py` + `verify_wellness_prod.sh` (PHQ-lite backend — p1-06)
- [x] **p1-17** — Pillar router v1 в `ai_companion_router` (не ждать Ф3)
- [x] **p1-18** — Orchestrator guard: один столп на ответ
- [x] **p1-19** — iOS Child UI: только 2 кнопки (Принять + Маленькие шаги) — age gating в Hub
- [x] **p1-20** — `wellness_escalation.py` — L0–L3
- [x] **p1-21** — `wellness_referral.py` + API referral
- [x] **p1-22** — `wellness_pillar_guard.py` — hard block mix pillars
- [x] **p1-23** — `parent_share_aggregate` DEFAULT 0 для teen
- [x] **p1-24** — iOS `WellnessTrustCenterScreen`
- [x] **p1-25** — teen_parent_visibility — teen выбирает что видит родитель
- [x] **p1-26** — `wellness_prompt_builder.py` + `load_pillar_pack(pillar, locale, version)`
- [x] **p1-27** — Patch `ai_companion_router`: `wellness_prefix` в prefixed message (§4.3.3)
- [x] **p1-28** — Knowledge Pack v1.0: cognitive + humanistic (draft; clinical review p0-08)
- [x] **p1-29** — Smoke: `forbidden_phrases` + `wellness_pillar_guard` (vps_smoke_wellness.py)

---

## Фаза 2 — 4 столпа + automation (51)

- [x] **p2-01** — `wellness_cognitive_prompt.py`
- [x] **p2-02** — `wellness_cbt_exercises.py` + `wellness_exercise_engine.py` — thought record
- [x] **p2-03** — PHQ-9, GAD-7 + iOS AssessmentFlow
- [x] **p2-04** — `wellness_behavioral_exercises.py` + behavioral pack
- [x] **p2-05** — `wellness_habit_plans.py` + `POST/GET /habits`
- [x] **p2-06** — Burnout MBI-lite (parent/senior) + iOS AssessmentFlow `.mbiLite`
- [x] **p2-07** — `wellness_humanistic_prompt.py`
- [x] **p2-08** — Grounding, box breathing, DBT STOP (humanistic pack + API)
- [x] **p2-09** — `wellness_jung_prompt.py`
- [x] **p2-10** — `wellness_jung_exercises.py` + dream journal API (gate `FEATURE_WELLNESS_JUNG`)
- [x] **p2-11** — `wellness_reflective_prompt.py` — 4 age variants
- [x] **p2-12** — `wellness_reflective_modes.py` — 5 sub-modes
- [x] **p2-13** — `wellness_reflective_guards.py` — teen/crisis blocks
- [x] **p2-14** — `wellness_four_pillars.py` v2 — `suggest_pillar()` + `/session/suggest-pillar`
- [x] **p2-15** — Правило «один столп = одна сессия» в flow
- [x] **p2-16** — `wellness_insights_extractor` → exercise complete / timeline
- [x] **p2-17** — `wellness_emotion_agent` — regex mood + optional LLM (`FEATURE_WELLNESS_MOOD_LLM`)
- [x] **p2-18** — `wellness_plan_agent` + `GET /session/plan`
- [x] **p2-19** — iOS `WellnessTimelineScreen`
- [x] **p2-20** — iOS `WellnessDreamJournalScreen`
- [x] **p2-21** — iOS `WellnessExerciseScreen`
- [x] **p2-22** — iOS `WellnessReflectiveModeScreen` (+ Hub entry if `/reflective/modes` OK)
- [x] **p2-23** — iOS `WellnessOfflineStore` (pillars, recap, check-in draft, alliance)
- [x] **p2-24** — `wellness_alerts.py` + Family dashboard (`/alerts`, `/family/dashboard`)
- [x] **p2-25** — `wellness_scheduler` — `/scheduler/reminders` (hour=19 UTC; APNs → p18-11)
- [x] **p2-26** — social_bridge + wellness_alerts merge (L2 → alert `social_bridge`)
- [x] **p2-27** — `wellness_analytics.py` + событие на check-in
- [x] **p2-28** — Тесты: child no PHQ/Jung; crisis blocks pillars (`Tests/test_wellness_gates.py`)
- [x] **p2-29** — Proactive nudge 2d idle
- [x] **p2-30** — Session recap continuity
- [x] **p2-31** — Outcome 24h push + pillar adjust
- [x] **p2-32** — Pillar fatigue 5× без улучшения + Hub banner + `/pillar/fatigue`
- [x] **p2-33** — `wellness_mood_routing.py` + `message` on `/session/suggest-pillar`
- [x] **p2-34** — `wellness_trauma_referral.py` + `/trauma/check` + companion safety block
- [x] **p2-35** — `wellness_alliance.py` + `/alliance` + Hub chip
- [x] **p2-36** — iOS Apple Health sleep → check-in (`WellnessHealthSleepReader` + HealthKit entitlement)
- [x] **p2-37** — Clinician export `GET /export/clinician` (JSON summary for share)
- [x] **p2-38** — A/B copy 4 кнопок Hub (`wellness_hub_ab.py` + `/hub/copy`)
- [x] **p2-39** — `wellness_session_recap.py` + `/session/recap`
- [x] **p2-40** — `wellness_outcomes.py` + table + API
- [x] **p2-41** — `wellness_pillar_fatigue.py`
- [x] **p2-42** — iOS `WellnessOutcomeSheet`
- [x] **p2-43** — iOS `WellnessReferralSheet`
- [x] **p2-44** — Together Mode + `WellnessTogetherModeScreen` + `/together/session`
- [x] **p2-45** — `wellness_weekly_meaning.py` + `/weekly-meaning` + iOS Hub banner
- [x] **p2-46** — API `/family/themes` + iOS Hub card (parent, `teen_user_id`)
- [x] **p2-47** — `wellness_security_fusion.py` + `/security/fusion`
- [x] **p2-48** — iOS streaks / badges + `/streaks` + Hub banner
- [x] **p2-49** — Knowledge Pack v1.0: behavioral (привычки, if-then; без «рефлекс»)
- [x] **p2-50** — Knowledge Pack v1.0: jung (метафоры; gate p0-08 + p0-11)
- [x] **p2-51** — Policy упражнений: 80% JSON/i18n, LLM только перефраз hint шага (`wellness_exercise_engine`)

---

## Фаза 3 — orchestrator + premium (20)

- [x] **p3-01** — `wellness_orchestrator.py` — full Wellness Loop (`run_wellness_loop`, `prepare_wellness_chat_turn`)
- [x] **p3-02** — Агенты cbt/habit/presence/symbol + screening + crisis (`WELLNESS_AGENTS`, `resolve_agents_for_turn`)
- [x] **p3-03** — `FEATURE_WELLNESS_ORCHESTRATOR` → full loop в chat + consent gate + stream `wellness_pillar` + `GET /session/loop` (≠ `COMPANION_USE_ORCHESTRATOR`)
- [x] **p3-04** — Crisis log + self_harm 48h monitor (`wellness_crisis_log`, `/crisis/status`)
- [x] **p3-05** — API export/DELETE wellness (`/export/personal`, `DELETE /data`)
- [x] **p3-06** — Premium paywall (timeline, full assessments, packs)
- [x] **p3-07** — Values card (ACT) optional в «Принять себя»
- [x] **p3-08** — Senior: merge elderly health journal
- [x] **p3-09** — Rive emotions 4 pillars + neuro TTS
- [x] **p3-10** — Canary 5% → 100% + runbook
- [x] **p3-11** — Postgres migration + encryption at rest
- [x] **p3-12** — Premium ONLY after ethics + 48h crisis clean (`/premium/eligibility`, dreams gate)
- [x] **p3-13** — Family prompt parent «как поговорить»
- [x] **p3-14** — Seasonal playbooks (школа/экзамены)
- [x] **p3-15** — Voice-first pillar senior
- [x] **p3-16** — `wellness_parent_playbook.py`
- [x] **p3-17** — Sleep wind-down audio 5–10 stories
- [x] **p3-18** — iOS Wellness Widget
- [x] **p3-19** — Weekly auto PDF «Мой прогресс»
- [x] **p3-20** — `wellness_pack_registry`: pack_version по pillar + session lock

---

## §18 i18n (15)

- [x] **p18-01** — `docs/WELLNESS_I18N_GLOSSARY.md`
- [x] **p18-02** — Legal keys `wellness_consent_*`, `wellness_trust_*` ru+en (LocalizationManager + Consent/Trust screens)
- [x] **p18-03** — LocalizationManager: Hub, check-in, consent, 4 столпа
- [x] **p18-04** — Backend `wellness_i18n/ru+en` PHQ-lite
- [x] **p18-05** — API `locale` / Accept-Language на wellness endpoints
- [x] **p18-06** — suggested_actions + crisis L2/L3 ru/en в chat
- [x] **p18-07** — PHQ-9, GAD-7 JSON (`wellness_i18n/assessments/`; MBI-lite → p2-06)
- [x] **p18-08** — CBT/Jung exercise steps JSON
- [x] **p18-09** — Reflective sub-modes + Outcome/Referral sheets
- [x] **p18-10** — Together, family dashboard, themes
- [x] **p18-11** — Push wellness ru/en
- [x] **p18-12** — `scripts/check_wellness_l10n.py`
- [x] **p18-13** — Widget, PDF, parent playbook strings
- [x] **p18-14** — Child/teen keys `_child` / `_teen` (`WellnessAgeL10n`, `age_variants_v1.json`, Hub/Check-in/Consent/Outcome/Assessment)
- [x] **p18-15** — Backend `wellness_error_*` ru/en

---

## Прогресс

| Фаза | Всего | Готово | % |
|------|-------|--------|---|
| 0 — подготовка | 16 | 16 | 100% |
| 1 — MVP | 29 | 29 | 100% |
| 2 — столпы + automation | 51 | 51 | 100% |
| 3 — orchestrator + premium | 20 | 20 | 100% |
| §18 i18n | 15 | 15 | 100% |
| **Σ** | **131** | **131** | **100%** |

---

## PO — дополнительные задачи (+3 → **134** в Cursor TodoWrite)

> Не входят в «131 ядро», но добавлены в этом чате как обязательные шаги перед/после релиза.  
> **~140** в переписке — округление; канонический счёт: **131 + 3 PO = 134**.

- [x] **po-clinical-signoff** — PO self-review p0-08: [WELLNESS_CLINICAL_REVIEW.md](./WELLNESS_CLINICAL_REVIEW.md) ☑ 2026-06-01; prod flags JUNG/REFLECTIVE/ORCHESTRATOR=1
- [x] **po-verify-prod** — `./scripts/verify_wellness_prod.sh https://aladdin-ai.ru` после deploy → **14/14** (2026-06-01)
- [ ] **po-healthkit** — HealthKit capability в Apple Developer Portal → [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) (код ✅, Portal — PO)

**PO прогресс:** 2/3 · **134 tracking:** 133/134 (99%)

---

**Осталось:** 0 задач ядра · **1 PO:** HealthKit capability — см. [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md)

### Приоритеты (P0 → P2 + PO)

| Приоритет | ID | Суть |
|-----------|-----|------|
| **P0** | p3-04, p3-12 | Crisis 48h + premium ethics gate |
| **P0** | p18-02 … p18-06 | Legal i18n + Accept-Language + crisis в chat |
| ~~P0~~ | ~~po-clinical-signoff~~ | ✅ PO self-review 2026-06-01; JUNG/REFLECTIVE/ORCHESTRATOR=1 в deploy |
| **P1** | p3-11, p3-05 | Postgres + export/DELETE GDPR |
| **P1** | p3-06, p3-10 | Premium paywall + canary runbook |
| **P1** | p18-12 | `scripts/check_wellness_l10n.py` |
| **P2** | p3-13, p3-16, p3-18, p3-19 | Family playbook, widget, PDF |
| **P2** | p3-15, p3-08, p3-09 | Senior voice, health journal, Rive/TTS |
| **P2** | p3-14, p3-17, p3-07, p3-20 | Seasonal, sleep audio, values card, pack_version |
| **PO** | po-healthkit | Apple Developer — WELLNESS_APPLE_HEALTHKIT_SETUP.md |
| **PO** | po-verify-prod | `./scripts/verify_wellness_prod.sh` после каждого deploy |

### Срез «что сделали» (кратко)

| Блок | Результат |
|------|-----------|
| **Ф0** | ADR, дисклеймеры, escalation/referral, clinical review, 4 Knowledge Pack scaffold |
| **Ф1 backend** | `/api/wellness/*`, consent/age, PHQ-lite, journal, triggers, escalation, pillar guard, orchestrator guard, packs cognitive+humanistic, deploy+smoke |
| **Ф1 iOS** | Consent, Hub (4 столпа / child 2), Check-in, Trust, PHQ-lite, Companion pillar banner, ~40 `wellness_*` keys |
| **Ф2 срез 1** | Exercise engine + API, behavioral/jung packs, grounding/box/STOP, `suggest_pillar`, recap/outcomes, Timeline/Exercise/Dream iOS |
| **Ф2 срез 2** | PHQ-9 + GAD-7 + MBI-lite, AssessmentFlow, Hub recap/outcome/fatigue banners, Reflective screen |

### Деплой backend (актуально)

| Дата | Результат |
|------|-----------|
| 2026-06-01 21:36 UTC | **131/131** — redeploy + `errors_v1.json` fix → smoke **ALL PASSED**, prod **14/14** |
| 2026-06-01 | `deploy_wellness_p1.sh` → VPS **OK** · pytest **110/110** · l10n **297 keys** |
| PO | `./scripts/verify_wellness_prod.sh https://aladdin-ai.ru` — ✅ 14/14 (2026-06-01) |
| PO | HealthKit — [WELLNESS_APPLE_HEALTHKIT_SETUP.md](./WELLNESS_APPLE_HEALTHKIT_SETUP.md) (Portal manual) |

### Следующий срез

**Wellness Platform закрыта (131/131).** Дальше: App Store билд, canary rollout ([WELLNESS_CANARY_RUNBOOK.md](./WELLNESS_CANARY_RUNBOOK.md)), Postgres cutover ([WELLNESS_POSTGRES_MIGRATION.md](./WELLNESS_POSTGRES_MIGRATION.md)).

### Пакет документов для передачи ML

`WELLNESS_ML_HANDOFF.md` · `WELLNESS_IMPLEMENTATION_STATUS.md` · `WELLNESS_CURSOR_TODO.md` · `WELLNESS_PLATFORM_MASTER_PLAN.md` · `WELLNESS_APPLE_HEALTHKIT_SETUP.md` · `WELLNESS_I18N_*` · `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`

---

*Gate Фазы 1 — см. [WELLNESS_ML_HANDOFF.md](./WELLNESS_ML_HANDOFF.md) §4*
