# Companion + Rive — главный handoff для следующей ML-системы

> **Открой этот файл первым.** Он объясняет, что уже сделано, что делать дальше, и как не сломать канон.  
> **Дата:** 2026-06-04 · **Репо:** `ALADDIN_FAMILY` · **Папка:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Build (трекер):** 216 · **Прогресс:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) (90/102)

---

## 0. За 2 минуты — что происходит

| | |
|--|--|
| **Продукт** | Семейный AI-компаньон: 3 героя (🦄 Единорог, 🧑 Аладдин-человек, 🧞 Джин), вход **Kids → Игры → Мир героев** |
| **Визуал** | **2D Rive** (не 3D), artboard **360×480**, 12 эмоций + lip-sync |
| **UI чата** | **AIL** — 3 режима сцены (standard / focused / immersive), в голосе герой **~72–75%** экрана |
| **Figma** | ✅ **02b** — 36/36 кадров live audit → [COMPANION_FIGMA_AUDIT_LIVE_2026-06-04.md](./COMPANION_FIGMA_AUDIT_LIVE_2026-06-04.md) |
| **Блокер продакшена** | **HERO-3-07** — нет финальных `unicorn.riv` · `aladdin.riv` · `genie.riv` в бандле |
| **iOS под Rive** | ✅ Код готов (RiveRuntime, emotion map, AIL layout, Wellness 48pt reuse) — ждёт только `.riv` |

**Критический путь Rive:**

```
02b Figma ✅  →  07 export 3×.riv  →  11c GATE-EMO / MIMIC-Q  →  device sign-off
```

Параллельно (не блокирует 07): TestFlight QA, STT 11b, BE P1+.

---

## 1. Что уже реализовано (не переделывать)

### 1.1 iOS — Companion + AIL (2026-06-04)

| Компонент | Статус | Где в коде |
|-----------|--------|------------|
| **AIL P0** — 3 режима `ConversationPresence` | ✅ | `UI/Companion/CompanionHeroLayout.swift` |
| **AIL P0** — immersive при голосе, tab bar скрыт | ✅ | `Screens/CompanionConversationScreen.swift`, `CompanionHomeScreen.swift` |
| **AIL P1** — chip rail баннеров в immersive (32 pt) | ✅ | `UI/Companion/CompanionConversationBannersSection.swift` |
| **AIL P2** — настройка родителя «Размер героя» | ✅ | `CompanionMineTabView.swift`, `CompanionSettings.HeroPresencePinMode` |
| Hero PNG fallback | ✅ | `Resources/Companion/*_master.png` |
| Rive host + lip-sync | ✅ | `CompanionHeroRiveHost.swift`, `CompanionHeroLipSync.swift` |
| Hub превью **96 pt** | ✅ | `hubThumbnailDiameterPt` |
| Wellness pillar **48 pt** | ✅ | `WellnessPillarEmotionView` |
| Feature flag AIL | ✅ | `AppConfig.heroImmersiveLayoutEnabled` |

Детали AIL: [COMPANION_HERO_IMMERSIVE_IMPLEMENTATION_PLAN.md](./COMPANION_HERO_IMMERSIVE_IMPLEMENTATION_PLAN.md) · ADR: [GROK §6.2b](./GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md)

### 1.2 Figma (02b)

| Параметр | Значение |
|----------|----------|
| File | [Companion-Heroes](https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes) |
| Key | `vwKcGPUUEZjgayEHNn0BJM` |
| Кадры | **36** = 3 героя × 12 эмоций |
| Размер кадра | **360 × 480 pt** |
| Аудит | [COMPANION_FIGMA_AUDIT_LIVE_2026-06-04.md](./COMPANION_FIGMA_AUDIT_LIVE_2026-06-04.md) |

Подключение Figma MCP: [FIGMA_MCP_ENABLE.md](./FIGMA_MCP_ENABLE.md) · env: [FIGMA_COMPANION.env](./FIGMA_COMPANION.env) (не коммитить токены).

### 1.3 Backend / API

- Префикс: `/api/ai/companion/*` — см. [GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md](./GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md)
- `character_id`: `unicorn` | `aladdin` | `genie`
- Child: только unicorn; genie — teen/parent + consent
- **Prod:** no mock bypass — [.cursor/rules/prod-no-mock-bypass.mdc](../.cursor/rules/prod-no-mock-bypass.mdc)

---

## 2. Что делать дальше — только Rive (пошагово)

### Шаг 1 — Аниматор / Rive Editor (**HERO-3-07**) ← ГЛАВНЫЙ БЛОКЕР

| # | Действие | DoD |
|---|----------|-----|
| 1 | Открыть Figma 02b → импорт в Rive (3 файла или 1 с 3 artboards) | Лицо в **верхних ~60%** artboard (MIMIC-Q1 под AIL `fill`) |
| 2 | State machine: 12 emotion + inputs `mouth_open`, фазы listening/thinking/speaking | Имена = [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) §2.2 |
| 3 | Export | `unicorn.riv`, `aladdin.riv`, `genie.riv` |
| 4 | Размер каждого | ≥ 25 KB, **< 500 KB** (CI gate) |
| 5 | Положить в репо | `Resources/Companion/` |
| 6 | Прогнать gate | `scripts/companion_riv_size_gate.py` (см. [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)) |

**Чеклист export:** [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md)  
**Канон art:** [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md)  
**Краткий Rive-план:** [RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md)

### Шаг 2 — iOS после появления `.riv`

| # | ID | Действие |
|---|-----|----------|
| 1 | **HERO-3-08b** | Device: чат — Rive вместо PNG, lip-sync, 3 героя |
| 2 | **HERO-3-11** | GATE-DIALOG D10 + **GATE-EMO** |
| 3 | **HERO-3-11c** | MIMIC-Q1…Q6 — скриншот-сетка 12 state × 3 героя |
| 4 | **07b QA** | Wellness Hub — тот же `.riv` на pillar 48 pt |

**Не делать:** 4× `wellness_*_hero.riv` — deprecated. Wellness = те же 3 файла ([WELLNESS_PILLAR_RIVE_PLAN.md](./WELLNESS_PILLAR_RIVE_PLAN.md)).

### Шаг 3 — Sign-off

- [ ] iPhone 15: immersive голос → герой ~72–75%, лицо не обрезано
- [ ] Child profile: 2 wellness карточки — **один** выбранный герой
- [ ] Обновить [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md)
- [ ] `[x]` **HERO-3-07**, **11c**, **GATE-EMO** в [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)

---

## 3. Роли и ответственность

| Роль | Задачи | Не трогать |
|------|--------|------------|
| **ML / Cursor (код)** | После 07: wire bundle, фиксы runtime, QA баги | Figma кадры, export .riv |
| **Дизайн / Figma** | Правки 02b только по тикету PO | iOS layout fractions AIL |
| **Аниматор / Rive** | 07 export, motion spec | API, backend |
| **QA** | Device matrices, GATE-EMO | — |
| **PO** | Приоритет 07 vs TF/STT | — |

---

## 4. Иерархия документов (что читать)

| Приоритет | Файл | Зачем |
|-----------|------|-------|
| **0 — этот файл** | **COMPANION_ML_RIVE_HANDOFF_MASTER.md** | Rive + общий контекст для ML |
| **0a — Cursor batch** | [COMPANION_RIVE_HERO307_CURSOR_BATCH.md](./COMPANION_RIVE_HERO307_CURSOR_BATCH.md) | Пошаговый `[ ]`/`[x]` HERO-3-07 |
| **0d — production 100%** | [COMPANION_HERO_07_PRODUCTION_100_PIPELINE.md](./COMPANION_HERO_07_PRODUCTION_100_PIPELINE.md) | 12 лиц · Figma v2 vs Rive rig · export scripts |
| **0b** | [COMPANION_ML_MASTER_ONE_FILE.md](./COMPANION_ML_MASTER_ONE_FILE.md) | Figma + layout + аудит + ссылки |
| **0c** | [COMPANION_ML_HANDOFF_START_HERE.md](./COMPANION_ML_HANDOFF_START_HERE.md) | Расширенная карта + BE/deploy |
| **1** | [RIVE_MASTER_PLAN.md](./RIVE_MASTER_PLAN.md) | Только Rive pipeline |
| **1** | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) | Единственный `[x]`/`[ ]` |
| **2** | [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) | 360×480, PNG, node ID |
| **2** | [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) | Motion, mimic, речь |
| **2** | [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md) | Описание ID задач |
| **3** | [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) | BE, stream, deploy |
| **3** | [COMPANION_WHAT_REMAINS.md](./COMPANION_WHAT_REMAINS.md) | 12 открытых из 102 |

---

## 5. Ключевые файлы кода (быстрый поиск)

```
UI/Companion/
  CompanionHeroLayout.swift          # AIL fractions + resolvePresence
  CompanionHeroAvatarView.swift      # Rive / PNG / Animated
  CompanionHeroRiveHost.swift        # RiveRuntime
  CompanionConversationBannersSection.swift  # P1 chips

Screens/
  CompanionHomeScreen.swift          # 4 вкладки, tab bar hide
  CompanionConversationScreen.swift  # Чат + голос + presence
  CompanionMineTabView.swift         # P2 hero pin (parent)

Resources/Companion/
  unicorn_master.png                 # ← заменить на unicorn.riv
  aladdin_master.png
  genie_master.png
  (целевые) unicorn.riv aladdin.riv genie.riv

Core/Companion/
  CompanionPersonalityPresets.swift  # CompanionSettings, pin mode
```

---

## 6. Правила (нарушение = регресс)

1. **Один art-пайплайн:** 3 героя · 3× `.riv` · **360×480** — без 4× wellness riv.
2. **Не менять** Hub **96 pt**, Wellness **48 pt**, порядок **02b → 07 → 07b**.
3. **AIL** меняет только presentation iOS; artboard Figma не расширять под «100% экран».
4. **Prod:** без mock/fallback на parental bypass API.
5. **Трекер:** `[x]` только после device/API proof — [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md).

---

## 7. Параллельные дорожки (пока нет .riv)

| Дорожка | Действие |
|---------|----------|
| **Rive (критично)** | HERO-3-07 → 11c → GATE-EMO |
| **iOS без Rive** | TF QA, STT 11b, [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) |
| **BE** | P1+ по [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) |

---

## 8. Команды для ML-агента

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Аудит Figma 02b (нужен FIGMA_ACCESS_TOKEN в FIGMA_COMPANION.env)
python3 scripts/audit_companion_figma_02b.py

# Размер .riv после export
python3 scripts/companion_riv_size_gate.py   # если есть в репо

# Сборка
xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' build
```

**Figma MCP (Cursor):** `whoami` → `get_metadata` fileKey `vwKcGPUUEZjgayEHNn0BJM`, nodeId `4:2` / `5:2` / `6:2`.

---

## 9. Контакты / ссылки

| | |
|--|--|
| Git remote | `git@github.com:sergey234/ALADDIN_FAMILY.git` |
| Figma Companion | https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes |
| Rive Editor | https://rive.app |
| Архитектура Grok→ALADDIN | [GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md](./GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md) |

---

*Документ — единая точка входа для следующей ML-системы по Rive и Companion. Обновляй дату при смене блокера (07 → QA).*
