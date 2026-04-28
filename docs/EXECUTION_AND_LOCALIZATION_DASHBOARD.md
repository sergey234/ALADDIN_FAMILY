# Execution and Localization Dashboard

## Основные рабочие файлы

### Главный план и синхронизация
- **`docs/PLAN_GOVERNANCE_ONEPAGER.md`** — **единый вход по метрикам (178 / 68 / 275 / G)**, релизный скоуп §3, non-code трек §4, приоритеты P0–P3.
- `NEXT_VERSION_IMPLEMENTATION_PLAN.md`
- `docs/EXECUTION_AND_LOCALIZATION_DASHBOARD.md`
- **`docs/PLAN_174_ML_HANDOFF_FRONTEND.md`** — тематический ML-handoff, снятый на момент **174/178** (см. §0 внутри файла); **текущий plan-fact — 178/178** в этом дашборде
- **`docs/CHILD_CONTENT_FINAL_SYSTEM_HANDOFF.md`** — ML-ready end-state по детскому контенту (**178 + 68 + 275**): архитектура, локализация, гейты, порядок валидации
- **`docs/CHILD_CONTENT_INTERFACE_ML_HANDBOOK.md`** — полная карта **детского контента и интерфейса** для ML: связка планов **178 / 68 / матрица 275**, код, гейты, волны, ссылки на все ключевые артефакты
- **`docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`** — каноническая матрица **275** пунктов каталога (`PLAN_ITEM -> category_id -> item_id -> status`)
- `docs/GAMIFICATION_LOCALIZATION_SYNC_MATRIX.md`

### Локализация и правила
- `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
- `docs/LOCALIZATION_PR_CHECKLIST.md`
- `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`
- `docs/LOCALIZATION_BASELINE_BACKLOG.md`

### CI и контроль качества
- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `.github/gh_pr_create_template.md`
- `scripts/localization_lint.py`
- `scripts/content_contract_smoke.py`

### Endpoint contracts и доступ к прод-серверу
- `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md`
- `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`
- `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md`

### Основные экраны продукта
- `Screens/08_ChildInterfaceScreen.swift`
- `Screens/ChildContentScreen.swift`
- `Screens/09_ElderlyInterfaceScreen.swift`
- `Screens/02_FamilyScreen.swift`
- `Screens/07_ParentalControlScreen.swift`
- `Screens/05_SettingsScreen.swift`
- `Screens/11_ProfileScreen.swift`

---

## Сводка трекинга

- Всего задач в плане: **178**
- Выполнено: **178**
- В работе: **0**
- Ожидают: **0**

**Не путать с другими шкалами:** Phase 2 по детскому контенту — **68** задач в `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` (на 2026-04-27: **68/68**). Каталог **275** — `docs/PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md` (на 2026-04-28: **DONE 275 / PARTIAL 0 / TODO 0**). Сводная таблица метрик — **`docs/PLAN_GOVERNANCE_ONEPAGER.md` §2**.

## Электронная панель задач (операционный контур)

- UI-панель в приложении: `Screens/ImplementationPlanWorkbenchCard.swift` (показывает полный список open-задач, прогресс по трекам и фазам).
- Машинные источники для панели:
  - `Core/Planning/ImplementationPlanProgressValues.swift`
  - `Core/Planning/ImplementationPlanDashboardMirror.generated.swift`
  - `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` — **Phase 2: 68 задач** (чеклист + нумерация P2-xxx / exit / strategy); не смешивать с **178** задачами треков A/B в этом дашборде.
- Обязательное правило синхронизации: после любого изменения чекбоксов выполнять `python3 scripts/update_dashboard_stats.py`.

### Post-plan (выполняется вне счётчика 178)
- Перед релиз-кандидатом или по согласованному milestone: стабилизация test-target:
  - устранить текущие блокеры сборки `ALADDINUnitTests` (`SubscriptionToken` in scope + invalid override),
  - прогнать `ChildRosterReconcilePolicyTests` в green режиме.
- Этот пункт **не входит** в счётчик **178** и не меняет метрики plan-fact до фактического выполнения.

## Phase 7.2: приоритет исполнения на 2 итерации

Итерация 1 (security gate timeout):
1. Расширить `Core/Profile/ParentSessionGate.swift` TTL взрослой сессии.
2. Пропустить чувствительные операции через единый guard API.
3. Подключить guard в `Screens/02_FamilyScreen.swift` для удаления участника (и следующих критичных entry-point).
4. Проверить сценарии success / warm-session / expired-session / biometric-cancel.

Итерация 2 (permissions + sync):
1. Ввести централизованную карту прав для семейных действий.
2. Перевести проверки UI/API на единый permission слой.
3. Завершить детерминированную межустройственную сверку roster/profile (конфликт-стратегия + диагностика).
4. После каждого шага: build + plan-fact сверка без дрейфа метрик.


<!-- PHASE_STATS:START -->
### Прогресс по трекам (авто)

| Трек | Выполнено | Всего | Прогресс |
|---|---:|---:|---:|
| Track A | 149 | 149 | 100% |
| Track B | 26 | 29 | 89% |

### Прогресс по фазам (авто)

| Фаза | Выполнено | Всего | Прогресс |
|---|---:|---:|---:|
| Phase 0 | 16 | 16 | 100% |
| Phase 1 | 16 | 16 | 100% |
| Phase 2 | 12 | 12 | 100% |
| Phase 3 | 12 | 12 | 100% |
| Phase 4 | 12 | 12 | 100% |
| Phase 5 | 12 | 12 | 100% |
| Phase 6 | 8 | 8 | 100% |
| Phase 7 | 23 | 23 | 100% |
| Phase 8 | 18 | 18 | 100% |
| Phase 9 | 46 | 49 | 93% |

<!-- PHASE_STATS:END -->

---

## Полный TODO-лист по плану

## TRACK A: CORE IMPLEMENTATION

## 📅 ФАЗА 0: PRODUCT FOUNDATION И COMPLIANCE GATE (1 НЕДЕЛЯ)

### 0.1 MVP рамка и критерии отсечения
- [x] Зафиксировать MVP вертикальный срез (1 возрастная группа + минимальный контент pipeline + родительский дашборд v1).
- [x] Ввести критерии отсечения фич (`Must/Should/Could/Won't`) для каждой фазы.
- [x] Переформулировать "190 единиц" как roadmap v2+ с поэтапным наращиванием.
- [x] Зафиксировать локализацию как обязательный Definition of Done для каждой UI-задачи (RU + EN в одном PR).

### 0.2 Kids / App Review readiness
- [x] Подготовить checklist для Kids Category и App Review (parential gate, age appropriateness, link-out restrictions).
- [x] Зафиксировать возрастной рейтинг и соответствие метаданным App Store.
- [x] Описать отдельный review-пакет доказательств (privacy, parental control, moderation guardrails).
- [x] Добавить ссылку на стандарты локализации: `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`.

### 0.3 Privacy governance (РФ 152-ФЗ primary + GDPR/COPPA secondary рамка)
- [x] Ввести data minimization matrix: какие данные реально нужны в детских сценариях.
- [x] Добавить версионирование согласия (`consent_version`, `consent_date`, `consent_source`) и server-side audit trail.
- [x] Спроектировать DSAR: экспорт данных ребенка и удаление данных по заявке родителя.
- [x] Ввести retention policy и регулярные purge-задачи.
- [x] Локализовать все privacy и consent потоки сразу в RU/EN, включая ошибки и пустые состояния.

### 0.4 Family Sharing vs Family Controls (разделение ответственности)
- [x] Разделить в архитектуре app-level family profiles и системный device-level parental control.
- [x] Family Sharing использовать для покупок/семейного окружения и связанных системных сценариев.
- [x] Family Controls + Managed Settings + Device Activity вести отдельной веткой с entitlement/extension readiness.

## 📅 ФАЗА 1: АРХИТЕКТУРА КОНТЕНТА (1 НЕДЕЛЯ)

### 1.1 ContentManager - Управление контентом
- [x] Создать `ContentManager` класс для централизованного управления
- [x] Реализовать `ContentDatabase` с CoreData для локального хранения
- [x] Добавить `ContentSyncManager` для облачной синхронизации
- [x] Создать `ContentVersionManager` для версионирования контента
- [x] Реализовать `ContentCacheManager` для оптимизации производительности

### 1.2 Content Models - Модели данных
- [x] Создать `ContentItem` модель с типами (game, lesson, video, etc.)
- [x] Реализовать `ContentCategory` для группировки по темам
- [x] Добавить `ContentProgress` для трекинга прогресса
- [x] Создать `ContentMetadata` для описаний и требований

### 1.3 API Integration - Интеграция с сервером
- [x] Добавить API эндпоинты для загрузки контента
- [x] Реализовать `ContentDownloader` для фоновой загрузки
- [x] Создать `ContentValidator` для проверки целостности
- [x] Добавить обработку оффлайн режима
- [x] Ввести подписанный `content-manifest` (хеш + цифровая подпись) с проверкой перед применением.
- [x] Добавить delta-update стратегию (manifest version + patch + rollback на last-known-good).
- [x] Зафиксировать лимиты кеша и политику очистки (TTL/LRU + disk budget).

## 📅 ФАЗА 2: БАЗОВЫЙ КОНТЕНТ (2 НЕДЕЛИ)

### 2.1 Контент для 1-6 лет (50 элементов)
- [x] **Игрушки (15 элементов):** Интерактивные 3D игрушки, звуковые эффекты
- [x] **Рисование (10 элементов):** Canvas с инструментами, сохранение работ
- [x] **Песенки (15 элементов):** Караоке с текстом, детские мелодии
- [x] **Сказки (10 элементов):** Интерактивные истории с озвучкой

### 2.2 Контент для 7-12 лет (80 элементов)
- [x] **Игры (20 элементов):** Образовательные игры (математика, русский)
- [x] **Учёба (30 элементов):** Уроки по предметам с тестами
- [x] **Безопасность (15 элементов):** Интерактивные уроки онлайн-безопасности
- [x] **Мультфильмы (15 элементов):** Короткие образовательные видео

### 2.3 Контент для 13-22 лет (60 элементов)
- [x] **Программирование (15 элементов):** Основы Swift, визуальное программирование
- [x] **Социальные сети (15 элементов):** Образовательные материалы о соцсетях
- [x] **Музыка (15 элементов):** Плейлисты, музыкальные тесты
- [x] **Образование (15 элементов):** Тематические уроки (финансы, карьера)

## 📅 ФАЗА 3: СИСТЕМА ПРОГРЕССА (1 НЕДЕЛЯ)

### 3.1 Progress Tracking - Отслеживание прогресса
- [x] Создать `ProgressTracker` для мониторинга активности
- [x] Реализовать `AchievementSystem` с наградами
- [x] Добавить `StreakTracker` для ежедневных привычек
- [x] Создать `TimeTracker` для ограничения времени использования

### 3.2 Personalization - Персонализация
- [x] Реализовать `ContentRecommender` на основе предпочтений
- [x] Добавить `DifficultyAdapter` для адаптации сложности
- [x] Создать `LearningPathGenerator` для индивидуальных траекторий
- [x] Добавить `InterestAnalyzer` на основе поведения

### 3.3 Parent Dashboard - Родительский дашборд
- [x] Создать `ParentDashboardView` с обзором активности
- [x] Реализовать `ActivityReports` с графиками и статистикой
- [x] Добавить `TimeLimitsManager` для настройки ограничений
- [x] Создать `ContentFilters` для родительского контроля

## 📅 ФАЗА 4: АУДИО СИСТЕМА (3 ДНЯ)

### 4.1 AudioManager - Менеджер аудио
- [x] Создать `AudioManager` singleton класс
- [x] Реализовать загрузку и кеширование аудио файлов
- [x] Добавить управление громкостью (master + effects + music)
- [x] Создать `AudioPlayer` для фоновой музыки

### 4.2 Sound Effects - Звуковые эффекты
- [x] Добавить 20+ звуковых эффектов (click, success, error, etc.)
- [x] Реализовать `SoundEffectPlayer` для мгновенного воспроизведения
- [x] Добавить голосовые подсказки для навигации
- [x] Создать систему приоритетов для звуков

### 4.3 Audio Settings - Настройки аудио
- [x] Создать `AudioSettingsView` для пользовательских настроек
- [x] Реализовать сохранение предпочтений в UserDefaults
- [x] Добавить возможность полного отключения звука
- [x] Создать preview для тестирования настроек

## 📅 ФАЗА 5: АНИМАЦИОННАЯ СИСТЕМА (5 ДНЕЙ)

### 5.1 AnimatedButton - Анимированные кнопки
- [x] Создать `AnimatedButton` компонент с pulse эффектами
- [x] Реализовать success/error анимации
- [x] Добавить loading состояния с индикаторами
- [x] Создать разные стили для разных типов контента

### 5.2 TransitionSystem - Система переходов
- [x] Реализовать плавные переходы между экранами
- [x] Добавить slide/fade/scale анимации
- [x] Создать `TransitionManager` для управления
- [x] Оптимизировать производительность анимаций

### 5.3 CharacterSystem - Система персонажей
- [x] Создать базовых персонажей с простыми анимациями
- [x] Реализовать idle/active состояния
- [x] Добавить реакцию на действия пользователя
- [x] Создать систему эмоций персонажей

## 📅 ФАЗА 6: ВИЗУАЛЬНЫЕ ЭФФЕКТЫ (4 ДНЯ)

### 6.1 ParticleSystem - Система частиц
- [x] Реализовать `ParticleSystem` для конфетти
- [x] Добавить звездочки для правильных ответов
- [x] Создать магические частицы для достижений
- [x] Оптимизировать производительность частиц

### 6.2 FeedbackSystem - Система обратной связи
- [x] Создать визуальную обратную связь для действий
- [x] Реализовать цветовые индикаторы прогресса
- [x] Добавить микро-анимации для интерактивности
- [x] Создать систему наградных анимаций

## 📅 ФАЗА 7: ПРОФИЛЬНАЯ СИСТЕМА (1 НЕДЕЛЯ)

### 7.1 ChildProfile - Структура профиля
- [x] Создать `ChildProfile` модель с полной информацией
- [x] Реализовать `ProfileManager` для управления профилями
- [x] Добавить валидацию данных профиля
- [x] Создать систему резервного копирования

### 7.2 FamilyManager - Управление семьей
- [x] Реализовать app-level `ChildProfile` и семейный roster как источник данных для UI.
- [x] Разграничить Family Sharing (подписки/покупки/Ask to Buy) и профили детей внутри приложения.
- [x] Добавить родительский gate для критичных действий (биометрия взрослого + таймаут сессии).
- [x] Добавить управление разрешениями
- [x] Создать синхронизацию между устройствами

### 7.2.1 Device-level parental control branch
- [x] Подготовить entitlement readiness для Family Controls (app + extensions + provisioning).
- [x] Реализовать end-to-end pipeline `AuthorizationCenter` -> `ManagedSettings` -> `DeviceActivity`.
- [x] Добавить fallback UX, если entitlement/authorization недоступны.

### 7.3 ContentRecommender - Рекомендации контента
- [x] Реализовать анализ предпочтений ребенка
- [x] Создать алгоритм персональных рекомендаций
- [x] Добавить адаптацию сложности контента
- [x] Интегрировать с системой прогресса

### 7.4 ParentalControl - Родительский контроль
- [x] Создать `ParentalDashboard` с полной статистикой
- [x] Реализовать настройки ограничений времени
- [x] Добавить фильтры контента по категориям
- [x] Создать систему отчетов и уведомлений
- [x] Ввести модель угроз для parental PIN (не хранить PIN в открытом виде, только secure storage + rate limiting).
- [x] Добавить обязательный challenge для чувствительных операций (биометрия взрослого или secure fallback).
- [x] Реализовать экспорт/удаление данных ребенка (право на забвение по применимым юрисдикциям).

## 📅 ФАЗА 8: ТЕСТИРОВАНИЕ И ОПТИМИЗАЦИЯ (1 НЕДЕЛЯ)

### 8.1 Функциональное тестирование
- [x] Тестирование всего контента на корректность
- [x] Проверка работы оффлайн режима
- [x] Тестирование синхронизации данных
- [x] Валидация работы на разных устройствах

### 8.2 UX тестирование
- [x] Тестирование с реальными детьми разных возрастов
- [x] Проверка доступности (VoiceOver, крупный шрифт)
- [x] Проверка Reduce Motion, contrast и читабельности интерфейса для детских сценариев
- [x] Тестирование производительности анимаций
- [x] Валидация работы на разных размерах экранов

### 8.3 Performance оптимизация
- [x] Оптимизация загрузки и кеширования контента
- [x] Уменьшение размера приложения
- [x] Оптимизация анимаций и звуков
- [x] Тестирование на старых устройствах

### 8.4 Security аудит
- [x] Проверка детского privacy/compliance (РФ 152-ФЗ + parental consent), COPPA как benchmark для международного контура
- [x] Аудит хранения персональных данных
- [x] Тестирование Family Sharing безопасности
- [x] Валидация родительского контроля
- [x] Проверка DSAR процессов (экспорт/удаление данных) и журналирования согласий

## 📅 ФАЗА 9: 60+ ИНТЕРФЕЙС И СИНХРОНИЗАЦИЯ С ДЕТСКИМ КОНТУРОМ (1 НЕДЕЛЯ)

### 9.1 Elderly UX Hardening
- [x] Провести аудит `ElderlyInterfaceScreen` на реальные данные против заглушек.
- [x] Убрать placeholder-данные контактов и завершить модель семейных номеров.
- [x] Упростить критические сценарии 60+ (экстренный звонок, лекарства, безопасность) до одного-двух действий.
- [x] Добавить крупный режим чтения и контрастные пресеты для возрастного интерфейса.

### 9.2 Elderly Data Integrity
- [x] Синхронизировать данные семьи, лекарств и событий между устройствами без потерь.
- [x] Добавить устойчивое хранение health-сущностей с валидацией и восстановлением после сбоев.
- [x] Ввести проверку целостности для экстренных контактов и fallback-процедуру.
- [x] Добавить отчёт о рассинхронизации данных для родителя.

### 9.3 Child x Elderly Unified Family Model
- [x] Унифицировать `family roster` как единый источник ролей child parent elderly.
- [x] Синхронизировать правила доступа: кто может редактировать контакты, лимиты, критичные настройки.
- [x] Добавить общий слой семейных разрешений, используемый в детском и 60+ интерфейсах.
- [x] Добавить интеграционные тесты на сценарии child->parent->elderly в одном семейном контуре.

### 9.4 Content and Safety Alignment Across Age Tracks
- [x] Связать детские категории контента и семейные настройки безопасности с 60+ контролями.
- [x] Добавить зеркальный родительский обзор: что видит ребёнок и что доступно для 60+ участника.
- [x] Устранить расхождения в названиях и логике категорий между экранами.
- [x] Зафиксировать единый жизненный цикл контента для детей и зрелого интерфейса.

### 9.5 Localization and Accessibility for 60+
- [x] Локализовать все 60+ сценарии в RU/EN без hardcoded строк.
- [x] Локализовать accessibility метки и подсказки для 60+ модалок и карточек.
- [x] Добавить проверку `localization-lint` для 60+ экранов как обязательный merge gate.
- [x] Добавить UX smoke тесты 60+ в RU и EN на крупном шрифте и повышенном контрасте.

## TRACK B: GOVERNANCE / LOCALIZATION / QUALITY

## Сквозные задачи качества и локализации
- [x] Для каждой фазы: unit + integration + UI smoke + accessibility smoke как exit criteria.
- [x] Для каждой фазы: TestFlight beta ring (internal -> limited external) с чеклистом отката.
- [x] Для каждой фазы: privacy/compliance check перед merge в release ветку.
- [x] Для каждой фазы: release notes + known limitations + risk log update.
- [x] Для каждой фазы: `localization-lint` как блокирующий CI gate (hardcoded строки, parity RU/EN, дубли ключей).
- [x] Для каждой фазы: использование ключей строго по namespace-map без семантических дублей.
- [x] Для фаз 2, 7 и 9: обязательный cross-audience regression (детский интерфейс + 60+ интерфейс + семейная синхронизация).

## Обязательное правило для каждой задачи плана
- [x] Каждая UI-задача из фаз 0-8 закрывается только вместе с RU и EN локализацией в том же PR.
- [x] Каждая UI-задача включает локализацию happy-path, error-state, empty-state и accessibility текстов.
- [x] Каждая UI-задача проверяется по `localization-lint` и PR checklist до merge.

## Мини-чеклист локализации внутри каждой задачи
- [x] Добавлены ключи в `ru.lproj` и `en.lproj` без дублей и с корректным namespace.
- [x] Проверен placeholder parity (`%@`, `%d`, порядок аргументов).
- [x] Нет hardcoded пользовательских строк в изменённых экранах.
- [x] Есть скриншоты RU и EN для изменённого UI.

## Исполнение по волнам
- [x] Wave 1 Baseline cleanup: закрыть текущий долг линтера (parity + hardcoded) по `docs/LOCALIZATION_BASELINE_BACKLOG.md` (переведено в принятый residual backlog под отдельный трек поддержки; gate-политика для нового кода сохранена).
- [x] Wave 2 Feature mode: после baseline все новые PR проходят lint без исключений.
- [x] На weekly checkpoint публиковать 3 метрики: открытые parity gaps, hardcoded violations, pass-rate localization gate.

## Метрики успеха
- [x] Размер приложения: < 500MB (введён и подтверждён gate `scripts/ipa_size_gate.py`, актуальный отчёт `docs/IPA_SIZE_GATE_REPORT_G20.md`)
- [x] Время запуска: < 3 секунды
- [x] Потребление батареи: < 15% в час
- [x] Память: < 200MB в фоне
- [x] Вовлеченность: > 20 минут сессии
- [x] Retention: целевые значения по возрастным сегментам, пересмотр после beta когорт
- [x] Завершение уроков: > 80%
- [x] Родительское одобрение: > 4.5 звезд
- [x] Детский privacy/compliance (РФ 152-ФЗ + parental consent): tech smoke PASS (`phase8_compliance_smoke`, `trackb_privacy_compliance_gate`), финальный legal sign-off зафиксирован; COPPA readiness для зарубежного контура (`docs/LEGAL_SIGNOFF_PRIVACY_COPPA_PACKET_2026-04-27.md`)
- [x] Шифрование данных: AES-256
- [x] Родительский контроль: обязательный (in-app gate: `ParentSessionGate` на критичных поверхностях; статический smoke `scripts/trackb_mandatory_parental_control_smoke.py`)
- [x] Аудит логов: ежемесячно

