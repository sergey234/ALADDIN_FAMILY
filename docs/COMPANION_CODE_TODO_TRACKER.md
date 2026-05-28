# Companion — финальный трекер кода (v2)

> **План:** [COMPANION_CODE_PLAN_NO_RIVE.md](./COMPANION_CODE_PLAN_NO_RIVE.md) (v2)  
> **Главный план:** [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md)  
> **102 задачи (после QA):** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)  
> **Обновлено:** 2026-05-29 · **PO:** 3 героя (🦄🧑🧞) доступны **всем** пользователям

**Правило:** `[x]` = код в репо (+ pytest/unit где есть). iPhone/TestFlight — секция «Отложено».

---

## Сводка прогресса

| Спринт | Готово | Всего |
|--------|--------|-------|
| 0 — уже сделано | 3 | 3 |
| **1 — UX + герои + mic** | **17** | **17** |
| **2 — голос + l10n + offline** | **4** | **4** |
| 3 — prod hardening | 5 | 5 |
| 4 — BE масштаб | 0 | 6 |
| 5 — Grok parity | 0 | 14 |
| **Итого очередь** | **29** | **49** |

---

## Спринт 0 — уже в коде ✅

- [x] **POL-11 / P1-13g** — STT: finalize, Retry, min hold (build 214)
- [x] **POL-12** — карточка «Мир героев» на Child Rewards (**UX-10** polish ✅)
- [x] **UX-01…05** — CompanionHomeScreen, 3 вкладки, embedded режим

---

## Спринт 1 — UX, три героя, mic (~3–4 дня)

### A. Три героя для всех (копирайт = правда)

- [x] **UX-HERO-01** — Backend: **unicorn + aladdin + genie** в `allowed_characters` для **всех** age_band (PG контент сохраняем)
  - `age_policy.py`, capabilities, pytest `test_companion_age_policy` обновить
- [x] **UX-HERO-02** — iOS: Hub/Home показывают **3 карточки** всем; убрать хардкод «child = только unicorn»
  - `CompanionHomeScreen`, `CompanionHubScreen`, `CompanionCapabilitiesService`
- [x] **UX-HERO-03** — Voice WS: **genie** в `config` и `audio.stop` (сейчас только unicorn/aladdin)
  - `ai_voice_ws_router.py`

### B. Единый копирайт 🦄 🧑 🧞

- [x] **UX-10** — исправить **`companionWorldHeroCard`**: три героя в тексте **и** три emoji (🦄 🧑 🧞); без «ложного» обещания
  - `ChildRewardsScreen.swift`
- [x] **UX-10b** — проверить все строки Companion (Home, empty state, hub): **одинаковые три героя**; канон имён: Единорог · Аладдин · Джин
  - grep `companion` + `LocalizationManager`

### C. Входы (один push → Мир героев)

- [x] **UX-06** — **Big button «Друзья»** 🦄 в Child Interface (как игры в `bigButtonsGrid`), не отдельный tab bar
  - `08_ChildInterfaceScreen.swift`
- [x] **UX-07** — в **Единорог-питомец**: кнопка «Поговорить с единорогом» → `companionHome` + hero=unicorn
  - `UnicornPetView.swift`
- [x] **UX-08** — legacy `.companionHub` / `.companionConversation` → redirect на `companionHome`
  - `ALADDINApp.swift`, `NavigationManager.swift`
- [x] **UX DoD** — audit: Rewards ✅, Друзья, pet, legacy → только **`companionHome`**

### D. Микрофон понятный детям

- [x] **UX-11** — **Mic coach** при первом входе (3 шага: зажми → говори → отпусти); больше не показывать после прохождения
  - `CompanionConversationScreen` + `@AppStorage companion_mic_coach_seen`
- [x] **UX-12** — для **child**: упрощённый mic — **hold-only** или большая кнопка **«Говори»** на сцене; tap/swipe — для teen+
  - `CompanionConversationScreen.swift`
- [x] **UX-13** — если mic занят Assistant: **детское сообщение** («Сначала закрой другого помощника»), не технический текст
  - `CompanionConversationScreen.swift`

### E. Чище сцена героя

- [x] **UX-14** — для **child**: убрать текст «Доверие N» и длинный emotion label с overlay → в «Моё» или компактная иконка
  - `CompanionConversationScreen.swift` · `heroStatusOverlay`
- [ ] **UX-14b** — *(после Rive)* emotion на сцене = анимация/цвет, минимум текста

### F. Параллельно (не откладывать)

- [x] **P1-20a** — **RU+EN** для всех **новых** строк Sprint 1 (Друзья, coach, карточка, mic)
  - `LocalizationManager.swift` — **без хардкода** в Swift
- [x] **P1-17a** — VoiceOver + Dynamic Type: кнопка Друзья, coach, big mic, карточка Rewards

---

## Спринт 2 — голос, языки, offline (~3–5 дней)

- [x] **P1-13d** — Voice WS production polish (E2E STT→chat→TTS; доработки после UX-HERO-03)
- [x] **P1-20** — **полная** локализация Companion (Home, Mine, Conversation, Hub — весь хардкод RU)
- [x] **P1-17** — accessibility deep pass (stream, feedback, cosmetics)
- [x] **P1-21** — offline: последний thread + черновик сообщения

---

## Спринт 3 — prod hardening (~5–7 дней)

- [x] **P1-14** — XCUITest: Kids → Друзья → Companion → сообщение
  - `Tests/UITests/CompanionSmokeUITests.swift` + launch flags `-UITestCompanionSmoke`
- [x] **P1-18** — rate limit 429 + понятный текст в приложении
  - `CompanionErrorMapper.swift`, l10n `companion_error_*`, wiring в `CompanionConversationScreen`
- [x] **P1-22** — модерация после LLM
  - `companion_post_llm_moderation.py` + hook в `ai_companion_router.py`
- [x] **P1-16** — ADR hot path chat/stream
  - `docs/adr/ADR-P1-16-companion-hot-path.md`
- [x] **P1-19 (часть)** — App Store pack без Rive-скриншотов
  - `docs/COMPANION_APP_STORE_PACK_P1-19.md`

---

## Спринт 4 — backend масштаб (~1–2 недели)

- [ ] **P1-12** — Postgres + Redis
- [ ] **P2-02** — orchestrator + feature flag
- [ ] **P2-12** — API тем «О чём поговорим?» + chips iOS
- [ ] **P2-13** — social bridge (одиночество → написать близкому)
- [ ] **P2-15** — teen loneliness playbook
- [ ] **P2-16** — trust за эмпатию

---

## Спринт 5 — Grok parity (позже)

- [ ] **P2-01** — web search + citations
- [ ] **P2-03** — Fast / Reasoning / Think
- [ ] **P2-04** — фото и PDF
- [ ] **P2-05** — trust decay/streak
- [ ] **P2-06** — family context в промпте
- [ ] **P2-07** — Responses API + tools
- [ ] **P2-08** — COGS dashboard
- [ ] **P2-14** — Senior 60+ вход с Main
- [ ] **P3-01…04, P3-06, A-01…03** — см. [CODE_PLAN](./COMPANION_CODE_PLAN_NO_RIVE.md) §7

---

## Отложено — QA и Rive (не код)

- [ ] Push build **214** → TestFlight
- [ ] Device QA: STT, TTS (SPEECH-Q6), **11b**
- [ ] **UX-09** GATE навигации R6/R8
- [ ] **GATE-DIALOG** D01–D10 · **GATE-DIALOG-REGRESS** · **GATE-CX/P1/EMO**
- [ ] **HERO-3-07** production `.riv` ×3 · **UX-14b** финал overlay
- [ ] **P1-19** 3 скриншота Hub с живым Rive

---

## Порядок «с чего начать завтра»

```text
UX-HERO-01 (BE) → UX-HERO-02 (iOS) → UX-10 (карточка)
→ UX-06 (Друзья) → UX-07 (pet) → UX-08 (legacy)
→ UX-11 → UX-12 → UX-13 (mic)
→ P1-20a + P1-17a → Sprint 2–3 ✅
→ Sprint 4: P1-12 → P2-02 → P2-12/13/15/16
```

---

*Следующий пункт: **Sprint 4** — P1-12 (Postgres/Redis).*
