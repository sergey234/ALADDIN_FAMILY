# 🧞 Companion — СТАРТ ДЛЯ СЛЕДУЮЩЕЙ ML-СИСТЕМЫ

> **Открой этот файл первым.** Здесь — карта документов. **Главный handoff «доделать до 100%»:** [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) · **План:** [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md)  
> **Дата:** 2026-05-29 · **Handoff №4** — [COMPANION_ML_HANDOFF_2026-05-29.md](./COMPANION_ML_HANDOFF_2026-05-29.md) · **Без Rive:** [COMPANION_TASKS_WITHOUT_RIVE.md](./COMPANION_TASKS_WITHOUT_RIVE.md) · **Код-спринты:** [CODE_PLAN](./COMPANION_CODE_PLAN_NO_RIVE.md) · [CODE_TODO](./COMPANION_CODE_TODO_TRACKER.md)

---

## 0. За 60 секунд

| | |
|---|---|
| **Продукт** | AI-компаньон для детей/семьи: 3 героя, голос, эмоции, trust, вход **Kids → Игры → Мир героев** |
| **Визуал** | **2D Rive** (не 3D), сцена **56%** экрана, субтитр снизу — как Grok Companions |
| **Репозиторий** | `git@github.com:sergey234/ALADDIN_FAMILY.git` · ветка **`master`** |
| **Рабочая папка iOS** | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` |
| **Карта кода + LOC + CSV** | [MOBILE_CODEBASE_MAP.md](./MOBILE_CODEBASE_MAP.md) · [data/mobile_loc_local.csv](./data/mobile_loc_local.csv) · [data/mobile_loc_vps.csv](./data/mobile_loc_vps.csv) |
| **Build iOS** | **216** (Info.plist + project.pbxproj + AppConfig) |
| **Прогресс** | **90 / 102 (88%)** · Sprint 4–5 MVP код ✅ · **осталось:** [WHAT_REMAINS](./COMPANION_WHAT_REMAINS.md) |
| **Главный TODO** | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) — ставь `[x]` только после реальной проверки |
| **Доделать** | [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) — TF215, Sprint 4–5 MVP, блок G |
| **Cursor TODO** | [COMPANION_CURSOR_TODO_STAGE2_3.md](./COMPANION_CURSOR_TODO_STAGE2_3.md) — этап 2–3 |
| **Что осталось (102)** | [COMPANION_WHAT_REMAINS.md](./COMPANION_WHAT_REMAINS.md) — все открытые задачи |
| **Rive** | **Отложено** (12 задач) — не блокирует «100% без Rive» |

### Что делать дальше (две параллельные дорожки)

```mermaid
flowchart LR
  subgraph now["Сейчас без Rive"]
    A[214 STT + UX]
    B[P1+ BE/iOS]
    C[GATE-DIALOG]
  end
  subgraph later["После подключения Rive"]
    D[07 export .riv]
    E[11c MIMIC]
    F[GATE-EMO]
  end
  now --> later
```

| Дорожка | ID | Действие |
|---------|-----|----------|
| **Сейчас** | Этап 2–3 | [RUNBOOK](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md): Redis, chips device, PhotosPicker, COGS UI |
| **Сейчас** | TF **215** | Archive если ещё не в TestFlight (git ✅, VPS ✅) |
| **Сейчас** | Блок G | Проверить карточку Rewards на device (build 215) |
| **Потом** | TF **214** QA | device STT (11b) — отложено в 12 задач |
| **Потом** | **HERO-3-07** | Rive Editor → [5 steps](./COMPANION_RIVE_EDITOR_5_STEPS.md) |
| **Потом** | **11b/11c**, **GATE-EMO** | MOTION/MIMIC/D10 + приёмка |

**iOS-код под `.riv` уже готов** — после **07** меняются только файлы в бандле.

---

## 1. Порядок чтения (рекомендуется)

Читай **по номеру** в первый день. Не нужно читать все 23 файла подряд.

| # | Документ | Зачем | Время |
|---|----------|-------|-------|
| **1** | [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) | **Главный:** что сделано, stream, deploy, блоки A–L | 15 мин |
| **2** | [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md) | Пошаговый план этапов 1–5 | 10 мин |
| **3** | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) | Единый список 102 задач с `[x]` | 15 мин |
| **4** | [COMPANION_HERO_ART_CANON.md](./COMPANION_HERO_ART_CANON.md) | **PO ✅ art** — где лежат все картинки | 5 мин |
| **4b** | [COMPANION_GATE_OPS_SIGNOFF_2026-05-29.md](./COMPANION_GATE_OPS_SIGNOFF_2026-05-29.md) | **GATE-OPS ✅** verify 18/18 | 2 мин |
| **5** | [COMPANION_100_PERCENT_PARALLEL.md](./COMPANION_100_PERCENT_PARALLEL.md) | План vs факт, кто что закрывает | 5 min |
| **5** | [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md) | **Аудит Figma** — что реально в файле | 5 мин |
| **6** | [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) | **HERO-3-07** — размеры, SM, export | 10 мин |
| **7** | [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) | Device QA 11b / 11c | 10 мин |
| **8** | [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) | Полная спека 3 героов (§2.2 Motion, §2.3 Mimic) | по необходимости |
| **9** | [COMPANION_ML_HANDOFF_2026-05-27.md](./COMPANION_ML_HANDOFF_2026-05-27.md) | SSH, BE, скрипты, история | по задаче |

---

## 2. Что уже сделано ✅ (не переделывать)

### 2.1 Продукт и iOS (build 214)

| Сделано | Где в коде / доках |
|---------|-------------------|
| **3 героя всем** (PO 29.05) | `age_policy.py`, Hub/Home, voice WS genie |
| Big button **«Друзья»** + pet + legacy redirect | `08_ChildInterfaceScreen`, `UnicornPetView`, `ALADDINApp` |
| Mic coach + child hold-only mic | `CompanionConversationScreen` |
| Единый вход **«Мир героев»** (Главное / Герои / Моё) | `CompanionHomeScreen`, [UNIFIED_HOME_UX](./COMPANION_UNIFIED_HOME_UX.md) |
| Layout **56%** герой + субтитр | `CompanionHeroLayout`, `CompanionConversationScreen` |
| Rive host + placeholder `.riv` ×3 | `CompanionHeroRiveHost`, `Resources/Companion/` |
| **08b PASS** на реальном iPhone (placeholder art) | [08b checklist](./COMPANION_08B_DEVICE_CHECKLIST.md) |
| **TTS** + **Voice WS polish** + **offline** + **l10n RU/EN** | Sprint 2 |
| **XCUITest**, **429 errors**, **post-LLM moderation**, **ADR** | Sprint 3 |
| pytest companion **49 passed** | `Tests/test_companion*.py` |

### 2.2 Backend / OPS

| Сделано | Документ |
|---------|----------|
| P0 MVP (19/19), P1 (11/11), CX (6/6), OPS (4/4) | [TRACKER](./COMPANION_PROGRESS_TRACKER.md) |
| Deploy + verify prod 27.05 | `COMPANION_DEPLOY_P0.md`, HERO-3-10 |
| 3 героя BE + age_policy (**всем** age_band, PG) | `companion_persona`, `age_policy.py`, routers |

### 2.3 Figma (только спека)

| Сделано | Не путать с |
|---------|-------------|
| Страница **`00_Spec`**: ADR, Motion, Mimic, Sign-off, RIVE_EXPORT | ❌ это **не** 36 готовых кадров |
| **HERO-3-17** sign-off PO 2026-05-26 | разблокирует рисование 02b |

---

## 3. Что НЕ сделано ⏳ (твоя работа)

| ID | Задача | Блокер |
|----|--------|--------|
| **P1-12** | Postgres + Redis | Sprint 4 |
| **P2-02, P2-12…16** | orchestrator, domains, эмпатия | Sprint 4 |
| **HERO-3-07** | Production `.riv` ×3 | Rive Editor |
| **HERO-3-11b** | Device QA MOTION/MIMIC/D10 | После 07 (SPEECH часть ⏳ TF) |
| **HERO-3-11c** | MIMIC после 07 | После 07 |
| **GATE-*** | D01–D10, EMO, PROD | TestFlight QA |
| **P1-19b** | 3 marketing screenshots Hub | После 07 |

### Устарело (исправлено 29.05)

- ~~**HERO-3-02b** 36 frames~~ — ✅ сделано  
- ~~**Джин не виден child**~~ — PO: **3 героя всем**

---

## 4. Figma — правда на 2026-05-27

| Ресурс | URL / ключ |
|--------|------------|
| **Companion Heroes** | https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM/Companion-Heroes |
| **File key** | `vwKcGPUUEZjgayEHNn0BJM` |
| **Env** | [FIGMA_COMPANION.env](./FIGMA_COMPANION.env) |
| **Онбординг (READ-ONLY!)** | `KvkUdyb5Ll31Z9FSzCbpNl` — **не редактировать** |

| Страница Figma | Статус |
|----------------|--------|
| `00_Spec` | ✅ есть |
| `01_Unicorn` | ✅ 12 frames v2 |
| `02_Aladdin_Human` | ✅ 12 frames |
| `03_Genie` | ✅ 12 frames OB_03 headfix |

Подробный аудит: [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md)

**Размеры для 02b и 07:**

| Параметр | Значение |
|----------|----------|
| Artboard Rive | **360 × 480 pt** |
| Сцена на телефоне | ~**56%** высоты, прямоугольник |
| Лицо (QA) | короткая сторона ≥ **96 pt** |
| Файлы | `< 500 KB` каждый |
| SM inputs | `emotion` (triggers) + `mouth_open` (0…1) |

---

## 5. Команды (копируй в терминал)

```bash
# Рабочая директория
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Backend tests
PYTHONPATH=. python3 -m pytest Tests/test_companion*.py -q

# Rive size gate (после замены .riv)
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion

# iOS bundle check
./scripts/verify_companion_rive_ios_bundle.sh

# Xcode build (simulator)
xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' build

# Prod verify (нужен SSH)
./scripts/verify_companion_p0_prod.sh
```

**Git (последние коммиты Companion):**

| Commit | Содержание |
|--------|------------|
| `80aa62a7` | docs: Figma audit, tracker |
| `0bde7929` | build 210: TTS text, Hub preview |
| `30e917b2` | fix CI: `.companion` audio consumer |
| `6fe20feb` | Мир героев, Rive host, build 209 |

---

## 6. Полный каталог документов `docs/COMPANION_*`

Все пути относительно:  
`ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/`

### 6.1 🟢 Старт и трекинг (читать в первую очередь)

| Файл | Назначение |
|------|------------|
| **COMPANION_ML_HANDOFF_START_HERE.md** | **Этот файл** — входная точка |
| **COMPANION_PROGRESS_TRACKER.md** | **102 задачи** `[x]`/`[ ]` — единственный источник прогресса |
| **COMPANION_CODE_PLAN_NO_RIVE.md** | **Финальный план кода v2** — 3 героя всем, UX+mic, спринты 1–5 |
| **COMPANION_CODE_TODO_TRACKER.md** | **Трекер кода v2** — 49 задач, галочки простым языком |
| **COMPANION_100_PERCENT_PARALLEL.md** | План vs факт, зоны ответственности |
| **COMPANION_ML_HANDOFF_2026-05-27.md** | Handoff: BE, SSH, скрипты, индекс кода |
| **COMPANION_ML_HANDOFF_FULL.md** | Расширенный handoff (часть устарела — сверять с TRACKER) |

### 6.2 🎨 Figma · Rive · герои (HERO-3)

| Файл | Назначение |
|------|------------|
| **COMPANION_FIGMA_STATUS.md** | Аудит Figma: что есть / чего нет |
| **FIGMA_COMPANION.env** | URL, file key, страницы |
| **COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md** | Мастер-план 3 героев, §2.1–2.3, QA |
| **COMPANION_FIGMA_PRODUCT_DECISIONS.md** | PO-решения, 12 vs 13 emotions |
| **COMPANION_2D_VS_3D_ADR.md** | ADR: 2D Rive, не SceneKit |
| **COMPANION_RIVE_EXPORT_CHECKLIST.md** | **HERO-3-07** DoD export |
| **COMPANION_RIVE_UNBLOCK.md** | SPM RiveRuntime, симулятор 15.x |
| **COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md** | HERO-3-17 sign-off |
| **COMPANION_HERO3_READINESS_MATRIX.md** | Матрица Spec/BE/iOS/.riv/QA |
| **ALADDIN_Character_Bible.md** | Character Bible §4 (герои) |

### 6.3 ✅ QA и device

| Файл | Назначение |
|------|------------|
| **COMPANION_HERO3_11_QA_CHECKLIST.md** | **11b / 11c**: D10, MOTION, MIMIC, SPEECH |
| **COMPANION_08B_DEVICE_CHECKLIST.md** | Rive на device (08b) |
| **COMPANION_FINAL_PLAN_AND_VERIFICATION.md** | GATE-EMO, D10 таблица, регресс |
| **COMPANION_UNIFIED_HOME_UX.md** | UX «Мир героев» |
| **COMPANION_GATE_CX_D01_D03_2026-05-26.md** | CX gate сценарии |
| **COMPANION_GATE_DIALOG_REGRESS_REPORT_2026-05-26.md** | R1–R19 регресс |
| **COMPANION_OPS05_DOD_2026-05-26.md** | OPS DoD |

### 6.4 🏗 Архитектура · деплой · планирование

| Файл | Назначение |
|------|------------|
| **COMPANION_MASTER_PLAN_v1.md** | Roadmap P0→P3 |
| **COMPANION_IMPLEMENTATION_TODOS.md** | Описание каждой задачи по ID |
| **COMPANION_MODULAR_ARCHITECTURE.md** | Модули платформы |
| **COMPANION_DEPLOY_P0.md** | Деплой VPS, env |
| **GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md** | Grok parity, API |
| **GROK_FULL_FEATURE_MATRIX.md** | 102 фичи трассировка |

### 6.5 🔧 Инфраструктура (вне docs/)

| Файл | Назначение |
|------|------------|
| `../.github/workflows/companion-gate.yml` | CI: pytest + riv gate |
| `../.cursor/rules/prod-no-mock-bypass.mdc` | **Prod: no mock bypass** |
| `../scripts/companion_riv_size_gate.py` | Лимит 500 KB на `.riv` |
| `../scripts/deploy_companion_p0.sh` | Деплой |
| `../scripts/verify_companion_p0_prod.sh` | Prod verify |

---

## 7. Каталог кода iOS (Companion)

База: `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`

### 7.1 Экраны

| Файл | Роль |
|------|------|
| `Screens/CompanionHomeScreen.swift` | Корень: вкладки Главное / Герои / Моё |
| `Screens/CompanionConversationScreen.swift` | **56%** сцена + субтитр + mic + TTS |
| `Screens/CompanionHubScreen.swift` | Выбор героя (вкладка Герои) |
| `Screens/CompanionMineTabView.swift` | Trust, TTS toggle, история |
| `Screens/ChildRewardsScreen.swift` | Вход «Мир героев» из Игр |

### 7.2 UI / Rive

| Файл | Роль |
|------|------|
| `UI/Companion/CompanionHeroLayout.swift` | 56% / 28%, artboard 360×480 |
| `UI/Companion/CompanionHeroAvatarView.swift` | Rive → shell → procedural |
| `UI/Companion/CompanionHeroRiveHost.swift` | RiveRuntime, sim 15 guard |
| `UI/Companion/CompanionHeroAnimatedView.swift` | Emoji fallback |
| `UI/Companion/CompanionHubHeroPreview.swift` | Hub preview 88pt |
| `UI/Companion/CompanionDialogueStrip.swift` | Субтитр |
| `UI/Companion/CompanionHeroEmotion+Timeline.swift` | Debounce 400 ms |

### 7.3 Core

| Файл | Роль |
|------|------|
| `Core/Voice/CompanionVoiceSession.swift` | WebSocket голос |
| `Core/Voice/CompanionSpeechOutput.swift` | TTS AVSpeech |
| `Core/Audio/VoiceAudioSessionCoordinator.swift` | `.companion` consumer |
| `Core/Services/CompanionAPIService.swift` | REST |
| `Core/Models/CompanionModels.swift` | DTO, emotions |
| `Core/Config/AppConfig.swift` | build **214** |

### 7.4 Ресурсы

| Путь | Роль |
|------|------|
| `Resources/Companion/unicorn.riv` | Placeholder → заменить в **07** |
| `Resources/Companion/aladdin.riv` | Placeholder |
| `Resources/Companion/genie.riv` | Placeholder |

### 7.5 Backend (в том же репо)

| Путь | Роль |
|------|------|
| `security/services/ai_platform/companion_*.py` | Persona, emotions, chat |
| `app/routers/companion*.py` | API routes |
| `Tests/test_companion*.py` | 49 pytest |

---

## 8. Правила для ML (обязательно)

1. **Прогресс** — только в [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md); не выдумывай %.
2. **Figma onboarding** `KvkUdyb5Ll31Z9FSzCbpNl` — **read-only**, не удалять.
3. **Prod** — no mock bypass: `.cursor/rules/prod-no-mock-bypass.mdc`.
4. **`[x]` на 11b/08b/07** — только после device/файлов/аудита, не «на словах».
5. **Коммиты** — только если пользователь просит; **push** — явно.
6. **HERO-3-02** = spec в `00_Spec`; **02b** = 36 frames — не смешивать.
7. Симулятор **iOS 15.x**: Rive **выключен** (краш Metal); QA Rive — **реальный iPhone**.

---

## 9. Сценарии «что открыть, если…»

| Ситуация | Открой |
|----------|--------|
| Нужен общий план спринта | [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md) |
| Рисовать в Figma | [COMPANION_FIGMA_STATUS.md](./COMPANION_FIGMA_STATUS.md) + [HEROES_3_PLAN](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) §5 |
| Export в Rive | [COMPANION_RIVE_EXPORT_CHECKLIST.md](./COMPANION_RIVE_EXPORT_CHECKLIST.md) |
| Падает CI / Xcode | [COMPANION_RIVE_UNBLOCK.md](./COMPANION_RIVE_UNBLOCK.md) |
| Тест на iPhone | [COMPANION_HERO3_11_QA_CHECKLIST.md](./COMPANION_HERO3_11_QA_CHECKLIST.md) |
| Деплой на VPS | [COMPANION_DEPLOY_P0.md](./COMPANION_DEPLOY_P0.md) + [ML_HANDOFF_2026-05-27](./COMPANION_ML_HANDOFF_2026-05-27.md) §SSH |
| Пользователь: «герой молчит» | Проверь toggle **Моё → Озвучивать**; mic = voice WS; текст = TTS build 210 |
| Пользователь: «кружки не герои» | Это **07** / **02b**, не баг layout |

---

## 10. Чеклист первого дня для новой ML

- [ ] Прочитал §0–§3 этого файла  
- [ ] Открыл [TRACKER](./COMPANION_PROGRESS_TRACKER.md) — понял **76/102** и открытые HERO-3 / Sprint 4  
- [ ] Прочитал [CODE_TODO](./COMPANION_CODE_TODO_TRACKER.md) — Sprints 0–3 ✅, Sprint 4 ⏳  
- [ ] Прогнал `pytest Tests/test_companion*.py` — ожидаю **49 passed**  
- [ ] Понял: **Sprint 4** (BE scale) + **07** (Rive) параллельно по роли  
- [ ] Не трогал onboarding Figma  

---

## 11. Связь с предыдущим handoff

| Документ | Статус |
|----------|--------|
| [COMPANION_ML_HANDOFF_2026-05-27.md](./COMPANION_ML_HANDOFF_2026-05-27.md) | Актуален для BE/SSH; цифры — сверять с TRACKER |
| [COMPANION_ML_HANDOFF_FULL.md](./COMPANION_ML_HANDOFF_FULL.md) | Архив, детали VPS |

**При расхождении цифр** — верь [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md).

---

*Конец handoff. Следующая ML: TRACKER → CODE_TODO Sprint 4 или HERO-3-07 по роли.*
