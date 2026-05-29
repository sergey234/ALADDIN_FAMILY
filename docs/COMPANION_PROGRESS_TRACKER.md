# Companion — полный трекер задач (открой в Cursor)

**Обновлено:** 2026-05-29 (iOS build **214** на TF · CODE Sprints **0–5 ✅ 49/49** локально · pytest companion **~80** · push Sprint 4–5 ⏳)  
**Handoff для следующей ML:** [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) · **План до 100%:** [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md)  
**Handoff AI:** [COMPANION_HANDOFF_AI_NEXT.md](./COMPANION_HANDOFF_AI_NEXT.md) · **ML №4:** [HANDOFF_29](./COMPANION_ML_HANDOFF_2026-05-29.md) · **Без Rive:** [TASKS_NO_RIVE](./COMPANION_TASKS_WITHOUT_RIVE.md) · **Код-спринты v2:** [CODE_PLAN](./COMPANION_CODE_PLAN_NO_RIVE.md) · [CODE_TODO](./COMPANION_CODE_TODO_TRACKER.md)  
**Rive connect:** [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md) · **Art canon:** [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) · **UX:** [UNIFIED_HOME](./COMPANION_UNIFIED_HOME_UX.md)  
**Прогресс спринта:** **90 / 102 (88%)** · **осталось 12** · **CODE v2: 49/49 ✅** · **HERO-3: 24/26** · **07 + 11 ⏳** · **02b-PO-lock ✅** · **unicorn.riv >25KB ✅**  
**Вне 102 (iOS polish):** **11/12 ✅** · **1 в работе** (STT device QA → **214**) · **POL-12 ✅**  
**Синхронизация цифр:** только этот файл — остальные `COMPANION_*.md` ссылаются сюда.  
**ADR 2D vs 3D:** [COMPANION_2D_VS_3D_ADR.md](./COMPANION_2D_VS_3D_ADR.md) ✅ · **Export 07:** [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)  
**Матрица HERO-3:** [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md)  
**Figma Companion:** https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM — **`00_Spec` ✅** · **`01` unicorn v2 ✅** · **`03` genie OB_03×12 + OB_02–06 row ✅** [аудит](./COMPANION_FIGMA_STATUS.md)  
**Цель:** 2D Rive · 56% full-body rect · субтитр · 12 эмоций + lip-sync  
**Следующий шаг:** **QA TestFlight 214** · **Rive 07** → **11c** → GATE-EMO · push Sprint 4+5 ⏳  
**iOS:** build **214** · pytest companion **78** · **08b PASS** · capabilities decode + coalescing ✅

Отмечай `[x]` при закрытии. Источник деталей: [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md)

---

## Сводка по блокам

| Блок | Готово | Всего |
|------|--------|-------|
| P0 | 19 | 19 |
| P1 | 11 | 11 |
| CX | 6 | 6 |
| OPS | 4 | 4 |
| HERO-3 | 24 | 26 |
| P1+ | 11 | 12 |
| P2 | 16 | 17 |
| P3 | 6 | 6 |
| Adult | 3 | 3 |
| **Итого** | **90** | **102** |

> **12 открытых** = не в «90»: HERO-3-07, HERO-3-11b/11c, P1-12 Postgres (MVP Redis+SQLite ✅ код), P2-09, P2-17, UX-14b, P1-19 Rive screenshots, GATE-* (см. [PLAN_100](./COMPANION_PLAN_TO_100_PERCENT.md)).

---

## P0 — MVP (19/19) ✅

- [x] **P0-01** — JWT: app_id, age_band, parent_consent
- [x] **P0-02** — policy_engine child/teen/parent
- [x] **P0-03** — База trust, threads, usage
- [x] **P0-04** — WebSocket voice realtime
- [x] **P0-05** — Ephemeral voice token
- [x] **P0-06** — Companion API + store
- [x] **P0-07** — iOS модели + API
- [x] **P0-08** — iOS Hub + Conversation
- [x] **P0-09** — CompanionVoiceSession
- [x] **P0-10** — эмоции + lip-sync lite
- [x] **P0-11** — вход только Kids/Игры
- [x] **P0-12** — PII gate, no mock prod
- [x] **P0-13** — usage meters
- [x] **P0-14** — smoke tests
- [x] **P0-15** — деплой VPS
- [x] **P0-16** — PlatformModule registry
- [x] **P0-17** — GET /capabilities
- [x] **P0-18** — CompanionCapabilitiesService
- [x] **P0-19** — env flags + deploy doc

---

## P1 — спринт 2 (11/11) ✅

- [x] **P1-01** — threads (история)
- [x] **P1-02** — UI согласия родителя
- [x] **P1-03** — память вкл/выкл, экспорт
- [x] **P1-04** — инструкции + personality preset
- [x] **P1-05** — feedback лайк/дизлайк
- [x] **P1-06** — resume stream
- [x] **P1-07** — косметика iOS
- [x] **P1-08** — Rive инфра (финал → HERO-3-07)
- [x] **P1-09** — legal тексты
- [x] **P1-10** — аналитика N1–N6 (`CompanionAnalytics` + `POST /analytics`, без PII)
- [x] **P1-11** — banner 20% лимита
- [x] **P1-13c-text** — TTS на текстовый stream + toggle «Моё» (build 210)

---

## CX — компаньон «жизнь» (6/6) ✅

- [x] **P1-25** — этика L1–L3
- [x] **P1-26** — persona life-first
- [x] **P1-27** — intent router domains+mood
- [x] **P1-28** — возрастные персоны
- [x] **P1-29** — режим эксперта безопасности
- [x] **P1-30** — полный спектр эмоций (BE+iOS enum)

---

## OPS (4/4) ✅

- [x] **OPS-01** — деплой на aladdin-ai.ru
- [x] **OPS-02** — verify расширенный (+ HERO-3-10 age_policy)
- [x] **OPS-04** — алерт LLM cost ✅ cron на VPS `:15` + `/var/log/aladdin-backend/companion_llm_cost.log`
- [x] **OPS-05** — DoD после деплоя

---

## HERO-3 — 3 героя Figma→Rive (24/26) 🟡

### Ядро (01–19)

- [x] **HERO-3-01** — ADR план §1–11 + §2.1–2.3
- [x] **HERO-3-02** — Spec в Figma `00_Spec` (Motion/Mimic/ADR/sign-off) ✅
- [x] **HERO-3-02b** — Figma `01`–`03` — **36/36** frames 360×480 ✅ 2026-05-27 ([FIGMA_STATUS](./COMPANION_FIGMA_STATUS.md))
  - [x] **02b-v1.1 unicorn** — v2 cinematic во всех 12; CONCEPT_v1/A–E (круги) удалены
  - [x] **02b-v1.1 genie** — OB_03 headfix в 12× `genie/emotion/*`; ряд OB_02–06 headfix для PO
  - [x] **02b-v1.1 aladdin** — OB_01 master (без изменений в art-сессии)
  - [x] PNG: `docs/assets/onboarding_OB0{2..6}_APP_360x480_FILL_headfix_v1.png`, `onboarding_OB03_APP_*`
  - [x] **02b-PO-lock** — genie master = **OB_03 headfix** в [CANON](./COMPANION_HERO_ART_CANON.md) ✅ 2026-05-28 → **07**
- [x] **HERO-3-03** — BE genie + age_policy
- [x] **HERO-3-04** — Pydantic + cosmetics genie
- [x] **HERO-3-05** — companion_persona 3 ветки
- [x] **HERO-3-06** — iOS Hub 3 карточки **всем** age_band (PO 29.05: 🦄🧑🧞 всем; PG + consent)
- [ ] **HERO-3-07** — Rive export `.riv` ×3 — 🟡 placeholder в бандле · production art ⏳ → [brief](./COMPANION_RIVE_ANIMATOR_BRIEF.md) · [supplement](./COMPANION_RIVE_ANIMATOR_PLAN_SUPPLEMENT.md) · [6 hats](./COMPANION_RIVE_ANIMATOR_6_HATS_AUDIT.md)
- [x] **HERO-3-08** — Rive на сцене ([unblock](./COMPANION_RIVE_UNBLOCK.md))
  - [x] **08a** — SPM 6.20.5 + Xcode build + `.riv` в бандле (`verify_companion_rive_ios_bundle.sh`)
  - [x] **08b** — UI: `CompanionHome` → `Главное`, Rive на **реальном iPhone** PASS 2026-05-27 (placeholder art)
- [x] **HERO-3-09** — Character Bible §4 в [ALADDIN_Character_Bible.md](./ALADDIN_Character_Bible.md)
- [x] **HERO-3-10** — deploy + verify prod ✅ 2026-05-27 (`deploy_companion_p0.sh` + `verify_companion_p0_prod.sh` PASS)
- [ ] **HERO-3-11** — QA D10 + SPEECH/MOTION/MIMIC-Q ([чеклист](./COMPANION_HERO3_11_QA_CHECKLIST.md))
  - [x] **11a** — pytest companion + SPEECH-Q5 + riv gate (**49** tests, 2026-05-29)
  - [ ] **11b** — device: MOTION-Q1–5, MIMIC-Q1–6, D10, SPEECH-Q6 STT/TTS (iPhone, build **213+**; STT-fix → **214+**)
  - [ ] **11c** — повтор MIMIC-Q1 после HERO-3-07 production `.riv`
- [x] **HERO-3-12** — preset witty
- [x] **HERO-3-13** — default preset + humor_density
- [x] **HERO-3-14** — intent humor по герою
- [x] **HERO-3-15** — iOS witty + TTS
- [x] **HERO-3-16** — test_companion_persona_speech.py
- [x] **HERO-3-17** — Motion + Mimic Spec Figma sign-off ([чеклист](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md)) — PO 2026-05-26
- [x] **HERO-3-18** — iOS таймлайн + debounce 400ms
- [x] **HERO-3-19** — lip-sync mouth_open MVP

### Документы, QA, iOS-полировка (20–26) — 6 шляп 26.05

- [x] **HERO-3-20** — ADR: 13 state (9 контент + 4 фазы) vs CX.4
- [x] **HERO-3-21** — матрица spec/BE/iOS/.riv/QA
- [x] **HERO-3-22** — `companion_riv_size_gate.py` + CI [companion-gate.yml](../.github/workflows/companion-gate.yml)
- [x] **HERO-3-23** — iOS: stream emotion во время `thinking`
- [x] **HERO-3-24** — iOS: sad/comfort без playful overlay
- [x] **HERO-3-25** — pytest sync iOS ↔ `companion_emotions.py`
- [x] **HERO-3-26** — unit-тест debouncer 400 ms

**Порядок:** ~~`17` → `02`~~ ✅ → **`07`+`22`** → `08` → `10` → `11` (iOS **18/19/23–26** ✅)  
**После каждого .riv:** MIMIC-Q1 (в **11**)

---

## P1+ Production (11/12)

- [~] **P1-12** — Postgres + Redis — **MVP ✅** (`companion_stream_redis.py`, SQLite store; `COMPANION_STORE_BACKEND=postgres` → warning only). Полная миграция Postgres ⏳ отдельный проект.
- [x] **P1-13** — голос production (P1-13d WS + STT→chat→TTS; genie в voice WS)
- [x] **P1-14** — XCUITest: Kids → Друзья → Companion → message (`CompanionSmokeUITests.swift`)
- [x] **P1-15** — prod verify полный (= OPS-02 + VPS deploy Sprint 3 BE)
- [x] **P1-16** — ADR hot path (`docs/adr/ADR-P1-16-companion-hot-path.md`)
- [x] **P1-17** — accessibility (VoiceOver, Dynamic Type, stream/feedback/cosmetics)
- [x] **P1-18** — rate limit 429 + `CompanionErrorMapper` + l10n
- [x] **P1-19** — App Store pack doc ✅ · **3 скриншота Hub с Rive ⏳** ([pack](./COMPANION_APP_STORE_PACK_P1-19.md))
- [x] **P1-20** — RU/EN Companion (полная l10n Sprint 2)
- [x] **P1-21** — offline cache (`CompanionOfflineStore`)
- [x] **P1-22** — post-LLM moderation (`companion_post_llm_moderation.py`)
- [x] **P1-23** — эмоции Grok-level (BE+iOS; **GATE-EMO визуал ⏳** после 07)

---

## P2 — фаза B (16/17)

- [x] **P2-01** — web search + citations
- [x] **P2-02** — orchestrator + `COMPANION_USE_ORCHESTRATOR`
- [x] **P2-03** — Fast/Reasoning/Think (`chat_mode` + iOS)
- [x] **P2-04** — фото и PDF (attachments MVP)
- [x] **P2-05** — trust decay/streak
- [x] **P2-06** — family context в промпте
- [x] **P2-07** — Responses API tools manifest
- [x] **P2-08** — COGS dashboard `GET /cogs`
- [ ] **P2-09** — Figma↔Rive (→ HERO-3)
- [x] **P2-11** — mood-aware MVP
- [x] **P2-12** — life domains API + chips
- [x] **P2-13** — social bridge
- [x] **P2-14** — вход Senior 60+ (Main)
- [x] **P2-15** — teen loneliness playbook
- [x] **P2-16** — trust за эмпатию
- [ ] **P2-17** — A/B humor_density (genie+teen, после HERO-3)

---

## P3 (6/6)

- [x] **P3-01** — генерация картинок (stub + flag)
- [x] **P3-02** — генерация видео (stub)
- [x] **P3-03** — workspaces API
- [x] **P3-04** — длинный контекст (recap hint)
- [x] **P3-05** — Android checklist doc
- [x] **P3-06** — Adult scaffold doc

---

## Adult backend (3/3)

- [x] **A-01** — OpenAPI aladdin_adult
- [x] **A-02** — policy tests NSFW
- [x] **A-03** — repo stub Adult app

---

## GATE — контрольные ворота

- [ ] **GATE-P0** — smoke ✅ · prod verify ✅ · **Мир героев** ✅ · **08b** ✅ · **11b** ⏳
- [ ] **GATE-OPS** — health + verify prod
- [ ] **GATE-CX** — 5 фраз CX (без VPN spam)
- [ ] **GATE-P1** — cosmetics, legal
- [x] **GATE-HERO-3-IOS-α** — debounce + timeline + TTS text + **23/24/26** ✅ (без production .riv)
- [ ] **GATE-EMO** — 13 state + Rive + D10 лица
- [ ] **GATE-EMO-EMPATHY** — 5 мин × child / teen / senior (device)
- [ ] **GATE-PROD** — P1+ 4 слоя
- [ ] **GATE-P2** — senior, teen, search
- [ ] **GATE-P3** — после PROD
- [ ] **GATE-DIALOG-REGRESS** — R1–R19 (14/19 auto ✅)
- [ ] **GATE-DIALOG** — D01–D10 TestFlight

---

## Отменено (не в спринте)

X-01 · X-02 · X-03 · X-04 · X-05 · X-06 · X-07  
**Viseme/phoneme** — не HERO-3 (только P2+, план §2.2)

---

## Сессия 2026-05-28 — Node + RiveMCP (зафиксировано)

- [x] Homebrew **Node v26** · **rivemcp 1.3.6** (`/usr/local/bin/`)
- [x] Cursor MCP: `~/.cursor/mcp.json` + `ALADDIN_iOS/.cursor/mcp.json`
- [x] RiveMCP connected (`user-rivemcp-*` tools)
- [x] Черновик: `Resources/Companion/unicorn_mcp_draft.{rev,riv}` (2/3 free exports used)
- [x] `unicorn.riv` пересобран (Hero360 + HeroSM + 13 triggers + `mouth_open`) → **158,578 bytes**
- [x] Gate после `unicorn.riv`: `companion_riv_size_gate.py` + `verify_companion_rive_ios_bundle.sh` PASS
- [x] RiveMCP free exports исчерпаны (**3/3**): для `aladdin.riv` / `genie.riv` — manual Rive Editor export
- [x] Доки: [RIVE_CONNECT](./COMPANION_RIVE_CONNECT_NODE_MCP.md) · [5_STEPS](./COMPANION_RIVE_EDITOR_5_STEPS.md) · [ML_HANDOFF_28](./COMPANION_ML_HANDOFF_2026-05-28.md)
- [ ] **07** production `.riv` ×3 — ⏳ осталось `aladdin.riv` + `genie.riv`

### Блокер 07 (передать следующей ML-системе)

- [ ] `aladdin.riv` manual steps:
  - Import PNG: `docs/assets/aladdin_master_OB01_crop_360x480.png`
  - Разместить на Hero360 (360×480 full cover) → File Export в `Resources/Companion/aladdin.riv`
- [ ] `genie.riv` manual steps:
  - Import PNG: `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png`
  - Разместить на Hero360 (360×480 full cover) → File Export в `Resources/Companion/genie.riv`
- [ ] После каждого export: прогнать gate-скрипты и device smoke

## Сессия 2026-05-27 — Figma art (зафиксировано)

> Дублирует подпункты **HERO-3-02b** выше; отдельных новых ID в списке 102 нет.

- [x] **01_Unicorn:** все `unicorn/emotion/*` = **v2 cinematic**; удалены CONCEPT_v1 / A–E (круги)
- [x] **03_Genie:** ряд **OB_02–06** headfix 360×480 (`PO_MASTER_OB02_06_360x480` · `101:2`)
- [x] **03_Genie:** сетка **12× OB_03** headfix (`GRID_12_genie_emotions_OB03` · `122:2`) — восстановлено после ошибочной чистки
- [x] OB_02/04/05/06 headfix по образцу OB_03 (FILL 360×480, crop headfix v1)
- [x] PNG в `docs/assets/` (см. **02b** подпункты)
- [x] Handoff: [COMPANION_HANDOFF_AI_NEXT.md](./COMPANION_HANDOFF_AI_NEXT.md)
- [x] **PO:** OB_03 = genie master в каноне → **HERO-3-07** Rive ✅ 2026-05-28

## Сессия 2026-05-26…27 (зафиксировано)

- [x] Rive SPM кэш: `scripts/reset_rive_spm_cache.sh`  
- [x] iOS 15 fixes: `onChange`, `NavigationView`, `CompanionAPIService`, `Color`/Rive split  
- [x] `CompanionChatResponse.cosmeticUnlocked`, `ALADDINNavigationBar` companion cases  
- [x] **Проект ALADDIN собирается в Xcode**
- [x] Unified **Мир героев** + build **209** push
- [x] CI fix `Consumer.companion` · build **210**: TTS на текст, Hub Rive-превью
- [x] **08b PASS** на реальном device (placeholder Rive)
- [x] **11a** pytest 46 · **P1-13c-text** TTS
- [x] Figma аудит: только `00_Spec` — [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md)

## Сессия 2026-05-28…29 — iOS стабильность + UX (вне счётчика 102)

> Коммиты: `e5e37cb7` (build 112→стабилизация) · `62c4a35f` (build **213**, capabilities coalescing).  
> Локально (ещё не в TestFlight): STT device + карточка Child Rewards — целевой **build 214**.

| ID | Задача | Статус |
|----|--------|--------|
| **iOS-POL-01** | Decode `CompanionFeatureUI` / capabilities без `typeMismatch` | ✅ + unit test |
| **iOS-POL-02** | Один `companion_open` (убран дубль с `CompanionHomeScreen`) | ✅ |
| **iOS-POL-03** | Кэш + coalescing `profile` / `state` / `legal` в `CompanionAPIService` | ✅ |
| **iOS-POL-04** | TTL 30s + in-flight coalescing `GET /capabilities` | ✅ `62c4a35f` |
| **iOS-POL-05** | Кэш PNG masters для Hub thumbnails (`CompanionHeroRiveHost`) | ✅ |
| **iOS-POL-06** | `SpeechManager`: debounce/cooldown, shared assistant + companion | ✅ |
| **iOS-POL-07** | **P1-13e** — гибридный микрофон (tap + hold + swipe-cancel) | ✅ |
| **iOS-POL-08** | **P1-13f** — Settings «AI-помощник и 3 героя» | ✅ |
| **iOS-POL-09** | Клавиатура + consent banner в `CompanionConversationScreen` | ✅ |
| **iOS-POL-10** | TestFlight build **213** push | ✅ |
| **iOS-POL-11** | STT на реальном iPhone (finalize delay, Retry, min hold 1s) | ✅ код build **214** · device QA ⏳ |
| **iOS-POL-12** | Child Rewards: featured «Мир героев» ✨ над балансом | ✅ build **214** |

**UX (Фаза 1–3 код):** [UX-01…05](./COMPANION_UNIFIED_HOME_UX.md) ✅ · **UX-06…08** ✅ (Друзья, pet, legacy) · **UX-09** GATE R6/R8 ⏳ QA

## Блок G — UX «Мир героев» (CODE Sprint 1, 17 задач) ✅ код / ⏳ TF215

| № | Задача | Код | 100%? |
|---|--------|-----|-------|
| 74–76 | Три героя BE/iOS/голос | блок E | ✅ |
| 77–78 | Карточка Rewards + текст 🦄🧑🧞 | `ChildRewardsScreen.swift` | ✅ код · проверить **build 215** |
| 79–82 | «Друзья», питомец, legacy→Home | `08_ChildInterfaceScreen`, pet, nav | ✅ |
| 83–85 | Mic coach, hold детей, busy assistant | `CompanionConversationScreen` | ✅ |
| 86 | Чистый overlay ребёнка | `heroStatusOverlay` | ✅ |
| 87–88 | RU/EN, VoiceOver | `LocalizationManager` | ✅ |

**До 100% блока G:** commit → TF **215** → device: Rewards card видна родителю и ребёнку, все входы → `companionHome`.

---

## Сессия 2026-05-29 — CODE Sprints 0–5 (v2, зафиксировано)

> **CODE_TODO:** Sprints **0–5 = 49/49** ✅ в рабочей копии · **git push** ⏳ (remote на `771340a3` = только 0–3).

| Блок | ID | Статус |
|------|-----|--------|
| Sprint 1 UX+герои (блок G) | UX-HERO-01…03, UX-06…14, P1-20a, P1-17a | ✅ код |
| Sprint 2 | P1-13d, P1-20, P1-17, P1-21 | ✅ код · push 214 |
| Sprint 3 | P1-14, P1-18, P1-22, P1-16, P1-19 (doc) | ✅ код · push 214 |
| Sprint 4 | P1-12 MVP, P2-02, P2-12/13/15/16 | ✅ код · **VPS ⏳** |
| Sprint 5 | P2-01…08, P2-14, P3-01…06, A-01…03 | ✅ код · **VPS ⏳** |
| Stream-fix | `chat_mode`, `attachments`, `workspace_id` в SSE | ✅ локально |
| Отложено Rive | UX-14b, HERO-3-07, P1-19 screenshots, P2-09, P2-17 | ⏳ не в плане 100% |
| Следующий шаг | commit → deploy → TF **215** | [PLAN_100](./COMPANION_PLAN_TO_100_PERCENT.md) этап 1 |

## В конце (по решению команды)

- [x] **Xcode compile** (2026-05-27)  
- [x] **08b** device Rive  
- [x] **02b** Figma 36 frames + art ✅ 2026-05-27  
- [ ] **07** Rive `.riv` ×3 (aladdin + genie production export)  
- [ ] **11b / 11c** device QA (STT после **214**)  
- [ ] **TestFlight** build **214** — push ⏳ → device QA (11b SPEECH, GATE-DIALOG)

---

*Файл для ежедневного трекинга. Обновляй галочки и [матрицу](./COMPANION_HERO3_READINESS_MATRIX.md) при закрытии задач.*
