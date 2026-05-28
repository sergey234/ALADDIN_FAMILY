# 🧞 Companion — Handoff для ML-системы (2026-05-28)

> **Открой после:** [COMPANION_ML_HANDOFF_START_HERE.md](./COMPANION_ML_HANDOFF_START_HERE.md)  
> **Главный трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) — **66 / 102 (65%)** · **36 открыто**  
> **План на завтра:** [COMPANION_PLAN_TOMORROW_2026-05-29.md](./COMPANION_PLAN_TOMORROW_2026-05-29.md)  
> **Rive / Node / MCP:** [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md)

---

## 0. За 60 секунд

| | |
|---|---|
| **Продукт** | AI-компаньон Kids: 3 героя, голос, 13 эмоций + lip-sync, 2D Rive, сцена 56% |
| **Репо iOS** | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` |
| **Build** | **210** (`AppConfig.buildNumber`) |
| **Прогресс** | **66/102** · HERO-3: **24/26** (открыты **07**, **11**) |
| **Критический путь** | **07** production `.riv` ×3 → **11c** → **GATE-EMO** (параллельно **11b**) |
| **Figma** | `vwKcGPUUEZjgayEHNn0BJM` — **36/36** frames ✅ · PO lock genie = OB_03 ✅ |
| **Rive на Mac** | Editor ✅ · Node v26 ✅ · RiveMCP 1.3.6 ✅ · `unicorn.riv` обновлён (158,578 bytes) |

**Правило:** галочку `[x]` в TRACKER — только после реальной проверки (gate / device / PO).

---

## 1. Как устроен продукт (для ML)

```
Онбординг (393×852, Lottie)     — read-only, file KvkUdyb5Ll31Z9FSzCbpNl
        ↓ стиль референс
Figma Companion (360×480×36)    — макеты, v1.1 = 1 PNG × 12 имён / герой
        ↓ аниматор
Rive Editor → .riv ×3           — runtime в iOS
        ↓
CompanionHeroRiveHost           — 13 triggerInput + setInput mouth_open
        ↓
Экран «Главное» ~56% rect       — Hub 88×88 круг
```

| `character_id` | Master PNG | `.riv` |
|----------------|------------|--------|
| unicorn | `docs/assets/unicorn_master_crop_360x480.png` | `Resources/Companion/unicorn.riv` |
| aladdin | `docs/assets/aladdin_master_OB01_crop_360x480.png` | `aladdin.riv` |
| genie | `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` | `genie.riv` |

**3 героя — разные персонажи.** Джин: дым/искры только playful / excited / speaking.

---

## 2. Что сделано (сессии 2026-05-27 … 2026-05-28)

### Figma & PO
- [x] **HERO-3-02b** — 36 frames 360×480 (unicorn v2, aladdin OB_01, genie OB_03×12)
- [x] **02b-PO-lock** — genie master = OB_03 headfix в [CANON](./COMPANION_HERO_ART_CANON.md)
- [x] Live Figma audit: [COMPANION_FIGMA_AUDIT_LIVE_2026-05-28.md](./COMPANION_FIGMA_AUDIT_LIVE_2026-05-28.md)

### iOS
- [x] **08b** Rive на device (placeholder)
- [x] **PNG bridge** — `CompanionHeroRasterView`, masters в `Resources/Companion/`
- [x] Build **210**, TTS на текст, Hub Rive-превью
- [x] **11a** pytest 46

### Rive / инфра
- [x] Доки: [5 шагов Editor](./COMPANION_RIVE_EDITOR_5_STEPS.md), animator brief/supplement, export checklist
- [x] Скрипты `companion_07_*.sh`
- [x] **Node v26** + **RiveMCP 1.3.6** + Cursor MCP config
- [x] Пробный MCP export: `unicorn_mcp_draft.rev` / `.riv` (не production)
- [x] `unicorn.riv` production partial: Hero360 + HeroSM + 13 triggers + `mouth_open`, размер >25 KB
- [x] Gate check PASS после `unicorn.riv` (size_gate + verify_bundle)
- [x] RiveMCP free exports: **0/3 осталось** (дальше manual export или license key)

### Не закрыто (не ставить [x])
- [ ] **HERO-3-07** — production `.riv` ×3 (&gt;25 KB, настоящий art)
- [ ] **HERO-3-11b** — device QA placeholder
- [ ] **HERO-3-11c** — MIMIC после 07

### Что осталось по 07 (точные действия для следующей ML)

- [ ] `aladdin.riv`:
  - `Cmd+Shift+I` → `Cmd+Shift+G`
  - PNG: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/assets/aladdin_master_OB01_crop_360x480.png`
  - Перетащить на Hero360 full-cover (360×480)
  - Export в `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion/aladdin.riv`
- [ ] `genie.riv`:
  - `Cmd+Shift+I` → `Cmd+Shift+G`
  - PNG: `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png`
  - Перетащить на Hero360 full-cover (360×480)
  - Export в `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion/genie.riv`
- [ ] После export:
  - `python3 scripts/companion_riv_size_gate.py --dir Resources/Companion`
  - `./scripts/verify_companion_rive_ios_bundle.sh`
  - iPhone smoke: живой Rive (не PNG bridge)

---

## 3. Полный спектр открытых задач (36 + GATE)

### Критический хвост HERO-3 (сделать первым)

- [ ] **HERO-3-07** — Rive export production `unicorn.riv`, `aladdin.riv`, `genie.riv`
- [ ] **HERO-3-11** — QA umbrella
  - [ ] **11b** — device MOTION-Q1–5, MIMIC-Q1–6, D10, SPEECH-Q6 (build 210+, placeholder OK)
  - [ ] **11c** — повтор MIMIC-Q1 после production `.riv`

### P1+ Production (12)

- [ ] **P1-12** — Postgres + Redis
- [ ] **P1-13** — голос production
- [ ] **P1-14** — XCUITest
- [ ] **P1-15** — prod verify полный
- [ ] **P1-16** — ADR hot path
- [ ] **P1-17** — accessibility
- [ ] **P1-18** — rate limit
- [ ] **P1-19** — App Store pack
- [ ] **P1-20** — RU/EN
- [ ] **P1-21** — offline cache
- [ ] **P1-22** — post-LLM moderation
- [ ] **P1-23** — эмоции Grok-level (= GATE-EMO)

### P2 (16)

- [ ] **P2-01** — web search
- [ ] **P2-02** — orchestrator
- [ ] **P2-03** — Fast/Reasoning/Think
- [ ] **P2-04** — фото и PDF
- [ ] **P2-05** — trust decay/streak
- [ ] **P2-06** — family context в промпте
- [ ] **P2-07** — Responses API
- [ ] **P2-08** — COGS dashboard
- [ ] **P2-09** — Figma↔Rive (→ HERO-3)
- [ ] **P2-12** — life domains API
- [ ] **P2-13** — social bridge
- [ ] **P2-14** — вход Senior 60+
- [ ] **P2-15** — teen loneliness playbook
- [ ] **P2-16** — trust за эмпатию
- [ ] **P2-17** — A/B humor_density

### P3 (6)

- [ ] **P3-01** … **P3-06** — картинки, видео, workspaces, контекст, Android, Adult Store

### Adult backend (3)

- [ ] **A-01** · **A-02** · **A-03**

### GATE (11 ворот)

- [ ] **GATE-P0** — ждёт **11b**
- [ ] **GATE-OPS** · **GATE-CX** · **GATE-P1**
- [ ] **GATE-EMO** — 13 state + Rive + D10 (после **07** + **11c**)
- [ ] **GATE-EMO-EMPATHY** — 5 мин × возраст (device)
- [ ] **GATE-PROD** · **GATE-P2** · **GATE-P3**
- [ ] **GATE-DIALOG-REGRESS** (14/19 auto ✅)
- [ ] **GATE-DIALOG** — D01–D10 TestFlight

### Конец спринта (команда)

- [ ] **TestFlight**
- [x] Xcode compile · 08b · 02b Figma — уже ✅

---

## 4. Каталог документов (обязательные для ML)

| # | Файл | Когда читать |
|---|------|--------------|
| 1 | [COMPANION_ML_HANDOFF_START_HERE.md](./COMPANION_ML_HANDOFF_START_HERE.md) | Первый вход |
| 2 | [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md) | **Этот файл** — состояние 28.05 |
| 3 | [COMPANION_PLAN_TOMORROW_2026-05-29.md](./COMPANION_PLAN_TOMORROW_2026-05-29.md) | План дня |
| 4 | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) | Единственный источник `[x]` |
| 5 | [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md) | Node + RiveMCP + Editor |
| 6 | [COMPANION_RIVE_EDITOR_5_STEPS.md](./COMPANION_RIVE_EDITOR_5_STEPS.md) | Production export |
| 7 | [COMPANION_HANDOFF_AI_NEXT.md](./COMPANION_HANDOFF_AI_NEXT.md) | Figma / PO / порядок |
| 8 | [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) | PO art |
| 9 | [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) | DoD 07 |
| 10 | [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) | 11b/11c |
| 11 | [COMPANION_HERO3_11B_DEVICE_SESSION.md](./COMPANION_HERO3_11B_DEVICE_SESSION.md) | Сессия iPhone |
| 12 | [COMPANION_100_PERCENT_PARALLEL.md](./COMPANION_100_PERCENT_PARALLEL.md) | План vs факт |
| 13 | [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md) | Аудит Figma |
| 14 | [FIGMA_COMPANION.env](./FIGMA_COMPANION.env) | file keys |

---

## 5. Ключевой код iOS

| Файл | Назначение |
|------|------------|
| `UI/Companion/CompanionHeroRiveHost.swift` | Rive runtime, triggers, mouth_open |
| `UI/Companion/CompanionHeroRasterView.swift` | PNG fallback &lt; 25 KB .riv |
| `UI/Companion/CompanionHeroAvatarView.swift` | raster → Rive → shell |
| `Resources/Companion/*.riv` | бандл |
| `scripts/companion_riv_size_gate.py` | size gate |

---

## 6. Ошибки прошлых сессий

1. Не удалять genie 12× + ряд OB_02–06 в Figma без PO.
2. Не путать онбординг 393×852 и Companion 360×480.
3. Не переименовывать Rive triggers — iOS hardcoded.
4. Не коммитить без запроса пользователя.
5. RiveMCP ≠ production art; не перезаписывать `unicorn.riv` черновиком без проверки.
6. Бесплатные RiveMCP exports исчерпаны (**3/3**) — без ключа только manual export через Rive Editor.

---

## 7. Сообщение PO при закрытии 07

Текст в чат: **«07 готов»** → обновить TRACKER `[x]` HERO-3-07 → запустить **11c** → цель **GATE-EMO**.

---

*Следующая ML-система: начни с [PLAN_TOMORROW](./COMPANION_PLAN_TOMORROW_2026-05-29.md) §1.*
