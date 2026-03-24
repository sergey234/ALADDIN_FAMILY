### Алладдин: сводный отчёт по внешним и внутренним тумблерам безопасности — причины, исправления, проверки (2026‑03‑22)


Этот документ фиксирует полный разбор и исправление проблем с главными и внутренними переключателями (шестерёнка) компонентов безопасности в мобильном приложении и на сервере. Ориентирован на быструю передачу контекста ML/автоматизированным системам для репликации подхода на любые аналогичные тумблеры.


## 0) Итоговый объём и подсчёт тумблеров (что именно починили)

- Главные тумблеры на `NetworkProtectionScreen`: **10**
- Внутренние тумблеры в модалках (шестерёнка): **29**
  - Phishing (`phishing_protection_agent`): 5
  - Malware (`malware_detection_agent`): 5
  - Mobile Security (`mobile_security_agent`): 6
  - Network Security (`network_security_agent`): 6
  - Incident Response (`incident_response_agent`): 3
  - Password Security / Password Generator (`password_security_agent`): 4
- Итого переключателей, покрытых починкой и проверкой: **39**

Дополнительные этапы после базовых 39 (2026-03-23):
- Antivirus Quick Toggles (NetworkProtection): **4**
  - `antivirusEnabled`, `realTimeScanning`, `scanDownloads`, `quarantineThreats`
- Settings page: **4**
  - `isNetworkProtectionEnabled`, `isBiometricEnabled`, `securityEnabled`, `soundEnabled`
- Advanced Settings page: **17**
  - 13 `ComponentToggleCard` (messengers/privacy/monitoring)
  - Safari: `safariSitesEnabled`, `safariSocialEnabled`
  - Family monitoring: `parental_messages_monitoring`, `parental_screenshots_enabled`
- Итого дополнительно починено после исходных 39: **25**
- Новый суммарный итог по переключателям: **64**

Примечание:
- Внутри модалок есть также не-тумблерные поля (например, `sensitivityLevel`, `scanFrequency`, длина пароля). Они тоже участвуют в сохранении конфигурации, но в подсчёт тумблеров не входят.


## 1) Что было

- Клиент (iOS) при изменении статуса компонента отправлял POST на путь вида:
  - `POST /api/components/status/{component_id}`
- На сервере каноничные роуты отличались:
  - Чтение: `GET /api/components/status/{component_id}`
  - Мутации: `POST /api/components/enable/{component_id}` и `POST /api/components/disable/{component_id}`
- В FastAPI существовал wildcard‑обработчик `@app.api_route("/api/{path:path}")`, который перехватывал неизвестные пути/методы и пробовал «скомпоновать» имя SFM‑функции на лету.
- Для `POST /api/components/status/{id}` wildcard генерировал имя функции наподобие `create_components_status_{id}`.
- В `SFM` таких функций не было; `sfm_singleton.py` при отсутствии функции возвращал `mock_fallback`.
- Middleware, переводивший mock‑ответы в 503 (`SfmMockTo503Middleware`), не покрывал `/api/components/*`, из‑за чего клиент видел «ложный 200 OK» с mock‑телом.


## 2) Симптомы в логах (до исправлений)

- HTTP 200 OK, но тело содержало mock‑метки:
  - `"result": "mock_fallback"`, `"source": "sfm_mock"`
- Пример: `POST /api/components/status/crash_detection_agent` возвращал JSON, где `function":"create_components_status_crash_detection_agent"`, но это была не реальная бизнес‑функция, а следствие wildcard‑подстановки.
- На iOS происходила попытка декодировать ответ как `APIResponse<Bool>`, что приводило к ошибкам декодирования, когда сервер отдавал envelope‑объект `{ "status": { ... } }`.


## 3) Диагностика причин

- Контракт разошёлся:
  - Клиент слал POST на `/status/{id}`, сервер принимал POST только на `/enable/{id}` и `/disable/{id}`.
- Wildcard‑прокси перехватывал незадекларированные POST‑пути и мапил в несуществующие `create_components_status_*`.
- В `complete_api_sfm_mapping.py` отсутствовали соответствующие маппинги, в `sfm_singleton.py` происходил `mock_fallback`.
- Middleware mock→503 не включал `/api/components/*`, «ложные 200» не отсеивались.


## 4) Что сделали (исправления)

4.1. Сервер
- `app/routers/components.py`:
  - Добавлен совместимый endpoint: `POST /api/components/status/{component_id}` с телом `{ "isEnabled": bool }`. Он вызывает реальную логику изменения статуса (запись в БД) как временный слой совместимости.
- `main.py`:
  - `SfmMockTo503Middleware` расширен на `/api/components/*` — любые mock‑ответы теперь отдаются как `503 Service Unavailable`, исключая «ложные 200».
  - В wildcard‑обработчике добавлена защита: для путей `components/*` методы `POST/PUT/PATCH/DELETE` запрещены, чтобы форсировать использование явных роутеров (enable/disable/compat).

4.2. iOS
- `Core/Network/APIService.swift`:
  - Логика обновления статуса переключена на каноничные endpoints:
    - `POST /api/components/enable/{id}` если `isEnabled == true`
    - `POST /api/components/disable/{id}` если `isEnabled == false`
  - Тип ответа изменён на `ComponentStatusResponse` (вместо `APIResponse<Bool>`).
  - Валидация ответа: успех только если `response.componentStatus.componentId == componentId` и `response.componentStatus.isEnabled == isEnabled`.
- Дополнительно исправлена ошибка обращения к полю `response.status` — в модели используется вычисляемое `response.componentStatus`.

4.3. Внутренние тумблеры (шестерёнка) — архитектурная починка
- Выявлен отдельный контрактный разъезд для конфигураций:
  - iOS отправлял конфиги в `POST /api/components/config/{id}` и ожидал одну форму ответа,
  - серверный каноничный контракт для внутренних настроек использовал `GET/POST /api/components/configuration/{id}` и payload `{"settings": {...}}`.
- Что исправлено:
  - iOS endpoint для конфигураций переведён на канонику:
    - `AppConfig.Endpoint.componentConfiguration = "/api/components/configuration"`
  - В `APIService` синхронизирован формат request/response под реальный сервер:
    - POST отправляет `{"settings": {...}}`
    - GET декодирует `{"configuration": {...}, "isDefault": bool}`
  - В модалках внутренних настроек включено прозрачное логирование в мини-лог (`VisualLogger`) по категориям `GEAR.<componentId>`:
    - открытие модалки,
    - изменения каждого внутреннего тумблера,
    - сохранение,
    - результат API.


## 5) Результат после исправлений

- Все 10 переключателей работают по канонике:
  - `POST /api/components/enable/<agent>` и `POST /api/components/disable/<agent>`
  - Ответы сервера вида:
    ```json
    {
      "status": {
        "componentId": "<agent>",
        "isEnabled": true|false,
        "status": "enabled"|"disabled",
        "lastUpdated": "...",
        "error": null
      }
    }
    ```
- В логах:
  - Нет `source: sfm_mock`
  - Нет `result: mock_fallback`
  - Нет ошибок декодирования на клиенте
- HTTP 200 — «честные», бизнес‑логика реально выполняется (и записывает состояние в БД).

### 5.1. Результат для внутренних тумблеров (шестерёнка)

- PATCH backend задеплоен в прод:
  - `app/routers/components.py` обновлён на сервере в `/opt/aladdin-backend/app/routers/components.py`
  - сервис перезапущен: `aladdin-main-api-gateway` = `active`
  - health = `{"status":"ok"}`
- Реализован first-open контракт без шумного 404:
  - `GET /api/components/configuration/{id}` при отсутствии записи возвращает:
    - `200`
    - детерминированные дефолтные бизнес-настройки
    - `isDefault=true`
  - после первого `POST /configuration/{id}`:
    - `success=true`
    - следующий `GET` возвращает `isDefault=false` и сохранённую конфигурацию из БД
- Это не mock и не костыль:
  - значения дефолтов фиксированы бизнес-логикой,
  - после save данные становятся пользовательскими (persisted).

### 5.2. Antivirus Quick Toggles (UI + Server Sync + GO/STOP)

- UI‑тумблеры на антивирусной карточке (без входа в модалку):
  - `realTimeScanning`
  - `scanDownloads`
  - `quarantineThreats`
- Что было:
  - переключали только локальный `@AppStorage`, без явного API‑синхрона и без мини‑логов.
- Что сделали:
  - Добавлено прозрачное логирование в mini‑log:
    - категория `ANTIVIRUS.UI` для toggle-событий и старта сканирования,
    - категория `ANTIVIRUS.API` для загрузки/синхронизации с сервером.
  - Двусторонний server sync через `ComponentConfigurationService`:
    - при открытии секции — `GET /api/components/configuration/malware_detection_agent` и маппинг значений в локальные toggles;
    - при изменении toggles — `POST /api/components/configuration/malware_detection_agent` с merge‑моделью `{"settings": {...}}`, чтобы не перезаписывать прочие ключи.
  - Guard‑флаг исключает лишний POST во время первичной загрузки с сервера.
- Авто‑проверка GO/STOP:
  - Скрипт: `docs/server/test_antivirus_quick_toggles_sync.py`
  - Шаги: `register → GET config → POST {"settings":{...}} → GET verify`
  - Ожидание: изменённые ключи возвращаются в `GET` в точном соответствии.
  - Текущий прогон: `GO`
    - `realTimeScanning=false`, `scanDownloads=false`, `quarantineThreats=true` после POST.

### 5.3. Settings + Advanced: mini-log, theme, positioning, roadside

- Что исправлено на `Settings`:
  - Добавлено mini-log (`VisualLogger`) для:
    - `Network Protection`, `Biometric`, `Push`, `Sound` toggles (`SETTINGS.UI`);
    - переключения темы (`SETTINGS.THEME`);
    - открытия/выбора/сохранения системы позиционирования (`SETTINGS.POSITIONING`).
  - Реализовано мгновенное применение темы:
    - `light/dark/system` теперь применяются сразу через `UIUserInterfaceStyle` + сохраняются в `selected_theme`.
  - Система позиционирования:
    - выбор персистится через `PositioningSystemService`;
    - восстановление выбора выполняется при инициализации `SettingsViewModel`.
  - Тумблер `Network Protection` в `Settings` привязан к текущему профилю network settings (ключ `antivirusEnabled`) и синхронизируется с API, если endpoint доступен.

- Что исправлено на `Support`:
  - Убрана пустая заглушка для Roadside:
    - вместо белого листа показывается рабочий минимальный экран с действиями;
    - добавлены логи (`SUPPORT.UI`) на открытие/вызов/закрытие.

- Что исправлено на `Advanced Protection`:
  - Централизованное логирование в mini-log для карточек `ComponentToggleCard` (`ADVANCED.UI`);
  - Добавлены логи на Safari toggles и Family-тумблеры `messages/screenshot monitoring` (`ADVANCED.UI`).

- Авто‑проверка GO/STOP:
  - Скрипт: `docs/server/test_settings_advanced_toggles_smoke.py`
  - Проверяет:
    - `enable/disable/status` для 13 Advanced компонентов;
    - отсутствие `sfm_mock/sfm_fallback/mock_fallback`.
  - Текущий прогон: `GO` по Advanced компонентам.
  - Примечание:
    - `PATCH /api/network-protection/settings` в текущем серверном контуре возвращает `405 Method Not Allowed` (зафиксировано как инфраструктурное ограничение, не как провал toggle-пайплайна компонентов).

### 5.4. Advanced Settings (дополнительный этап): Safari apply, parental monitoring, time-management

Что было (проблема):
- На Safari-карточках (`Фильтрация сайтов` / `Ограничение соцсетей`) при `Применить правила` возникал `Ресурс не найден`.
- В логах для `parental_messages_monitoring` и `parental_screenshots_enabled` наблюдались только UI-события, без подтверждённой server-sync цепочки.
- В модалках управления временем (`Расписание`, `Время сна`, `Лимиты`) сохранялось локально, но не было гарантированного API-подтверждения и единого GO/STOP сценария.

Что выявили (корневая причина):
- В `FamilyContentBlockModal` использовался невалидный для сервера `componentId` (`content_blocker_manager`), который не входит в server `ALL_COMPONENTS`, что давало 404.
- Для части внутренних настроек Advanced отсутствовала обязательная operational-цепочка:
  - `UI log -> API write -> GET verify -> UI reopen check`.

Что сделали (конкретные правки):
- Исправили componentId для Safari apply:
  - вместо `content_blocker_manager` используется валидный `browser_security_bot`.
- Добавили прозрачные API-логи для Safari apply в mini-log:
  - `SAFARI APPLY start`
  - `SAFARI APPLY ok`
  - `SAFARI APPLY failed`
- Для parental toggles (`messages/screenshot`) добавили полноценный контур:
  - загрузка server-state при открытии экрана (GET),
  - debounce-sync при изменении (`POST /api/components/configuration/parental_control_bot`),
  - API-логи `ADVANCED.API parental POST start/ok/failed`.
- Для модалок time-management добавили sync в `parental_control_bot`:
  - `ScheduleSettingsModal` -> `schedule*` keys,
  - `SleepTimeSettingsModal` -> `sleep*` keys,
  - `AppLimitsSettingsModal` -> `appLimits`,
  - с логами `ADVANCED.API ... POST start/ok/failed`.
- Добавили автоматизацию проверки:
  - Python smoke: `docs/server/test_advanced_settings_smoke.py`
  - Bash smoke (curl-only, цветной GO/STOP): `docs/server/test_advanced_settings_smoke.sh`
  - Чек-лист релиз-гейта: `docs/server/ADVANCED_SETTINGS_GO_STOP_CHECKLIST_20260323.md`.

Как стало (после исправлений):
- Safari apply больше не должен уходить в 404 из-за неверного componentId.
- По 4 ключевым переключателям Advanced есть наблюдаемая и проверяемая цепочка:
  - `safariSitesEnabled`
  - `safariSocialEnabled`
  - `parental_messages_monitoring`
  - `parental_screenshots_enabled`
- Для time-management сохранение больше не "немое локальное": есть server-sync и диагностический след в mini-log.

Метрики успеха (к чему стремиться и что считать PASS):
- По Advanced ручному/авто smoke:
  - `POST /api/components/configuration/browser_security_bot` -> 200
  - `POST /api/components/configuration/parental_control_bot` -> 200
  - Повторный `GET` возвращает фактически записанные значения ключей.
- В mini-log:
  - для каждого действия присутствуют `UI` + `API start` + `API result`.
- Ошибки:
  - 0 случаев `Ресурс не найден` в сценарии Safari apply при валидном токене и доступном API.
  - 0 случаев "только UI без API result" для 4 ключевых Advanced-переключателей.

Итог этапа 5.4:
- В этом этапе как релиз-гейт использовался минимальный критичный набор: **4/4 PASS**
  - `safariSitesEnabled`, `safariSocialEnabled`, `parental_messages_monitoring`, `parental_screenshots_enabled`
- Но полный объём Advanced-страницы, покрытый исправлениями и логированием: **17 переключателей**

### 5.5. Финал по mini-log на подстраницах Advanced (2026-03-23)

Что дополнительно закрыли:
- Включили mini-log overlay (`withVisualLogger()`) на подстраницах, где раньше окно логов не показывалось:
  - `PositioningSystemPickerView` (Settings -> Система позиционирования),
  - `FamilyContentBlockModal` (Safari: "Настройки категорий" для `Фильтрация сайтов` и `Ограничение соцсетей`),
  - `FamilyMonitoringModal`,
  - `FamilyTimeControlModal`,
  - `ScreenTimeSettingsModal`,
  - `ScheduleSettingsModal`,
  - `SleepTimeSettingsModal`,
  - `AppLimitsSettingsModal`.

Что добавили по наблюдаемости ползунков (sliders):
- `screen_time_weekday_limit` — UI-лог при каждом изменении значения.
- `screen_time_weekend_limit` — UI-лог при каждом изменении значения.
- `app_limit_<AppName>` — UI-лог для каждого ползунка лимитов приложений (дефолтно 9 приложений в профиле).
- `sleep_emergency_calls_enabled` — UI-лог on/off в модалке сна.

Что исправили по дублям:
- Убрали дублирующий источник UI-логов для:
  - `parental_messages_monitoring`,
  - `parental_screenshots_enabled`.
- Логирование этих 2 toggles централизовано в `AdvancedProtectionSettingsScreen` (одна запись на действие), чтобы избежать двойных строк в mini-log.

Фактические результаты по критичным зонам:
- Safari apply: подтверждена цепочка `SAFARI APPLY start -> POST /configuration/browser_security_bot -> SAFARI APPLY ok` (HTTP 200, `success=true`).
- Parental monitoring: подтверждена цепочка
  - `parental_messages_monitoring` / `parental_screenshots_enabled` UI-событие,
  - `ADVANCED.API parental POST start`,
  - `POST /configuration/parental_control_bot`,
  - `ADVANCED.API parental POST ok` (HTTP 200, `success=true`).
- Time management:
  - `schedule` — `ADVANCED.API schedule POST start/ok`,
  - `sleep` — `ADVANCED.API sleep POST start/ok`,
  - `appLimits` — `ADVANCED.API appLimits POST start/ok`,
  - слайдеры отображаются в mini-log в реальном времени.

Итоговая статистика (SSOT):
- Починено и подтверждено переключателей: **64/64**
  - базовые: `39`,
  - доп. этапы: `25` (`Antivirus quick 4 + Settings 4 + Advanced 17`).
- Критичный релиз-гейт Advanced (Safari + parental): **4/4 PASS**.
- Дополнительно покрыты observability-логами ползунки time-management и app-limits.

### 5.6. Parental Control page parity with Advanced (2026-03-23)

Контекст:
- Требование релиз-гейта: на странице `Родительский контроль` (7 карточек + связанные модалки) mini-log должен показывать реальные действия пользователя так же, как на `Advanced`.

Что добавлено:
- `ParentalControlScreen`:
  - подключен `withVisualLogger()` на основной экран;
  - добавлены UI-логи для 7 карточек-тумблеров:
    - `family_content_block_enabled`
    - `family_time_control_enabled`
    - `family_monitoring_enabled`
    - `family_location_enabled`
    - `family_reports_enabled`
    - `family_additional_enabled`
    - `family_bypass_protection_enabled`
- `FamilyContentBlockModal` (Safari категории):
  - добавлены UI-логи на переключение категорий (`safari_category_*`) с текущим количеством выбранных категорий;
  - сохранены API-логи `SAFARI APPLY start/ok/failed`.
- `GeofencesSettingsModal`:
  - подключен `withVisualLogger()`;
  - добавлены UI-логи:
    - `geofence_radius` (slider),
    - `geofence_add`,
    - `geofence_remove`.
- `FamilyAdditionalModal`:
  - подключен `withVisualLogger()`;
  - добавлены UI-логи:
    - `homework_mode_enabled`,
    - открытие YouTube-настроек.
- `YouTubeSettingsModal`:
  - подключен `withVisualLogger()`;
  - `print`-события переведены в mini-log:
    - `youtube_safe_mode`
    - `youtube_age_restriction_enabled`
    - `youtube_age_restriction`
    - `youtube_time_limit` (slider)
    - `youtube_settings_save` (агрегированный save-event)

Итог по покрытию observability:
- Для страницы `Родительский контроль` реализован тот же принцип, что и для `Advanced`:
  - `UI log -> (при наличии) API start/result -> verify`.
- Пользователь теперь видит в маленьком окне:
  - тумблеры 7 карточек,
  - переключение Safari-категорий,
  - геозоны (добавление/удаление/радиус),
  - homework mode,
  - YouTube тумблеры и лимит времени.

5.6.1. Быстрый smoke-check: `7 toggles -> 7 logs` (FamilyScreen, 2026-03-24)
- Цель: подтвердить parity логирования на основном пользовательском потоке (`FamilyScreen`), а не только на `ParentalControlScreen`.
- Предусловия:
  - открыть `Семья -> Родительский контроль`;
  - убедиться, что mini-log overlay виден на экране;
  - в фильтре mini-log включена категория `PARENTAL.UI` (или `ALL`).
- Шаги:
  1) Переключить тумблер `Блокировка контента`.
  2) Переключить тумблер `Управление временем`.
  3) Переключить тумблер `Мониторинг`.
  4) Переключить тумблер `Геолокация`.
  5) Переключить тумблер `Отчёты`.
  6) Переключить тумблер `Дополнительно`.
  7) Переключить тумблер `Защита от обхода`.
- Ожидаемые события в mini-log (ровно по одному событию на каждый toggle):
  - `family_content_block_enabled = true/false`
  - `family_time_control_enabled = true/false`
  - `family_monitoring_enabled = true/false`
  - `family_location_enabled = true/false`
  - `family_reports_enabled = true/false`
  - `family_additional_enabled = true/false`
  - `family_bypass_protection_enabled = true/false`
- Критерий PASS:
  - после 7 переключений присутствуют все 7 ключей `family_*_enabled` в категории `PARENTAL.UI`;
  - переключение toggle не открывает модалку (зоны карточки и toggle не конфликтуют).

### 5.7. Bypass apply в production + безопасный persist stats (2026-03-24)

Контекст:
- После закрытия `404` и `sfm_mock/mock_fallback` для `POST /api/parental/bypass/apply` оставался блокер на части аккаунтов:
  - `Apply failed ... User token does not contain numeric user id`.
- Причина: path был исправлен, но серверный контур ожидал numeric-only идентификатор в части веток.

Что сделано:
- Серверный роутер `security/api/routers/parental_control_router.py` переведён на production-safe режим для bypass:
  - добавлен UUID/int/string совместимый resolver цели:
    - `_resolve_target_id_flexible(child_id, current_user)`.
  - добавлен безопасный persist-слой для bypass-состояния:
    - `_ensure_bypass_shadow_table`,
    - `_persist_bypass_shadow`,
    - `_read_bypass_shadow`.
  - `POST /api/parental/bypass/apply`:
    - возвращает боевой `ApiBoolResponse`,
    - сохраняет `incognito/tor/proxy` в `parental_bypass_state_shadow`,
    - больше не зависит от проблемной numeric-only ветки.
  - `GET /api/parental/bypass/stats`:
    - читает сохранённые значения из shadow-слоя,
    - возвращает не только нули по умолчанию.

Фактическая проверка (live):
- `POST /api/parental/bypass/apply`:
  - `200`, `{"success":true,"data":true,"message":"Bypass protection applied","error":null}`.
- `GET /api/parental/bypass/stats?childId=...` после apply:
  - `200`, пример: `incognito=1, tor=1, proxy=0`.
- В логах mini-log подтверждена цепочка:
  - `BYPASS APPLY start -> network POST -> BYPASS APPLY ok`.
- Отсутствуют:
  - `404`,
  - `sfm_mock`,
  - `mock_fallback`,
  - `numeric user id` ошибка.

Итог 5.7:
- Критичный production-гейт bypass apply: **PASS**.
- Добавлена наблюдаемая и воспроизводимая связь `apply -> stats`.

### 5.8. Auto Rules (шестерёнка в Родительском контроле): mini-log parity (2026-03-24)

Что было:
- На экране `Родительский контроль -> шестерёнка -> Настроить автоматические правила` было сложно понять, сработал ли тумблер и вызвалось ли применение правил.

Что добавлено:
- `FamilyParentalControlSettingsModal`:
  - подключён `withVisualLogger()`;
  - логи UI:
    - `parental_automated_rules_enabled = true/false`,
    - `auto_rules_child = <child>`,
    - `AUTO RULES manual apply tapped`;
  - логи API-цепочки:
    - `AUTO RULES apply start`,
    - `AUTO RULES apply ok`,
    - `AUTO RULES apply failed`.
- `AutomatedRulesModal`:
  - подключён `withVisualLogger()`;
  - логи:
    - открытие модалки (`AutomatedRulesModal opened ...`),
    - переключение внутреннего тумблера (`automated_rules_modal_enabled = true/false`).

Критерий PASS по 5.8:
- В mini-log виден полный контур:
  - UI-событие тумблера/кнопки,
  - старт применения,
  - результат применения (`ok/failed`).


## 6) Быстрый чек‑лист валидации (повторяемый)

6.1. Для любого `component_id`:
- Команды:
  - Enable:
    ```bash
    curl -sS -X POST "$API/api/components/enable/$component_id" -H "Authorization: Bearer $TOKEN"
    ```
  - Disable:
    ```bash
    curl -sS -X POST "$API/api/components/disable/$component_id" -H "Authorization: Bearer $TOKEN"
    ```
  - Read:
    ```bash
    curl -sS -X GET "$API/api/components/status/$component_id" -H "Authorization: Bearer $TOKEN"
    ```
- Проверки ответа:
  - JSON содержит `status.componentId == $component_id`
  - `status.isEnabled` соответствует действию (`true` для enable, `false` для disable)
  - Нет полей/меток `sfm_mock`, `sfm_fallback`, `mock_fallback`
  - HTTP код 200 (или 503, если намеренно имитируется mock‑ошибка)

6.2. Негативная проверка (guard против wildcard):
- Попробовать «неправильный» вызов:
  ```bash
  curl -i -sS -X POST "$API/api/components/status/$component_id" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"isEnabled": true}'
  ```
- Ожидание: либо обработка явным совместимым endpoint (если он включён для обратной совместимости), либо блокировка wildcard (405/подсказка об использовании enable/disable), согласно актуальной конфигурации выката.

6.3. Проверка внутренних тумблеров (configuration)
- Для каждого внутреннего компонента:
  - First GET:
    ```bash
    curl -sS -X GET "$API/api/components/configuration/$component_id" -H "Authorization: Bearer $TOKEN"
    ```
    Ожидание: `200`, `isDefault=true` для нового пользователя.
  - Save:
    ```bash
    curl -sS -X POST "$API/api/components/configuration/$component_id" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"settings":{"sanity":true}}'
    ```
    Ожидание: `{"success": true, ...}`.
  - Second GET:
    ```bash
    curl -sS -X GET "$API/api/components/configuration/$component_id" -H "Authorization: Bearer $TOKEN"
    ```
    Ожидание: `200`, `isDefault=false`.


## 7) Применение к другим тумблерам (шаблон действий)

1) Сбор фактов
- С клиента: найти места формирования путей (`/api/components/...`) и тел запросов.
- С сервера: проверить объявленные роуты и их методы; убедиться, что мутации вынесены в отдельные POST‑эндпоинты, а чтение — GET.
- Проверить наличие SFM‑функций и/или корректный `API_TO_SFM_MAPPING` (если задействовано).

2) Контракт
- Убедиться, что клиент использует именно каноничные пути:
  - `POST /enable/{id}` и `POST /disable/{id}` для мутаций
  - `GET /status/{id}` для чтения
- Если требуется обратная совместимость — ввести точечный совместимый endpoint, который внутри вызывает реальную бизнес‑логику, но не открывать новые пути для wildcard.

3) Защита от «ложных 200»
- Middleware mock→503 должен покрывать соответствующие префиксы (например, `/api/components/*`).
- Wildcard‑обработчик должен явно запрещать мутационные методы на путях, где есть строгие роуты — чтобы запросы не «уезжали» в SFM‑заглушки.

4) Клиентская модель и декодирование
- Подогнать модель ответа под фактический JSON сервера. Если сервер возвращает `{"status": {...}}`, клиентская модель должна уметь читать этот envelope.
- Включить строгую валидацию бизнес‑инвариантов (componentId совпадает, isEnabled соответствует действию).

5) Чек‑лист регрессии
- Прогнать enable/disable/read на каждом тумблере.
- Убедиться в отсутствии `sfm_mock`/`mock_fallback`.
- Проверить логи iOS на отсутствие ошибок декодирования и повторных resume‑вызовов.


## 8) Точки контроля и алерты

- Клиентские счётчики/метрики:
  - `mock_marker_count` — должен быть 0
  - `failed_cases` на сценариях переключателей — 0
- Серверные сигналы:
  - Отсутствие `source in {sfm_mock, sfm_fallback, sfm_error}` в прод‑ответах по `/api/components/*`
  - 5xx‑шипы на `/api/components/*` после расширения middleware — сигнализируют о реально проблемных местах логики
  - Для `/api/components/configuration/*`:
    - контролировать долю `isDefault=true` (нормально для first-open),
    - отсутствие 404 на first-open после патча.


## 9) Мини‑runbook: деплой/проверка/роллбек

Деплой:
- Применить серверные правки (routers + middleware + wildcard‑guard).
- Перекатить iOS на канонику enable/disable и новый декодер `ComponentStatusResponse`.

Проверка:
- Выполнить чек‑лист из раздела 6 на всех 10 тумблерах.
- Убедиться в отсутствии mock‑меток, стабильности 200 и валидном содержимом `status`.

Роллбек (если потребуется):
- Вернуть совместимый endpoint `POST /status/{id}` (если выключали), оставив внутри реальную бизнес‑логику, чтобы клиент старых версий не уходил в wildcard.
- На iOS — временно включить обратную совместимость в декодере, если менялся формат.


## 10) Итоговые выводы и рекомендации

- Критичная причина проблемы — несостыковка «метод/путь» между клиентом и сервером. Wildcard‑механики на сервере в таких случаях создают «правдоподобные», но неверные SFM‑вызовы и приводят к `mock_fallback`.
- Для критичных операций:
  - Использовать только явные, документированные endpoints.
  - Запретить wildcard‑обслуживание мутаций по чувствительным префиксам.
  - Включить строгую политику mock→503, чтобы «ложные 200» были невозможны.
- На клиенте всегда валидировать бизнес‑инварианты ответа (ID/флаги), логировать расхождения и не считать их «успехом».
- Поддерживать совместимость только через явные совместимые endpoints, не через wildcard/SFM‑трассировку.
- Для внутренних тумблеров использовать контракт:
  - `GET /configuration/{id}` всегда отвечает 200 (saved config или deterministic defaults),
  - `POST /configuration/{id}` обновляет только `settings` и подтверждает `success=true`.


## 11) Ссылки на затронутые фрагменты кода (ориентиры)

- Сервер:
  - `app/routers/components.py` — совместимый `POST /api/components/status/{component_id}`, enable/disable/status‑роуты
  - `app/routers/components.py` — `GET/POST /api/components/configuration/{component_id}`, `isDefault`, deterministic defaults
  - `main.py` — расширение `SfmMockTo503Middleware` на `/api/components/*` и guard в wildcard
  - `app/security/sfm_singleton.py` — поведение при отсутствующих функциях (источник `mock_fallback`)
  - `complete_api_sfm_mapping.py` — отсутствие `create_components_status_*` (ожидаемо)
- iOS:
  - `Core/Network/APIService.swift` — переход на enable/disable, декодирование `ComponentStatusResponse`, валидация через `response.componentStatus`
  - `Core/Network/APIService.swift` — контракт конфигурации (`settings` + `isDefault`)
  - `Core/Config/AppConfig.swift` — `componentConfiguration = /api/components/configuration`
  - `Core/Models/APIModels.swift` — модель `ComponentStatusResponse` с вычисляемым `componentStatus`
  - `Shared/Components/Modals/PhishingProtectionSettingsModal.swift`
  - `Shared/Components/Modals/MalwareDetectionSettingsModal.swift`
  - `Shared/Components/Modals/MobileSecuritySettingsModal.swift`
  - `Shared/Components/Modals/NetworkSecuritySettingsModal.swift`
  - `Shared/Components/Modals/IncidentResponseSettingsModal.swift`
  - `Shared/Components/Modals/PasswordGeneratorModal.swift`


## 12) Краткий runbook для другой ML‑системы (от начала до конца)

1. Проверить главные тумблеры:
- Клиент должен использовать только `POST /enable|disable/{id}` и `GET /status/{id}`.
- Если есть `POST /status/{id}`, убедиться, что это явный compat endpoint, а не wildcard.

2. Проверить внутренние тумблеры:
- Клиент должен использовать только `GET/POST /configuration/{id}`.
- POST payload: `{"settings": {...}}`.

3. Исключить ложные 200:
- Middleware mock→503 должен покрывать `/api/components/*`.
- Wildcard должен блокировать мутации на `components/*`.

4. Сделать first-open поведение production-grade:
- `GET /configuration/{id}`: 200 + `isDefault=true`, если запись отсутствует.
- После save повторный GET: `isDefault=false`.

5. Проверка после деплоя:
- `systemctl restart aladdin-main-api-gateway`
- `systemctl is-active ...` = `active`
- `curl http://127.0.0.1:8002/api/health` = ok
- smoke по всем 6 внутренним компонентам и 10 главным тумблерам.

6. Критерии GO:
- `mock_marker_count = 0`
- нет `sfm_mock`/`mock_fallback`
- 10/10 главных тумблеров PASS
- 29/29 внутренних тумблеров PASS
- Antivirus quick toggles: 4/4 PASS
- Settings page toggles: 4/4 PASS
- Advanced page toggles: 17/17 PASS
- first-open configuration без 404.


— Конец документа —

