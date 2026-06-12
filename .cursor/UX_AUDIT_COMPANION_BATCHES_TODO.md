# UX Audit — Companion / Wellness / Antifake (2026-06-12)

**Источник:** отзыв пользователя build 229 · **Build:** 229  
**Рабочий корень:** `ALADDIN_iOS`  
**Связанные планы:** `.cursor/IMPLEMENTATION_BATCHES_TODO.md` (143 security), `docs/WELLNESS_CURSOR_TODO.md` (131 wellness)

> **ПРАВИЛО:** каждый batch — отдельный commit/PR; не смешивать с `telegram_stars_shop_bot/`.

---

## Карта: где что в приложении

### Antifake (140+ security batch)

| Что | Где на телефоне | Файл |
|-----|-----------------|------|
| **Antifake Hub** (текст/URL/аудио/видео/звонок) | Нет прямого пункта в меню! Входы: Share Extension «Проверить в ALADDIN», Identity/Family/Device Hub → coverage row, deep link | `Screens/AntifakeHubScreen.swift` |
| Категория Deepfakes | Настройки → Защита → категория **только тумблер**, не открывает Hub | `Components/ProtectionCategoryRow.swift` |
| Документация 140+ задач | Не в UI — `.cursor/IMPLEMENTATION_BATCHES_TODO.md`, `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` | — |

**Почему не находите:** Hub спрятан за coverage rows и Share; из «Защита» тап = toggle, не навигация.

### Wellness / AI поддержка (Мир героев → вкладка «AI поддержка»)

| Раздел | Экран | Файл |
|--------|-------|------|
| Хаб AI поддержки | Companion → таб 2 «AI поддержка» | `WellnessHubScreen.swift` |
| Сны и образы | Карточка в хабе | `WellnessDreamJournalScreen.swift` |
| Глубокое исследование | Карточка в хабе | `WellnessReflectiveModeScreen.swift` |
| Разговор с героем | Companion → таб 1 «Главная» | `CompanionConversationScreen.swift` |
| Правила AI | Sheet при первом входе | `CompanionLegalScreen.swift` |

---

## Batch 0 — Карта и воспроизведение (QA baseline)

| ID | Задача | Статус |
|----|--------|--------|
| ux-0-01 | Зафиксировать пути воспроизведения всех 8 пунктов отзыва | ⬜ |
| ux-0-02 | Screen recording: IoT toggle, Support freeze, Wellness back nav | ⬜ |
| ux-0-03 | Проверить backend smoke: `/api/wellness/reflective/modes`, `/api/protection/enable` iotThreats | ⬜ |

---

## Batch 1 — Antifake: найти на телефоне (discoverability)

**Проблема:** пользователь не видит antifake после 140+ задач.  
**Дополнение продукта (2026-06-12):** главная точка входа — **экран «Защита»**, не Главная.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-1-01 | В **Защита → Deepfakes**: кнопка **«Открыть проверку»** рядом с тумблером (короткий тап = toggle, кнопка/chevron = Hub) | `ProtectionCategoryRow.swift`, `ProtectionGroupSection.swift`, `ThreatProtectionScreen.swift` | ⬜ |
| ux-1-02 | **Заметная карточка в Защите** (верх экрана): «Проверить ссылку · голос · видео» → Antifake Hub | `ThreatProtectionScreen.swift` | ⬜ |
| ux-1-03 | Короткая подсказка при первом заходе в Hub (3 шага) | sheet / `UserDefaults` once | ⬜ |
| ux-1-04 | Обновить `docs/release/QA_HUB_DEMO_R08_R10.md` — путь: **Защита → Открыть проверку** | docs | ⬜ |
| ux-1-05 | *(опционально P2)* Analytics / Identity coverage — без дублирования карточки | hub cards | ⬜ |

---

## Batch 2 — IoT: «ресурс не найден»

**Корневая причина (2 пути):**

1. **Network Protection → IoT Security** → `POST /api/components/enable/iot_security_agent` → **404** (`iot_security_agent` нет в `ALL_COMPONENTS` на сервере)
2. **Device Hub → IoT tab** → `POST /api/protection/enable` `iotThreats` — может работать, но ошибка 404 показывается как «Job not found» (копипаста antifake)

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-2-01 | Backend: добавить `iot_security_agent` в `ALL_COMPONENTS` ИЛИ убрать дублирующий toggle из Network Protection | `app/routers/components.py` (VPS) | ⬜ |
| ux-2-02 | iOS: единый IoT путь — Device Hub только; скрыть/redirect Network Protection row | `03_NetworkProtectionScreen.swift` | ⬜ |
| ux-2-03 | iOS: правильные сообщения ошибок для IoT (не antifake job) | `DeviceIoTPanelViewModel.swift` | ⬜ |
| ux-2-04 | Навигация: категория iotThreats → Device Hub IoT tab | `ThreatProtectionCategory.swift`, navigation | ⬜ |

---

## Batch 3 — Помощь и поддержка: зависание + медленный отклик

**Причины:** 44 FAQ карточки с `stormGlassCard` + spring; поиск без debounce; полный rebuild при смене языка.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-3-01 | LazyVStack / пагинация FAQ (показывать 10, «ещё») | `13_SupportScreen.swift` | ⬜ |
| ux-3-02 | Debounce поиска 300ms | `13_SupportScreen.swift` | ⬜ |
| ux-3-03 | Убрать лишний glass с каждой FAQ-карточки | `13_SupportScreen.swift` | ⬜ |
| ux-3-04 | Глобальный аудит: задержка 1–2с при навигации — profile Instruments Time Profiler | `NavigationManager`, `ALADDINApp` | ⬜ |
| ux-3-05 | Отложить тяжёлые `.task` на экранах до после transition | hot paths | ⬜ |

---

## Batch 4 — Контакты: Telegram вместо email, убрать адрес

**Сейчас:** `privacy_policy_section_contacts_content_1` = email, `_3` = адрес Самара.  
**Бот:** `AppConfig.supportTelegramURL` = `https://t.me/AladdinchatAI_bot`

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-4-01 | RU/EN: Email → Telegram @AladdinchatAI_bot | `LocalizationManager.swift` | ⬜ |
| ux-4-02 | Убрать строку адреса (`_content_3`) | `LocalizationManager.swift`, `18_PrivacyPolicyScreen.swift` | ⬜ |
| ux-4-03 | Убрать hardcoded fallback email в PrivacyPolicy | `18_PrivacyPolicyScreen.swift` ~737 | ⬜ |
| ux-4-04 | **Помощь и поддержка:** первая кнопка — **«Написать в Telegram»** + SF Symbol `paperplane.fill` + `@AladdinchatAI_bot` в подзаголовке (сейчас «Чат поддержки» без слова Telegram) | `13_SupportScreen.swift`, `LocalizationManager.swift` | ⬜ |
| ux-3-06 | *(связка)* Telegram-кнопку вынести **выше FAQ**, sticky при скролле (видна сразу) | `13_SupportScreen.swift` | ⬜ |

---

## Batch 5 — Навигация «Назад» из AI поддержки → не на Главную

**Корневая причина:** subpages вызывают `goBack()` → remount `CompanionHomeScreen` → `tab` сбрасывается на `.main` (разговор), а не на вкладку «AI поддержка».  
**Правильный паттерн:** `finishWellnessFlow()` (уже есть для упражнений).

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-5-01 | Заменить `goBack()` → `finishWellnessFlow()` на всех wellness subpages | см. список ниже | ⬜ |
| ux-5-02 | Persist `companionHome` tab в `NavigationManager` / `@AppStorage` | `CompanionHomeScreen.swift`, `NavigationManager.swift` | ⬜ |
| ux-5-03 | UITest: back из Dreams → Wellness hub (не Main) | `WellnessCompanionNavUITests.swift` | ⬜ |

**Экраны для правки back:**
- `WellnessDreamJournalScreen.swift`
- `WellnessReflectiveModeScreen.swift`
- `WellnessTrustCenterScreen.swift`
- `WellnessTimelineScreen.swift`
- `WellnessCheckinScreen.swift`
- `WellnessAssessmentFlowScreen.swift`
- `WellnessExerciseScreen.swift` (проверить consistency)

---

## Batch 6 — Сны и образы: текст не виден + copy (6 шляп)

**Баг (P0, даёт ~70% жалобы):** `.foregroundColor(.white)` на root + `.roundedBorder` TextField = белый текст на белом фоне.  
**Copy (даёт ~20%):** две строки disclaimer пугают и дублируют друг друга.  
**Сохранение (даёт ~10%):** проверить API после fix цвета.

### Анализ 6 шляп — disclaimers

| Шляпа | Вывод |
|-------|--------|
| ⚪ Факты | Сейчас 2 строки caption 75% opacity; Jung pillar; не клиника; слова «предсказания»/«приговор» — юридическая страховка |
| 🔴 Эмоции | «Не приговор» звучит тревожно — пользователь не думал о приговоре; ощущение «юридической стены» перед полем |
| ⚫ Риски | Без disclaimer — риск «приложение гадает»; только disclaimer без fix цвета — **0% решения** видимости текста |
| 🟡 Плюсы | Одна тёплая фраза + иконка ⓘ лучше строит доверие |
| 🟢 Идеи | Placeholder в поле объясняет смысл; sheet «Подробнее» один раз; первый визит — coachmark |
| 🔵 Процесс | Сначала ux-6-01 (цвет), потом ux-6-02 (copy); не обещать «100%» только текстом |

### Рекомендуемый copy (вместо двух строк)

**Одна строка под заголовком (RU):**
> «Личный дневник снов — чтобы заметить образы и поразмышлять. Это не гадание и не медицинский совет.»

**EN:**
> «A private dream journal for reflection — not fortune-telling or medical advice.»

**Кнопка:** `ⓘ Подробнее` → sheet с 3 пунктами (не предсказания / символы как метафоры / при тревоге — к взрослому).

**Убрать с экрана:** отдельную строку «Символы — только как метафоры, не приговор» (слово «приговор» — в sheet только).

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-6-01 | **P0** Fix цвета поля ввода (тёмный glass input / `.primary` на field) | `WellnessDreamJournalScreen.swift`, `WellnessSwiftUICompat.swift` | ⬜ |
| ux-6-02 | Одна строка disclaimer + sheet «Подробнее» (см. copy выше) | `LocalizationManager.swift`, `WellnessDreamJournalScreen.swift` | ⬜ |
| ux-6-03 | Placeholder поля: «Опиши сон своими словами…» | `LocalizationManager.swift` | ⬜ |
| ux-6-04 | Проверить сохранение + отображение в списке ниже | `WellnessAPIService` | ⬜ |
| ux-6-05 | Первый визит: один coachmark (опционально P2) | `UserDefaults` | ⬜ |

---

## Batch 7 — Разговор с героем: грузится / микрофон / чипы доверия

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-7-01 | ProgressView во время `loadState()` | `CompanionConversationScreen.swift` | ⬜ |
| ux-7-02 | Показать spinner при `isSending` | `CompanionDialogueStrip.swift` | ⬜ |
| ux-7-03 | Переформулировать mic hint: «Нажми микрофон и говори» (без tap/hold EN) | `LocalizationManager.swift` | ⬜ |
| ux-7-04 | Документировать логику чипов (настроение, маленькие шаги, доверие) — product copy | `docs/` или tooltip | ⬜ |
| ux-7-05 | Контраст текста на StormMesh фоне (companion + unicorn) | `CompanionHeroLayout.swift`, theme tokens | ⬜ |

**Логика чипов над полем ввода:**
- **Доверие (trust)** — gamification: streak за регулярность
- **Настроение** — контекст для LLM (pillar routing)
- **Маленькие шаги / в прошлый раз** — behavioral pillar, continuity
- **Сегодня можно начать** — nudge для новой сессии

---

## Batch 8 — Глубокое исследование: «Не удалось выбрать направление»

**Ошибка:** `wellness_error_pillar` при `setSessionPillar` API fail (не при загрузке карточек).

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-8-01 | Smoke: `POST /api/wellness/session/pillar` на VPS | server | ⬜ |
| ux-8-02 | Offline fallback: локально set pillar без API | `WellnessSessionStore` | ⬜ |
| ux-8-03 | После выбора карточки — `finishWellnessFlow` pattern для back | `WellnessReflectiveModeScreen.swift` | ⬜ |
| ux-8-04 | Показать 5 карточек с описанием что откроется (чат с героем) | copy review | ⬜ |

---

## Batch 9 — Правила AI компаньона: читаемость и лишний текст

**Проблема:** технические блоки («запасное распознавание на сервере») не для пользователей; тёмный фон + glass.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-9-01 | User-facing legal: убрать server/STT jargon | `CompanionModels.swift` offlineFallback | ⬜ |
| ux-9-02 | Локализовать hardcoded RU в CompanionLegalScreen | `CompanionLegalScreen.swift` | ⬜ |
| ux-9-03 | Повысить контраст body text на `.legal` background | `CompanionLegalScreen.swift` | ⬜ |
| ux-9-04 | Оставить: кризис, конфиденциальность, не терапия, возрастные рамки | product review | ⬜ |

---

## Batch 10 — Глобальная производительность UI

| ID | Задача | Статус |
|----|--------|--------|
| ux-10-01 | Profile main thread: navigation tap → screen appear delay | ⬜ |
| ux-10-02 | Audit `stormGlassCard` count per screen (cap 3–5 visible) | ⬜ |
| ux-10-03 | `NavigationManager.navigateTo` — sync work before screen swap | ⬜ |
| ux-10-04 | Target: переход < 200ms (ощущение мгновенного) | ⬜ |

---

## Приоритет выполнения (рекомендация)

| Приоритет | Batch | Почему |
|-----------|-------|--------|
| P0 | **5** (back nav), **6** (dreams input), **2** (IoT 404) | Блокеры UX, красные ошибки |
| P1 | **3** (support freeze), **7** (hero loading), **8** (deep explore) | Ежедневное использование |
| P2 | **4** (contacts), **9** (legal copy), **1** (antifake find) | Контент/ discoverability |
| P3 | **10** (global perf) | Системная оптимизация |

---

## Ответы на каждый пункт отзыва (кратко)

| # | Вопрос | Ответ |
|---|--------|-------|
| 1 | Где antifake / 140+ задач? | Hub есть, но спрятан; см. Batch 1 |
| 2 | IoT «ресурс не найден» | 404 component на сервере; Batch 2 |
| 2b | Support зависает, медленно везде | FAQ perf + global nav; Batch 3, 10 |
| 3 | Контакты | Privacy Policy §Контакты; Batch 4 |
| 4 | Микрофон tap/hold, чипы, контраст | Batch 7 |
| 5 | Разговор с героем грузится | Нет loading UI; Batch 7 |
| 6 | Сны: disclaimers + белый текст | Баг цвета + copy; Batch 6 |
| 7 | Правила AI | Batch 9 |
| 8 | Назад → Главная | `goBack` vs `finishWellnessFlow`; Batch 5 |
| 9 | Глубокое исследование пустое | API pillar fail; Batch 8 |

---

*UX Audit v1.1 · верификация по коду 2026-06-11 · attach in Cursor: `.cursor/UX_AUDIT_COMPANION_BATCHES_TODO.md`*

---

## ВЕРИФИКАЦИЯ: каждое предложение отзыва (честный статус)

> **Важно:** правки есть в **локальном коде**, commit/push **не делался**. На телефоне build 229 поведение **ещё старое**, пока не соберёте новый билд.

### Пункт 1 — Antifake / 140+ задач: где на телефоне?

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Не могу найти antifake | 🟡 **Код готов, не на устройстве** | Карточка в **Защита** (верх) + кнопка **«Открыть проверку»** у Deepfakes → `ThreatProtectionScreen`, `ProtectionCategoryRow` |
| Где посмотреть 140+ задач | 🔴 **Не в UI** | Это backend/security batch; на телефоне только **Antifake Hub** (текст/URL/аудио/видео/звонок). Док: `.cursor/IMPLEMENTATION_BATCHES_TODO.md` |
| Подсказка при первом входе в Hub | ⬜ **Не сделано** | ux-1-03 |

### Пункт 2 — IoT: «ресурс не найден»

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Тумблер IoT → красная ошибка | 🟡 **Частично** | iOS: редирект в Device Hub + нормальные тексты ошибок. Backend: `iot_security_agent` в `components.py` — **нужен deploy на VPS** |
| На телефоне сейчас | 🔴 **Может остаться 404** | Пока сервер не обновлён |

### Пункт 3 — Помощь зависает + медленно везде

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Support — ничего не нажимается | 🟡 **Код готов** | FAQ 10+«ещё», debounce 300ms, убран glass, Telegram сверху — `13_SupportScreen.swift` |
| Переходы 1–2 сек везде | 🔴 **Не сделано** | Batch 10: Instruments, отложенные `.task`, audit NavigationManager |
| Мгновенный отклик | ⬜ **Цель не достигнута** | ux-10-01…04 |

### Пункт 4 — Контакты: Telegram, убрать адрес

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Почта → Telegram бот | ✅ **Сделано в коде** | `privacy_policy_section_contacts_content_1`, Support кнопка `@AladdinchatAI_bot` |
| Убрать адрес Самара | ✅ **Сделано** | `_content_3` убран из Privacy Policy UI |

### Пункт 5 — Микрофон tap/hold, чипы, контраст

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| «tap или hold» — переформулировать | ✅ **Сделано** | `companion_voice_mic_modes` → «Нажми микрофон и говори» |
| Логика чипов (доверие, настроение, шаги…) | 🟡 **Только в плане** | Код есть, **подсказок в UI нет** (ux-7-04) |
| Текст плохо читается на фоне | 🟡 **Частично** | Контраст чипов в `CompanionConversationBannersSection`; **не весь ALADDIN/единорог** |

### Пункт 6 — Разговор с героем грузится

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Страница грузится, ничего не происходит | 🟡 **Код готов** | `ProgressView` + «Загружаем разговор…» при `loadState()`. Нужен билд + проверка при offline API |

### Пункт 7 — Сны: disclaimers + белый текст

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| «метафоры / не предсказания» — что это? | ✅ **Переписано** | Одна строка + «Подробнее» sheet |
| «символы — не приговор» | ✅ **Убрано с экрана** | Только в sheet |
| Белый текст в белом поле | ✅ **Исправлено P0** | `wellnessReadableInput()` — тёмный текст на белом фоне |

### Пункт 8 — Правила AI: читаемость, лишний текст

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Текст тёмный / не читается | 🟡 **Частично** | Offline: белый текст. **С сервера** (`fetchLegal`) текст может быть старым |
| «Запасное распознавание на сервере» | ✅ **Убрано из offline** | Новые user-facing тексты в `CompanionLegalScreen` |
| Кратко о голосе | ✅ **Сделано** | Один простой блок в offline fallback |

### Пункт 9 — Назад из AI поддержки → не на Главную (ВСЕ карточки)

| Карточка хаба | Back-кнопка | Статус |
|---------------|-------------|--------|
| Сны и образы | `wellnessGoBack()` | ✅ в коде |
| Глубокое исследование | `wellnessGoBack()` | ✅ в коде |
| Вместе | `wellnessGoBack()` | ✅ в коде |
| Как мы работаем (Trust) | `wellnessGoBack()` | ✅ в коде |
| Упражнения | `wellnessGoBack()` | ✅ в коде |
| Как ты? (Check-in) | `wellnessGoBack()` | ✅ в коде |
| Мой прогресс (Timeline) | `wellnessGoBack()` | ✅ в коде |
| Опросы (Assessments hub → flow) | `wellnessGoBack()` | 🟡 **Риск**: flow открывается через `navigateTo` без явного return |
| Поговорить с героем | смена вкладки на Main | ⚪ **По дизайну** — не «назад», а переход к чату |
| Внутри вложенных экранов опроса | — | 🟡 **Нужна доработка** ux-5-04 |

**Механизм:** `navigateToWellnessScreen(..., returnTo: .companionHome)` + `finishWellnessFlow()` → вкладка **AI поддержка** (tab=1).  
**НЕ подтверждено на устройстве.** UITest есть только для Exercise (`WellnessCompanionNavUITests`).

### Пункт 10 — Глубокое исследование: пусто + «не удалось выбрать направление»

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Внутри карточки ничего | 🟡 **По плану** | Выбор карточки → **разговор с героем** (Main tab), не отдельный экран |
| «Не удалось выбрать направление» | 🟡 **Код готов** | Pillar сохраняется локально даже если API падает |
| Назад из карточки → Главная | 🟡 **Должно быть исправлено** | `wellnessGoBack` + offline pillar; **проверить на билде** |
| Описание 5 карточек для пользователя | ⬜ **Не сделано** | ux-8-04 |

---

## Сводка: подтверждаю или опровергаю

| Утверждение | Вердикт |
|-------------|---------|
| «Каждое слово отработано» | 🔴 **ОПРОВЕРГАЮ** — ~70% в коде, ~30% открыто (perf, VPS, QA на устройстве, подсказки чипов, все UITest) |
| «Назад на все карточки AI поддержки» | 🟡 **ЧАСТИЧНО ПОДТВЕРЖДАЮ** — основные 7 экранов в коде; опросы и edge cases — риск; **на build 229 ещё сломано** |
| «Antifake найдёте на телефоне» | 🟡 **После нового билда** — путь: Защита → карточка / «Открыть проверку» |
| «IoT исправлен» | 🟡 **После deploy VPS** |
| «Support не зависает» | 🟡 **После нового билда** |
| «Сны — текст виден» | ✅ **В коде да** |
| «Глубокое исследование работает» | 🟡 **В коде да (offline pillar)**; контент = чат с героем |

---

## Оставшиеся задачи (актуальный backlog)

| ID | Batch | Задача | Приоритет |
|----|-------|--------|-----------|
| ux-verify-01 | QA | Собрать билд с локальными правками и пройти 8 пунктов на устройстве | P0 |
| ux-2-deploy | 2 | Deploy `components.py` на VPS 149.154.65.180:8002 | P0 |
| ux-5-04 | 5 | Assessments hub/flow: `navigateToWellnessScreen` вместо `navigateTo` | P0 |
| ux-5-05 | 5 | UITest: back из Dreams, Reflective, Timeline → AI поддержка | P1 |
| ux-7-04 | 7 | Tooltip/sheet: что значат чипы (доверие, настроение, шаги) | P1 |
| ux-7-05 | 7 | Глобальный контраст StormMesh (не только companion) | P2 |
| ux-8-01 | 8 | Smoke VPS: `POST /api/wellness/session/pillar` | P1 |
| ux-8-04 | 8 | Copy на 5 карточках глубокого исследования | P2 |
| ux-1-03 | 1 | Coachmark первого входа в Antifake Hub | P2 |
| ux-10-01…04 | 10 | Глобальная perf навигации <200ms | P1 |
| ux-commit | — | Commit + push UX batches (по запросу) | — |
