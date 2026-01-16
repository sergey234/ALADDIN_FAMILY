## TODO (чеклист работ) — ведём по порядку, исправляем по 1 пункту за раз

Правила:
- **Автосохранение сразу** — только где **нет** кнопки “Сохранить”.
- Где кнопка “Сохранить” есть — **оставляем как есть**, только проверяем.
- Исправляем **по 1 пункту/ключу/правке за раз**, после каждого шага делаем быструю проверку.

### 1) NetworkProtection — missing localization keys (вариант B)
1. ~~☐ Собрать точный список missing keys для `Screens/03_NetworkProtectionScreen.swift` (только активный код) и разложить по секциям UI.~~
2. ~~☐ Собрать точный список missing keys для `Screens/24_NetworkProtectionEnergyStatsScreen.swift` и разложить по секциям UI.~~ ✅
   - **Navigation / Accessibility**
     - `network_protection_energy_title`
     - `network_protection_energy_subtitle`
     - `network_protection_energy_nav_accessibility`
     - `network_protection_energy_accessibility`
   - **Battery Impact Card**
     - `network_protection_energy_battery`
     - `network_protection_energy_battery_usage`
     - `network_protection_energy_battery_today`
     - `network_protection_energy_battery_progress`
     - `network_protection_energy_battery_efficient`
   - **Period Selector**
     - `network_protection_energy_period_today`
     - `network_protection_energy_period_week`
     - `network_protection_energy_period_month`
     - `network_protection_energy_period_selector`
     - `network_protection_energy_period_accessibility`
     - `network_protection_energy_period_selected_hint`
     - `network_protection_energy_period_switch_hint`
   - **Energy Stats**
     - `network_protection_energy_stats_title`
     - `network_protection_energy_stats_consumed`
     - `network_protection_energy_stats_time`
     - `network_protection_energy_stats_average`
     - `network_protection_energy_stats_traffic`
   - **Comparison**
     - `network_protection_energy_comparison_title`
     - `network_protection_energy_comparison_percent`
     - `network_protection_energy_comparison_chart`
     - `network_protection_energy_comparison_row`
   - **Tips**
     - `network_protection_energy_tips_title`
     - `network_protection_energy_tip_wifi`
     - `network_protection_energy_tip_disable`
     - `network_protection_energy_tip_server`
     - `network_protection_energy_tip_icon`
     - `network_protection_energy_tip_format`
3. ☐ Добавить RU+EN переводы для missing keys (делаем **по 1 ключу за раз**) в `Core/Localization/LocalizationManager.swift`.  
   - ~~network_protection_settings_title~~ ✅
   - ~~network_protection_done~~ ✅
   - ~~network_protection_retry~~ ✅
   - ~~network_protection_inactive~~ ✅
   - ~~network_protection_connect_action~~ ✅
   - ~~network_protection_disconnect_action~~ ✅
   - ~~network_protection_kill_switch~~ ✅
   - ~~network_protection_dns_leak~~ ✅
   - ~~network_protection_energy_title~~ ✅
   - ~~network_protection_energy_subtitle~~ ✅
   - ~~network_protection_energy_nav_accessibility~~ ✅
   - ~~network_protection_energy_accessibility~~ ✅
   - ~~network_protection_energy_battery~~ ✅
   - ~~network_protection_energy_battery_usage~~ ✅
   - ~~network_protection_energy_battery_today~~ ✅
   - ~~network_protection_energy_battery_progress~~ ✅
   - ~~network_protection_energy_battery_efficient~~ ✅
   - ~~network_protection_energy_period_today~~ ✅
   - ~~network_protection_energy_period_week~~ ✅
   - ~~network_protection_energy_period_month~~ ✅
   - ~~network_protection_energy_period_selector~~ ✅
   - ~~network_protection_energy_period_accessibility~~ ✅
   - ~~network_protection_energy_period_selected_hint~~ ✅
   - ~~network_protection_energy_period_switch_hint~~ ✅
   - ~~network_protection_energy_stats_title~~ ✅
   - ~~network_protection_energy_stats_consumed~~ ✅
   - ~~network_protection_energy_stats_time~~ ✅
   - ~~network_protection_energy_stats_average~~ ✅
   - ~~network_protection_energy_stats_traffic~~ ✅
   - ~~network_protection_energy_comparison_title~~ ✅
   - ~~network_protection_energy_comparison_percent~~ ✅
   - ~~network_protection_energy_comparison_chart~~ ✅
   - ~~network_protection_energy_comparison_row~~ ✅
   - ~~network_protection_energy_tips_title~~ ✅
   - ~~network_protection_energy_tip_wifi~~ ✅
   - ~~network_protection_energy_tip_disable~~ ✅
   - ~~network_protection_energy_tip_server~~ ✅
   - ~~network_protection_energy_tip_icon~~ ✅
   - ~~network_protection_energy_tip_format~~ ✅
4. ☐ После каждого добавленного ключа: проверить, что UI показывает перевод (не raw key) и сборка не сломана.
5. ☐ Подтвердить: для NetworkProtection + EnergyStats **0 missing literal keys** (обновить отчёт и этот чеклист).

### 2) Хардкод-строки UI (Must-fix)
6. ☐ Определить список “активных/используемых” экранов (исключить демо/черновики).
7. ☐ По активным экранам: заменить `Text/Button/Label(\"...\")` на `localized(\"key\")` + добавить RU/EN (по 1 строке за раз).
8. ☐ Подтвердить критерий: на активных экранах нет RU-only/EN-only хардкода (кроме чисел/единиц/эмодзи/бренда).

### 3) Wiring Toggle/Picker + автосохранение
9. ☐ Собрать список всех экранов/модалок с `Toggle/Picker` и их источников истины (`@AppStorage`/Service/ViewModel).
10. ☐ Для каждого: убрать “локальный @State без сохранения” (по 1 правке за раз), соблюдая правило про кнопку “Сохранить”.
    - ~~NetworkProtectionSettingsView: guard initial server load, чтобы не триггерить автосинк обратно на сервер~~ ✅
11. ☐ Проверить: после перезапуска приложения настройки сохраняются/восстанавливаются.

### 4) Динамические ключи локализации (6 шаблонов)
12. ☐ Для каждого шаблона: заменить строковые ключи на enum/таблицу допустимых значений (по 1 шаблону за раз).
13. ☐ Подтвердить: ключи детерминированы и покрыты RU/EN.

### 5) Финальный контроль
14. ☐ Пересобрать отчёты: missing keys = 0 (активный код), хардкод (Must-fix) = 0, wiring проверен.
15. ☐ Итоговая проверка ключевых экранов вручную.

### 6) Advanced Settings — “7 карточек” + Safari Content Blocker (2 карточки)
16. ☐ Утвердить дизайн: в `Screens/AdvancedProtectionSettingsScreen.swift` добавить 7 карточек‑функций, без переходов на другие страницы (детали только через модалки).
17. ☐ Safari (Content Blocker): сделать 2 отдельные карточки:
   - ☐ **Фильтрация сайтов** (опасный/нежелательный контент) → `ContentBlockerManager` + `FamilyContentBlockModal`
   - ☐ **Ограничение соцсетей** → `ContentBlockerManager` + `FamilyContentBlockModal` (предустановленный набор категорий)
18. ☐ Для каждой из 7 карточек: зафиксировать источник истины (42 компонента / семейные `@AppStorage` / `ContentBlockerManager`) и исключить дубль `ProtectionFeaturesManager`.
19. ~~☐ Обновить документацию “карта 42” по фактическому коду (ParentalControlScreen componentId сейчас расходится с документом).~~ ✅

### 6.1) Advanced Settings — wiring/сохранение/навигация (обязательно)
19.0 ☐ Единый TODO реализации финального плана: `docs/TODO_IMPLEMENTATION_FINAL_PLAN.md`
19.1 ~~☐ Встроить аккордеон **Safari** в Advanced Settings + честный статус `enabled/needsActivation/error` (обновлять на `onAppear` и после возврата из настроек).~~ ✅
19.2 ~~☐ Реализовать 2 пресета для Safari:~~ ✅
   - Фильтрация сайтов: `adult + violence + gambling + forums + fileSharing`
   - Ограничение соцсетей: `socialMedia`
19.3 ☐ Добавить аккордеон **Контроль и мониторинг (семья)**: Monitoring/Time/App limits (всё открывается `.sheet`, без переходов).
19.4 ☐ Добавить карточку **Блокировка угроз** (агрегатор 4 компонент) + `.sheet` на существующие модалки настроек.
19.5 ☐ Проверка сохранения (после каждого блока):
   - toggle → выйти со страницы → зайти снова
   - kill app → открыть снова → значения сохранились
19.6 ~~☐ Локализация RU/EN для новых заголовков/статусов карточек (если не reuse existing ключей).~~ ✅ (Safari)
19.7 ☐ UI: сделать “Расширенные настройки” **фиолетовым акцентом** (как цвет иконки премиум тарифа), при этом:
   - “Улучшить защиту” остаётся **золотым**
   - “История защиты” остаётся **синим**
   - реализовать через существующие дизайн‑токены/палитру (не добавлять случайный оттенок)

### 7) Исследование: настоящий Ad/Tracker Blocking (AdGuard‑уровень)
20. ☐ Исследовать вариант **B**: добавить `ContentBlockerCategory.ads` / `ContentBlockerCategory.trackers` и правила (доменные списки и/или `css-display-none`, `resource-type`), без приватных API.
21. ☐ Проработать контроль “ложных блокировок”:
   - ☐ механизм **исключений (allowlist)** на домены/сайты/правила
   - ☐ быстрый переключатель “выключить блокировку на этом сайте” (в рамках возможностей Safari Content Blocker — вероятно только через allowlist и перегенерацию правил)
   - ☐ UX: “Сообщить о проблеме” + логирование/сбор сигналов
   - ☐ стратегия обновления списков правил (версии/rollback)
22. ☐ Согласовать критерии качества: процент ложных срабатываний, тест‑набор сайтов, регресс‑план.

### 8) Advanced Settings — баги Safari/Threat + UX переносы (текущие замечания)
23. ☐ Safari: развести **2 карточки** (“Фильтрация сайтов” vs “Ограничение соцсетей”) так, чтобы:
   - ☐ “Настроить” в каждой карточке открывает **свою** модалку/контекст (не один и тот же список без разницы)
   - ☐ пресеты/категории не затирают друг друга (нужна **логика объединения**: сайты ∪ соцсети)
   - ☐ тумблеры в карточках **реально переключаются** (и ясно что именно включают/выключают)
24. ☐ Safari: определить “истину” (source of truth) для 2 карточек:
   - ☐ Safari extension state (enabled/needsActivation) = **отдельно**
   - ☐ Включенность карточек (сайты/соцсети) = **отдельно** (по правилам/категория-юнитам) + сохраняется
25. ☐ Threat: убрать “запаздывание” открытия 4 модалок (phishing/malware/mobile/network):
   - ☐ не использовать цепочку из нескольких `.sheet` одновременно
   - ☐ сделать единый маршрут (NavigationStack в sheet или `sheet(item:)` через enum destination)
26. ☐ Threat: проверить wiring + сохранение во всех 4 модалках:
   - ☐ toggle → выйти → зайти
   - ☐ kill app → открыть → значения сохранились
27. ☐ UX: исправить некрасивые переносы (“нг”, “и” на отдельных строках) в карточке “Мониторинг активности”:
   - ☐ проверить lineLimit/minimumScaleFactor/layoutPriority/fixedSize
   - ☐ убедиться, что на SE/Pro Max текст выглядит аккуратно
28. ☐ Ответить на вопрос “две защиты от угроз” (Advanced Settings vs ALADDIN Защита):
   - ☐ подтвердить что это **одни и те же componentId** (единый источник `ComponentStatusService`)
   - ☐ исключить конфликты/двойную запись и объяснить пользователю логику
29. ☐ Документировать (в `docs/…`) как мы искали missing keys:
   - ☐ grep/python: сбор `localized("key")` из активного кода (без BACKUPS/архивов) + сравнение с ключами в `LocalizationManager.swift`
   - ☐ обновление `docs/AUDIT_LOCALIZATION_MISSING_KEYS_ACTIVE.json`

Порядок фиксов (выполняем **по очереди**, по 1 правке за раз):
1. ☐ Threat: убрать задержку/пачку `.sheet` (самый критичный баг поведения)
2. ☐ Safari: сделать тумблеры карточек реально переключаемыми + сохраняемость
3. ☐ Safari: развести модалки/контент (sites vs social) + честные заголовки/описания
4. ☐ Threat: wiring + persistence в 4 модалках
5. ☐ UX: переносы текста в “Мониторинг активности”
6. ☐ Аудит пересечений “защита от угроз” между экранами + объяснение логики


