# План-рекомендация для следующей ML‑системы (2026‑03‑28)

Этот документ — краткая, практичная инструкция: что уже сделано, в чём проблема, что именно требуется сделать для 100% боевых, «честных» данных по всем компонентам (42) и функциям безопасности (138), и как это проверить.

**Единый список того, что ещё не закрыто (включая 11 задач из старого трекера и хвосты после него):** `docs/REMAINING_TASKS_MASTER.md`.

## 1) Краткий контекст
- Клиент (iOS) стабилизирован: единый источник `componentsAnalytics`, анти‑livelock, Retry, мини‑логи, Dark Web переведён на агрегатор; все mock‑ответы на уровне gateway/middleware блокируются (503).
- Сервер (пять доменов компонентной аналитики: Dark Web, Identity Theft, Tracker, Location Bubble, Data Cleanup): основной путь **stats + list** и персистентность на стороне API описаны в §2.1 (миграции, ingest, чтение из БД). Дальше по плану — **gateway precision**, **наблюдаемость**, **полная верификация 42/138** и наполнение данными по SLA, а не «включить таблицы с нуля».

## 2) Что уже реализовано (факт)
- Gateway/middleware:
  - Блокировка `sfm_mock/mock_fallback` → 503 (включая `/api/reports/*`, `/api/family/*` и т.д.).
  - Нормализация компонентных ответов в единый DTO v1 (метрики — строки, согласованные ключи).
- Precision‑роутинг: ключевые семейства подключены так, чтобы не проваливаться в wildcard/SFM.
- iOS:
  - Аналитика переведена на `componentsAnalytics` (единый источник), удалены повторные GET.
  - Добавлены watchdog/дефер/дебаунсы/минимизация публикаций (устранён livelock).
  - **Dark Web scan (старт):** клиент вызывает боевой **`POST`** на `…/dark-web/scan/start` (запись события на сервере); легаси‑**GET** не используется. **Продуктовый рубильник:** `AppConfig.isDarkWebServerScanEnabled` / ключ `UserDefaults` `dark_web_server_scan_enabled` — если ключ **не** задан, скан **включён**; явное `false` отключает UI и сетевые вызовы скана без пересборки.
- Контрактные смоук‑тесты для компонентных DTO: `tools/contract_tests_components.py` на **stdlib** (`urllib`), без зависимости **`requests`**; переменная окружения `ALADDIN_API_BASE` (команды — в `docs/ANALYTICS_COMPONENTS_CONTRACT_SMOKE.md`).

## 2.1) Текущий статус выполнения (2026‑04‑19)
- Выполнено:
  - A. Миграции БД по 5 доменам (схемы/таблицы/индексы/UNIQUE для идемпотентности).
  - B. Минимальный ingestion (идемпотентные upsert’ы + функции агрегатов; свежесть подтверждена).
  - C. Боевые stats‑роутеры 5 доменов читают из БД (200 OK; нет `reports_compat/sfm_mock/mock_fallback`).
  - Расширение C на **list‑эндпоинты** с курсором: реализовано в `security/api/routers/reports_router.py` (напр. `/dark-web/leaks/list`, `/identity-theft/attempts/list`, …); на проде отвечают **200** с полем `items`.
  - `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` дополнен пошаговым алгоритмом входа/аудита и блоком malware/threats/quarantine.
  - **Malware (iOS + API):** PostgreSQL `user_malware_threats`, запись при скане с JWT, карантин `POST /api/malware/quarantine/action`, метаданные + `file_hash`, смоук **`tools/smoke_malware_threats_persist.py`** (реальный прод: скан EICAR → список → quarantine → `status=quarantined`).
  - **Смоук отчётов по плану F:** **`tools/smoke_reports_five_domains.py`** — 7×`stats` (включая driving и ai-categories) + 5×list, проверка отсутствия mock‑маркеров в теле ответа.
  - **Контракт компонентных stats (расширение):** **`tools/contract_tests_components.py`** — регистрация устройства → JWT → GET канонических `stats` (в т.ч. driving week, dark-web, identity-theft, privacy/*, ai-categories); **503** по политике блокировки моков считается допустимым проходом; транспорт только **stdlib** (без `requests`).
  - **iOS Dark Web scan:** см. §2 (POST + рубильник); дублирующий клиент в `Family_Registration_Removal_Files/Client/APIService.swift` выровнен по **POST** с основным `APIService`.
- В работе:
  - D. **Precision `/api/reports/*`** — для `main:app` на `:8002` закрыто; файл **`api_gateway.py`** на сервере выровнен с репо (см. §2.2 п.1). Если где‑то ещё поднимают **отдельный** процесс gateway — сверять с репозиторием вручную (`docs/REMAINING_TASKS_MASTER.md` → B5).
- Осталось (см. **очередь §2.2** и **`docs/REMAINING_TASKS_MASTER.md`**):
  - E. Наблюдаемость **на инфраструктуре** (вкатить правила/дашборд; см. §5.3 obs‑5).
  - F. Регулярный прогон смоуков/контрактов в CI + секрет базового URL; ручные `curl` по чеклисту §7.
  - Инвентаризация и приёмка **42/138** — канон: `docs/audit/AUDIT_42_INVENTORY.md`, `docs/audit/EXTENDED_138_CHECKLIST.md`.

## 2.2) Очередь выполнения (по порядку, без расползания по прочим TODO‑файлам)

Делать **строго по шагам**; следующий шаг не начинать, пока не зафиксирован результат предыдущего (лог смоука, PR, деплой по гайду).

1. **[precision-gw]** — **выполнено (код + прод 2026‑04‑19):** `api_gateway.py` / `api_gateway_server_current.py` + `reports_router` на хосте; `main:app` на `:8002` с precision `/api/reports/*`; контроль `ALADDIN_API_BASE=… python3 tools/contract_tests_components.py` → **7/7**.
2. **[obs-5]** — **в репозитории зафиксированы артефакты (2026‑04‑19):** пороги `docs/observability/THRESHOLDS_CONFIRMED.md`; пример правил Prometheus `docs/observability/prometheus_aladdin_analytics_alerts.example.yml`; чеклист PII `docs/observability/PII_METRICS_CHECKLIST.md`; минимум панелей Grafana `docs/observability/GRAFANA_DASHBOARD_MINIMUM.md`. Экспортёр freshness уже в **`main.py`** и **`api_gateway.py`** (`/metrics`, gauge `aladdin_analytics_freshness_seconds`). **Осталось на инфраструктуре:** применить YAML в реальном Prometheus/Alertmanager, импортировать дашборд в Grafana.
3. **[driving-verify]** — **автосмоук 1‑го уровня:** `ALADDIN_API_BASE=… python3 tools/smoke_plan_cards_driving_ai.py` (ветка Driving); полная цепочка ingest→SLA + мини‑лог iOS — в backlog.
4. **[ai-categories-verify]** — то же скрипт, ветка AI Categories; полная верификация содержимого — в backlog.
5. **[extended-42-verify]** — журнал старта в **§5.4**; дальше заполнять пакетами по §5.2.
6. **CI** — workflow **`.github/workflows/api-contract-components.yml`**: Ubuntu, `contract_tests_components.py` + `smoke_plan_cards_driving_ai.py`; опционально секрет `ALADDIN_CONTRACT_API_BASE`, иначе дефолтный базовый URL в скриптах.

## 3) Главная проблема
Исторически «compat» давал контракт без боевых цифр. После шагов A–C (§2.1) **персистентный слой и чтение stats/list из БД** для пяти доменов заведены; остаётся риск **пустых или редко обновляемых агрегатов** без нормального **ingest‑потока по SLA**, без **наблюдаемости (freshness)** и без завершённой **precision‑маршрутизации** на всех входах (в т.ч. отдельный gateway). Клиент по-прежнему честно показывает пустоту/503, если данных нет или маршрут заблокирован политикой моков.

## 4) Что конкретно сделать (шаги А→G)

- A. База данных (PostgreSQL) — создать и применить миграции по 5 доменам:
  - darkweb_leaks(id, data_type, value_or_hash, leak_date, source, severity, status, created_at)
  - darkweb_scans(id, method, status, created_at)
  - darkweb_stats(total, new, resolved, critical, last_scan_at)
  - identity_attempts(id, data_type, action, severity, timestamp, details)
  - identity_stats(total_attempts, blocked, suspicious)
  - tracker_blocks(id, tracker_name, blocked_count, last_blocked_at)
  - tracker_stats(total_blocked, blocked_this_week)
  - location_requests(id, app_name, action, accuracy, timestamp)
  - location_stats(blocked, allowed, modified, current_accuracy)
  - cleanup_records(id, cleanup_date, freed_space_bytes, categories_json)
  - cleanup_stats(total_freed_bytes, last_cleanup_at, cleanups_count)

- B. Ingestion (агенты/пайплайны) — включить поток данных:
  - события → очередь/consumer → upsert в таблицы;
  - материализованные представления (или cron‑агрегации) для суточных/недельных сводок.

- C. Боевые роутеры (без SFM) — читать из БД и возвращать совместимый JSON:
  - GET `/api/reports/dark-web/{stats,leaks,scans}`
  - GET `/api/reports/identity-theft/{stats,attempts}`
  - GET `/api/reports/privacy/location/{stats,requests}`
  - GET `/api/reports/privacy/cleanup/{stats,records}`
  - GET `/api/reports/privacy/tracker/{stats,top}`
  - (Gateway уже умеет маппить к DTO v1 — допускается вернуть «сырой» JSON, который он нормализует.)

- D. Gateway/precision — подключить новые роутеры как precision (никаких wildcard/SFM), оставить блок мока/нормализацию.

- E. Наблюдаемость/SLA — добавить:
  - метрики RPS/latency p50/p95/error%/5xx rate (Prometheus pull; http_* с лейблами job=gateway, route, method, code, env, version);
  - freshness: SQL‑view `analytics_freshness` + нативный Prometheus pull‑экспортёр (в gateway/sidecar), gauge `aladdin_analytics_freshness_seconds{domain=...}` = now - last_event_at, кеш 30–60 сек, RO‑подключение к БД;
  - алёрты (Alertmanager):
    - NoFreshData: darkweb≤72h, identity≤24h, tracker≤12h, location≤6h, cleanup≤168h,
    - Latency p95>500ms (10m),
    - 5xx rate > 1% (5m);
  - Grafana: единый дашборд (RPS, p50/p95, 5xx%, freshness per domain) с фильтрами по env/version и аннотациями релизов;
  - логи ошибок парсинга/БД; PII‑аудит лейблов/логов (нет emails/phones/hash значений в метриках/лейблах).

- F. Деплой и проверка:
  - Применить миграции → задеплоить роутеры → перезапустить gateway.
  - Прогнать:
    - `tools/contract_tests_components.py` (ожидаем 200 OK или 503 для явно заблокированных моков);
    - ручные GET всех новых эндпоинтов (ожидаем 200 OK, без mock‑маркеров; при пустых данных — нули/пустые массивы).

- G. Разморозка клиентских фич (Dark Web scan):
  - **Сделано на iOS:** боевой **POST** старта скана + рубильник в UserDefaults (по умолчанию включено).
  - **Продуктово:** при необходимости «заморозки» для стора — выставить `dark_web_server_scan_enabled = false` без смены кода; при полной готовности оставить ключ незаданным или `true`.
  
- H. Почему «5 из 7 карточек» и что с оставшимися двумя:
  - Эти 5 доменов (Dark Web, Identity Theft, Tracker, Location Bubble, Data Cleanup) — первыми выровнены по схеме A→C (БД, ingest, роутеры); дальнейшая работа — **SLA данных**, gateway, наблюдаемость и полная инвентаризация 42/138.
  - Оставшиеся 2 карточки («Driving», «AI Categories») — проходят такую же верификацию по шаблону 5.2 (источник→БД/ingest→роутер→DTO→gateway precision).
  - Если выявим compat/отсутствие провайдера — применяем те же шаги A→G точечно для соответствующей карточки. Это не «передел плана», а локальное дополнение.

## 5) Туду‑лист: 42 компонента и 138 функций безопасности (инвентаризация и верификация)

> Задача ML‑системы: пройти по каждому компоненту/функции, связать «экран/фича → endpoint → провайдер данных → таблицы/агенты», и убедиться, что в проде отображаются реальные значения.

### 5.1. Инвентаризация (скелет чек‑листа)
- Компоненты (42) — группы и типовые примеры:
  - 7 карточек «Компоненты защиты» (дневные KPI): Driving, Dark Web, Identity, Location Bubble, Data Cleanup, Tracker, AI Categories.
  - Расширенная защита ALADDIN (остальные 35 компонентов): сети, устройства, угрозы/квазиреальные симуляторы, родительский контроль (углублённые подпакеты), система, уведомления, подписка и т.д.
- Функции (138): суммарно по всем экранам/модалкам/операциям (включая аналитические и action‑эндпоинты).

### 5.2. Шаблон проверки для каждого компонента
1) Привязка UI → endpoint’ов (GET/POST).
2) Источник данных на сервере:
   - провайдер (агент/процесс),
   - таблицы/представления,
   - периодичность обновления.
3) Контракт ответа: совместим с DTO v1 (или маппится gateway).
4) Gateway precision: не уходит в wildcard/SFM.
5) Смоук:
   - 200 OK, без `sfm_mock/mock_fallback`/`source: mock`,
   - при «пусто» — нули/пустые массивы,
   - задержка/таймауты в пределах SLA.
6) Клиент:
   - не шлёт прямые повторные GET, берёт из `componentsAnalytics`,
   - корректно показывает «Нет данных»/Retry,
   - mini‑лог фиксирует источник (api/cache) и причины пустоты.

### 5.3. Список задач (родительские тикеты)
- [in_progress] audit-42-inventory: Полная карта «экран/фича → endpoint → БД → агент → SLA». **Каноническая живая таблица:** `docs/audit/AUDIT_42_INVENTORY.md` (заполнять до `inventory=ok` по всем 42; старые отчёты `ПОЛНЫЙ_АНАЛИЗ_42_*` — справочно, не заменяют эту таблицу).
- [completed] db-migrations-5: Миграции под 5 доменов (DarkWeb/Identity/Tracker/Location/Cleanup).
- [completed] ingest-5: Настроить ingestion (очередь/consumer), MVs/cron агрегаты.
- [completed] routers-5: Боевые handlers чтения из БД для `stats` и **list** (cursor) по 5 доменам в `reports_router.py`.
- [completed] precision-gw: Precision `/api/reports/*` в коде + выкат на прод; wildcard `reports/*` в `api_gateway.py` → 503.
- [in_progress] obs-5: Наблюдаемость — **код/доки в репо [completed]**; **операции на прод‑инфраструктуре [pending]** (Prometheus rules, Alertmanager, Grafana, HTTP p95/5xx при готовности метрик). Детали: `docs/REMAINING_TASKS_MASTER.md` → B2, B3.
  - [completed] obs-freshness-exporter: Gauge + фоновое обновление в **`main.py`** и **`api_gateway.py`**, scrape `/metrics`.
  - [completed] obs-alerts-rules (репо): пример правил — `docs/observability/prometheus_aladdin_analytics_alerts.example.yml` (вкатить в боевой Prometheus вручную).
  - [completed] obs-grafana-dashboard (репо): минимум панелей — `docs/observability/GRAFANA_DASHBOARD_MINIMUM.md` (импорт JSON в Grafana вручную).
  - [completed] obs-pii-audit-metrics (репо): чеклист — `docs/observability/PII_METRICS_CHECKLIST.md`.
  - [completed] obs-thresholds-confirm: `docs/observability/THRESHOLDS_CONFIRMED.md`.
- [completed] smoke-contracts (база): автосмоуки `tools/smoke_malware_threats_persist.py`, `tools/smoke_reports_five_domains.py` (прод, без mock‑маркеров). Расширенный прогон **`tools/contract_tests_components.py`** — **только stdlib** (`urllib`), **`requests` не требуется**; прогон: `ALADDIN_API_BASE=<API> python3 tools/contract_tests_components.py`.
- [pending] extended-42-verify: Финальная верификация 42/138 с реальными данными (BusinessOK не только по контракту, но и по содержанию). **Трекер:** `docs/audit/EXTENDED_138_CHECKLIST.md`.
- [completed] unfreeze-dw-scan: Клиент iOS вызывает боевой **POST** старта скана; включение/выключение — **рубильник** `dark_web_server_scan_enabled` (см. §2). Дальнейшие изменения — только продуктовые (копирайт, лимиты, UX), без отката на GET‑заглушку для старта.
- [in_progress] driving-verify: автосмоук `tools/smoke_plan_cards_driving_ai.py`; полная цепочка + iOS mini‑log — далее.
- [in_progress] ai-categories-verify: то же.

### 5.4. Журнал прогресса extended‑42 / 138 (старт 2026‑04‑19)

Семь карточек «Компоненты защиты» (KPI дня) — контракт + прод‑смоук:

| Карточка        | GET stats (канон)                         | Контракт 7/7 | Смоук содержим. (source)      |
|-----------------|-------------------------------------------|--------------|-------------------------------|
| Driving         | `/api/reports/driving/stats?period=week`  | OK           | `smoke_plan_cards_driving_ai` |
| Dark Web        | `/api/reports/dark-web/stats`             | OK           | в составе contract 7/7        |
| Identity Theft  | `/api/reports/identity-theft/stats`       | OK           | в составе contract 7/7        |
| Location Bubble | `/api/reports/privacy/location/stats`     | OK           | в составе contract 7/7        |
| Data Cleanup    | `/api/reports/privacy/cleanup/stats`      | OK           | в составе contract 7/7        |
| Tracker         | `/api/reports/privacy/tracker/stats`      | OK           | в составе contract 7/7        |
| AI Categories   | `/api/reports/ai-categories/stats`        | OK           | `smoke_plan_cards_driving_ai` |

Остальные **35** компонентов и **138** функций — строки таблицы добавлять по мере прохождения §5.2.

- **2026‑04‑19:** в `docs/audit/AUDIT_42_INVENTORY.md` (таблица 2) уточнены цепочки API по `AppConfig.Endpoint` и экранам; добавлена таблица расхождений id реестра 42 vs Swift для четырёх компонентов; повторный прогон `ALADDIN_API_BASE=http://149.154.65.180:8002 python3 tools/contract_tests_components.py` — **7/7**.

## 6) Почему так и что уже устранено
- Mock‑данные больше не «притворяются успехом»: gateway/middleware возвращают 503, чтобы UI был честным (или реальные данные, или «сервис временно недоступен»).
- Клиентская часть объединена на уровне `componentsAnalytics` → меньше сетевых вызовов, одно место для оркестрации и таймаутов, нет «мига» источника и дублей.
- Остаточная «пустота» — это отсутствие боевого провайдера данных (а не проблема клиента).

## 7) Как быстро проверить прогресс (после внедрения шагов A→C)
1) `psql`: убедиться в наличии и наполнении таблиц по 5 доменам (последние записи < N часов).
2) `curl` по новым эндпоинтам: проверить 200 OK, отсутствие mock‑маркеров, корректные поля метрик/нули.
3) `tools/contract_tests_components.py`: ожидаем PASS.
4) Открыть iOS: карточки компонентов показывают «Реальные данные» (source=api), mini‑лог подтверждает.

---

Готовность к продакшену достигается, когда:
1) Все 5 доменов компонентной аналитики имеют БД‑таблицы и ingestion с актуальными данными.
2) Боевые роутеры читают из БД и возвращают совместимый JSON (или через gateway‑нормализацию).
3) Precision‑подключение исключает wildcard/SFM.
4) Смоук‑/контракт‑тесты PASS; iOS показывает «Реальные данные» стабильно.

## 8) Прод‑требования дополнительно (Security/PII/Compliance)
- Данные PII (emails/phones/hashes/locations) — хранить в зашифрованных полях/таблицах; доступ только по need‑to‑know.
- Политика хранения: retention по доменам (напр., raw events 30–90 дней, агрегаты 365+).
- Маскирование в логах/метриках; запрет на дампы PII в application logs.
- Контроль доступа к БД: отдельные роли RW/RO, минимум привилегий для роутеров (RO).
- Соответствие локальным политикам (GDPR‑аналог): удаление по запросу, traceability.

## 9) Контракты/DTO и версионирование
- Регистр контрактов (DTO v1) — единая спецификация ключей/типов для 7 карточек и расширенных отчётов.
- Правило несовместимых изменений: v2 рядом, параллельная поддержка; gateway выполняет down‑map в v1 до переключения клиента.
- Авто‑проверка: контрактные тесты на PR (JSON‑снимки + типы).

## 10) Ingestion: идемпотентность и дедупликация
- Идентификатор события (source_id + event_id + ts) → upsert с уникальным индексом.
- Повторная доставка из очереди должна быть безопасной (exactly‑once на уровне БД).
- Out‑of‑order: агрегации считать по окнам времени; поздние события не ломают инварианты.

## 11) Backfill и начальное наполнение
- Процедура бэкфилла для каждого домена (SQL/скрипт): источники, оконный период, лимиты RPS к БД.
- Контроль прогресса (счётчики/таймстампы); отключение/понижение частоты прод‑эндпоинтов при бэкфилле при необходимости.

## 12) Пагинация, лимиты, кэширование
- Списки (leaks/requests/records/attempts) — cursor‑based пагинация, page_size ≤ 100, серверные лимиты.
- Кэширование агрегатов (stats) 30–60s для снижения нагрузки; HTTP cache headers.
- Rate‑limit на роутеры (per IP/device/user) + circuit‑breaker серверный.

## 13) Наблюдаемость/KPI/SLO
- KPI: freshness (время с момента последнего события), coverage (доля клиентов с данными), latency p50/p95, error%, 5xx rate.
- SLO: latency p95 < 500ms, error% < 1%, freshness < N часов (доменно).
- Дашборды и алёрты: «нет свежих данных > N часов», «spike 5xx», «latency p95 рост».

## 14) Тестовая матрица
- Контрактные тесты: позитив/пустые/большие ответы; ключи/типы; совместимость v1.
- Перф‑тесты: p95 при 100 rps на каждый домен; деградация под нагрузкой.
- Пагинация: корректность курсора/крайние случаи; пустые страницы.
- Отказоустойчивость: 5xx/таймауты → 503 и корректные пустые состояния на клиенте.

## 15) План релиза и отката
- Релиз: миграции → ingest (драй‑ран) → боевые роутеры RO → включение precision в gateway → смоук/контракты → наблюдение 24–48 ч.
- Откат: фича‑флаги роутеров на gateway (переключение на compat), отключение ingest, возврат старых маршрутов; миграции — обратимые/безопасные.

## 16) Ответственность/Ownership
- Домены и владельцы: Dark Web, Identity, Tracker, Location, Cleanup — отдельные ответственные за БД/ingest/роутеры/метрики.
- Единый координатор компоненты аналитики — SLA/согласование DTO/релизы.

## 17) Acceptance‑критерии для 42 компонентов и 138 функций
- Для каждой из 42 компонент:
  - Привязка экран→эндпоинт→таблица/агрегат подтверждена.
  - Смоук возвращает 200 OK (или 204 при «нет данных»), без mock‑маркеров.
  - Freshness в норме, mini‑лог клиента фиксирует source=api, не «compat».
- Для 138 функций:
  - Операционные (POST/акции) завершаются 2xx, идемпотентность подтверждена (где применимо).
  - UI показывает реальные значения/состояния; нет флипа «реальные↔нет данных» без причины.

## 18) Риски и снижения
- Задержка бэкфилла → временная пустота на карточках: смириться, но алёрты «freshness» и явные «Нет данных».
- Схемные расхождения поставщиков → строгая нормализация в ingest; тесты на конвертацию.
- Нагрузка на БД от отчётов → кэш агрегатов + индексирование + RO‑реплики.

## 19) Runbooks / SLO-SLA / Ownership (выполнено)
- Подготовлен операционный runbook: `docs/observability/RUNBOOK_SLO_SLA_OWNERSHIP.md`.
- Зафиксированы:
  - SLO/SLA цели по availability, freshness, latency, 5xx;
  - матрица ownership и эскалации L1/L2/L3;
  - playbooks для инцидентов Freshness/Prometheus target/p95-5xx;
  - post-change checklist и регулярные операционные проверки.

