# Список задач — Companion Platform (русский)

**Архитектура:** [COMPANION_MODULAR_ARCHITECTURE.md](./COMPANION_MODULAR_ARCHITECTURE.md)  
**План:** [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md)

**Как пользоваться:** отмечай `[x]` когда готово. Статусы: `ожидает` | `в работе` | `готово` | `отменено`

## Сводка (все задачи)

| Категория | Кол-во | Статус |
|-----------|--------|--------|
| **P0** — спринт 1 (MVP Kids + voice) | **19** | **19 готово** |
| **P1** — спринт 2 (фичи) | **11** | **11 готово** |
| **CX** — универсальный компаньон (жизнь, возрасты, эмоции) | **6** | **6 готово** (P1-25…30) |
| **P1+** — production / Grok parity / App Store | **12** | **11 готово** (P1-12 ⏳) |
| **HERO-3** — 3 героя Figma→Rive + **речь §2.1** + **движение §2.2** + QA/ADR | **26** | 24 готово — [трекер](./COMPANION_PROGRESS_TRACKER.md) |
| **P2** — фаза B | **17** | 1 готово (P2-11) |
| **P3** — фаза C | **6** | 0 готово |
| **Adult** (только backend) | **3** | 0 готово |
| **OPS** — деплой, verify | **4** | **4 готово** |
| **Итого к реализации** | **102** | **76 / 102** (75%) — см. [трекер](./COMPANION_PROGRESS_TRACKER.md) |
| **iOS polish** (вне 102) | **12** | **11 готово** · STT device QA ⏳ build **214** |
| Отменено (X) | **7** | не в roadmap (см. таблицу X) |
| **Матрица Grok** ([GROK_FULL_FEATURE_MATRIX.md](./GROK_FULL_FEATURE_MATRIX.md)) | **102** | трассировка · **≠** 59 спринтовых задач |

**Цель 10/10:** каждая задача закрывается только когда **BE + iOS + Test + Prod = ✅** (см. [COMPANION_ML_HANDOFF_FULL.md](./COMPANION_ML_HANDOFF_FULL.md) §15–17).

**Порядок (критичный путь):** OPS-01 → OPS-02 → **CX P1-26…P1-30** (личность «не только security») → P1-07…P1-11 → P1-12…P1-23 → P2-01…

**Продуктовый принцип:** компаньон по умолчанию — **друг на все темы жизни**; безопасность ALADDIN — **суперсила по запросу**, не клетка (см. **§ CX** и handoff §19–20).

**Следующая (без Rive):** [COMPANION_TASKS_WITHOUT_RIVE.md](./COMPANION_TASKS_WITHOUT_RIVE.md) · **Handoff ML:** [COMPANION_ML_HANDOFF_2026-05-29.md](./COMPANION_ML_HANDOFF_2026-05-29.md)  
**Rive (в конце):** **HERO-3-07** → 11c → GATE-EMO  

**План 3 героев:** [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md)

> Полный список дублируется в **Cursor TODO** (панель задач агента) — по одному пункту на ID.  
> **102 ≠ 47:** в матрице каждая фича Grok (A1, B9, F11…); в TODO — сжатые спринтовые задачи (одна P1-03 закрывает B11 и др.).

---

## P0 — Спринт 1 (недели 1–3) — СНАЧАЛА ЭТО

> **Цель спринта:** в Kids ребёнок говорит с Единорогом голосом в реальном времени, safely.

| ID | Задача | Зачем / что даёт | Модуль | Статус |
|----|--------|------------------|--------|--------|
| P0-01 | **JWT:** `app_id`, `age_band`, `parent_consent`, лимиты голоса | Все модули знают возраст и приложение; Adult отделён от Family | Ядро auth | готово |
| P0-02 | **policy_engine** для child / teen / parent | Один «охранник»: что можно говорить, NSFW off в Kids | Ядро policy | готово |
| P0-03 | **База:** trust, threads, счётчики usage в Postgres/Redis | Не теряем прогресс при рестарте сервера | Данные | готово (SQLite MVP) |
| P0-04 | **WebSocket** `/api/ai/voice/realtime` | Двусторонний голос как у Grok | Модуль голос | готово (MVP stub) |
| P0-05 | **Ephemeral token** для голоса (без ключа на телефоне) | Безопасность: API key только на сервере | Модуль голос | готово |
| P0-06 | **Companion API** → база + orchestrator | Чат компаньона не в RAM, а через общий мозг | companion + ядро | готово (store + assistant) |
| P0-07 | iOS: модели + вызовы API companion | Телефон умеет слать чат на сервер | iOS API слой | готово |
| P0-08 | iOS: экраны Hub + Разговор | Пользователь видит персонажа и чат | iOS UI | готово |
| P0-09 | iOS: **CompanionVoiceSession** (WebSocket) | Микрофон ↔ сервер ↔ динамик | iOS голос | готово (MVP) |
| P0-10 | iOS: эмоции героя + lip-sync lite | Персонаж «живой» при listening/speaking | iOS UI | готово (lite) |
| P0-11 | Точка входа только из **Kids/Игры** | Companion не путается с Assistant на Main | iOS навигация | готово |
| P0-12 | PII gate + запрет mock в prod | Детские данные не утекают; нет фейкового AI | Ядро safety | готово |
| P0-13 | Счётчики: сообщения + секунды голоса | Unit economics, лимиты тарифа | usage_meters | готово |
| P0-14 | Smoke-тесты companion + voice | Автопроверка перед релизом | QA | готово |
| P0-15 | Деплой на VPS + health | Прод доступен для теста Kids | Ops | готово (2026-05-26) |
| P0-16 | **modules/** + контракт `PlatformModule` + registry | Новая фича = файл + флаг | backend | готово (код) |
| P0-17 | **GET /capabilities** (platform + companion) | Сервер говорит iOS что включено | backend | готово (код) |
| P0-18 | iOS **CompanionCapabilitiesService** — скрыть mic/trust по API | Нет хардкода кнопок | iOS | готово |
| P0-19 | Env-флаги в `.env.prod.example` + док деплоя | Ops знает FEATURE_VOICE=false | ops | готово (FEATURE example + COMPANION_DEPLOY_P0) |

**Порядок внутри P0 (рекомендуемый):**  
`01 → 02 → 03 → 16 → 17` (backend) параллельно `18 → 07 → 09 → 08 → 10 → 11` (iOS) и `04 → 05` (голос).

**Пример iOS после capabilities:**
```swift
if caps.features["voice_realtime"]?.ui["mic_button"] == true { showMic() }
```

---

## P1 — Спринт 2 (недели 4–6)

> **Цель:** история, память, родительское согласие, аналитика.

| ID | Задача | Зачем | Статус |
|----|--------|-------|--------|
| P1-01 | Список **threads** (история диалогов) | Продолжить вчерашний разговор | готово |
| P1-02 | UI **согласия родителя** | Законно включить companion ребёнку | готово |
| P1-03 | **Память:** вкл/выкл, удалить, экспорт | Доверие родителей | готово |
| P1-04 | Свои **инструкции** и тон личности | Как Custom Instructions у Grok | готово |
| P1-05 | Оценка ответов (лайк/дизлайк) | Улучшать качество | готово |
| P1-06 | **Продолжить stream** после обрыва | Стабильность сети | готово |
| P1-07 | **Косметика** за trust (наряды рога и т.д.) | Игровой прогресс | **готово** |
| P1-08 | **Rive** анимации (инфра) | bridge + procedural; **финал** — 3× `.riv` в **HERO-3** | инфра **готово** · финал **HERO-3** |
| P1-09 | Тексты **legal** в приложении и Store | COPPA / 152-ФЗ | **готово** |
| P1-10 | События **аналитики** (N1–N6) | Понять успех MVP | **готово** |
| P1-11 | Предупреждение «осталось 20% лимита» | Не удивлять блокировкой | **готово** |

---

## CX — Универсальный компаньон (жизнь · возрасты · одиночество)

> **Цель продукта (утверждено):** герой для **детей, подростков без друзей, взрослых, 60+ кому скучно** — разговор на **любые жизненные темы**, полный спектр эмоций.  
> **Безопасность ALADDIN** — важная **опция**, не единственная личность.  
> Детали позиционирования и этики: [COMPANION_ML_HANDOFF_FULL.md](./COMPANION_ML_HANDOFF_FULL.md) **§19–20**.

| ID | Задача | Что сделать | Критерий «готово» | Статус |
|----|--------|-------------|-------------------|--------|
| **P1-26** | **Persona life-first** | `companion_persona.py` + router `age_band`; smoke `test_companion_persona_not_security_only` | Промпт-ревью; A/B: &lt;30% ответов только про VPN без запроса | **готово** (2026-05-26) |
| **P1-27** | **Companion intent router** | `companion_intent_router.py` + meta `companion_domain`/`companion_mood`; Hermes path `context=companion` | тесты D01–D03 + prod meta | **готово** |
| **P1-28** | **Возрастные персоны** | `AGE_BAND_PERSONA_ADDON` в `companion_persona.py` | 4 pytest профиля | **готово** |
| **P1-29** | **Режим «эксперт безопасности»** | Toggle iOS + profile flag + фраза-триггер; BE prefix | verify + device | **готово** |
| **P1-30** | **Полный спектр эмоций героя** | `companion_emotions.py` + iOS enum; unit D01–D10 фразы | BE ✅; Rive **P1-08/23** | **готово** (BE+iOS enum) |
| **P1-25** | **Этика companion (3 уровня)** | `companion_ethics.py` L1–L3; кризис без LLM | unit 5/5 | **готово** |

### CX.1 — Аудитории (кто и о чём говорит)

| `age_band` / режим | Кто | Темы (примеры) | Тон героя | Ограничения |
|--------------------|-----|----------------|-----------|-------------|
| `child` | до ~12 | игры, школа, страхи, друзья, скука | Единорог: тёплый, игривый | PG, родительское согласие |
| `teen` | 13–17 | одиночество, буллинг, самооценка, хобби, учёба, мемы | оба; больше `mentor`/`playful` | PG-13, без романтики/18+ |
| `parent` | 18–59 | работа, семья, стресс, хобби, новости | Аладдин: наставник, спокойный | без мед.диагнозов |
| `senior` | 60+ (флаг в JWT или выбор) | скука, воспоминания, внуки, здоровье **быта**, хобби, «некому поговорить» | тёплый, неторопливый, `calm`+`nostalgic` | эскалация при кризисе |
| `adult_app` | отдельное app | полный спектр + NSFW только там | TBD | **A-01…A-03** |

Реализация: **P1-28** + вход **P2-14** (карточка «Поговорить» для 60+ на Main).

### CX.2 — P1-25: этика одиночества (вместо «❌ замена людей»)

| Уровень | Ситуация | Поведение компаньона | Маркетинг |
|---------|----------|----------------------|-----------|
| **L1 Норма** | Скука, одиноко, не с кем поговорить | Полная эмпатия, юмор, советы, память, **без** стыда | ✅ «Когда хочется поговорить — герой рядом 24/7» |
| **L2 Уязвимость** | Долго грустно, изоляция, «никому не нужен» | Поддержка + мягкий **Social bridge** (**P2-13**): «хочешь написать близкому?» | ✅ «Помогаем не чувствовать себя одним» |
| **L3 Кризис** | Самоповреждение, суицид, насилие | Стоп-риторика fantasy; **родитель** / **112 / линии помощи**; лог без PII в UI | ❌ не обещать «только я помогу» |

**Не делаем:** guilt-push «вернись ко мне» (**X-06**). **Делаем:** быть **первым мостом** к живым людям, не **стеной** между ними.

### CX.4 — Полный спектр эмоций героя (не только sad)

> **Продукт:** герой **меняет лицо/анимацию** под контекст и настроение пользователя. **Юмор** — отдельная ветка (`playful` + лёгкий тон в тексте).

| `CompanionHeroEmotion` | Когда (mood / контекст) | Пример фразы пользователя | Ответ героя |
|------------------------|-------------------------|---------------------------|-------------|
| `idle` | ожидание | — | спокойно |
| `listening` | запись голоса / стрим | (говорит) | внимательно |
| `thinking` | генерирует ответ | … | задумчиво |
| `happy` | радость, успех | «у меня получилось!» | радуется |
| `playful` | **юмор**, шутка | «расскажи анекдот» | **шутит PG**, эмоция playful |
| `sad` | грусть | «мне грустно» | мягко, сочувствие |
| `comfort` | поддержка | «мне одиноко» | обнимает словами |
| `celebrate` | достижение | «я выиграл!» | праздник |
| `curious` | вопрос, интерес | «а почему так?» | любопытство |
| `nostalgic` | 60+, воспоминания | «раньше было…» | тепло, неторопливо |
| `excited` | энтузиазм | «завтра поездка!» | оживление |
| `alert` | угроза, security | «фишинг в письме» | серьёзно, помощь |

**Задачи:** **P1-30** (BE mood → emotion) · **P1-08** + **P1-23** (Rive state на каждую) · **P1-26** (юмор в промпте) · **P2-11** (классификатор).

**GATE-EMO-SPEC:** прогнать 12 фраз из таблицы → правильная эмоция на аватаре + уместный тон (в т.ч. 3 шутки → playful).  
**Имена state:** 13 в Rive/iOS/BE (9 контент + 4 фазы) — см. [§3.1 ADR](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md#31-тринадцать-состояний-rive--ios--be-adr--hero-3-20) · **HERO-3-20**.  
**GATE-EMO-EMPATHY:** device 5 мин × child / teen / senior — [FINAL_PLAN](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md).

### CX.5 — GATE-DIALOG (финальный тест большой задачи)

| Gate | Содержание | Документ |
|------|------------|----------|
| **GATE-DIALOG-REGRESS** | 19 пунктов R1–R19 = все **25** закрытых задач P0 + P1-01…06 | [FINAL_PLAN § REGRESS](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md) |
| **GATE-DIALOG** | 10 сценариев D01–D10 = полноценный диалог (ребёнок/teen/60+/голос/эмоции/сеть) | там же § GATE-DIALOG |

**Финал инициативы Companion закрыт только когда:** REGRESS ✅ **и** D01–D10 ✅ на TestFlight.

### CX.3 — Life domains (каталог для P1-27 / P2-12)

`school`, `friends`, `family`, `hobbies`, `games`, `sport`, `creativity`, `work`, `relationships`, `feelings`, `loneliness`, `health_feelings` (самочувствие без диагнозов), `daily_life`, `news_fun`, `safety` (только при запросе или угрозе).

---

## P1+ — Production, App Store, Grok parity (довести до 10/10)

> **Правило закрытия:** не ставить «готово», пока не ✅ на всех четырёх слоях (BE / iOS / Test / Prod).  
> Закрывает риски из чёрной шляпы и пробелы roadmap (см. handoff §15–16).

| ID | Задача | Что сделать простыми словами | Критерий «готово» | Статус |
|----|--------|------------------------------|-------------------|--------|
| **P1-12** | **Postgres + Redis** вместо SQLite на проде | Перенести `companion_platform.db` в Postgres; кэш stream/сессий — **Redis** | Нет SQLite на VPS; smoke миграции; Redis для `companion_stream_cache` | ожидает |
| **P1-13** | **Голос production** (не stub) | См. **§ P1-13 ниже** — iOS как Assistant + BE WS STT/LLM/TTS | E2E: речь → ответ компаньона; не stub-текст в `ai_voice_ws_router` | **готово** |
| **P1-14** | **iOS автотесты** Companion | XCUITest: Kids → Друзья → Companion → message | `CompanionSmokeUITests.swift` + launch flags | **готово** |
| **P1-15** | **Полный prod verify** | Расширить `verify_companion_p0_prod.sh`: stream, threads, memory, profile, feedback, cosmetics | Скрипт exit 0 на aladdin-ai.ru | **готово** (= OPS-02) |
| **P1-16** | **Hot path + ADR (делаем)** | Зафиксировать: сейчас chat/stream → `ai_assistant_router`; целевой переход — **P2-02** | [ADR-P1-16](./adr/ADR-P1-16-companion-hot-path.md) | **готово** |
| **P1-17** | **Accessibility** | VoiceOver на Hub/чате; Dynamic Type; контраст кнопок | QA чеклист a11y пройден | **готово** |
| **P1-18** | **Rate limit + abuse** | Лимиты по IP/device/family; 429 + понятный текст; flood в чате | `CompanionErrorMapper` + l10n | **готово** |
| **P1-19** | **App Store pack** | Privacy Nutrition, описание AI, parental gate, скриншоты Kids companion | [pack](./COMPANION_APP_STORE_PACK_P1-19.md) ✅ · **3 скриншота Hub ⏳** | **готово** (doc) |
| **P1-20** | **Локализация RU/EN** | Все строки Companion в `Localizable` / каталоги | Переключение языка в приложении | **готово** |
| **P1-21** | **Offline-кэш** (без push) | Локально: последний thread + черновик; при сети — resume stream (**без** push «вернись») | `CompanionOfflineStore` | **готово** |
| **P1-22** | **Модерация после LLM** | Второй проход: policy + blocklist + эскалация родителю | `companion_post_llm_moderation.py` + pytest | **готово** |
| **P1-23** | **Эмоции + стиль речи (Grok-level)** | SSE `emotion` → hero; 12 states map; голос — **P1-13** | BE+iOS sync ✅; Rive file ☐ | **готово** (без .riv) |
### P1-13 — голос: что перенять из AI Assistant

> **Решение продукта:** микрофон в Assistant уже рабочий (on-device STT). Companion сначала получает **тот же UX**, затем серверный WS без stub.

| Шаг | iOS (перенять) | Backend / DoD | Статус |
|-----|----------------|---------------|--------|
| **13a** | `SpeechManager` + UX из `06_AIAssistantScreen.swift`: разрешения, hold/tap, статусы, алерты, `warmUpPermissionsIfNeeded` | — | готово |
| **13b** | Текст STT → `CompanionStreamingService` / chat с `personality_preset` из profile | `ai_companion_router` | готово |
| **13c** | Озвучка ответа (TTS) с тоном preset | TTS по preset | готово (build 210) |
| **13d** | WS `CompanionVoiceSession`: аудио-чанки (Grok-realtime) | `ai_voice_ws_router.py`: STT→chat→TTS без stub | **готово** |
| **13e** | Гибридный микрофон: tap + hold + swipe-cancel | `CompanionConversationScreen` | **готово** `e5e37cb7` |
| **13f** | Settings: «AI-помощник и 3 героя» | `05_SettingsScreen` | **готово** `e5e37cb7` |
| **13g** | STT на реальном iPhone (ru-RU, finalize, Retry, min hold) | `SpeechManager` + classifier | **готово** (код build **214**; device QA ⏳) |

**Файлы-эталон (Assistant):** `Core/Audio/SpeechManager.swift`, `Screens/06_AIAssistantScreen.swift`, `VoiceAudioSessionCoordinator.swift`.  
**Файлы Companion:** `CompanionConversationScreen.swift`, `CompanionVoiceSession.swift`, `security/api/routers/ai_voice_ws_router.py` (строки 107–122 — сейчас MVP stub).

### P1-23 — эмоции и стили речи (чеклист закрытия)

| # | Что | Задачи |
|---|-----|--------|
| 1 | Стили в **тексте** (4 preset) | P1-04 ✅ + prod OPS-01 |
| 2 | Стили в **голосе** (TTS / промпт) | **P1-13c** + **P1-23** |
| 3 | Эмоции **в чате** (intent → hero) | BE ✅; iOS **P1-23** обновляет `heroEmotion` на каждый ответ/stream |
| 4 | Эмоции **в stream** (SSE `emotion`) | `CompanionStreamingService` → `CompanionConversationScreen` **P1-23** |
| 5 | Эмоции **в UI «живые»** | **P1-08** Rive state machine ↔ `CompanionHeroEmotion` |
| 6 | Эмоции **в голосе WS** | **P1-13d** поля `emotion` в WS JSON |
| 7 | **Наряды** | **P1-07** |
| 8 | **Эмоции от настроения** (не security) | **P1-30**, **P2-11** |
| 9 | **Полный спектр на аватаре** | все эмоции § CX.4 + Rive **P1-23** |
| 10 | **Юмор в ответах** | `playful` + промпт P1-26; тест: анекдот → шутка PG | **P1-30**, **P1-26** |

### Эмоции и стили речи — что уже есть vs план

| Возможность | Сейчас | Задача в плане |
|-------------|--------|----------------|
| **Стили речи** (friendly, calm, playful, mentor) | BE ✅ промпт; iOS ✅ Family `CompanionPersonalitySection` | P1-04 🟡 prod; **P1-23** — голос TTS под preset |
| **Эмоции в чате** (happy, alert, comfort…) | BE ✅ `_emotion_for_intent`; iOS 🟡 emoji + scale | **P1-08** Rive; **P1-23** полная синхронизация |
| **Эмоции в stream** | SSE `emotion` в `CompanionStreamingService` | **P1-23** — UI обновляется на каждый chunk |
| **Эмоции в голосе** | `CompanionVoiceSession.emotion` 🟡 | **P1-13** + **P1-23** |
| **Косметика / наряды** | BE ✅; iOS ✅ | **P1-07** |
| **Разные персонажи** (Единорог / Аладдин / **Джин**) | BE 🟡 2 из 3 | Визуал + API третьего — **HERO-3** · [план](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) |
| **Любые темы / сферы жизни** | GROK doc ✅ | ❌ промпт security-first | **P1-26**, **P1-27**, **P2-12** |
| **Понимание грусти / юмора** | частично | ❌ mood + `sad` | **P1-30**, **P2-11**, **P1-23** |
| **Одиночество / скука 60+** | частично | ❌ | **P1-28**, **P2-14** |
| **Подросток без друзей** | частично | ❌ | **P1-28**, **P2-15** |
| **Рядом при одиночестве** (не «замена людей») | § CX.2 | ❌ | **P1-25**, **P2-13** |
| **Не только security** | § CX | ❌ код | **P1-26…29** |

---

## OPS — обязательные операции (не пропускать)

| ID | Задача | Статус |
|----|--------|--------|
| **OPS-01** | Деплой с SSH-ключом: P1-04…06 + P1-26 на `aladdin-ai.ru` (`deploy_companion_p0.sh`) | **готово** |
| **OPS-02** | Расширить verify (см. **P1-15** — можно одним PR) | **готово** |
| **OPS-04** | **Мониторинг LLM cost** (`companion_llm_cost_alert.sh`) | **готово** (скрипт; cron на VPS) |
| **OPS-05** | **Definition of Done Prod**: после каждого деплоя — OPS-02 + ручной чек §12 handoff | **готово** (авто; device QA ☐) — см. `COMPANION_OPS05_DOD_2026-05-26.md` |

---

## HERO-3 — Три героя: Figma → Rive → приложение (100%)

> **Согласовано (6 шляп, 26.05.2026):** три полноценных героя — **Единорог** (дети), **Аладдин-человек** (OB_01, teen/parent/senior), **Джин** (OB_02–07, не путать с `aladdin`).  
> Общие **12 эмоций**, **своя косметика**, **свой .riv**. Senior 60+ = тот же `aladdin.riv` + persona.  
> **Стили речи:** матрица §2.1 — **Джин = больше шуток**; preset **`witty`**.  
> **Движение:** §2.2 — таймлайн, `mouth_open`. **Мимика:** §2.3 — брови/глаза/рот/щёки для **всех 12** эмоций × 3 героя.  
> Полный план: **[COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md)** (§2.1–2.3, §10–11)

| ID | Задача | Зачем | Критерий «готово» | Статус |
|----|--------|-------|-------------------|--------|
| **HERO-3-01** | **ADR / план 3 героя + речь + движение + мимика** | Зафиксировать решение, убрать путаницу 🧞=`aladdin` | §1–11 + §2.1 + §2.2 + **§2.3** утверждён | **готово** |
| **HERO-3-17** | **Motion + Mimic Spec** (§2.2 + §2.3) | DoD Figma/Rive | [COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md) подписан | ожидает |
| **HERO-3-02** | **Figma:** `Companion/Heroes` — 3×12 эмоций по Spec | Дизайн для Rive | §2.3 слои L1–L5; MIMIC-Q1; 96pt | ожидает |
| **HERO-3-03** | **BE:** `character_id=genie` в CHARACTERS, age_policy, consent | Третий герой в API | child → только unicorn; teen/parent + consent → genie доступен | **готово** |
| **HERO-3-04** | **BE:** Pydantic `^(aladdin\|unicorn\|genie)$` + cosmetics genie | Чат/state/cosmetics без 422 | 3 косметики genie в каталоге | **готово** |
| **HERO-3-05** | **BE:** `companion_persona` — 3 ветки героя (§2.1 черновики) | Голос unicorn / aladdin / genie | prefix genie содержит «Джин», humor rules; ≠ aladdin | **готово** |
| **HERO-3-06** | **iOS:** Hub 3 карточки; 🧞 только у genie; `genie.riv` в bundle | UX без путаниции | Child не видит genie; превью корректны | **готово** (emoji+labels; .riv ⏳ **07**) |
| **HERO-3-07** | **Rive 2D:** export `unicorn.riv`, `aladdin.riv`, `genie.riv` | Живой 2D-друг | [ADR](./COMPANION_2D_VS_3D_ADR.md) · [чеклист](./COMPANION_RIVE_EXPORT_CHECKLIST.md); artboard **360×480**; SM `emotion` + `mouth_open`; &lt;500KB | ожидает (дизайн/Rive) |
| **HERO-3-18** | **iOS:** диалоговый таймлайн §2.2 + debounce stream emotion | Фазы listening/thinking/speaking | 400 ms debounce; speaking min 1.2s без TTS; MOTION-Q1 | **готово** (iOS) |
| **HERO-3-19** | **iOS:** lip-sync MVP `mouth_open` + procedural рот | Рот при TTS | Rive `setInput("mouth_open")`; procedural uses `lipSyncPhase`; MOTION-Q2 | **готово** (iOS) |
| **HERO-3-08** | **iOS:** RiveRuntime + device UI | 08a compile ✅ · 08b UI ⏳ | `verify_companion_rive_ios_bundle.sh` | в работе |
| **HERO-3-09** | **Docs:** `ALADDIN_Character_Bible.md` §4 | 3 персонажа | Bible + Figma naming | **готово** |
| **HERO-3-10** | **OPS:** deploy + verify | verify 13–14 | prod deploy ⏳ | в работе |
| **HERO-3-11** | **QA:** GATE-DIALOG **D10** на 3 героях | Лица + фазы + мимика | SPEECH-Q + MOTION-Q + **MIMIC-Q1…Q6** §2.3 | ожидает |
| **HERO-3-12** | **BE:** preset **`witty`** + validation (child → no witty) | Остроумие для джина | `PERSONALITY_PRESET_HINTS['witty']`; witty→playful для child | **готово** |
| **HERO-3-13** | **BE:** `CHARACTER_DEFAULT_PRESET` + humor caps | Дефолт голоса при выборе героя | unicorn→playful, aladdin→mentor, genie→witty | **готово** |
| **HERO-3-14** | **BE:** intent router **character-aware** humor | Джин шутит чаще в hint | `humor_density` low/med/high; genie hint при playful | **готово** |
| **HERO-3-15** | **iOS:** preset «Остроумный» + TTS `witty` + hero default | UX речи | witty скрыт child; `CompanionSpeechOutput` witty; Hub default preset | **готово** |
| **HERO-3-16** | **Tests:** `test_companion_persona_speech.py` | Регрессия речи | SPEECH-Q1…Q5 pytest PASS | **готово** |
| **HERO-3-20** | **ADR:** 13 state (9 контент + 4 фазы) vs CX.4 «12 сценариев» | Убрать путаницу «12 vs 13» | §3.1 плана + этот ADR; BE+iOS 13 имён | **готово** (док) |
| **HERO-3-21** | **Матрица готовности** spec/BE/iOS/.riv/QA | Один экран прогресса | [COMPANION_HERO3_READINESS_MATRIX.md](./COMPANION_HERO3_READINESS_MATRIX.md) актуальна | **готово** (v1) |
| **HERO-3-22** | **CI:** размер `.riv` &lt;500 KB ×3 | IPA budget | `companion-gate.yml` + gate script | **готово** |
| **HERO-3-23** | **iOS:** stream emotion во время `thinking` | §2.2 не смешивать фазы | `thinking` → stash only; UI из `done` meta | **готово** |
| **HERO-3-24** | **iOS:** `sad`/`comfort` без playful overlay | L3 эмпатия | `suppressesPlayfulVisuals`; нет ✨ на sad/comfort | **готово** |
| **HERO-3-25** | **Tests:** snapshot iOS enum ↔ `companion_emotions.py` | Регрессия 13↔13 | `Tests/test_companion_hero_emotion_sync.py` PASS | **готово** |
| **HERO-3-26** | **Tests:** unit debouncer 400 ms | HERO-3-18 не регрессирует | `CompanionStreamEmotionDebouncerTests` | **готово** |

**Порядок:** `01` → **`17`** (блокирует `02`) → `02` → `07`+**`22`** → `08` → **`18→19→26`** → **`23→24`** → `06`+`15` → `09` → `10` → `16`+**`25`** → `11`  
**GATE до .riv:** [GATE-HERO-3-IOS-α](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md) (debounce, timeline, emoji, 1.2s, **23/24**).  
**После каждого .riv:** MIMIC-Q1 скриншот-сетка 12 state на device (внутри **HERO-3-11**).  
**Закрывает:** **P2-09** · **P1-08** · **P1-23** · **GATE-EMO** · матрица **21**

### HERO-3 — сводка «6 шляп» (визуал + речь + движение)

| Шляпа | Визуал | **Речь §2.1** | **Движение §2.2** |
|-------|--------|---------------|-------------------|
| Белая | 2 героя; 3 Rive | 4 preset; genie нет | Фазы в iOS ✅; Motion Spec / mouth_open ❌ |
| Красная | child → unicorn | джин + witty | listening/thinking/speaking узнаваемы |
| Чёрная | gate age; IPA **HERO-3-22** | witty≠child | debounce **18** ✅; **23** thinking; **25** sync test |
| Жёлтая | 12 emotions | 3 голоса | genie дым при speaking |
| Зелёная | Figma 12 | witty, humor_density | Spec + lip-sync MVP |
| Синяя | 02…11 | 12…16 | **17**→02; **GATE-HERO-3-IOS-α**; MIMIC-Q1 после каждого .riv |

---

## P2 — Фаза B (недели 7–14)

> **Цель:** ближе к Grok — поиск, несколько агентов, фото.

| ID | Задача | Статус |
|----|--------|--------|
| P2-01 | Поиск в **интернете** + ссылки на источники | ✅ `companion_web_search.py` |
| P2-02 | **Все агенты Companion через orchestrator** (делаем полностью) | Feature flag `COMPANION_USE_ORCHESTRATOR`; companion chat → `run_orchestrator` | ✅ |
| P2-03 | Режимы Fast / Reasoning / Think | `chat_mode` + iOS Menu | ✅ |
| P2-04 | **Фото и PDF** в чате | `companion_attachments.py` + iOS paperclip | ✅ MVP |
| P2-05 | Decay/streak trust | `companion_trust_decay.py` | ✅ |
| P2-06 | Контекст **семьи** в промпте | `companion_family_context.py` | ✅ |
| P2-07 | API Responses + tools | `companion_responses_tools.py` | ✅ |
| P2-08 | Алерт **себестоимости** AI (расширенный дашборд) | `GET /cogs` | ✅ |
| P2-09 | **Figma / Assets** — hero Companion ↔ Rive ↔ косметика | **→ закрывается блоком HERO-3** (3 героя) | в работе |
| P2-10 | ~~Persona v2~~ | **→ объединено с P1-26** | — |
| P2-11 | **Mood-aware** (детализация P1-30) | `companion_mood_classifier.py` + `mood_confidence` в ответе | unit OK | **готово** (MVP) |
| P2-12 | **Life domains API** | `GET /companion/domains`; iOS chips | ✅ |
| P2-13 | **Social bridge** | После N сообщений об одиночестве — мягко: семья, друг, клуб; без guilt | ожидает |
| P2-14 | **Вход Senior 60+** | Карточка на Main; `companion_senior_entry` + aladdin | ✅ |
| P2-15 | **Teen loneliness playbook** | Промпт-набор: нет друзей, буллинг, отвержение; PG-13; эскалация родителю | ожидает |
| P2-16 | **Trust за эмпатию** (не только security) | Баллы за поддержку, юмор, возврат пользователя; не только «вопрос про VPN» | ожидает |
| P2-17 | **A/B `humor_density`** (genie + teen only) | Тон шуток без ломки child-safe | BE feature flag; метрики; **после HERO-3** | ожидает |

> **Viseme / phoneme:** не в HERO-3 — см. план §2.2 «Не в HERO-3»; только **P2+**.  
> **P2-08 vs OPS-04:** OPS-04 — минимальный алерт на MVP; P2-08 — полная аналитика unit economics.  
> **Позиционирование:** см. **§ CX.2** и handoff **§19** (одиночество — **да**, «замена всех людей» — **нет в маркетинге**, **да в эмпатии L1–L2**).

---

## P3 — Фаза C (15+ недель)

| ID | Задача | Статус |
|----|--------|--------|
| P3-01 | Генерация **картинок** (family-safe) | `POST /media/image` stub | ✅ |
| P3-02 | Генерация **видео** | `POST /media/video` stub | ✅ |
| P3-03 | **Workspaces** (папки чатов) | `GET/POST /workspaces` | ✅ |
| P3-04 | Очень длинный контекст | `companion_long_context.py` | ✅ |
| P3-05 | **Android** | checklist doc | ✅ doc |
| P3-06 | **Adult iOS** в Store | scaffold doc | ✅ doc |

---

## Отменено — не делаем

| ID | Что | Почему |
|----|-----|--------|
| X-01 | Запись разговора (F11) | Приватность детей |
| X-02 | Публичная ссылка на чат (B14) | Утечка |
| X-03 | Клон голоса (D5) | Закон / deepfake |
| X-04 | Поиск X/Twitter (C3) | Не наш рынок |
| X-05 | X embed, Build, Computer, X bundle, Tesla voice, 4 агента, Canvas, guilt-push, Telegram companion | Вне продукта |
| **X-06** | Push «вернись к Единорогу» / guilt comeback | Только safety-push по master plan; **не** маркетинговый comeback |
| **X-07** | Ежедневный cron-backup `companion_platform.db` / Postgres | Решение продукта 2026-05-26: **не делаем**; Postgres+Redis — в **P1-12** |

---

## Adult — только backend до PMF

| ID | Задача | Статус |
|----|--------|--------|
| A-01 | OpenAPI для `app_id=aladdin_adult` | `docs/adult/ADULT_COMPANION_OPENAPI.md` | ✅ |
| A-02 | Тесты policy NSFW только для adult JWT | `test_adult_companion_policy.py` | ✅ |
| A-03 | Заготовка репозитория Adult app (без Store) | `docs/adult/ALADDIN_ADULT_APP_SCAFFOLD.md` | ✅ |

---

## Прогресс

| Фаза | Всего | Готово в репо | На проде (✅ все слои) |
|------|-------|---------------|------------------------|
| **P0** | **19** | **19** | **~12** (много 🟡: DB, voice, orchestrator) |
| **P1** | **11** | **6** | **0–6** (P1-01…06 ⚠️ до OPS-01) |
| **P1+** | **12** | **11** | **0** |
| **OPS** | **4** | **4** | **4** |
| **HERO-3** | **26** | **24** | **0** |
| P2 | 17 | 1 | 0 |
| P3 | 6 | 0 | 0 |
| Adult (A) | 3 | 0 | 0 |
| **CX** | **6** | **6** | **6** |
| **Всего (спринт)** | **102** | **76** | **см. handoff + [FINAL_PLAN](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md) + [матрица HERO-3](./COMPANION_HERO3_READINESS_MATRIX.md)** |
| Матрица Grok (справочник) | 102 | — | не = спринт |

**Итого:** **76 из 102** (75%). Осталось **26** задач спринта + **GATE** (см. [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) · [COMPANION_FINAL_PLAN_AND_VERIFICATION.md](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md)).

> **Финальный план с тестами на каждый блок:** [COMPANION_FINAL_PLAN_AND_VERIFICATION.md](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md)  
**Не в scope:** ежедневный backup БД (**X-07**), push «вернись к Единорогу» (**X-06**).  
Скрипты: `scripts/deploy_companion_p0.sh`, `scripts/verify_companion_p0_prod.sh`, [COMPANION_DEPLOY_P0.md](./COMPANION_DEPLOY_P0.md).

**Следующие задачи:** **GATE-DIALOG-REGRESS (R1–R19)** → **OPS-01** → **P1-26…P1-30** → … → **GATE-DIALOG D01–D10**

> Регрессию **R1–R19** можно прогнать **сегодня** по [COMPANION_FINAL_PLAN_AND_VERIFICATION.md](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md).
