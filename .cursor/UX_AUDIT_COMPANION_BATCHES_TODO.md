# UX Audit — Companion / Wellness / Antifake (2026-06-12)

**Источник:** отзыв пользователя build 229 · **Build:** 230 (commit `32387ab0`)  
**Рабочий корень:** `ALADDIN_iOS`  
**Мастер-реестр всех задач:** `.cursor/ALADDIN_MASTER_TODO.md` (36 Cursor ids + ~100 детальных id)  
**Связанные планы:** `.cursor/IMPLEMENTATION_BATCHES_TODO.md` (143 security), `docs/WELLNESS_CURSOR_TODO.md` (131 wellness)  
**SSOT:** `docs/release/MASTER_STATUS_INDEX.md` · **Build:** **232** (2026-06-13)

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

## Карта Antifake — честно: что видит пользователь vs код

### Что вы видите (build 230) — это нормально

**Главная** → «Защита Aladdin» → `03_NetworkProtectionScreen`:

1. Экстренная помощь  
2. **Защита от угроз** (фишинг, malware, mobile, сеть, IoT) — **только тумблеры**  
3. Автоматическая система защиты  
4. Безопасность паролей  

**Antifake Hub на этом экране НЕТ.** Карточки «Проверить ссылку» и Deepfakes — на **другом** экране (`ThreatProtectionScreen`), до которого **нет ссылки** с Главной.

### Antifake Hub (когда откроется) — 4 вкладки

| Вкладка | Что проверяет |
|---------|---------------|
| **Текст** | Текст или **ссылка** на новость/пост (режимы «Текст» / «Ссылка») |
| **Голос** | Аудиофайл |
| **Видео** | Видеофайл |
| **Звонок** | Запись звонка |

Тариф **Premium**. «Новости» = вкладка **Текст**, не отдельная кнопка.

### Скрытые входы (не в меню приложения)

| Вход | Как |
|------|-----|
| Share | Safari/Telegram → **Поделиться** → «Проверить в ALADDIN» (включить в «Изменить») |
| Device/Identity Hub | Coverage deepfake → Hub (если знаете путь) |
| Уведомления | Редко → `ThreatProtectionScreen` |

**Fix P0:** ux-1-06 — карточка Antifake на `03_NetworkProtectionScreen`.

---

## Batch 1 — Antifake: найти на телефоне (discoverability)

**Проблема:** пользователь не видит antifake после 140+ задач.  
**Дополнение продукта (2026-06-12):** главная точка входа — **экран «Защита»**, не Главная.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-1-01 | Кнопка «Открыть проверку» у Deepfakes | `ProtectionCategoryRow.swift` | ✅ на `ThreatProtectionScreen` — **пользователь не видит** |
| ux-1-02 | Карточка «Проверить ссылку·голос·видео» | `ThreatProtectionScreen.swift` | ✅ — **пользователь не видит** |
| ux-1-06 | **P0** Карточка Antifake на **`03_NetworkProtectionScreen`** — **между `securityFeaturesCard` и `componentsSections`** (до аккордеона «Экстренная помощь»); reuse `antifakeQuickAccessCard` из `ThreatProtectionScreen` | `03_NetworkProtectionScreen.swift` | ⬜ |
| ux-1-07 | Строка в аккордеоне «Защита от угроз» → Hub | `03_NetworkProtectionScreen` | P2 ✅ build 232 |
| ux-1-08 | Ссылка `ThreatProtectionScreen` ↔ `NetworkProtection` или merge экранов | nav | ⬜ |
| ux-1-09 | **P1** Подсказка Share: Safari → Поделиться → «Проверить в ALADDIN» | Support / Settings | ⬜ |
| ux-1-03 | Coachmark первого входа в Hub (3 шага) | sheet | ⬜ |
| ux-1-04 | QA doc: путь **Главная → Защита Aladdin → Проверить фейк** | docs | ⬜ |
| ux-1-05 | Device/Identity coverage — без дубля если есть ux-1-06 | hub cards | P2 |
| ux-1-10 | **P1** Честный copy: карточка + Hub — «звонок = запись после разговора», не автоблок | `LocalizationManager.swift` | ⬜ |

### AF-VISION — дорога к «идеалу» (связь с `.cursor/ANTIFAKE_PRODUCTION_TODO.md`)

**Важно:** «100% перехват всех звонков в эфире» на **обычном** сотовом звонке iOS **не разрешает Apple**. Реалистичная цель — **максимальная защита в рамках iOS** (≈85–90% ценности для семьи).

| Фаза | Срок | Что получает пользователь | Батчи |
|------|------|---------------------------|-------|
| **M1 Ручная** (сейчас→) | 2–3 нед | Hub на экране Защиты, проверка текста/URL мгновенно, медиа/звонок по файлу, вердикт | ux-1-06, af-3, af-10, af-11 |
| **M2 Проактивная** | +4–6 нед | Метка «мошенник?» на номере (Call Directory), push после звонка «Проверить?», Share из Safari/TG | af-4-02…05, ux-1-09 |
| **M3 Полуавто** | +6–8 нед | Виджет «5 сек — проверить голос» во время разговора (с согласия), история проверок, AI-ассистент | af-4-04, af-6-08 |
| **M4 Нельзя на iOS** | — | Слушать все PSTN-звонки в фоне, класть трубку по ML без списка номеров, перехват FaceTime/видеочата | **не обещать** |

Полный техплан: `.cursor/ANTIFAKE_MASTER_ROADMAP.md` · 72+ задачи `af-*`.

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
| ux-6-01 | **P0** Fix цвета поля ввода — **глобально** `WellnessMultilineField.wellnessReadableInput()` | `WellnessSwiftUICompat.swift` | ✅ |
| ux-6-01b | Audit всех wellness TextField (Exercise, Values, Check-in notes) | все `Wellness*.swift` | ✅ Exercise; ✅ Values build 232 |
| ux-6-06 | **P0** «Дневник снов пока недоступен» — API/флаг `FEATURE_WELLNESS_JUNG` на VPS + offline save локально | `WellnessDreamJournalScreen`, `wellness_router.py` | 🟡 offline ✅ |
| ux-6-02 | Одна строка disclaimer + sheet «Подробнее» (см. copy выше) | `LocalizationManager.swift`, `WellnessDreamJournalScreen.swift` | ✅ |
| ux-6-03 | Placeholder поля сна | `LocalizationManager.swift` | ✅ build 232 |
| ux-6-04 | Проверить сохранение + отображение в списке ниже | `WellnessAPIService` | ✅ |
| ux-6-05 | Первый визит: один coachmark (опционально P2) | `UserDefaults` | ✅ build 232 |

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

## Batch 8 — Глубокое исследование

### Логика продукта (как задумано в коде)

Экран **«Глубокое исследование»** — это **не отдельные упражнения**, а **5 входов в разговор с героем** с разным «pillar» (стилем ответа):

| Карточка | id | Pillar | Что происходит при тапе |
|----------|-----|--------|-------------------------|
| Просто побудь рядом | `presence` | humanistic | → вкладка **Главная** (чат с героем), баннер «Принять себя» |
| Разбери глубоко | `deep_explore` | jung | → чат, образы/метафоры |
| Взгляд со стороны | `structured_view` | cognitive | → чат, факты vs интерпретации |
| Слепые зоны | `blind_spots` | jung | → чат, мягко про паттерны |
| Только вопрос | `single_question` | humanistic | → чат, один вопрос без нравоучений |

**Код:** `WellnessReflectiveModeScreen.selectMode` → `navigateToCompanionHome(returnTo: .wellnessReflective)` — **переход на героя — ожидаемое поведение**, не баг.

**UX-проблема:** пользователь ожидает контент **внутри карточки**, а получает смену экрана без предупреждения.

### Тексты для экрана (простой язык — внедрить в L10n)

**Подзаголовок экрана** (`wellness_deep_explore_subtitle`) — **без отрицания** («отдельного экрана нет» убрать: это техжаргон для разработчиков, не для пользователя):
> «Выберите формат — откроется **разговор с героем** в этом стиле.»

**Под каждой карточкой** (заменить `wellness_mode_*_hint`):

| Карточка | Текст для пользователя |
|----------|------------------------|
| Просто побудь рядом | «Спокойный разговор без советов — как „принять себя“» |
| Разбери глубоко | «Поговорим об образах и снах. Это метафоры, не диагноз» |
| Взгляд со стороны | «Разделим, что факт, а что — ваши догадки» |
| Слепые зоны | «Мягко посмотрим на привычные реакции» |
| Только вопрос | «Один честный вопрос — без нравоучений» |

**Баннер перед переходом** (ux-8-05): «Сейчас откроется чат с героем в формате „…“. Продолжить?»

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| ux-8-01 | Smoke: `POST /api/wellness/session/pillar` на VPS | server | ⬜ |
| ux-8-02 | Offline fallback: локально set pillar без API | `WellnessReflectiveModeScreen` | ✅ |
| ux-8-03 | Back из чата → «Глубокое исследование» (`returnTo: .wellnessReflective`) | `NavigationManager` | ✅ в коде |
| ux-8-04 | Copy на карточках — таблица выше в L10n | `LocalizationManager.swift` | ⬜ |
| ux-8-07 | **P1** Info-блок вверху экрана «Глубокое исследование» (subtitle + иконка 💬) | `WellnessReflectiveModeScreen` | ⬜ |
| ux-8-05 | **P1** Sheet «Продолжить в чате?» перед `navigateToCompanionHome` | `WellnessReflectiveModeScreen` | ⬜ |
| ux-8-06 | **P2** Опционально: промпт-экран внутри карточки | product | ✅ build 232 |

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

## Batch PERF-0 — VisualLogger / MasterLogger / SETTINGS_DIAG (симулятор)

**Проблема:** мини-экран «📋 логи Все» в симуляторе (DEBUG) — `VisualLogView` в `ALADDINApp` overlay. На реальном устройстве (RELEASE) по умолчанию **не показывается**.

**Влияние на perf (симулятор):** **ДА, заметное**
- Каждый лог → `DispatchQueue.main.async` → `@Published logs` → перерисовка overlay
- Сохранение в UserDefaults на каждую строку
- Сетевые логи (`metrics/upload`, family/stats) обновляют UI 10–30 раз/сек
- Дубли: `MasterLogger` → `SettingsDiagnosticsLogger` + `VisualLogger` + `print`
- Искажает FPS-метрики в симуляторе (Support 36 FPS мог быть частично из-за overlay + фоновый sync)

**Решение:** Xcode Console достаточно для ежедневной отладки. Overlay — opt-in.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| perf-0-01 | VisualLogger overlay **выкл по умолчанию** (DEBUG + RELEASE); флаг `enable_visual_logging` | `ALADDINApp.swift`, `MasterLogger.swift`, `VisualLogger.swift` | ✅ |
| perf-0-02 | `VisualLogger.log` — no-op когда overlay выкл (не трогать main thread) | `VisualLogger.swift` | ✅ |
| perf-0-03 | RELEASE: один канал логов — убрать дубль SETTINGS_DIAG + MasterLogger + print | `SettingsDiagnosticsLogger.swift`, `MasterLogger.swift` | ⬜ |
| perf-0-04 | Док: как включить overlay на устройстве (`UserDefaults enable_visual_logging=true`) | `.cursor/rules/aladdin-diagnostic-exports.mdc` | ⬜ |

---

## Batch PERF-1 — Главная: cold start < 300 ms UI, данные < 1 с

**Замер из логов:** `MainDashboard` **3.154 с** (сеть ~0.44 с, overhead ~2.7 с).

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| perf-1-01 | **Один bootstrap** загрузки: убрать дубль `.task onAppear` + `.onAppear requestRefreshDebounced` | `01_MainScreen.swift`, `MainViewModel.swift` | ⬜ |
| perf-1-02 | `endScreenLoad` — по первому интерактивному кадру, не после subscription sync | `MainViewModel.swift`, `PerformanceMonitor.swift` | ⬜ |
| perf-1-03 | Skeleton / кеш дашборда мгновенно; API в фоне | `01_MainScreen.swift` | ⬜ |
| perf-1-04 | Lazy init `AntivirusManager` (не на первом paint главной) | `AntivirusManager.swift` | ⬜ |
| perf-1-05 | Отложить `MetricsService` + `PerformanceMonitor` на +2 с после launch | `ALADDINApp.swift`, `PerformanceMonitor.swift` | ⬜ |
| perf-1-06 | Отложить `syncSubscriptionOnMainScreenAppear` до после первого кадра | `01_MainScreen.swift`, `SubscriptionManager.swift` | ⬜ |

**Цель:** первый интерактивный кадр **< 300 ms**, полные данные дашборда **< 1 с**.

---

## Batch PERF-2 — Support FPS + фоновая нагрузка

**Истинная причина FPS 36:** не только FAQ — совпадение с `syncWithServer`, `POST subscription/events/batch`, `MetricsService upload`, memory timer.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| perf-2-01 | Отложить `syncWithServer` / metrics batch пока открыт Support | `SubscriptionManager.swift`, `13_SupportScreen.swift` | ⬜ |
| perf-2-02 | `MetricsService` — очередь off main thread | `MetricsService` (найти файл) | ⬜ |
| perf-2-03 | FAQ: одна раскрытая карточка; убрать `.spring()` на 10 карточках | `13_SupportScreen.swift` | ⬜ |
| perf-2-04 | Instruments Time Profiler: Support scroll 5 с | QA runbook | ⬜ |

---

## Batch FIX-NOTIF — NotificationService недоступен

**Причина:** `SettingsScreen` → `SettingsViewModel()` без DI → `notificationService == nil`.

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| fix-notif-01 | `initializeNotifications()` через `NotificationManager.shared` если DI nil | `SettingsViewModel.swift` | ⬜ |
| fix-notif-02 | Или inject `NotificationServiceAdapter` из `AppCoordinator` | `05_SettingsScreen.swift` | ⬜ |
| fix-notif-03 | Симулятор: понятный hint «push недоступен», не `❌` | `SettingsViewModel.swift` | ⬜ |

---

## Batch FIX-SF — SF Symbols iOS 17

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| fix-sf-01 | `iphone.and.arrow.forward.inward` → fallback `iphone.and.arrow.forward` | `05_SettingsScreen.swift`, `NavigationManager.swift` | ⬜ |
| fix-sf-02 | `waveform.badge.mic` → fallback `waveform` / `mic.fill` | `05_SettingsScreen.swift`, `VoiceNotesScreen.swift` | ⬜ |

---

## Batch FIX-SETTINGS — тройное сохранение notifications

| ID | Задача | Файлы | Статус |
|----|--------|-------|--------|
| fix-settings-01 | Флаг `suppressRemoteNotificationServerLoop` на init Settings | `SettingsViewModel.swift` | ⬜ |
| fix-settings-02 | Один debounced POST вместо 2× `/api/settings/notifications/update` | `SettingsViewModel.swift`, `NotificationAppSettingsSync` | ⬜ |

---

## Batch 10 — Глобальная производительность навигации

| ID | Задача | Статус |
|----|--------|--------|
| ux-10-01 | Profile main thread: navigation tap → screen appear delay | ⬜ |
| ux-10-02 | Audit `stormGlassCard` count per screen (cap 3–5 visible) | ⬜ |
| ux-10-03 | `NavigationManager.navigateTo` — sync work before screen swap | ⬜ |
| ux-10-04 | Target: переход < 200ms (ощущение мгновенного) | ⬜ |

---

## Приоритет выполнения (актуально 2026-06-11)

| Приоритет | Batch | Почему |
|-----------|-------|--------|
| P0 | **PERF-1** (главная 3.1 с), **ux-2-deploy** ✅, **ux-verify-01** | Холодный старт — главная боль |
| P0 | **perf-0** ✅ overlay off | Честные замеры в симуляторе |
| P1 | **PERF-2**, **FIX-NOTIF**, **ux-5-04** | FPS Support, push в настройках, wellness back |
| P1 | **3** ✅ код, **7** ✅ код — device QA | Support / Hero |
| P2 | **FIX-SF**, **FIX-SETTINGS**, **ux-7-04/05**, **ux-8-04** | Полировка |
| P2 | **ux-1-03**, **ux-5-05** UITest | Discoverability + regression |

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

*UX Audit v1.2 · build 232 · SSOT `docs/release/MASTER_STATUS_INDEX.md`*

---

## ВЕРИФИКАЦИЯ: каждое предложение отзыва (честный статус)

> **Build 230** запушен (`32387ab0`). UX-батчи 1–9 в коде. **PERF-0** (VisualLogger off) — локально, не в 230. VPS IoT deploy — ✅.

### Пункт 1 — Antifake / 140+ задач: где на телефоне?

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Не могу найти antifake | 🟡 **Код готов, не на устройстве** | Карточка в **Защита** (верх) + кнопка **«Открыть проверку»** у Deepfakes → `ThreatProtectionScreen`, `ProtectionCategoryRow` |
| Где посмотреть 140+ задач | 🔴 **Не в UI** | Это backend/security batch; на телефоне только **Antifake Hub** (текст/URL/аудио/видео/звонок). Док: `.cursor/IMPLEMENTATION_BATCHES_TODO.md` |
| Подсказка при первом входе в Hub | ⬜ **Не сделано** | ux-1-03 |

### Пункт 2 — IoT: «ресурс не найден»

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Тумблер IoT → красная ошибка | 🟡 **Частично** | iOS: редирект в Device Hub + нормальные тексты. Backend: `iot_security_agent` — **deploy VPS ✅** (403 auth, не 404) |
| На телефоне сейчас | 🟡 **Проверить на build 230** | После deploy повторить toggle IoT |

### Пункт 3 — Помощь зависает + медленно везде

| Ваше замечание | Статус | Детали |
|----------------|--------|--------|
| Support — ничего не нажимается | 🟡 **Код готов** | FAQ 10+«ещё», debounce 300ms, убран glass, Telegram сверху — `13_SupportScreen.swift` |
| Переходы 1–2 сек везде | 🔴 **Подтверждено логами** | Главная 3.15 с — **PERF-1**; навигация — ux-10 |
| Мгновенный отклик | ⬜ **Цель не достигнута** | perf-1-01…06, ux-10-01…04 |
| FPS Support 36 | 🟡 **Анализ** | Overlay логов (симулятор) + фоновый sync — **PERF-0** ✅ + **PERF-2** |

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
| «Antifake найдёте на телефоне» | 🔴 **ОПРОВЕРГАЮ для вашего пути** — Hub есть в коде, но **не на экране Защиты**; нужен ux-1-06 |
| «IoT исправлен» | 🟡 **После deploy VPS** |
| «Support не зависает» | 🟡 **После нового билда** |
| «Сны — текст виден» | ✅ **В коде да** |
| «Глубокое исследование работает» | 🟡 **В коде да (offline pillar)**; контент = чат с героем |

---

## Оставшиеся задачи (актуальный backlog)

### Цели perf
- Первый интерактивный кадр главной: **< 300 ms**
- Полные данные дашборда: **< 1 с**
- Переход между экранами (ощущение): **< 200 ms**

### Сводная таблица батчей

| Batch | Приоритет | Статус | Cursor todo id |
|-------|-----------|--------|----------------|
| VPS-IoT | P0 | ✅ deploy | ux-2-iot |
| PERF-0 VisualLogger | P0 | ✅ overlay off (локально) | perf-0-logger |
| PERF-1 Главная | P0 | ⬜ | perf-1-main |
| PERF-2 Support | P1 | ⬜ | perf-2-support |
| FIX-NOTIF | P1 | ⬜ | fix-notif |
| FIX-SF | P2 | ⬜ | fix-sf |
| FIX-SETTINGS | P2 | ⬜ | fix-settings |
| UX batches 1–9 | mixed | 🟡 код в 230, QA ⬜ | ux-* |
| Batch 10 nav | P1 | ⬜ | ux-10-perf |

### Детальный backlog

| ID | Batch | Задача | Приоритет | Статус |
|----|-------|--------|-----------|--------|
| ux-verify-01 | QA | Build 230 + PERF-0 на симуляторе: 8 пунктов отзыва на устройстве | P0 | ⬜ |
| ux-2-deploy | 2 | Deploy `components.py` VPS | P0 | ✅ |
| perf-0-01…02 | PERF-0 | VisualLogger off by default | P0 | ✅ |
| perf-0-03 | PERF-0 | Убрать дубли SETTINGS_DIAG в RELEASE | P2 | ⬜ |
| perf-1-01…06 | PERF-1 | Главная cold start | P0 | ⬜ |
| perf-2-01…04 | PERF-2 | Support FPS + metrics off main | P1 | ⬜ |
| fix-notif-01…03 | FIX-NOTIF | Push / NotificationService в Settings | P1 | ⬜ |
| fix-sf-01…02 | FIX-SF | SF Symbol fallbacks iOS 17 | P2 | ⬜ |
| fix-settings-01…02 | FIX-SETTINGS | Один save notifications | P2 | ⬜ |
| ux-6-01 | 6 | Глобальный readable input wellness | P0 | ✅ |
| ux-6-06 | 6 | Dream journal API/offline | P0 | 🟡 |
| ux-1-06 | 1 | Antifake карточка NetworkProtection | P0 | 🟡 |
| ux-1-07 | 1 | Antifake accordion → Hub | P2 | ✅ build 232 |
| ux-8-04…07 | 8 | Reflective: copy + banner + confirm | P1 | 🟡 ux-8-06 ✅ |
| ux-5-04 | 5 | Assessments: `navigateToWellnessScreen` | P1 | ⬜ |
| ux-5-05 | 5 | UITest wellness back nav | P1 | ⬜ |
| ux-7-04 | 7 | Tooltip чипов героя | P1 | ⬜ |
| ux-7-05 | 7 | Глобальный контраст StormMesh | P2 | ⬜ |
| ux-8-01 | 8 | Smoke VPS wellness pillar | P1 | ⬜ |
| ux-8-04 | 8 | Copy 5 карточек reflective | P2 | ⬜ |
| ux-1-03 | 1 | Antifake coachmark | P2 | ⬜ |
| ux-10-01…04 | 10 | Nav perf <200ms | P1 | ⬜ |
| ux-commit | — | Commit PERF-0 + perf fixes (по запросу) | — | ⬜ |

### Шум в логах (не блокеры)

| Симптом | Причина | Действие |
|---------|---------|----------|
| `boringssl_metrics` | Apple system | Игнорировать |
| Дубли SETTINGS_DIAG + MasterLogger | Два канала | perf-0-03 |
| `Notification settings saved` ×3 | init + pullFromServer + sinks | fix-settings-01 |
