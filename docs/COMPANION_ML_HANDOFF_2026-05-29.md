# Companion — полный handoff для следующей ML-системы (2026-05-29)

> **Читать первым:** [COMPANION_ML_HANDOFF_START_HERE.md](./COMPANION_ML_HANDOFF_START_HERE.md) (карта документов).  
> **Этот файл:** всё сделанное, всё оставшееся, порядок работ, **стратегия «Rive в конце»**.  
> **Задачи без Rive:** [COMPANION_TASKS_WITHOUT_RIVE.md](./COMPANION_TASKS_WITHOUT_RIVE.md) — параллельная очередь.  
> **Трекер `[x]`:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) — единственный источник цифр **66/102**.

---

## 0. Решение команды: Rive = блокер, делаем в конце

| | |
|---|---|
| **Можно ли так?** | **Да.** iOS уже работает с **placeholder `.riv`** + **PNG bridge** (`CompanionHeroRasterView`). Чат, API, STT, TTS, навигация, бэкенд **не ждут** production Rive. |
| **Что откладываем** | Только задачи, где DoD = **качество анимации/мимики в `.riv`** или **GATE-EMO** с production art. |
| **Что делаем сейчас** | Build **214**, STT на iPhone, UX, P1+, бэкенд, диалоговый QA, XCUITest, локализация — см. [TASKS_WITHOUT_RIVE](./COMPANION_TASKS_WITHOUT_RIVE.md). |
| **Когда Rive** | После **подключения** Rive Editor / license / MCP — пакет **HERO-3-07** → **11c** → **GATE-EMO**. |

---

## 1. Продукт за 60 секунд

- **Что:** AI-компаньон для семьи — **3 героя** (Единорог / Аладдин-человек / Джин), чат + голос, trust, косметика, родительское согласие.
- **Вход:** Kids → Игры → **«Мир героев»** (`CompanionHomeScreen`: Главное / Герои / Моё).
- **Визуал целевой:** 2D **Rive**, герой ~**56%** экрана (`CompanionHeroLayout`), 12 эмоций + `mouth_open`.
- **Принцип:** компаньон — друг на **жизненные темы**; безопасность ALADDIN — по запросу, не единственная личность.
- **Не смешивать** с **AI Assistant** на Main — отдельные экраны; Settings: тумблер **«AI-помощник и 3 героя»** (P1-13f).

---

## 2. Репозитории и пути

| Что | Путь |
|-----|------|
| **iOS (работать здесь)** | `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` |
| **Git iOS** | отдельный репозиторий в этой папке, ветка **`master`** |
| **Backend (внутри iOS tree)** | `ALADDIN_iOS/security/` — routers, `companion_*`, deploy scripts |
| **`.riv` в бандле** | `Resources/Companion/{unicorn,aladdin,genie}.riv` |
| **PNG masters** | `docs/assets/*_360x480*.png` |
| **Figma** | https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM |
| **Prod API** | `https://aladdin-ai.ru` |
| **Build TestFlight** | **213** (`62c4a35f`); локально готовится **214** |

**Важно:** корневой `/Users/sergejhlystov/ALADDIN_NEW` может быть в другом git-состоянии — **Companion-работа только в nested `ALADDIN_iOS`.**

---

## 3. Прогресс (цифры на 29.05.2026)

| Блок | Готово | Всего |
|------|--------|-------|
| P0 MVP | 19 | 19 |
| P1 фичи | 11 | 11 |
| CX личность | 6 | 6 |
| OPS | 4 | 4 |
| HERO-3 | 24 | 26 |
| P1+ prod | 0 | 12 |
| P2 | 1 | 17 |
| P3 | 0 | 6 |
| Adult BE | 0 | 3 |
| **Спринт 102** | **66** | **102** |
| **iOS polish (вне 102)** | 10 | 12 |

---

## 4. Что уже сделано (не ломать)

### 4.1 Backend / OPS (закрыто)

- P0-01…19: JWT, policy, companion API, voice WS (MVP), capabilities, deploy, smoke.
- P1-01…11, CX P1-25…30, OPS-01…05.
- HERO-3 BE: `genie`, age_policy, persona 3 ветки, cosmetics, witty preset, humor.
- Скрипты: `deploy_companion_p0.sh`, `verify_companion_p0_prod.sh`, `companion_riv_size_gate.py`, CI `companion-gate.yml`.

### 4.2 iOS (закрыто)

- `CompanionHomeScreen`, Hub, Conversation, Mine, legal, consent, memory, cosmetics, analytics.
- `CompanionCapabilitiesService` + decode `CompanionFeatureUI` (iOS-POL-01).
- API cache/coalescing profile/state/legal + capabilities TTL (POL-03/04).
- Hybrid mic P1-13e, Settings P1-13f, TTS на текст P1-13c-text.
- Rive **инфра**: `CompanionHeroRiveHost`, SPM 6.20.5, **08b PASS** на device (placeholder).
- Emotion timeline, debounce 400ms, stream emotion при thinking (HERO-3-18…26).
- Commits: `e5e37cb7`, `62c4a35f` → build **213** в TestFlight.

### 4.3 Figma / art (закрыто для Rive-входа)

- **36/36** frames 360×480 (HERO-3-02b).
- PO lock: genie master = OB_03 headfix ([CANON](./COMPANION_HERO_ART_CANON.md)).
- `unicorn.riv` production partial **>25 KB** (158 KB); **aladdin/genie** — placeholder.

### 4.4 Локально (не в TestFlight — сделать build 214)

| Файл | Изменение |
|------|-----------|
| `Core/Audio/SpeechManager.swift` | finalize delay, session release |
| `Core/Audio/SpeechRecognitionErrorClassifier.swift` | Retry / user messages |
| `Screens/CompanionConversationScreen.swift` | min hold, STT errors |
| `Screens/ChildRewardsScreen.swift` | featured «Мир героев» ✨ |
| `Tests/UnitTests/SpeechPathTests.swift` | unit tests |

**Действие:** commit → bump `AppConfig` + `Info.plist` + `project.pbxproj` → **214** → push → TestFlight.

---

## 5. Блок Rive (делать ПОСЛЕ подключения) — не трогать первым

| ID | Задача | DoD | Инструкция |
|----|--------|-----|------------|
| **HERO-3-07** | Production `.riv` ×3 | каждый **>25 KB**, Hero360 full-cover | [5 STEPS](./COMPANION_RIVE_EDITOR_5_STEPS.md), [EXPORT](./COMPANION_RIVE_EXPORT_CHECKLIST.md) |
| | `aladdin.riv` | PNG: `docs/assets/aladdin_master_OB01_crop_360x480.png` | Export → `Resources/Companion/aladdin.riv` |
| | `genie.riv` | PNG: `docs/assets/onboarding_OB03_APP_360x480_FILL_headfix_v1.png` | Export → `Resources/Companion/genie.riv` |
| | `unicorn.riv` | уже production partial | при необходимости доработка в Editor |
| **HERO-3-11c** | MIMIC-Q1–6 повтор | после 07 | [11 QA](./COMPANION_HERO3_11_QA_CHECKLIST.md) |
| **HERO-3-11b** (часть) | MOTION-Q1–5, MIMIC-Q, **D10** лица | production art | только после 07 |
| **GATE-EMO** | 13 state + Rive + D10 | визуальная приёмка | после 07 + 11c |
| **P1-08 финал** | 3× production `.riv` | = 07 | |
| **P2-09** | Figma↔Rive pipeline | = HERO-3 | |
| **P2-17** | A/B humor_density | после HERO-3 | |
| **P1-19** (часть) | 3 скриншота Hub с **живым** Rive | marketing | после 07 |

**RiveMCP:** free trial **исчерпан** (3/3) — дальше **Rive Editor вручную** или license. См. [RIVE_CONNECT](./COMPANION_RIVE_CONNECT_NODE_MCP.md).

**После каждого export:**
```bash
python3 scripts/companion_riv_size_gate.py --dir Resources/Companion
./scripts/verify_companion_rive_ios_bundle.sh
```
Затем Xcode → iPhone smoke все 3 героя.

---

## 6. Порядок чтения документов (день 1)

| # | Файл | Зачем |
|---|------|-------|
| 1 | [START_HERE](./COMPANION_ML_HANDOFF_START_HERE.md) | Карта |
| 2 | **Этот файл** | Полный контекст + Rive defer |
| 3 | [TASKS_WITHOUT_RIVE](./COMPANION_TASKS_WITHOUT_RIVE.md) | Очередь работ **сейчас** |
| 4 | [TRACKER](./COMPANION_PROGRESS_TRACKER.md) | 102 задачи, `[x]` |
| 5 | [IMPLEMENTATION_TODOS](./COMPANION_IMPLEMENTATION_TODOS.md) | Детали P1-13, P1+ |
| 6 | [HERO_ART_CANON](./COMPANION_HERO_ART_CANON.md) | PNG пути |
| 7 | [UNIFIED_HOME_UX](./COMPANION_UNIFIED_HOME_UX.md) | Навигация UX-06…09 |

---

## 7. Ключевые файлы кода (iOS)

| Область | Файлы |
|---------|--------|
| Entry / Home | `Screens/CompanionHomeScreen.swift`, `ChildRewardsScreen.swift` |
| Chat | `Screens/CompanionConversationScreen.swift` |
| Hub | `Screens/CompanionHubScreen.swift`, `UI/Companion/CompanionHubHeroPreview.swift` |
| Hero / Rive | `UI/Companion/CompanionHeroRiveHost.swift`, `CompanionHeroRasterView.swift`, `CompanionHeroLayout.swift` |
| API | `Core/Services/CompanionAPIService.swift`, `CompanionCapabilitiesService.swift`, `CompanionModels.swift` |
| Stream | `Core/Network/CompanionStreamingService.swift` |
| Voice | `Core/Voice/CompanionVoiceSession.swift`, `Core/Audio/SpeechManager.swift` |
| TTS | `Core/Voice/CompanionSpeechOutput.swift` |
| Settings | `Screens/05_SettingsScreen.swift` |
| Build | `AppConfig.swift`, `Info.plist`, `ALADDIN.xcodeproj/project.pbxproj` |

## 8. Ключевые файлы (Backend)

| Область | Файлы |
|---------|--------|
| Voice WS | `security/api/routers/ai_voice_ws_router.py` |
| Companion chat | `security/api/routers/ai_companion_router.py` (и связанные services) |
| Persona / emotions | `security/services/ai_platform/companion_*` |
| Deploy | `scripts/deploy_companion_p0.sh`, `verify_companion_p0_prod.sh` |

**P1-13d:** WS сейчас принимает transcript на `audio.stop`; полный streaming raw audio — отдельная задача.

---

## 9. Голос и STT (важно для QA)

- **STT:** `SpeechManager` — общий для AI Assistant и Companion (`Consumer.companion`).
- На **device** для **ru-RU** часто идёт **облачное** распознавание Apple (не отдельная «интеграция Siri»).
- **Чеклист пользователя:** Settings → Privacy → Speech Recognition → ALADDIN; Siri (RU); Microphone; in-app «AI-помощник и 3 героя»; удержание микрофона **1–2 с**.
- **Android:** отдельного приложения в этом репо нет.

---

## 10. Продуктовые решения (не реализовывать без согласования)

- Не сливать Assistant и Companion в один чат.
- «Мир героев» — отдельный hub; на Child Rewards — крупная карточка (iOS-POL-12).
- Emoji → Figma/Rive для героев; SF Symbols для Main/Settings (фазы P1/P2).

---

## 11. Как ставить `[x]` в трекере

Галочка только если: **код + тест/скрипт + (для UI) device или TestFlight** подтверждены.  
Для Rive-задач — дополнительно gate scripts + визуал на iPhone.

---

## 12. История коммитов (последние)

| Commit | Содержание |
|--------|------------|
| `62c4a35f` | Build **213**, capabilities coalescing |
| `e5e37cb7` | Capabilities decode, API cache, hybrid mic, settings, analytics fix |
| `7ac456e2` | `CompanionHeroRasterView` access fix |

---

*Handoff №4 · 2026-05-29 · автор: сессия Cursor Companion*
