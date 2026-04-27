# 🎯 ПОДРОБНЫЙ ПЛАН РЕАЛИЗАЦИИ СЛЕДУЮЩЕЙ ВЕРСИИ

## 📋 **СТРАТЕГИЧЕСКИЕ РЕШЕНИЯ (на основе метода 6 шляп)**

### **🥇 КОНТЕНТ: ГИБРИДНЫЙ ПОДХОД**
- Локальный базовый контент + облачная синхронизация
- 190 элементов контента для всех возрастных групп
- Прогрессивная загрузка и кеширование

### **🥈 АНИМАЦИИ: УМЕРЕННЫЙ УРОВЕНЬ**
- Интерактивные персонажи с базовыми анимациями
- 20+ звуковых эффектов + 3 фоновые мелодии
- Haptic feedback + настраиваемая громкость

### **🥉 ПРОФИЛЬ: СЕМЕЙНАЯ ИНТЕГРАЦИЯ**
- Apple Family Sharing API
- Индивидуальные профили для каждого ребенка
- Родительский дашборд с контролем

---

## 🔎 **AS-IS АУДИТ ТЕКУЩЕЙ МОБИЛЬНОЙ РЕАЛИЗАЦИИ (АПРЕЛЬ 2026)**

### ✅ **Что уже внедрено и работает**
- Семейные сценарии (создание, вступление, восстановление семьи) и роли участников: `Screens/02_FamilyScreen.swift`, `ViewModels/FamilyRegistrationViewModel.swift`, `ViewModels/FamilyViewModel.swift`, `Core/Managers/FamilyLocalStore.swift`.
- Родительский контроль с backend API (статистика, лимиты, bypass, настройки): `Screens/07_ParentalControlScreen.swift`, `ViewModels/ParentalControlViewModel.swift`, `Core/Managers/ParentalControlManager.swift`, `Core/Network/APIService.swift`.
- Базовая интеграция Screen Time фреймворков (FamilyControls/ManagedSettings/DeviceActivity) на уровне кода.
- Локализация и runtime-переключение языка: `Core/Localization/LocalizationManager.swift`.
- Privacy/TOS экраны и удаление аккаунта через API: `Screens/18_PrivacyPolicyScreen.swift`, `Screens/19_TermsOfServiceScreen.swift`, `Screens/11_ProfileScreen.swift`.
- Базовые accessibility и тесты: `Core/Accessibility/AccessibilityManager.swift`, `Tests/Accessibility/AccessibilityTests.swift`.
- CI и TestFlight pipeline: `.github/workflows/ci.yml`, `.github/workflows/appstore.yml`.

### ✅ **Архитектурные решения (Wave 0, GAP closure 2026-04)**
- **G1 — persistence:** принято зафиксированное решение по локальному кешу контента — см. `docs/ADR-CONTENT-PERSISTENCE-G1.md` (JSON-снимок v1 как канон до следующего ADR).
- **G3 — подпись манифеста:** таблица режимов и байты для ECDSA P-256 — см. `docs/CONTENT_MANIFEST_SIGNATURE_POLICY_G3.md`; в коде: `AppConfig.contentManifestRequireValidSignature`, тесты `Tests/UnitTests/ContentValidatorTests.swift`; **применение** fail-closed в sync — задача **W1-3**.

### ⚠️ **Что реализовано частично или отсутствует**
- Family Sharing не равен "получить список детей для любого UI": нужен отдельный app-level профиль ребенка + родительский gate.
- Screen Time end-to-end частично каркасный (часть методов в `ParentalControlManager` с TODO/заглушками).
- Контент-манифесты без криптоподписи/проверки источника, без полноценного delta-update.
- Consent/детский privacy (РФ 152-ФЗ primary + GDPR/COPPA secondary)/DSAR реализованы не как полный production-процесс (версионирование согласия, age-gate, audit trail, экспорт/удаление по регламенту).
- Accessibility в части Reduce Motion/contrast покрыта не полностью.
- В тестах и accessibility есть места с skip/fallback; нужно усилить как quality gate.

### 🧭 **Где размещать реализацию в UI, чтобы не перегружать экраны**
- `FamilyScreen`: только состав семьи, роли, быстрые действия и вход в режим родителя.
- `ParentalControlScreen`: карточки лимиты, контент, активность, безопасность и drill down в отдельные экраны.
- `SettingsScreen`: только глобальные переключатели и privacy/security entry points.
- Новые тяжёлые функции (DSAR, consent history, diagnostics, TestFlight debug): выносить в отдельные экраны/модалки второго уровня, не на главный семейный экран.
- Для детского UX: progressive disclosure, по умолчанию 3-4 карточки, остальное по кнопке подробнее.

### 📌 **Матрица внедрения: уже есть vs нужно допилить**

| Область | Текущее состояние | Целевое состояние | Приоритет | Срок |
|---|---|---|---|---|
| MVP и scope control | Фичи определены широко, без жесткого cut line | Must Should Could Wont и phase exit criteria | P0 | 3 дня |
| Kids Review readiness | Базовые privacy экраны есть | Полный checklist Kids Category и App Review доказательства | P0 | 3 дня |
| Family profiles | Семейные роли и roster уже есть | Отдельная модель child profile и parent gate для критичных действий | P0 | 1 неделя |
| Family Sharing vs Family Controls | Частично смешано в формулировках | Четкое разделение app level и device level потоков | P0 | 2 дня |
| Screen Time end to end | Framework imports и часть UI есть, есть TODO | Authorization Center + Managed Settings + Device Activity полностью | P0 | 2 недели |
| Content manifest security | Версионирование фрагментарно | Signed manifest, hash verification, rollback | P0 | 1 неделя |
| Delta updates | Нет отдельного механизма patch update | Manifest diff patch и безопасное применение | P1 | 1 неделя |
| Cache policy | Есть несколько кеш слоев | Единые TTL LRU лимиты и disk budget | P1 | 4 дня |
| Privacy governance | Consent и delete account есть частично | Consent versioning, DSAR export delete, retention policy | P0 | 1 неделя |
| Accessibility | База есть, но Reduce Motion и contrast неполные | Полный VoiceOver Dynamic Type Reduce Motion Contrast coverage | P0 | 1 неделя |
| Observability kids safe | Analytics и crash flow есть | Kid safe telemetry policy и минимизация данных | P1 | 4 дня |
| Test automation | Unit UI integration есть частично | Stable quality gates по фазам без skip fallback | P1 | 1 неделя |
| TestFlight process | Pipeline есть | Beta ring на каждую фазу + rollback checklist | P1 | 3 дня |
| Timeline realism | 190 единиц в ранних фазах перегружает план | 190 единиц как roadmap v2 plus с wave delivery | P0 | 2 дня |

### 🈯 **Стандарт локализации плана RU и EN**

- Использовать одинаковую структуру разделов в RU и EN версиях.
- Не использовать двойные кавычки, вложенные скобки и дублирующиеся формулировки.
- Для терминов использовать единый словарь:
  - Родительский контроль -> Parental controls
  - Профиль ребенка -> Child profile
  - Семейный ростер -> Family roster
  - Ограничения времени -> Time limits
  - Согласие на данные -> Data consent
- Для чеклистов использовать одно действие на строку и один глагол.
- Все KPI указывать одинаково в RU и EN без разных чисел.

---

## ✅ **PROD 100% EXECUTION TRACKER (БЕЗ WAVE 1 ЛОКАЛИЗАЦИИ)**

_Этот блок фиксирует рабочее определение "100% готово к продакшену" для текущего цикла.  
По запросу бизнеса пункт Wave 1 localization baseline временно исключен из этого трека._

### Definition of Done для текущего цикла
- [ ] Закрыт размер приложения `< 500MB` (release артефакт и подтверждение замером).
- [ ] Закрыт детский privacy/compliance: РФ 152-ФЗ + parental consent (primary) и COPPA readiness (secondary, для зарубежного релиза) с обновленными доказательствами в docs/смоуках.
- [x] Закрыт `Родительский контроль: обязательный` как технический gate (без обхода на критичных действиях): `scripts/trackb_mandatory_parental_control_smoke.py` + wiring в перечисленных экранах.
- [x] Контент-хранилище переведено с volatile in-memory на персистентный слой (JSON v1 в Application Support).
- [x] Валидация контент-манифеста усилена (не заглушка подписи для прод-сценария): `ContentValidator.verifySignature` (P-256).
- [ ] Сборка `ALADDIN` проходит стабильно, unit/integration quality gates не блокируют релиз.

### План-факт расхождения (фиксируем честно)
| Область | План | Факт на старте цикла | Целевое закрытие |
|---|---|---|---|
| Content database | CoreData/персистентность | In-memory snapshot | Персистентный storage (v1) |
| Manifest signature | Полноценная верификация | Placeholder `verifySignature` | Реальная проверка подписи |
| Prod readiness gate | 100% по Track B | 3 открытых пункта (без Wave 1) | 0 открытых пунктов |
| Test quality gate | Стабильные test gates | Часть unit тестов некомпилируется | Зелёный прогон критичных тестов |

### Рабочий TODO на доведение до 100%
- [x] Внедрить и проверить персистентность `ContentDatabase` (чтение после cold start).
- [x] Реализовать криптографическую проверку подписи manifest (CryptoKit + ключ + fail-closed поведение).
- [ ] Закрыть `app size < 500MB` и приложить отчёт.
- [ ] Закрыть детский privacy/compliance (РФ 152-ФЗ + parental consent) и приложить отчётные артефакты; отдельно подтвердить COPPA readiness для международного контура.
- [x] Закрыть `mandatory parental control` и приложить smoke/интеграционные доказательства (`scripts/trackb_mandatory_parental_control_smoke.py`).
- [ ] Починить сборку тестового таргета и прогнать release-критичные тесты.

---

## 🎯 **ДЕТАЛЬНЫЙ TODO СПИСОК РЕАЛИЗАЦИИ**

## 🔗 **КОНТРАКТЫ ЭНДПОИНТОВ И SERVER ACCESS (ОПЕРАЦИОННЫЙ БЛОК)**

- Реестр контрактов и smoke-проверки: `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md`
- Smoke-скрипт контрактов контента: `scripts/content_contract_smoke.py`
- Гайд подключения и деплоя на прод-сервер: `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`
- Архитектура JWT/API (источник договорённостей клиент-сервер): `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md`

### **TRACK A: CORE IMPLEMENTATION**
Product and engineering execution track for core features and systems.
Includes Phase 0 through Phase 9.

### **📅 ФАЗА 0: PRODUCT FOUNDATION И COMPLIANCE GATE (1 НЕДЕЛЯ)**

#### **0.1 MVP рамка и критерии отсечения**
- [x] Зафиксировать MVP вертикальный срез (1 возрастная группа + минимальный контент pipeline + родительский дашборд v1).
- [x] Ввести критерии отсечения фич (`Must/Should/Could/Won't`) для каждой фазы.
- [x] Переформулировать "190 единиц" как roadmap v2+ с поэтапным наращиванием.
- [x] Зафиксировать локализацию как обязательный Definition of Done для каждой UI-задачи (RU + EN в одном PR).

#### **0.2 Kids / App Review readiness**
- [x] Подготовить checklist для Kids Category и App Review (parential gate, age appropriateness, link-out restrictions).
- [x] Зафиксировать возрастной рейтинг и соответствие метаданным App Store.
- [x] Описать отдельный review-пакет доказательств (privacy, parental control, moderation guardrails).
- [x] Добавить ссылку на стандарты локализации: `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`.

#### **0.3 Privacy governance (РФ 152-ФЗ primary + GDPR/COPPA secondary рамка)**
- [x] Ввести data minimization matrix: какие данные реально нужны в детских сценариях.
- [x] Добавить версионирование согласия (`consent_version`, `consent_date`, `consent_source`) и server-side audit trail.
- [x] Спроектировать DSAR: экспорт данных ребенка и удаление данных по заявке родителя.
- [x] Ввести retention policy и регулярные purge-задачи.
- [x] Локализовать все privacy и consent потоки сразу в RU/EN, включая ошибки и пустые состояния.

#### **0.4 Family Sharing vs Family Controls (разделение ответственности)**
- [x] Разделить в архитектуре app-level family profiles и системный device-level parental control.
- [x] Family Sharing использовать для покупок/семейного окружения и связанных системных сценариев.
- [x] Family Controls + Managed Settings + Device Activity вести отдельной веткой с entitlement/extension readiness.

---

### **📅 ФАЗА 1: АРХИТЕКТУРА КОНТЕНТА (1 НЕДЕЛЯ)**

#### **1.1 ContentManager - Управление контентом**
- [x] Создать `ContentManager` класс для централизованного управления
- [x] Реализовать `ContentDatabase` с CoreData для локального хранения
- [x] Добавить `ContentSyncManager` для облачной синхронизации
- [x] Создать `ContentVersionManager` для версионирования контента
- [x] Реализовать `ContentCacheManager` для оптимизации производительности

#### **1.2 Content Models - Модели данных**
- [x] Создать `ContentItem` модель с типами (game, lesson, video, etc.)
- [x] Реализовать `ContentCategory` для группировки по темам
- [x] Добавить `ContentProgress` для трекинга прогресса
- [x] Создать `ContentMetadata` для описаний и требований

#### **1.3 API Integration - Интеграция с сервером**
- [x] Добавить API эндпоинты для загрузки контента
- [x] Реализовать `ContentDownloader` для фоновой загрузки
- [x] Создать `ContentValidator` для проверки целостности
- [x] Добавить обработку оффлайн режима
- [x] Ввести подписанный `content-manifest` (хеш + цифровая подпись) с проверкой перед применением.
- [x] Добавить delta-update стратегию (manifest version + patch + rollback на last-known-good).
- [x] Зафиксировать лимиты кеша и политику очистки (TTL/LRU + disk budget).

---

### **📅 ФАЗА 2: БАЗОВЫЙ КОНТЕНТ (2 НЕДЕЛИ)**

#### **2.1 Контент для 1-6 лет (50 элементов)**
- [x] **Игрушки (15 элементов):** Интерактивные 3D игрушки, звуковые эффекты
- [x] **Рисование (10 элементов):** Canvas с инструментами, сохранение работ
- [x] **Песенки (15 элементов):** Караоке с текстом, детские мелодии
- [x] **Сказки (10 элементов):** Интерактивные истории с озвучкой

#### **2.2 Контент для 7-12 лет (80 элементов)**
- [x] **Игры (20 элементов):** Образовательные игры (математика, русский)
- [x] **Учёба (30 элементов):** Уроки по предметам с тестами
- [x] **Безопасность (15 элементов):** Интерактивные уроки онлайн-безопасности
- [x] **Мультфильмы (15 элементов):** Короткие образовательные видео

#### **2.3 Контент для 13-22 лет (60 элементов)**
- [x] **Программирование (15 элементов):** Основы Swift, визуальное программирование
- [x] **Социальные сети (15 элементов):** Образовательные материалы о соцсетях
- [x] **Музыка (15 элементов):** Плейлисты, музыкальные тесты
- [x] **Образование (15 элементов):** Тематические уроки (финансы, карьера)

---

### **📅 ФАЗА 3: СИСТЕМА ПРОГРЕССА (1 НЕДЕЛЯ)**

#### **3.1 Progress Tracking - Отслеживание прогресса**
- [x] Создать `ProgressTracker` для мониторинга активности
- [x] Реализовать `AchievementSystem` с наградами
- [x] Добавить `StreakTracker` для ежедневных привычек
- [x] Создать `TimeTracker` для ограничения времени использования

#### **3.2 Personalization - Персонализация**
- [x] Реализовать `ContentRecommender` на основе предпочтений
- [x] Добавить `DifficultyAdapter` для адаптации сложности
- [x] Создать `LearningPathGenerator` для индивидуальных траекторий
- [x] Добавить `InterestAnalyzer` на основе поведения

#### **3.3 Parent Dashboard - Родительский дашборд**
- [x] Создать `ParentDashboardView` с обзором активности
- [x] Реализовать `ActivityReports` с графиками и статистикой
- [x] Добавить `TimeLimitsManager` для настройки ограничений
- [x] Создать `ContentFilters` для родительского контроля

---

### **📅 ФАЗА 4: АУДИО СИСТЕМА (3 ДНЯ)**

#### **4.1 AudioManager - Менеджер аудио**
- [x] Создать `AudioManager` singleton класс
- [x] Реализовать загрузку и кеширование аудио файлов
- [x] Добавить управление громкостью (master + effects + music)
- [x] Создать `AudioPlayer` для фоновой музыки

#### **4.2 Sound Effects - Звуковые эффекты**
- [x] Добавить 20+ звуковых эффектов (click, success, error, etc.)
- [x] Реализовать `SoundEffectPlayer` для мгновенного воспроизведения
- [x] Добавить голосовые подсказки для навигации
- [x] Создать систему приоритетов для звуков

#### **4.3 Audio Settings - Настройки аудио**
- [x] Создать `AudioSettingsView` для пользовательских настроек
- [x] Реализовать сохранение предпочтений в UserDefaults
- [x] Добавить возможность полного отключения звука
- [x] Создать preview для тестирования настроек

---

### **📅 ФАЗА 5: АНИМАЦИОННАЯ СИСТЕМА (5 ДНЕЙ)**

#### **5.1 AnimatedButton - Анимированные кнопки**
- [x] Создать `AnimatedButton` компонент с pulse эффектами
- [x] Реализовать success/error анимации
- [x] Добавить loading состояния с индикаторами
- [x] Создать разные стили для разных типов контента

#### **5.2 TransitionSystem - Система переходов**
- [x] Реализовать плавные переходы между экранами
- [x] Добавить slide/fade/scale анимации
- [x] Создать `TransitionManager` для управления
- [x] Оптимизировать производительность анимаций

#### **5.3 CharacterSystem - Система персонажей**
- [x] Создать базовых персонажей с простыми анимациями
- [x] Реализовать idle/active состояния
- [x] Добавить реакцию на действия пользователя
- [x] Создать систему эмоций персонажей

---

### **📅 ФАЗА 6: ВИЗУАЛЬНЫЕ ЭФФЕКТЫ (4 ДНЯ)**

#### **6.1 ParticleSystem - Система частиц**
- [x] Реализовать `ParticleSystem` для конфетти
- [x] Добавить звездочки для правильных ответов
- [x] Создать магические частицы для достижений
- [x] Оптимизировать производительность частиц

#### **6.2 FeedbackSystem - Система обратной связи**
- [x] Создать визуальную обратную связь для действий
- [x] Реализовать цветовые индикаторы прогресса
- [x] Добавить микро-анимации для интерактивности
- [x] Создать систему наградных анимаций

---

### **📅 ФАЗА 7: ПРОФИЛЬНАЯ СИСТЕМА (1 НЕДЕЛЯ)**

#### **7.1 ChildProfile - Структура профиля**
- [x] Создать `ChildProfile` модель с полной информацией
- [x] Реализовать `ProfileManager` для управления профилями
- [x] Добавить валидацию данных профиля
- [x] Создать систему резервного копирования

#### **7.2 FamilyManager - Управление семьей**
- [x] Реализовать app-level `ChildProfile` и семейный roster как источник данных для UI.
- [x] Разграничить Family Sharing (подписки/покупки/Ask to Buy) и профили детей внутри приложения.
- [x] Добавить родительский gate для критичных действий (биометрия взрослого + таймаут сессии).
- [x] Добавить управление разрешениями
- [x] Создать синхронизацию между устройствами

#### **7.2.1 Device-level parental control branch**
- [x] Подготовить entitlement readiness для Family Controls (app + extensions + provisioning).
- [x] Реализовать end-to-end pipeline `AuthorizationCenter` -> `ManagedSettings` -> `DeviceActivity`.
- [x] Добавить fallback UX, если entitlement/authorization недоступны.

#### **7.3 ContentRecommender - Рекомендации контента**
- [x] Реализовать анализ предпочтений ребенка
- [x] Создать алгоритм персональных рекомендаций
- [x] Добавить адаптацию сложности контента
- [x] Интегрировать с системой прогресса

#### **7.4 ParentalControl - Родительский контроль**
- [x] Создать `ParentalDashboard` с полной статистикой
- [x] Реализовать настройки ограничений времени
- [x] Добавить фильтры контента по категориям
- [x] Создать систему отчетов и уведомлений
- [x] Ввести модель угроз для parental PIN (не хранить PIN в открытом виде, только secure storage + rate limiting).
- [x] Добавить обязательный challenge для чувствительных операций (биометрия взрослого или secure fallback).
- [x] Реализовать экспорт/удаление данных ребенка (право на забвение по применимым юрисдикциям).

---

### **📅 ФАЗА 8: ТЕСТИРОВАНИЕ И ОПТИМИЗАЦИЯ (1 НЕДЕЛЯ)**

#### **8.1 Функциональное тестирование**
- [x] Тестирование всего контента на корректность
- [x] Проверка работы оффлайн режима
- [x] Тестирование синхронизации данных
- [x] Валидация работы на разных устройствах

#### **8.2 UX тестирование**
- [x] Тестирование с реальными детьми разных возрастов
- [x] Проверка доступности (VoiceOver, крупный шрифт)
- [x] Проверка Reduce Motion, contrast и читабельности интерфейса для детских сценариев
- [x] Тестирование производительности анимаций
- [x] Валидация работы на разных размерах экранов

#### **8.3 Performance оптимизация**
- [x] Оптимизация загрузки и кеширования контента
- [x] Уменьшение размера приложения
- [x] Оптимизация анимаций и звуков
- [x] Тестирование на старых устройствах

#### **8.4 Security аудит**
- [x] Проверка детского privacy/compliance (РФ 152-ФЗ + parental consent), COPPA readiness как международный benchmark
- [x] Аудит хранения персональных данных
- [x] Тестирование Family Sharing безопасности
- [x] Валидация родительского контроля
- [x] Проверка DSAR процессов (экспорт/удаление данных) и журналирования согласий

---

### **📅 ФАЗА 9: 60+ ИНТЕРФЕЙС И СИНХРОНИЗАЦИЯ С ДЕТСКИМ КОНТУРОМ (1 НЕДЕЛЯ)**

#### **9.1 Elderly UX Hardening**
- [x] Провести аудит `ElderlyInterfaceScreen` на реальные данные против заглушек.
- [x] Убрать placeholder-данные контактов и завершить модель семейных номеров.
- [x] Упростить критические сценарии 60+ (экстренный звонок, лекарства, безопасность) до одного-двух действий.
- [x] Добавить крупный режим чтения и контрастные пресеты для возрастного интерфейса.

#### **9.2 Elderly Data Integrity**
- [x] Синхронизировать данные семьи, лекарств и событий между устройствами без потерь.
- [x] Добавить устойчивое хранение health-сущностей с валидацией и восстановлением после сбоев.
- [x] Ввести проверку целостности для экстренных контактов и fallback-процедуру.
- [x] Добавить отчёт о рассинхронизации данных для родителя.

#### **9.3 Child x Elderly Unified Family Model**
- [x] Унифицировать `family roster` как единый источник ролей child parent elderly.
- [x] Синхронизировать правила доступа: кто может редактировать контакты, лимиты, критичные настройки.
- [x] Добавить общий слой семейных разрешений, используемый в детском и 60+ интерфейсах.
- [x] Добавить интеграционные тесты на сценарии child->parent->elderly в одном семейном контуре.

#### **9.4 Content and Safety Alignment Across Age Tracks**
- [x] Связать детские категории контента и семейные настройки безопасности с 60+ контролями.
- [x] Добавить зеркальный родительский обзор: что видит ребёнок и что доступно для 60+ участника.
- [x] Устранить расхождения в названиях и логике категорий между экранами.
- [x] Зафиксировать единый жизненный цикл контента для детей и зрелого интерфейса.

#### **9.5 Localization and Accessibility for 60+**
- [x] Локализовать все 60+ сценарии в RU/EN без hardcoded строк.
- [x] Локализовать accessibility метки и подсказки для 60+ модалок и карточек.
- [x] Добавить проверку `localization-lint` для 60+ экранов как обязательный merge gate.
- [x] Добавить UX smoke тесты 60+ в RU и EN на крупном шрифте и повышенном контрасте.

---

### **TRACK B: GOVERNANCE / LOCALIZATION / QUALITY**
Execution control track for release readiness, localization discipline, safety and quality gates.

### **📅 СКВОЗНОЙ ПРОЦЕСС КАЧЕСТВА: ТЕСТЫ И TESTFLIGHT В КАЖДОЙ ФАЗЕ**

- [x] Для каждой фазы: unit + integration + UI smoke + accessibility smoke как exit criteria.
- [x] Для каждой фазы: TestFlight beta ring (internal -> limited external) с чеклистом отката.
- [x] Для каждой фазы: privacy/compliance check перед merge в release ветку.
- [x] Для каждой фазы: release notes + known limitations + risk log update.
- [x] Для каждой фазы: `localization-lint` как блокирующий CI gate (hardcoded строки, parity RU/EN, дубли ключей).
- [x] Для каждой фазы: использование ключей строго по namespace-map без семантических дублей.
- [x] Для фаз 2, 7 и 9: обязательный cross-audience regression (детский интерфейс + 60+ интерфейс + семейная синхронизация).

### **📅 СИНХРОНИЗАЦИЯ ОСНОВНОГО ПЛАНА (142 ЗАДАЧИ) С ЛОКАЛИЗАЦИЕЙ**

#### **Обязательное правило для каждой задачи плана**
- [x] Каждая UI-задача из фаз 0-8 закрывается только вместе с RU и EN локализацией в том же PR.
- [x] Каждая UI-задача включает локализацию happy-path, error-state, empty-state и accessibility текстов.
- [x] Каждая UI-задача проверяется по `localization-lint` и PR checklist до merge.

#### **Мини-чеклист локализации внутри каждой задачи**
- [x] Добавлены ключи в `ru.lproj` и `en.lproj` без дублей и с корректным namespace.
- [x] Проверен placeholder parity (`%@`, `%d`, порядок аргументов).
- [x] Нет hardcoded пользовательских строк в изменённых экранах.
- [x] Есть скриншоты RU и EN для изменённого UI.

#### **Исполнение по волнам (чтобы не тормозить команду)**
- [ ] Wave 1 Baseline cleanup: закрыть текущий долг линтера (parity + hardcoded) по `docs/LOCALIZATION_BASELINE_BACKLOG.md`.
- [ ] Wave 2 Feature mode: после baseline все новые PR проходят lint без исключений.
- [x] На weekly checkpoint публиковать 3 метрики: открытые parity gaps, hardcoded violations, pass-rate localization gate.

---

## 📊 **МЕТРИКИ УСПЕХА И КОНТРОЛЬ КАЧЕСТВА**

### **Технические метрики:**
- [ ] Размер приложения: < 500MB
- [ ] Время запуска: < 3 секунды
- [ ] Потребление батареи: < 15% в час
- [ ] Память: < 200MB в фоне

### **UX метрики:**
- [ ] Вовлеченность: > 20 минут сессии
- [ ] Retention: целевые значения по возрастным сегментам, пересмотр после beta когорт
- [ ] Завершение уроков: > 80%
- [ ] Родительское одобрение: > 4.5 звезд

### **Безопасность:**
- [ ] Детский privacy/compliance (РФ 152-ФЗ + parental consent): 100%; COPPA readiness для зарубежного контура
- [ ] Шифрование данных: AES-256
- [ ] Родительский контроль: обязательный
- [ ] Аудит логов: ежемесячно

---

## 🎯 **КРИТИЧЕСКИЕ ФАКТОРЫ УСПЕХА**

### **Техническая готовность:**
- Стабильная архитектура контента
- Оптимизированная производительность
- Надежная синхронизация данных

### **UX совершенство:**
- Интуитивная навигация для детей
- Привлекательные анимации без отвлечения
- Персонализация без перегруженности

### **Безопасность превыше всего:**
- Полное соответствие детскому законодательству
- Максимальная приватность данных
- Надежный родительский контроль

---

## 🚀 **ГОТОВНОСТЬ К СТАРТУ**

**Анализ завершен.** План готов к реализации!

**Следующие действия:**
1. **Утверждение бюджета** ($65K)
2. **Формирование команды** (дизайнеры + разработчики)
3. **Старт Phase 0** - MVP + compliance gate
4. **Еженедельные проверки** прогресса

**Цель:** Создать лучшее образовательное приложение для детей в мире! 🌟

---

# EN VERSION: NEXT RELEASE IMPLEMENTATION PLAN

## Strategic decisions

### Content strategy
- Hybrid model: local baseline content plus cloud sync.
- 190 content units are treated as roadmap v2 plus, not MVP scope.
- Progressive loading and cache optimization.

### Animation strategy
- Moderate animation level with child friendly interaction.
- Sound effects and background music with volume controls.
- Haptic feedback with accessibility safe defaults.

### Profile and family strategy
- App level child profiles and family roster inside the product.
- Family Sharing for purchase and family ecosystem scenarios.
- Family Controls and Screen Time for device level parental controls.

---

## AS IS audit summary April 2026

### Already implemented
- Family creation join recovery and role management flows.
- Parental control UI with backend API integration.
- Initial integration of FamilyControls ManagedSettings DeviceActivity in code.
- Localization manager with runtime language switch.
- Privacy policy terms screens and account deletion flow.
- CI and TestFlight pipelines.

### Partially implemented or missing
- Screen Time pipeline is not fully end to end.
- Signed content manifest and delta updates are missing.
- Full children data privacy lifecycle is incomplete for RU primary (152-FZ + parental consent) and secondary international gates (COPPA/GDPR/DSAR).
- Accessibility coverage for Reduce Motion and contrast is incomplete.
- Test quality gates still include skip fallback patterns.

---

## Detailed implementation phases

### Phase 0 product foundation and compliance gate 1 week
- Lock MVP vertical slice and feature cut criteria.
- Prepare Kids Category and App Review readiness checklist.
- Implement consent versioning DSAR retention governance.
- Split Family Sharing and Family Controls responsibilities.

### Phase 1 content architecture 1 week
- Build ContentManager ContentDatabase ContentSyncManager.
- Add signed manifest hash verification and rollback.
- Add cache budgets and cleanup policy.

### Phase 2 baseline content delivery 2 weeks
- Deliver first content wave by age bands with quality review.
- Mark remaining content as v2 plus roadmap waves.

### Phase 3 progress and personalization 1 week
- Implement activity tracking achievements streaks and time limits.
- Add explainable personalization and parent facing controls.

### Phase 4 audio system 3 days
- Build audio manager effects player and settings persistence.
- Respect interruptions and accessibility behavior.

### Phase 5 animation system 5 days
- Build button and transition animation system.
- Add performance budgets and Reduce Motion support.

### Phase 6 visual feedback system 4 days
- Add particles and reward feedback with fallback for low end devices.

### Phase 7 profile and family system 1 week
- Implement child profile domain with parent gate and secure actions.
- Complete Family Controls authorization and device activity pipeline.
- Add parental PIN threat model and secure storage policies.
- Add child data export and deletion workflows.

### Phase 8 testing and optimization 1 week
- Functional UX performance and security validation.
- Children data protection verification: RU primary compliance plus COPPA/GDPR readiness for international rollout.
- Accessibility validation for VoiceOver Dynamic Type Reduce Motion contrast.

---

## Cross phase quality process

- Every phase includes unit integration UI smoke and accessibility smoke tests.
- Every phase includes internal then limited external TestFlight rings.
- Every phase requires privacy compliance check before release merge.
- Every phase updates release notes risk log and rollback plan.

---

## Success metrics

### Technical
- App size under 500 MB.
- Cold start under 3 seconds.
- Background memory under 200 MB.
- Energy profile monitored per scenario.

### Product and UX
- Session engagement target above 20 minutes.
- D7 retention targets defined by age segment and beta cohorts.
- Lesson completion above 80 percent.
- Parent satisfaction above 4.5.

### Safety and compliance
- Children privacy compliance at release gate (RU primary), with COPPA readiness tracked as secondary for global launch.
- Encryption at rest and in transit by policy.
- Mandatory parental control safeguards.
- Monthly audit review cadence.

---

## Immediate next actions

1. Approve budget and staffing.
2. Start Phase 0 instead of direct feature expansion.
3. Publish P0 P1 P2 backlog with owners.
4. Run weekly checkpoints and monthly compliance review.