# Companion — полный трекер задач (открой в Cursor)

**Обновлено:** 2026-05-27  
**Handoff ML:** [COMPANION_ML_HANDOFF_2026-05-27.md](./COMPANION_ML_HANDOFF_2026-05-27.md) ← **главный файл передачи**  
**Прогресс спринта:** **66 / 102 (65%)** · **HERO-3:** **25 / 26**  
**Синхронизация цифр:** только этот файл — остальные `COMPANION_*.md` ссылаются сюда.  
**ADR 2D vs 3D:** [COMPANION_2D_VS_3D_ADR.md](./COMPANION_2D_VS_3D_ADR.md) ✅ · **Export 07:** [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)  
**Матрица HERO-3:** [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md)  
**Figma Companion:** https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM (`00_Spec` + `01`–`03` grid ✅)  
**Цель:** 2D Rive · 56% full-body rect · субтитр · 12 эмоций + lip-sync  
**Следующий шаг:** **07** Figma→`.riv` (дизайн) · **11b** device QA · **11c** после 07 · [100% runbook](./COMPANION_100_PERCENT_PARALLEL.md)  
**iOS:** ✅ build **210** · TTS на текст · Hub Rive-превью · **08b PASS** (device)

Отмечай `[x]` при закрытии. Источник деталей: [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md)

---

## Сводка по блокам

| Блок | Готово | Всего |
|------|--------|-------|
| P0 | 19 | 19 |
| P1 | 11 | 11 |
| CX | 6 | 6 |
| OPS | 4 | 4 |
| HERO-3 | 25 | 26 |
| P1+ | 0 | 12 |
| P2 | 1 | 17 |
| P3 | 0 | 6 |
| Adult | 0 | 3 |
| **Итого** | **66** | **102** |

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

## HERO-3 — 3 героя Figma→Rive (23/26)

### Ядро (01–19)

- [x] **HERO-3-01** — ADR план §1–11 + §2.1–2.3
- [x] **HERO-3-02** — Figma 3×12 эмоций (wireframe grid; final art → Rive **07**)
- [x] **HERO-3-03** — BE genie + age_policy
- [x] **HERO-3-04** — Pydantic + cosmetics genie
- [x] **HERO-3-05** — companion_persona 3 ветки
- [x] **HERO-3-06** — iOS Hub 3 карточки (🧞 только genie)
- [ ] **HERO-3-07** — Rive export `.riv` ×3 — 🟡 **3/3 placeholder** в бандле ([unblock](./COMPANION_RIVE_UNBLOCK.md)) · production art ⏳
- [x] **HERO-3-08** — Rive на сцене ([unblock](./COMPANION_RIVE_UNBLOCK.md))
  - [x] **08a** — SPM 6.20.5 + Xcode build + `.riv` в бандле (`verify_companion_rive_ios_bundle.sh`)
  - [x] **08b** — UI: `CompanionHome` → `Главное`, Rive на **реальном iPhone** PASS 2026-05-27 (placeholder art)
- [x] **HERO-3-09** — Character Bible §4 в [ALADDIN_Character_Bible.md](./ALADDIN_Character_Bible.md)
- [x] **HERO-3-10** — deploy + verify prod ✅ 2026-05-27 (`deploy_companion_p0.sh` + `verify_companion_p0_prod.sh` PASS)
- [ ] **HERO-3-11** — QA D10 + SPEECH/MOTION/MIMIC-Q ([чеклист](./COMPANION_HERO3_11_QA_CHECKLIST.md))
  - [x] **11a** — pytest companion + SPEECH-Q5 + riv gate (46 tests, 2026-05-27)
  - [ ] **11b** — device: MOTION-Q1–5, MIMIC-Q1–6, D10 (iPhone, build 209+)
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

## P1+ Production (0/12)

- [ ] **P1-12** — Postgres + Redis
- [ ] **P1-13** — голос production
- [ ] **P1-14** — XCUITest
- [ ] **P1-15** — prod verify полный
- [ ] **P1-16** — ADR hot path
- [ ] **P1-17** — accessibility
- [ ] **P1-18** — rate limit
- [ ] **P1-19** — App Store pack (+ 3 скриншота Hub)
- [ ] **P1-20** — RU/EN
- [ ] **P1-21** — offline cache
- [ ] **P1-22** — post-LLM moderation
- [ ] **P1-23** — эмоции Grok-level (= GATE-EMO)

---

## P2 — фаза B (1/17)

- [ ] **P2-01** — web search
- [ ] **P2-02** — orchestrator
- [ ] **P2-03** — Fast/Reasoning/Think
- [ ] **P2-04** — фото и PDF
- [ ] **P2-05** — trust decay/streak
- [ ] **P2-06** — family context в промпте
- [ ] **P2-07** — Responses API
- [ ] **P2-08** — COGS dashboard
- [ ] **P2-09** — Figma↔Rive (→ HERO-3)
- [x] **P2-11** — mood-aware MVP
- [ ] **P2-12** — life domains API
- [ ] **P2-13** — social bridge
- [ ] **P2-14** — вход Senior 60+
- [ ] **P2-15** — teen loneliness playbook
- [ ] **P2-16** — trust за эмпатию
- [ ] **P2-17** — A/B humor_density (genie+teen, после HERO-3)

---

## P3 (0/6)

- [ ] **P3-01** — генерация картинок
- [ ] **P3-02** — генерация видео
- [ ] **P3-03** — workspaces
- [ ] **P3-04** — длинный контекст
- [ ] **P3-05** — Android
- [ ] **P3-06** — Adult iOS Store

---

## Adult backend (0/3)

- [ ] **A-01** — OpenAPI aladdin_adult
- [ ] **A-02** — policy tests NSFW
- [ ] **A-03** — repo stub Adult app

---

## GATE — контрольные ворота

- [ ] **GATE-P0** — smoke ✅ · prod verify ✅ 27.05 · **единый вход «Мир героев» ✅ (Kids/Игры)** · device 08b ⏳
- [ ] **GATE-OPS** — health + verify prod
- [ ] **GATE-CX** — 5 фраз CX (без VPN spam)
- [ ] **GATE-P1** — cosmetics, legal
- [ ] **GATE-HERO-3-IOS-α** — debounce + timeline + emoji + 1.2s + **23/24** (**без** production .riv)
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

## Сессия 2026-05-26…27 (зафиксировано)

- [x] Rive SPM кэш: `scripts/reset_rive_spm_cache.sh`  
- [x] iOS 15 fixes: `onChange`, `NavigationView`, `CompanionAPIService`, `Color`/Rive split  
- [x] `CompanionChatResponse.cosmeticUnlocked`, `ALADDINNavigationBar` companion cases  
- [x] **Проект ALADDIN собирается в Xcode**

## В конце (по решению команды)

- [x] **Xcode compile** (2026-05-27)  
- [ ] **Device QA** HERO-3-08b + MOTION-Q, MIMIC-Q, D10, GATE-EMO-EMPATHY  
- [ ] **TestFlight**

---

*Файл для ежедневного трекинга. Обновляй галочки и [матрицу](./COMPANION_HERO3_READINESS_MATRIX.md) при закрытии задач.*
