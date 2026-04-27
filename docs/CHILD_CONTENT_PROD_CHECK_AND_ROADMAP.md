# Детский контент: проверка прода, API и что добавить в план (выход на 100%)

Канон контракта: `docs/ENDPOINT_CONTRACT_AND_SERVER_ACCESS.md`.  
Подключение к хосту: `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` (сначала `curl` health, затем SSH по ключу).  
**Telegram Shop Bot** (другой продукт, `8090`, `/opt/aladdin-telegram-shop-bot`) — `telegram_stars_shop_bot/docs/ML_SYSTEM_HANDOFF_FINAL.md`; **не** является источником детского `ContentManifest` и **не** заменяет `GET /api/content/*` на `8002`.

---

## 1) Факты с production (проверено 2026-04-27)

| Проверка | Результат |
|----------|-----------|
| `curl -sS -m 8 http://149.154.65.180:8002/api/health` | `{"status":"ok"}` |
| `GET http://149.154.65.180:8002/api/content/manifest` | `HTTP 200`, тело `{"manifest":{...}}` |
| `GET .../api/content/delta?fromVersion=0` | `HTTP 200`, тело `{"delta":{...}}` |
| `python3 scripts/content_contract_smoke.py` (дефолтный `ALADDIN_API_BASE`) | **SMOKE RESULT: PASS** |
| Роуты на сервере | `misc_other_compat.py` — примерно строки **571** и **577** (`/api/content/manifest`, `/api/content/delta`) |

Итог: **публичный конвейер контента на основном бэкенде существует и отвечает**; плотность `items` на проде **меньше**, чем 275 строк матрицы (матрица — **продуктовый каталог/факт-учёт**, а не обязательный размер манифеста в день релиза).

---

## 2) Какой API **нужен** vs **необязателен** (для детского хаба и синка)

### Нужно, чтобы мобильный сетевой путь «засиял»

| Endpoint / поведение | Нужен? | Комментарий |
|----------------------|--------|-------------|
| `GET /api/content/manifest` | **Да** | Полный снимок категорий и элементов (конвертация DTO в домен: `Core/Content/Sync/NetworkContentAPIClient.swift`). |
| `GET /api/content/delta?fromVersion=n` | **Да** | Дельта между версиями; при ошибке клиент **может** запросить полный `manifest` (логика в `ContentSyncManager.sync`). |
| `openapi.json` содержит пути `content` | **Да для смоука** | `content_contract_smoke.py` требует наличия путей в OpenAPI. |
| Корректные `categoryId` + `ageBand` в элементах | **Да (продуктово)** | iOS фильтрует: `ContentManager.loadContent(for:ageBand:)`; несоответствие = «пусто» в категории. |

### Не обязательно в тот же день, что и UI-вехи по матрице

- **Полные 275 пунктов** в одном `manifest` — **нет**; поставка волнами, как в `wave` / сквады в `PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`.
- **Все** остальные **REST** из `AppConfig` (геймификация, семья, …) — **не** блокер для *открытия карточек контента*; нужны **для** семейного продукта и монетизации отдельно.
- **Telegram-бот** и Partner API `8090` — **другой контур**; в плане детского контента **не** ставить как зависимость для `manifest`.

### iOS-фоллбек, если сеть/сервер не отдали манифест

- `DefaultContentAPIClient` возвращает `ContentSeedProvider.shared.initialManifest()` (см. комментарий «until backend… finalized») — **локальная** база для офлайна/фоллбека; для прод-политики обхода родительских/платёжных API см. workspace-правило `prod-no-mock-bypass` и бизнес-правила.

---

## 3) Что **добавить/улучшить в плане** (чтобы после реализации «всё стыковалось»)

1. **Связка матрица 275 ↔ бэкенд-манифест**  
   При закрытии волны (Wn): пункт «поднять `manifest_version` + проверить `content_contract_smoke.py` + сценарий `delta` с предыдущей версии».

2. **Политика версий приложения**  
   В манифесте поле `min_supported_app_version` должно **синхронизироваться** с минимальной версией в сторе перед принудительным нет-совместимым изменением схемы DTO.

3. **Подпись манифеста (если включили на iOS `contentManifestRequireValidSignature`)**  
   План на бэке: канон тела для подписи, деплой публичного ключа в `AppConfig.contentManifestSigningPublicKeyBase64`, тест `403/invalid` при подделке (см. `ContentSyncManager.validateManifestSignatureIfNeeded`).

4. **Полезная нагрузка**  
   Для пунктов с `payloadURL` + `checksumSHA256` — runbook: хостинг, HTTPS, бюджет кэша (`ContentManifestPayloadHydration` + `ContentPayloadDiskCachePolicy`).

5. **Локализация контента**  
   Сейчас `metadata` часто RU-ориентир; план: либо многоязычные поля в манифесте, либо ключи + `Localizable.strings` (см. `PLAN_ITEM_275_AUDIT_REPORT.md` §1a).

6. **Наблюдаемость**  
   Метрика/лог: доля успешного `NetworkContentAPIClient` vs тихий fallback (без PII) — чтобы не путать «релиз прошёл» с «клиент живёт на сиде».

7. **E2E-приёмка**  
   После деплоя бэка: `curl` manifest + запуск приложения + убедиться, что `ContentManager` подхватил новую версию (foreground refresh / BG refresh по `ContentBackgroundSyncScheduler`).

---

## 4) Что **ещё реализовать** на бэкенде (относительно амбиций 275)

- Расширение **категорий и** `items` по всем `child_interface_category_*` из `ChildCategoryKey` / матрицы, с согласованным `ageBand` (iOS-тип `ContentAgeBand`).
- Регресс: уникальность `item.id`, ссылки `categoryId` → существующие категории, соблюдение **минимума** для smoke (`ALADDIN_CONTENT_MIN_ITEMS_PER_CATEGORY`, по умолчанию 3) — **или** согласованное снижение в CI.
- (Опционально) **Подпись** и строгая валидация, если продукт требует.

---

## 5) Краткое разделение ответственности

| Слой | Роль |
|------|------|
| **iOS** | `ContentManager` + `ContentSyncManager`, UX в `ChildContent*`, ветки в `ChildContentExperienceScreen`, сид. |
| **/opt/aladdin-backend** | `manifest` / `delta`, в будущем — плотное наполнение, подписи, неизменяемый канон. |
| **Telegram shop bot** | Магазин/Stars; **не** источник детского `manifest`. |

Этот файл — **живой** список доп. пунктов плана: при изменении прода обновляйте §1 датой и ссылками на коммит/runbook.
