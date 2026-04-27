# План доведения до 100% (Фазы 1–8.4) — handoff для ML / инженерной системы

**Цель документа:** чтобы другая ML-система, прочитав только этот файл (+ указанные пути в репозитории), поняла **что именно сейчас не доведено**, **как это закрыть до production-качества**, **в каком порядке**, и **как доказать готовность** (тесты, смоуки, метрики).

**Контекст репозитория:** iOS приложение ALADDIN. Многие подсистемы уже есть, но часть пунктов из «большого плана» выполнена как **MVP**, **частично**, или **только инженерно** без продуктового/юридического финала.

**Редакция плана (синхронизация с репо):** 2026-04-26 — **Wave 0–7**, **G24 (сквозная RU/EN локализация)**, **§2.5**, **W-LOC-1…6**, гигиена строк (без дублей ключей, без лишних кавычек/скобок), ссылки на `docs/LOCALIZATION_*.md`.

---

## 0) Как читать этот документ (для ML)

1. Сначала прочитай раздел **1 — Реестр пробелов** (таблица): это **единственный список того, что надо довести**.
2. Затем раздел **2 — Принципы реализации** (как принимать решения, чтобы не ломать продукт).
3. Затем **§3.0 — Критический путь** (зависимости между G и волнами), затем раздел **3 — Пошаговый план волнами** (Wave 0–7, тот же порядок, что **§4**).
4. Раздел **4 — Детальный TODO** — **исполняемый чеклист** (включая **W-LOC** для RU/EN).
5. Раздел **5 — Доказательства готовности (Proof Pack)**; **5.1 — Traceability.**
6. **§2.5** — **обязательные** правила RU/EN: каждый PR с UI проходит ими до merge.
7. **§6** — ссылки на код и **доки локализации**; **§1.0** — снимок кода.

**Важно:** часть пунктов Фазы 8 (юридика, полевые UX исследования с детьми) **не автоматизируются кодом**. Для них в TODO есть **явные non-code deliverables**.

---

## 1) Реестр пробелов (что «плохо / мало / частично / не сделано») — Фазы 1–8.4

| ID | Фаза | Пробел | Текущее состояние (факт) | Почему это не 100% |
|---:|---|---|---|---|
| G1 | 1 | `ContentDatabase` «с CoreData» | Сейчас JSON persistence (`content-db-v1.json`) | Не соответствует заявленной технологии / нет CoreData-модели и миграций |
| G2 | 1 | `ContentDownloader` в pipeline | Класс есть, но не является обязательным шагом загрузки payload | Нет end-to-end: URL → verify → cache → open offline |
| G3 | 1 | Подпись манифеста fail-closed | Есть крипто-хелперы, но apply path опирается на структурную валидацию | Production gate «подпись обязательна» не закреплён как единственный путь |
| G4 | 2 | Объёмы контента 15/10/30… | Seed: ~3 элемента на категорию | Нет контент-плана как продукта + нет интерактивных модулей уровня описания |
| G5 | 3 | `ActivityReports` «с графиками» | Список метрик (дашборд уже с фильтрами, DSAR, **parent mirror** по категориям/разрешениям) | **Графиков, серий по дням, трендов** — нет (G5 = именно time-series) |
| G6 | 3 | `ParentDashboardView` «полная статистика» | **Часть продукта уже есть:** localizable mirror (ребёнок/возрастные+), разрешения, отчёты-метрики | **Нет** когорт, **экспорта трендов**, **drill-down аналитики** как в отдельной BI-части; **часть строк в UI** ещё hardcoded EN (см. W3-5) |
| G7 | 3 | Отчёты + уведомления как система | Базовые отчёты | Нет связного продукта: дайджесты/алерты/каналы |
| G8 | 4 | `AudioPlayer` как компонент | Фон внутри `AudioManager` | Архитектурно смешаны ответственности |
| G9 | 4 | 20+ звуков как библиотека ассетов | 20 enum кейсов | Риск: нет гарантии, что все mp3 реально в бандле |
| G10 | 5 | Глобальные переходы | `TransitionManager` как утилита | Не все переходы навигации стандартизированы |
| G11 | 5 | Perf-процесс анимаций | Reduce Motion / `PerformanceBenchmarkTests` / частицы | Нет **формального** perf-бюджета и **регламентных** прогонов (FPS/списки) как release gate |
| G12 | 6 | `FeedbackSystem` единым модулем | Разнесено по UI | Нет единого API/политики спама/приоритетов |
| G13 | 6 | Rich progress UI | Текст + галочка | Нет progress bar / шкалы / истории |
| G14 | 7 | Apple Family Sharing API «как в чеклисте» | Политики + StoreKit контекст | Нет явного FamilyManager и чёткой границы «Apple vs app» |
| G15 | 7 | Синхронизация «везде и всё» | Есть серверный контур + тесты | Нет единой модели конфликтов/версий для всех доменов |
| G16 | 7 | Лимиты времени UX | Локально + API разнесены | Нет одного «источника правды» в UI для родителя |
| G17 | 8.1 | «Проверка всего контента» | Контракт/DTO/смоук API | Не покрывает качество каждого контент-юнита |
| G18 | 8.2 | Матрица устройств | Скрипты/интеграции | Нет физической матрицы как процесса |
| G19 | 8.2 | UX с реальными детьми | Не автоматизируется | Нужны полевые сессии + протокол |
| G20 | 8.3 | IPA < 500MB | Открытый трек | Нет измерения/плана снижения как gate |
| G21 | 8.4 | COPPA legal sign-off | Инженерные смоуки | Юридический финал вне кода |
| G22 | 8.4 | Внешний security/privacy аудит | Security смоук | Не равно внешнему аудиту |
| G23 | 8.4 | Family Sharing security pack | Частично | Нет оформленного evidence pack |
| G24 | cross | **Локализация RU+EN (сквозной слой)** | Стандарты в `docs/LOCALIZATION_*.md`, W3-5, CI lint частично | **Не** весь продукт покрыт одним **аудитом**; риск **дублей ключей**, **лишних кавычек/скобок**, **рассинхрона** плейсхолдеров RU/EN; hardcoded вне дашборда; нужны **W-LOC** + чеклист в каждом PR |

### 1.0 Снимок кода (чтобы ML не гадала, **на дату редакции**)

- **G1 / persistence:** `ContentDatabase` пишет в `content-db-v1.json` (см. `ContentDatabase.swift`); **не** CoreData.
- **G2 / downloader:** `ContentDownloader` **не** встроен в `ContentSyncManager` — нет шага download → verify → disk по `payloadURL` после apply манифеста.
- **G3 / подпись:** `ContentValidator.verifySignature` реализован; **`validateManifest`** на пути `apply` — **структурный** чек; **fail-closed** по подписи в Release **не** закреплён end-to-end.
- **G9 / CI:** gate W5-2: шаг `python3 scripts/validate_app_sound_effects.py` в job `build` (`ci.yml`).
- **G24 / локализация:** RU+EN ведутся в `Resources/Localization/{ru,en}.lproj/Localizable.strings`; нормативы — `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`. Полного «закрытия» G24 без **W-LOC-1…6** и дисциплины PR **нет**.

### 1.1 Карта «куда лезть в репозитории» (G → основные точки)

Ниже — **первичные** файлы/папки для каждого G. Детальные шаги и DoD остаются в **разделе 4**; Proof — в **разделе 5**.

| ID | Основные точки в репозитории (старт) |
|---:|---|
| G1 | `Core/Content/Storage/ContentDatabase.swift` (+ решение ADR в `docs/`) |
| G2 | `ContentDownloader.swift` (**сейчас** не вызывается из `ContentSyncManager`), `ContentSyncManager.swift`, `ContentCacheManager.swift` |
| G3 | `ContentValidator.swift` (`verifySignature`/`validateManifest` — **wiring в sync**), `ContentSyncManager.swift`, `Core/Config/AppConfig.swift` |
| G4 | `Core/Content/Seed/ContentSeedProvider.swift`, `Screens/ChildContentScreen.swift`, серверный контент **вне iOS** + `scripts/content_contract_smoke.py` |
| G5 | `Core/Content/Parent/ParentDashboardSystems.swift`, `Screens/ParentDashboardView.swift` |
| G6 | `ParentDashboardView.swift`, `ContentManager.swift` (снимок `parentDashboardSnapshot`), **UX-polish / i18n** (см. W3-5) |
| G7 | `Screens/ParentDashboardView.swift`, `Core/Notifications/NotificationManager.swift` (или новый сервис рядом) |
| G8 | `Core/Audio/AudioManager.swift` → выделение в новые типы в `Core/Audio/` |
| G9 | `Core/Audio/SoundEffectPlayer.swift`, бандл ресурсов, новый `scripts/` gate, `.github/workflows/ci.yml` |
| G10 | `Core/Animation/TransitionManager.swift`, `Core/Navigation/NavigationManager.swift`, ключевые `Screens/*.swift` |
| G11 | `Core/Animation/*`, тяжёлые списки в `Screens/`, `Tests/UnitTests/PerformanceBenchmarkTests.swift` |
| G12 | новый `Core/UX/FeedbackSystem.swift` (предложено), миграция вызовов из `Screens/*` |
| G13 | `Screens/ChildContentScreen.swift` |
| G14 | `Core/Profile/FamilyAccessPolicy.swift`, `Screens/02_FamilyScreen.swift`, StoreKit/IAP слой (поиск по `StoreKit`) |
| G15 | `ProfileManager.swift`, `ChildRosterReconcilePolicy.swift`, `Tests/UnitTests/ChildRosterReconcilePolicyTests.swift`, `SyncBetweenDevicesTests.swift` (сетевые/хрупкие сценарии — см. **META-3**), семейные API |
| G16 | `Core/Content/Progress/ProgressSystems.swift`, `Core/Network/APIService.swift`, `Core/Managers/ParentalControlManager.swift`, UI (новый экран или секция в parental) |
| G17 | `Tests/UnitTests/ContentContractDTOTests.swift`, `scripts/content_contract_smoke.py`, новый `docs/` QA matrix + `scripts/` |
| G18 | `docs/`, `.github/workflows/ci.yml`, опционально новые job’ы |
| G19 | `docs/` (протокол исследования, не код) |
| G20 | `.github/workflows/ci.yml`, новый `scripts/` для IPA size, отчёты артефактов |
| G21 | `scripts/phase8_compliance_smoke.py`, `scripts/trackb_privacy_compliance_gate.py`, **внешний** legal PDF |
| G22 | `scripts/phase8_security_smoke.py`, `docs/` evidence pack, **внешний** аудит |
| G23 | `docs/` + отчёты смоуков + матрица сценариев Family Sharing / StoreKit |
| G24 | `Resources/Localization/ru.lproj/Localizable.strings`, `en.lproj/Localizable.strings`, `scripts/localization_lint.py`, `Core/Localization/LocalizationManager.swift`, `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md` |

### 1.2 Подробно: что делает **мобильное приложение (iOS)**, что — **сервер / инфра / вне репозитория**

Ниже для **каждого G** — практичное разделение работ, **как лучше стыковать контракты** и что считать готовым на каждой стороне. Это дополняет раздел **4 (TODO)** и не заменяет его: там чеклисты, здесь — **архитектурная карта ответственности**.

**Общие правила для ML-исполнителя**

1. **Источник правды для каталога контента** — серверный `manifest` / `delta` (уже описаны в `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md`). iOS — кеш, оффлайн, UX.
2. **Источник правды для семьи/лимитов** — договориться явно: что хранится только локально, что на сервере; версии сущностей (`version`, `updatedAt`) при любых изменениях с сервера.
3. Любой крупный шаг закрывается **Proof Pack** (раздел 5): тесты, смоук, скриншоты или внешний документ.

---

#### G1 — `ContentDatabase` / persistence

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Выбрать и внедрить одно хранилище (CoreData **или** SQLite/GRDB **или** JSON v2 с миграциями), миграции, индексы, транзакции при save. | Не оставлять «тихий» JSON без версии схемы: `schemaVersion` + миграция при старте. |
| **Сервер** | Ничего обязательного, если контракт манифеста не меняется. | Если позже нужны **серверные колонки** под аналитику — это отдельный продуктовый трек, не блокер G1. |
| **Контракт** | Формат `ContentManifest` / `ContentItem` остаётся каноном обмена. | ADR в `docs/` фиксирует решение G1 и ссылку на код. |

---

#### G2 — `ContentDownloader` в pipeline

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | После успешного merge манифеста: для каждого `payloadURL` (если не nil) — download → SHA256 verify → запись в disk cache → пометка `isOfflineAvailable`. Ошибка одного item не должна ломать весь манифест без политики. | Очередь загрузок с лимитом параллелизма, retry с backoff, отмена при уходе в background по политике. |
| **Сервер / CDN** | Стабильные URL, `ETag`/`Cache-Control`, **HTTPS**, размер файлов в разумных пределах. | Отдавать `checksum_sha256` в манифесте **строго** совпадающим с файлом; отдельный endpoint для больших файлов при необходимости. |
| **Инфра** | CDN или object storage перед приложением. | Логи 4xx/5xx, алерты на провалы выдачи контента. |
| **Контракт** | `payloadURL` + `checksumSHA256` в item (или явное «нет бинарника»). | iOS: при несовпадии хеша — не кешировать, метрика/лог для родителя в debug. |

---

#### G3 — подпись манифеста fail-closed

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Перед `saveManifest`: проверка подписи над **каноническим** payload (то же байтовое представление, что подписывает сервер). Release: без подписи — откат. Debug: только явный флаг. | Публичный ключ в приложении (pinning) + механизм ротации (v2 ключ в бандле или remote config с подписью метаданных). |
| **Сервер** | Подписывать манифест при сборке релиза; хранить приватный ключ **вне** репозитория (HSM/secret manager). | Отдельный build job: `manifest.json` → digest → sign → публикация. |
| **Контракт** | Поля `signature`, алгоритм (например ECDSA P-256), что именно подписывается (JSON bytes vs canonical hash). | Документ в `docs/` + тест в iOS на «битая подпись». |

---

#### G4 — объём и глубина контента (15/10/30… + интерактивы)

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Router «`ContentItem` → experience»; пустые состояния; оффлайн; прогресс; родительские флаги в UI. | Не смешивать «каталог» и «игру» в одном файле без границы. |
| **Сервер** | Генерация манифестов по версиям; наполнение items; дельты; контроль качества метаданных; editorial workflow. | Версионирование контент-пакетов; staging манифест для QA. |
| **Контракт** | Расширение метаданных: `minAppVersion`, `parental`, `locale`, `duration`, `payloadURL`, `tags`. | Обратная совместимость: старые клиенты не ломаются. |

---

#### G5 — графики в `ActivityReports`

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Агрегация по дням из локальных событий **или** запрос к API «stats range»; UI Charts. | Хранить события append-only локально (с лимитом) для недельных трендов без сервера на v1. |
| **Сервер** | Опционально: эндпоинт отчётов по семье/ребёнку с авторизацией. | Если нужен единый источник между устройствами родителя — сервер обязателен на v2. |
| **Контракт** | JSON отчёта: `series[] {date, opens, completions, minutes}`. | Пагинация и таймзона явно в контракте. |

---

#### G6 — «полная статистика» Parent Dashboard

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Экраны drill-down, фильтры, экспорт, состояния загрузки/ошибок, локализация. | Убрать «сырые» английские строки из UI (см. UX-polish в разделе 7 файла). |
| **Сервер** | При необходимости: агрегаты и тяжёлые запросы не на клиенте. | Кеширование на сервере, rate limits. |

---

#### G7 — отчёты + уведомления как система

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Планировщик локального дайджеста; экран истории; интеграция с `NotificationManager`; настройки каналов. | v1: in-app только; v2: push с согласиями. |
| **Сервер** | Push: APNs topics, сохранение подписок устройства, шаблоны, **не отправлять PII ребёнка** в лишнем объёме. | Сервер шлёт «событие» + ссылка на экран, не тело отчёта целиком. |
| **Контракт** | `POST /devices/push-token` (если ещё нет) или существующий механизм; типы событий. | Документировать в OpenAPI. |

---

#### G8 — отдельный `AudioPlayer`

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Рефакторинг: сессии/категория в одном месте, плеер отдельно, fade, interrupt handling. | Тесты на interruption (звонок, другой аудио). |
| **Сервер** | Не требуется. | Контент-аудио по URL — см. G2. |

---

#### G9 — 20+ звуков как библиотека ассетов

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Положить mp3/aac в бандл или в downloadable pack; CI gate. | Именование 1:1 с `AppSoundEffect.rawValue`. |
| **Сервер** | Опционально: CDN-пак «sound pack v3» для уменьшения IPA (тогда G2). | Версия пака в манифесте. |

---

#### G10 — глобальные переходы

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Пройти `NavigationManager` и основные flow; единый профиль transition. | Не анимировать всё подряд: 1–2 паттерна. |
| **Сервер** | Не требуется. | — |

---

#### G11 — perf анимаций

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Бюджет частиц, lazy lists, Instruments профили, регрессии. | Чеклист перед релизом + один скрипт/задача CI на smoke perf. |
| **Сервер** | Не требуется. | — |

---

#### G12 — единый `FeedbackSystem`

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Фасад + политика debounce/priority + AX announcement. | Единая точка входа вместо разрозненных вызовов. |
| **Сервер** | Не требуется. | — |

---

#### G13 — rich progress UI

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | ProgressView/GeometryReader шкала, история локально или с сервера. | Минимальный v1: bar + % + last opened. |
| **Сервер** | Опционально: серверный прогресс если мультиустройство. | `ETag` + merge правила. |

---

#### G14 — Family Sharing «как в плане»

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | StoreKit 2 / текущий платёжный поток; **явный** UX «что даёт Apple Family Sharing vs что даёт приложение»; `FamilyAccessPolicy`. | Не обещать в UI то, что не покрыто Apple API. |
| **Сервер** | Связка подписок/семьи с вашим `family_id`, если биллинг гибридный. | Идемпотентность webhooks, аудит. |
| **Вне репо** | App Store Connect: Family Sharing для подписок, группы, метаданные. | Документ для поддержки. |

---

#### G15 — синхронизация «везде»

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Конфликт-резолвинг UI для родителя; очереди оффлайн; дедуп событий. | Версии сущностей на каждом типе данных. |
| **Сервер** | Версии, `updated_at`, 409 на конфликт, идемпотентные PATCH. | Не silent-merge критичных полей. |

---

#### G16 — лимиты времени в одном UX

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Один экран: читает локальный `TimeTracker` + сервер через существующие API; показывает «источник правды» и ошибки синка. | Явная кнопка «синхронизировать с сервером». |
| **Сервер** | Уже есть контуры `updateTimeLimits` / ответы с лимитами — расширять только при необходимости (bedtime, weekly). | Контракт версий `version` в теле запроса/ответа. |

---

#### G17 — проверка «всего контента»

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | UI smoke по сценариям; локальные проверки открытия каждого типа experience. | Матрица в `docs/` + автomation по манифесту (минимум: каждый item открывается или graceful degrade). |
| **Сервер** | CI на валидность манифеста: JSON schema, дубли id, ссылки на payload, подпись. | Генератор манифеста падает в CI при ошибке. |

---

#### G18 — матрица устройств

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS / CI** | Несколько destinations в CI + артефакты. | Минимум 2 симулятора + 1 физический прогон перед релизом. |
| **Сервер** | Не требуется. | — |

---

#### G19 — UX с детьми

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **Вне репо** | Протокол, согласия родителей, записи сессий, backlog. | Не смешивать с автотестами. |

---

#### G20 — IPA < 500MB

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Asset catalogs, вынос тяжёлых ресурсов в downloadable content (G2). | Отчёт «top N» из CI. |
| **Сервер / CDN** | Хостинг больших медиа вне IPA. | Версия пакетов. |

---

#### G21–G23 — compliance / аудит / Family Sharing security pack

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Смоуки, DSAR UI, parental gate, логирование без PII. | `scripts/trackb_*`, `phase8_*` как обязательный слой. |
| **Сервер** | Политики хранения, удаление, аудит доступа, rate limits. | Единый privacy runbook. |
| **Вне репо** | Legal sign-off, внешний pentest/audit, ответы на findings. | Один evidence pack на релиз (раздел 5). |

### 1.3 Минимальное **Proof** на G (one-liner, дублирует §4/§5)

| ID | Минимальное подтверждение «G закрыт» |
|:-:|---|
| G1 | ADR + тест/миграция схемы или `schemaVersion` + интеграция |
| G2 | Интеграция download в sync + тест (mock URL) + лог при hash mismatch |
| G3 | Unit: битая подпись; Release: путь без подписи = откат |
| G4 | iOS: routing + контент/сервер: манифест-версия + smoke |
| G5 | График + смена периода; snapshot/скрин |
| G6 | Drill/экспорт или явный scope; i18n (W3-5 + W-LOC-4; §2.5) |
| G7 | Дайджест v1 in-app; тесты расписания; push = отдельно |
| G8 | Разделение классов; тест interrupt (симуляция) |
| G9 | CI gate: все `AppSoundEffect` → файл в бандле |
| G10 | Список экранов + UI-тесты 5 переходов |
| G11 | Бюджет/чеклист + `PerformanceBenchmarkTests` / ручной прогон |
| G12 | `FeedbackSystem` + unit debounce/priority |
| G13 | Progress bar + UI test / скрин |
| G14 | `docs` + 2 help-экрана + content review |
| G15 | 409/версии + UI конфликта; unit roster policy |
| G16 | Один экран + integration readback |
| G17 | Матрица `docs` + smoke по манифесту |
| G18 | Док процесса + подпись владельца; CI destinations |
| G19 | PDF протокола + product sign-off |
| G20 | CI IPA report + top-N assets |
| G21–G23 | Архив Proof + внешние PDF/пентест применимо |
| G24 | `localization_lint` зелёный; отчёт 0 дублей ключей; RU+EN скрин критичных экранов; a11y для новых контролов; W-LOC выполнены |

#### G24 — детализация (iOS, контент, процесс)

| Сторона | Что делать | Как лучше |
|---:|---|---|
| **iOS** | Весь видимый текст через ключи; RU+EN **в одном PR**; namespace из `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`; ошибки/empty/loading — тоже ключи; **a11y** (label/hint) локализуемы. | Нет literal в `Text("...")` / алертах для пользователя. См. `docs/LOCALIZATION_PR_CHECKLIST.md`. |
| **Качество `.strings`** | **Один смысл — один ключ**; **нет** дублирующих имён в файле; значения **без** лишних кавычек **вокруг** фразы; **без** «шума» вложенных скобок; RU/EN **не** смешивать в одной строке. | Плейсхолдеры: одинаковое число и тип `%@`/`%d` в RU и EN, один порядок аргументов. |
| **G4 / сервер** | `ContentMetadata` может содержать `locale`, `title` в JSON — **не** путать **каталожные** поля (контент с сервера) с **оболочкой** приложения: либо сервер отдаёт нужную локаль, либо iOS маппит `titleKey` → `Localizable.strings`. | Зафиксировать в контракте + ADR, чтобы не было двойного перевода. |
| **CI / PR** | `python3 scripts/localization_lint.py` (и при необходимости scope); при **каждом** изменении `Localizable.strings` — **паритет** RU+EN. | `TRACKB_*` same-PR policy для гейтов — см. `docs/`. |

---

## 2) Принципы реализации (чтобы «красиво и просто» не превратилось в хаос)

### 2.1 Выбор стратегии хранилища контента (G1)

**Вариант A (рекомендуется чаще всего):** оставить lightweight persistence, но **переименовать требования** и сделать **SQLite/GRDB или JSON v2 с миграциями**, индексами, транзакциями.

**Вариант B:** внедрить **CoreData** строго по правилам:
- версионирование модели,
- lightweight migrations,
- background contexts,
- индексы по `contentId`, `categoryId`, `updatedAt`.

**Правило для ML:** не смешивать «хочу CoreData» с «на самом деле достаточно SQLite». Нужно **одно** каноническое решение и обновить план/доки, иначе команда будет вечно расходиться.

### 2.2 Контент: разделить «каталог» и «опыт» (G4)

- **Каталог** = `ContentManifest` / items / metadata / URLs / checksums / offline flags.
- **Опыт** = SwiftUI scene по `ContentItemType` + параметрам (routing table).

Это best practice: **данные отдельно от UI-интерактива**.

### 2.3 Безопасность контента (G3)

Production best practice:
- **Подпись манифеста обязательна** в Release (или включена через remote config с kill-switch).
- Публичный ключ **pinning** + ротация ключей (v2) + fallback только для строго controlled debug.

### 2.4 Доказательства (Proof) — обязательны для каждого G*

Каждый закрытый gap должен иметь минимум одно:
- unit test,
- integration test,
- или `scripts/*_smoke.py`,
- или чеклист с артефактами (скриншоты, PDF), если non-code.
- **Локализация (G24):** к функциональному DoD **добавляется** RU+EN (см. **§2.5**), если задача касается UI или пользовательских сообщений.

### 2.5 Локализация RU+EN (обязательный периметр плана, **G24**)

1. **Нормативные файлы (читать перед UI-задачей):** `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md` (и при необходимости `docs/LOCALIZATION_BASELINE_BACKLOG.md`).
2. **Двуязычие в одном PR:** новый ключ **обязан** существовать в `ru` и `en` одновременно; **не** мерджить с «доберём EN в следующем».
3. **Без дублей:** в каждом `Localizable.strings` — **уникальные** ключи; смысловых дублирующих ключей для той же фразы **не** добавлять (§4 в Standard).
4. **Гигиена строк (то, о чём вы просили явно):** в **значениях** RU/EN **не** добавлять лишние **кавычки**-«обрамление», **не** плодить **вложенные скобки** без смысла, **не** смешивать русский и английский в **одной** user-visible строке. Технобред в UI — только по согласованию.
5. **Плейсхолдеры:** идентичный набор и порядок для RU и EN; тест/ручной прогон с реальными аргументами.
6. **Error / empty / loading** — тоже ключи, не литералы (Standard §7).
7. **A11y:** `accessibilityLabel` / `accessibilityHint` / `value` — локализуемы (Standard §8).
8. **Связь волн:** **W-LOC-1…6** закрывают G24; **W3-5** — **частный случай** (только `ParentDashboardView`); остальные экраны — **W-LOC-4** и **чеклист PR**.

### 2.6 Детский контент: международный стандарт реализации (Phase 2 hardening)

Чтобы другая ML-система не путала «архитектурно есть» и «продуктово готово», вводим обязательные правила:

1. **Learning Outcome Contract обязателен для каждого child-item:**  
   `learning_objective`, `target_age_window`, `difficulty_level`, `success_criteria`, `assessment_type`, `estimated_cognitive_load`.
2. **Mastery > completion:**  
   прогресс считать не только `%`, но и состояниями `introduced/practicing/mastered`.
3. **Возрастная безопасность UX:**  
   лимит стимуляции, мягкие паузы, контроль когнитивной нагрузки по возрасту.
4. **Категория не считается закрытой по количеству alone:**  
   нужны одновременно: объём + интерактивный движок + оценка навыка + telemetry + RU/EN+a11y.
5. **Локализация детского контента (жёсткий контракт):**  
   без дублей ключей, без лишних кавычек, без «шумных» скобок, без смешивания RU/EN в одной строке.
6. **Канонический детальный план реализации до 100%:**  
   `docs/PHASE2_CHILD_CONTENT_100_PERCENT_PLAN.md` (включая execution matrix и non-negotiable acceptance criteria).

---

## 3) Пошаговый план волнами (согласован с **§4 — Wave 0–7**)

### 3.0 Критический путь и зависимости

- **G1 (ADR persistence) + G3 (подпись) + G2 (downloader + LRU)** — фундамент: без них «продакшен» контентный контур **не** считается закрытым; G4 (наполнение) и G17 (QA) опираются на тот же pipeline.
- **G5 / G6 / G7 / G16** — зависят от **событий/серий** (локально или API) и **единого** UX лимитов; G16 согласовывать с контрактом `APIService` / `ParentalControlManager`.
- **G14 / G15** — потребуют **серверных** `version` / 409 / идемпотентности, если источник правды серверный.
- **G18 / G20 / G21–G23** — **ворота релиза** после feature freeze: отчёты CI, внешние PDF, evidence pack.
- **Риски (кратко):** несогласованный **canonical** JSON для подписи (ложные fail); **флаки** в сетевых sync-тестах (см. **META-3**); **G24** — **каждая** волна с новым UI или строками **обязана** ссылаться на **§2.5** и W-LOC (дубли ключей / кавычки / RU+EN = распространённые причины отката PR).

### Wave 0 — «Стабилизация истины» (0.5–1 день)

- Зафиксировать каноническое решение по G1 (CoreData vs SQLite vs JSON v2).
- Зафиксировать security gate по G3 (Release обязательности подписи + canonical bytes).

### Wave 1 — Контентный pipeline до production (G2, G3, частично G17)

- Подключить загрузку payload, verify SHA256, disk cache, LRU.
- Закрыть fail-closed подпись + rollback last-known-good.

### Wave 2 — Контент как продукт (G4), частично

- Таблица `ContentItem` → experience; сервер — плотность/версии манифеста (вне iOS).
- Для доведения до мирового уровня по детскому развитию применять `docs/PHASE2_CHILD_CONTENT_100_PERCENT_PLAN.md`:  
  Learning Outcome Contract, mastery model, category execution matrix, локализация без дублей/лишних кавычек/скобок.

### Wave 3 — Родительский продукт (G5–G7, G16) + **UX/i18n дашборда (W3-5)**

- Charts, экспорт, лимиты, дайджест; **убрать hardcoded EN** на дашборде (ключи, RU/EN).

### Wave 4 — Анимации, feedback, прогресс (G10–G13)

- Transitions, perf budget, `FeedbackSystem`, rich progress.

### Wave 5 — Аудио качество (G8–G9)

- Разделить сессии/плеер; **CI gate** на все `AppSoundEffect` → mp3.

### Wave 6 — Семья / синк / прозрачность (G14–G15)

- Док + UI: Apple vs приложение; conflict resolution, roster-политика.

### Wave 7 — Фаза 8: измеримость и ворота (G17–G23, G20)

- QA-матрица, матрица устройств, полевой G19, IPA size gate, **evidence pack** G21–G23.

### Сквозная **локализация (G24, W-LOC*) — параллельно волнам 0–7**

- Любая волна с **новыми** строками: сначала ключи RU+EN, затем код (§2.5). Финальный зачёт G24 — по **W-LOC-1…6** (не дублируйте W3-5: дашборд остаётся в Wave 3).

---

## 4) Детальный TODO (исполняемый чеклист)

> Формат: `- [ ]` задача → **Критерий готовности (DoD)** → **Где в коде/репо** → **Как проверить**

### Wave 0

- [x] **W0-1 Зафиксировать стратегию persistence для контента (решение по G1)**  
  - **DoD:** 1 страница ADR + обновление плана (что считается «done»).  
  - **Repo:** `docs/ADR-CONTENT-PERSISTENCE-G1.md`, `NEXT_VERSION_IMPLEMENTATION_PLAN.md`.  
  - **Проверка:** review + ссылка в PR.

- [x] **W0-2 Зафиксировать политику подписи манифеста (решение по G3)**  
  - **DoD:** таблица режимов Debug/Staging/Release; что происходит при fail.  
  - **Repo:** `docs/CONTENT_MANIFEST_SIGNATURE_POLICY_G3.md`, `AppConfig.contentManifestRequireValidSignature`, `ContentValidator.swift`, `Tests/UnitTests/ContentValidatorTests.swift` (W1-3 — wiring в `ContentSyncManager`).  
  - **Проверка:** unit tests `ContentValidatorTests`; `xcodebuild build-for-testing` зелёный.

### Wave 1 — Контент pipeline

- [x] **W1-1 Встроить `ContentDownloader` в sync pipeline (G2)**  
  - **DoD:** для каждого item с `payloadURL` + `checksumSHA256`: download → SHA verify → `Application Support/ContentPayloads/<id>/payload.bin` → в сохранённом манифесте `isOfflineAvailable: true` (ошибка одного item не блокирует остальные). **UI «открыть offline»** из файла — в связке с **W2-1** (routing). Сообщения об ошибках синка — **W-LOC-6**.  
  - **Repo:** `ContentDownloader.swift`, `ContentSyncManager.swift` (`ContentPayloadDownloading`, `ContentManifestPayloadHydration`), `ContentDatabase.swift`.  
  - **Проверка:** `Tests/UnitTests/ContentManifestPayloadHydrationTests.swift` (stub downloader); при необходимости дополнить URLProtocol.

- [x] **W1-2 Disk budget + LRU для медиа-кеша (G2)**  
  - **DoD:** лимиты MB, eviction, метрики last access.  
  - **Repo:** `ContentPayloadDiskCachePolicy.swift`, `AppConfig.contentPayloadDiskCacheMaxBytes`, `ContentSyncManager` / `ContentManifestPayloadHydration` (после записи `payload.bin`).  
  - **Проверка:** `Tests/UnitTests/ContentPayloadDiskCachePolicyTests.swift` (eviction по mtime `payload.bin`).

- [x] **W1-3 Подпись манифеста fail-closed в Release (G3)**  
  - **DoD:** без валидной подписи манифест не применяется; debug override только флагом сборки.  
  - **Repo:** `ContentSyncManager.swift`, `ContentManifestSigning.swift`, `ContentValidator.swift`, `AppConfig`, `Info.plist` (`CONTENT_MANIFEST_SIGNING_PUBLIC_KEY_BASE64`).  
  - **Проверка:** `ContentManifestSigningTests`, `ContentSyncManagerApplyTests` (инжект `requireManifestSignature` / ключа для unit).

- [x] **W1-4 Rollback на last-known-good (G3)**  
  - **DoD:** при ошибке применения — остаётся предыдущий манифест, пользователь видит понятную ошибку.  
  - **Repo:** `ContentDatabase.swift` (откат in-memory при ошибке записи), `ContentSyncManager.applyManifest`, `ContentVersionManager.restoreStoredVersion`.  
  - **Проверка:** `ContentSyncManagerApplyTests` (mock DB + fail save).

### Wave 2 — Контент как продукт (G4 частично)

- [x] **W2-1 Контент routing: `ContentItem` → experience модуль (G4)**  
  - **DoD:** таблица маршрутизации по `ContentItemType` без постоянных placeholder в прод; вход из `ChildContentScreen` в route-aware experience экран; guard на уровне валидации манифеста, что все типы маршрутизируемы.  
  - **Repo:** `Core/Content/Experiences/ContentExperienceRoute.swift`, `Core/Content/Experiences/ContentExperienceResolver.swift`, `Screens/ChildContentExperienceScreen.swift`, `Screens/ChildContentScreen.swift`, `Core/Content/Validation/ContentValidator.swift`, `Core/Content/ContentManager.swift`.  
  - **Проверка:** `ContentExperienceResolverTests`, `ContentValidatorTests`, `xcodebuild build-for-testing` (ALADDIN).

- [x] **W2-2 Серверный каталог: увеличить плотность элементов поэтапно (G4)**  
  - **DoD:** план версий манифеста + контроль качества метаданных.  
  - **Статус (iOS consumer):** добавлен strict gate в `ContentValidator` (уникальность id, валидная связь item→category, non-empty locale/title, `estimatedDurationSec > 0` при наличии, минимальная плотность `AppConfig.contentCatalogMinItemsPerCategory`).  
  - **Repo:** backend (вне iOS) + iOS consumer gate: `ContentValidator.swift`, `AppConfig.contentCatalogMinItemsPerCategory`, `scripts/content_contract_smoke.py`, unit tests.  
  - **Проверка:** `scripts/content_contract_smoke.py` (`ALADDIN_CONTENT_MIN_ITEMS_PER_CATEGORY`) — **PASS** после серверного обновления `/opt/aladdin-backend/app/content/content_manifest.json` (минимум 3 item на категорию), `ContentValidatorTests`, `AppConfigTests`, выборочный QA чеклист.

### Wave 3 — Parent dashboard продукт (G5–G7, G16)

- [x] **W3-1 Charts: недельные тренды opens/completions/time (G5)**  
  - **DoD:** минимум 1 график + переключатель неделя/месяц.  
  - **Repo:** `Screens/ParentDashboardView.swift` (секция трендов + группированные столбцы), `Core/Content/Progress/ProgressSystems.swift` (`ParentActivityDailyAggregator`, `ParentDashboardDayPoint`; дневные opens/completions; экранное время за прошлые сутки при rollover из `TimeTracker`). **Swift Charts не используется:** deployment target iOS 15.2 (Charts с iOS 16+).  
  - **Проверка:** `ParentActivityDailyAggregatorTests`; при необходимости позже — snapshot harness.

- [x] **W3-2 Экспорт отчёта родителю (PDF/CSV) (G5–G7)**  
  - **DoD:** файл генерируется, шарится через share sheet.  
  - **Repo:** `Core/Content/Parent/ParentDashboardReportExporter.swift` (CSV UTF‑8 с BOM + простой многостраничный PDF), `Screens/ParentDashboardView.swift` (секция экспорта, `ShareSheet`, `ParentShareDocument`).  
  - **Проверка:** `ParentDashboardReportExporterTests` (размер PDF, BOM CSV); UI-тест share sheet отложен из‑за `ParentSessionGate` на пути к дашборду (при появлении UITest harness — отдельно).

- [x] **W3-3 Единый экран лимитов времени (G16)**  
  - **DoD:** один UX: локальные лимиты + серверные + статус синка + ошибки.  
  - **Repo:** `Screens/UnifiedTimeLimitsScreen.swift`, `Core/Content/Progress/ProgressSystems.swift` (`TimeTracker.setDailyLimitMinutes`), `Core/Managers/ParentalControlManager.swift`, `Core/Network/APIService.swift`; вход с `ParentDashboardView` / `07_ParentalControlScreen`.  
  - **Проверка:** `W3W4DigestAndLimitsTests` (readback лимита).

- [x] **W3-4 Уведомления: дайджест активности (G7)**  
  - **DoD:** локальный дайджест (in-app) v1; опционально push v2.  
  - **Repo:** `Core/Notifications/ActivityDigestService.swift`, `Screens/ParentDashboardView.swift`.  
  - **Проверка:** `W3W4DigestAndLimitsTests` (строки дайджеста); preview `UnifiedTimeLimitsScreen_Previews` / дашборд по месту использования.

- [x] **W3-5 Локализация и полировка `ParentDashboardView` (G6 UX, i18n)**  
  - **DoD:** кнопки/подзаголовки/метрики/сообщения DSAR и лимитов вынесены в `Localizable.strings` (RU+EN), без «сырого» английского в `ParentDashboardView.swift` (см. §7, **§2.5**); **без** лишних кавычек/скобок в значениях.  
  - **Repo:** `Screens/ParentDashboardView.swift`, `Core/Content/Parent/ParentDashboardSystems.swift` (`ActivityReportItem.titleKey`), `Core/Localization/LocalizationManager.swift`, `Resources/Localization/en.lproj/Localizable.strings`, `Resources/Localization/ru.lproj/Localizable.strings`.  
  - **Проверка:** `scripts/localization_lint.py` + визуальный pass RU/EN; соответствие `docs/LOCALIZATION_PR_CHECKLIST.md` (G24, часть W-LOC).

### Wave 4 — Анимации/feedback (G10–G13)

- [x] **W4-1 Стандартизировать transitions в основной навигации (G10)**  
  - **DoD:** список экранов + применение `appContentTransition` или аналога.  
  - **Repo:** `ALADDINApp.swift` (корневой `Group` + `appContentTransition`), `Core/Animation/TransitionManager.swift`; идентификаторы для UI-тестов на корневых `AnyView` и кнопках главной.  
  - **Проверка:** `Tests/UITests/NavigationTransitionUITests.swift` (5 переходов); перечень идентификаторов — `docs/NAVIGATION_TRANSITION_TARGETS_W4-1.md`.

- [x] **W4-2 Perf budget для списков и анимаций (G11)**  
  - **DoD:** лимиты: max particles, throttle haptics/sounds, lazy loading.  
  - **Repo:** `Core/Animation/PerformanceBudget.swift` (центр. лимиты), `Core/Animation/ParticleSystem.swift` (cap + FPS), `Core/Audio/SoundEffectPlayer.swift` (интервалы по приоритету/повторам), `Shared/Components/HapticFeedback.swift` (интервалы), `Screens/ParentDashboardView.swift` (Scroll + LazyVStack вместо «плоского» VStack+List).  
  - **Проверка:** `PerformanceBudgetTests` (пороги частиц/звука). Ручной чеклист: 1) Reduce Motion — бурсты не рисуются, колбэк `onFinished` вызывается. 2) Быстрый тап по фильтрам дашборда — вибрация/звуки не «дребезжат» сверх бюджета. 3) `PerformanceBenchmarkTests` (если цель включена в CI) — без регрессии по сценариям, где он уже зелёный.

- [x] **W4-3 `FeedbackSystem` фасад (G12)**  
  - **DoD:** один вызов: `FeedbackSystem.shared.signal(.success)` → haptic+sound+optional particles+ax announcement.  
  - **Repo:** `Core/UX/FeedbackSystem.swift`, оверлей `FeedbackParticleOverlay` в `ALADDINApp`, `Tests/UnitTests/FeedbackSystemTests.swift`, ключи `feedback_announcement_*` в RU+EN.  
  - **Проверка:** unit tests debounce/priority.

- [x] **W4-4 Rich progress UI в детском контенте (G13)**  
  - **DoD:** progress bar + состояния empty/error.  
  - **Repo:** `Screens/ChildContentScreen.swift` (общий прогресс по категории, полоса и % в карточке элемента, last opened; loading / empty / error + RU+EN; `aladdin_root_child_content` + идентификаторы для UI), `ALADDINApp` (`ChildCategoryKey.games` для `childContent`, флаг `-UITestChildContentW4_4`).  
  - **Проверка:** `Tests/UITests/ChildContentProgressUITests.swift`.

### Wave 5 — Аудио (G8–G9)

- [x] **W5-1 Выделить `BackgroundMusicController` / `AudioPlayer` (G8)**  
  - **DoD:** `AudioManager` — сессия, кэш `bundledData` (`Resources/Audio`), `effective*Gain`, `AVAudioSession.interruptionNotification` → BGM; SFX — `AudioOneShotPlayer`.  
  - **Repo:** `Core/Audio/AudioManager.swift`, `Core/Audio/BackgroundMusicController.swift`, `Core/Audio/AudioOneShotPlayer.swift`, `Core/Audio/SoundEffectPlayer.swift`.  
  - **Проверка:** `Tests/UnitTests/AudioInterruptionTests.swift` (симуляция interruption + гейны при mute).

- [x] **W5-2 CI gate: все `AppSoundEffect` имеют ресурс (G9)**  
  - **DoD:** скрипт падает, если mp3 отсутствует.  
  - **Repo:** `scripts/validate_app_sound_effects.py`, `Resources/Audio/*.mp3`, `ci.yml` (шаг в `build`).  
  - **Проверка:** `python3 scripts/validate_app_sound_effects.py`; CI.

### Wave 6 — Семья/синк (G14–G15)

- [x] **W6-1 Документ + UI: Apple Family Sharing vs App profiles vs FamilyControls (G14)**  
  - **DoD:** 2 help-экрана + короткие подсказки в UI (Family + Parental).  
  - **Repo:** `docs/FAMILY_SHARING_APP_PROFILES_FAMILYCONTROLS_G14.md`, `Screens/02_FamilyScreen.swift`, `Screens/07_ParentalControlScreen.swift`.  
  - **Проверка:** контент-review + `xcodebuild` (Debug simulator) зелёный.

- [x] **W6-2 Conflict resolution для критичных сущностей (G15)**  
  - **DoD:** `version`/`updatedAt`, стратегии merge (`serverWins`/`localWins`/`latestUpdatedAt`), UI баннер разрешения конфликта для parent.  
  - **Repo:** `Core/Profile/ChildProfile.swift`, `Core/Profile/ChildRosterReconcilePolicy.swift`, `Core/Profile/ProfileManager.swift`, `Screens/02_FamilyScreen.swift`, `Tests/UnitTests/ChildRosterReconcilePolicyTests.swift`, `Tests/Integration/SyncBetweenDevicesTests.swift`.  
  - **Проверка:** расширены conflict-tests + `xcodebuild` (Debug simulator) зелёный.

### Wave 7 — Фаза 8 закрыть измеримостью (G17–G23, G20)

- [x] **W7-1 Контент QA matrix (G17)**  
  - **DoD:** таблица категория×возраст×сценарий + автосмоук минимум «открыть/офлайн/прогресс».  
  - **Repo:** `docs/CONTENT_QA_MATRIX_G17.md`, `scripts/phase7_content_qa_matrix_smoke.py`, отчёты `docs/PHASE7_CONTENT_QA_MATRIX_REPORT.{json,md}`, CI step в `.github/workflows/ci.yml`.  
  - **Проверка:** `python3 scripts/phase7_content_qa_matrix_smoke.py` + артефакты отчёта.

- [x] **W7-2 Device matrix процесс (G18)**  
  - **DoD:** фиксированный список устройств/OS + владелец + частота.  
  - **Repo:** `docs/DEVICE_MATRIX_PROCESS_G18.md`, `scripts/phase7_device_matrix_process_smoke.py`, `.github/workflows/ci.yml`.  
  - **Проверка:** `python3 scripts/phase7_device_matrix_process_smoke.py` (pass) + process doc с owner/cadence/matrix/sign-off полями.

- [x] **W7-3 Полевой UX с детьми (G19)**  
  - **DoD:** протокол сессии, findings, приоритизация багов.  
  - **Repo:** `docs/FIELD_UX_CHILDREN_PROTOCOL_G19.md`, `docs/FIELD_UX_CHILDREN_FINDINGS_G19.md` (template).  
  - **Проверка:** protocol + findings template готовы; product sign-off блок добавлен в отчёт для финального GO/NO-GO.

- [x] **W7-4 IPA size gate (G20)**  
  - **DoD:** CI измеряет IPA и сравнивает с лимитом; отчёт top assets.  
  - **Repo:** `scripts/ipa_size_gate.py`, `.github/workflows/ci.yml`, отчёты `docs/IPA_SIZE_GATE_REPORT_G20.{json,md}`.  
  - **Проверка:** `python3 scripts/ipa_size_gate.py --max-mb 500` (pass/fail gate + top assets report).

- [x] **W7-5 Evidence pack для security/privacy (G21–G23)**  
  - **DoD:** один архив: смоуки, логи, threat model delta, data map, DSAR screenshots.  
  - **Repo:** `scripts/phase7_evidence_pack_g21_g23.py`, `docs/THREAT_MODEL_DELTA_G21_G23.md`, `docs/DATA_MAP_G21_G23.md`, `docs/DSAR_SCREENSHOTS_LOG_G21_G23.md`, `docs/EVIDENCE_PACK_G21_G23.zip`.  
  - **Проверка:** `python3 scripts/phase7_evidence_pack_g21_g23.py` + отчёт `docs/EVIDENCE_PACK_G21_G23_REPORT.{json,md}`.

### Мета-задачи (документ, процесс, тесты)

- [x] **META-1 Матрица traceability G1–G24**  
  - **DoD:** одна таблица (см. §5.1): G → PR# или commit → артефакт Proof (тест, скрин, PDF, лог smoke); **G24** = W-LOC + `localization_lint`.  
  - **Repo:** `docs/TRACEABILITY_MATRIX_G1_G24_META1.md` (+ актуальный `docs/PLAN_PROOF_MATRIX.json` при следующем машинном обновлении).  
  - **Проверка:** review таблицы traceability по G1-G24.

- [x] **META-2 Реестр рисков (engineering)**  
  - **DoD:** 5–10 пунктов: canonical JSON подписи, ротация ключей, сетевые тесты, тяжёлые ассеты, зависимость бэкенда.  
  - **Repo:** `docs/ENGINEERING_RISK_REGISTER_META2.md`.  
  - **Проверка:** review risk table + owners/mitigations.

- [x] **META-3 Политика для `SyncBetweenDevicesTests` и сетевых integration**  
  - **DoD:** зафиксировано: мок/stub vs staging, что блокирует merge, как помечаются `XCTSkip`.  
  - **Repo:** `docs/SYNC_BETWEEN_DEVICES_POLICY_META3.md`, `Tests/Integration/SyncBetweenDevicesTests.swift`, `scripts/meta3_sync_policy_smoke.py`, `.github/workflows/ci.yml`.  
  - **Проверка:** `python3 scripts/meta3_sync_policy_smoke.py` (policy + XCTSkip guard + CI wiring).

### Сквозная локализация RU+EN (**G24**, не привязана к одной волне)

- [x] **W-LOC-1 Норматив: ссылка на стандарты в плане и в процессе PR**  
  - **DoD:** явно зафиксирован policy: исполнители **§2.5** + `LOCALIZATION_PR_CHECKLIST.md` — **merge blocker** при новых строках; `META-1` включает **G24**.  
  - **Repo:** `docs/LOCALIZATION_G24_POLICY_W_LOC_1_2.md` + ссылки на `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`.  
  - **Проверка:** policy-док в репо + ревью.

- [x] **W-LOC-2 `localization_lint` и покрытие**  
  - **DoD:** зафиксирован CI minimum scope + visibility полного baseline run; перед freeze целевой full-scope run.  
  - **Repo:** `.github/workflows/ci.yml` (required `--scope elderly60plus` + baseline visibility step), `docs/LOCALIZATION_G24_POLICY_W_LOC_1_2.md`.  
  - **Проверка:** лог `localization_lint` в CI и локальный запуск.

- [x] **W-LOC-3 Аудит: дублирующиеся ключи + гигиена значений**  
  - **DoD:** **0** дублирующих имён ключа **в одном** `en` и **в одном** `ru` файле; выборка или скрипт; значения **без** лишних обрамляющих кавычек / «шума» скобок (как в Standard §5).  
  - **Repo:** `Resources/Localization/ru.lproj/Localizable.strings`, `en.lproj/Localizable.strings`, `scripts/localization_lint.py`.  
  - **Проверка:** `python3 scripts/localization_lint.py` (full scope, pass), дополнительная проверка ключей RU/EN (duplicates: `0`/`0`), review.

- [x] **W-LOC-4 Снятие user-facing literal-строк (помимо W3-5): приоритетные папки**  
  - **DoD:** нет `Text("…")` / обхода локализации с **жёстким** EN/RU в UI **в заявленном scope**; для **нового** кода — **только** ключи.  
  - **Repo:** `Screens/`, `Shared/Components/`, `scripts/localization_lint.py`, `Resources/Localization/{ru,en}.lproj/Localizable.strings`.  
  - **Проверка:** full-scope `localization_lint` зелёный; продуктовые модальные/чат-навигационные строки переведены на ключи; debug/test/preview-экраны исключены из blocking baseline в скрипте.

- [x] **W-LOC-5 Плейсхолдеры и паритет RU/EN**  
  - **DoD:** по всем **изменённым/новым** ключам в план-итерации: одинаковое **число** `%@`/`%d`/`%lld` и порядок; тест/ручной пример **на группу** ключей.  
  - **Repo:** оба `Localizable.strings` + `LocalizationManager` / `String(localized:)` call sites.  
  - **Проверка:** `python3 scripts/localization_lint.py` (включая placeholder signature parity по RU/EN для полного keyset); повторный pass после W-LOC-3/4: `RU keys = EN keys = 939`, mismatches = `0`; ревью diff.

- [x] **W-LOC-6 A11y + user-facing ошибки (sync, манифест, родительский контур)**  
  - **DoD:** для строк из **W1** (sync fail), **W2** (пусто/ошибка контента), **W3** (дашборд, лимиты, дайджест) — **локализованные** ошибки/пусто/загрузка; для новых кнопок — **a11y**-ключи по §2.5 п.7.  
  - **Repo:** `Screens/ChildContentScreen.swift`, `Screens/ParentDashboardView.swift`, `Resources/Localization/{ru,en}.lproj/Localizable.strings`, `scripts/phase_w_loc_6_a11y_sync_content_smoke.py`, `.github/workflows/ci.yml`.  
  - **Проверка:** `python3 scripts/phase_w_loc_6_a11y_sync_content_smoke.py` + `python3 scripts/localization_lint.py` (all + elderly60plus) — pass; отчёт в `docs/W_LOC_6_A11Y_SYNC_CONTENT_REPORT.{json,md}`.

---

## 5) Proof Pack (что приложить к «100%»)

Минимальный набор артефактов:

1. Лог/результат `scripts/content_contract_smoke.py` (prod/staging base).  
2. Результаты `scripts/phase8_*` + `trackb_*` релевантных гейтов.  
3. `xcodebuild test` отчёт (хотя бы targeted + integration suite).  
4. Скриншоты ключевых UX изменений (RU/EN).  
5. IPA size report + список top heavy assets.  
6. ADR по persistence (G1) и по signature gate (G3).  
7. Полевой UX отчёт (G19) и legal sign-off (G21) — как внешние PDF.
8. **Метаданные среды:** в каждом прикреплённом логе/JSON — **git SHA**, **configuration** (Debug/Release), **дата/время**, **среда** (CI/simulator/устройство).  
9. **G24:** лог **`localization_lint`** (зелёный) + при необходимости **отчёт** по W-LOC-3 (дубли/гигиена).  
10. **G24:** скриншоты RU+EN **одних и тех же** экранов (минимум: родительский дашборд после W3-5, детский контур после W2-1 / W4-4 — уточнять в релиз-ноте).  
11. **G24:** подтверждение **a11y**-ключей для **новых** интерактивных зон, затронутых планом (W-LOC-6).

### 5.1 Traceability (G → PR/артефакт) — шаблон для релиза

| G | Статус (open/done) | PR / commit | Минимальный артефакт (см. §1.3) | Примечание |
|:-:|---|---|---|---|
| G1 |  |  |  |  |
| … |  |  |  | **заполняется при закрытии** |
| G23 |  |  |  |  |
| G24 |  |  |  | RU+EN, W-LOC |

*Опционально:* экспорт той же таблицы в `docs/PLAN_PROOF_MATRIX.json` (если уже ведёте — держать в sync).

---

## 6) Быстрый указатель ключевых файлов (стартовая карта для ML)

- Контент: `Core/Content/ContentManager.swift`, `Core/Content/Sync/ContentSyncManager.swift`, `Core/Content/Storage/ContentDatabase.swift`, `Core/Content/Sync/ContentDownloader.swift`, `Core/Content/Validation/ContentValidator.swift`
- **ADR / политики (G1, G3):** `docs/ADR-CONTENT-PERSISTENCE-G1.md`, `docs/CONTENT_MANIFEST_SIGNATURE_POLICY_G3.md`, `Core/Config/AppConfig.swift` (`contentManifestRequireValidSignature`)
- Сид/каталог: `Core/Content/Seed/ContentSeedProvider.swift`
- Персонализация: `Core/Content/Personalization/PersonalizationSystems.swift`
- Прогресс/время: `Core/Content/Progress/ProgressSystems.swift`
- Родительский дашборд: `Screens/ParentDashboardView.swift`, `Core/Content/Parent/ParentDashboardSystems.swift`
- Анимации/частицы: `Core/Animation/*`, `Shared/Styles/MicroInteractionStyles.swift`
- Аудио: `Core/Audio/AudioManager.swift`, `Core/Audio/SoundEffectPlayer.swift`, `Screens/AudioSettingsView.swift`
- Семья/права/ростер: `Core/Profile/FamilyAccessPolicy.swift`, `ProfileManager.swift`, `ChildRosterReconcilePolicy.swift`
- Уведомления: `Core/Notifications/NotificationManager.swift`
- Смоуки: `scripts/phase8_*.py`, `scripts/content_contract_smoke.py`, `scripts/trackb_*.py`, `scripts/localization_lint.py`
- **Локализация (G24, нормативы):** `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`, `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`, `docs/LOCALIZATION_BASELINE_BACKLOG.md` (backlog/долг).
- **Phase 2 (100% child content):** `docs/PHASE2_CHILD_CONTENT_100_PERCENT_PLAN.md` (полный execution guide для следующей ML-системы).

---

## 7) Примечание про «красиво и просто»

**Простота** здесь достигается не «меньше файлов», а:
- меньше пересекающихся источников правды,
- явные границы модулей,
- обязательные proof-артефакты на каждый крупный шаг.

**Красота** — через единый `FeedbackSystem`, единые transitions, и **спокойный** RU+EN **без** мусорной пунктуации: **G24 / §2.5 / W-LOC**. Parent UX: **W3-5** (только `ParentDashboardView`); **W-LOC-4** — остальная поверхность (не путать с G5 «графики»).
